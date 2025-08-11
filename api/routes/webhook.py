"""
Rutas para webhooks de WhatsApp usando WAHA
"""
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Dict, Any

router = APIRouter()

@router.get("/test")
async def webhook_test():
    """
    Endpoint de prueba para verificar que el webhook está accesible
    """
    return {
        "status": "webhook_ready",
        "service": "Korei Assistant",
        "webhook_url": "https://recollecto.andreivarela.com/webhook/c0e371b3-fa4d-4313-a29b-5dc892f5124c/waha",
        "ready_for": ["message", "status", "presence"]
    }

@router.post("")
async def webhook_handler(
    request: Request, 
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Maneja webhooks de WAHA
    Documentación WAHA: https://waha.devlike.pro/docs/how-to/webhooks
    """
    try:
        data = await request.json()
        
        # Log completo del payload para debugging
        logger.info(f"📥 Webhook WAHA recibido: {data}")
        
        # WAHA estructura: {"event": "message", "session": "default", "payload": {...}}
        event_type = data.get("event")
        session = data.get("session", "unknown")
        payload = data.get("payload", {})
        
        if not event_type:
            return {"status": "ignored", "reason": "no event type"}
        
        logger.info(f"🔄 Evento: {event_type} | Sesión: {session}")
        
        # Solo procesar mensajes
        if event_type != "message":
            logger.info(f"⏭️ Ignorando evento: {event_type}")
            return {"status": "ignored", "event": event_type}
        
        # Ignorar mensajes propios
        if payload.get("fromMe", False):
            logger.info("⏭️ Ignorando mensaje propio")
            return {"status": "ignored", "reason": "own message"}
        
        # IDEMPOTENCIA: Verificar si ya procesamos este mensaje
        message_id = payload.get("id")
        if message_id:
            # Verificar si ya existe en la DB
            from core.supabase import supabase
            try:
                existing = supabase._get_client().table("entries").select("id").eq(
                    "id_waha", message_id
                ).execute()
                
                if existing.data:
                    logger.info(f"⚠️ Mensaje duplicado ignorado: {message_id}")
                    return {"status": "duplicate", "message_id": message_id}
            except Exception as e:
                logger.warning(f"Error verificando idempotencia: {e}")
                # Continúa procesando si hay error en verificación
        
        # Procesar en background para respuesta rápida
        background_tasks.add_task(
            process_message_async,
            payload,
            session
        )
        
        return {"status": "accepted", "timestamp": data.get("timestamp")}
        
    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return {"status": "error", "message": str(e)}

async def process_message_async(payload: Dict[str, Any], session: str = "default"):
    """
    Procesa mensaje de WAHA de forma asíncrona
    
    Estructura de payload de WAHA:
    {
        "id": "message_id",
        "timestamp": 1234567890,
        "from": "1234567890@c.us",
        "fromMe": false,
        "body": "Mensaje de texto",
        "type": "text|image|document|audio|video",
        "notifyName": "Nombre del contacto"
    }
    """
    try:
        # Extraer información del mensaje
        message_id = payload.get("id", "unknown")
        phone = payload.get("from", "").replace("@c.us", "")
        message_type = payload.get("type", "text")
        notify_name = payload.get("notifyName", "Usuario")
        timestamp = payload.get("timestamp", 0)
        
        logger.info(f"📱 Procesando mensaje de {notify_name} ({phone})")
        logger.info(f"🆔 ID: {message_id} | Tipo: {message_type} | Sesión: {session}")
        
        # Obtener contexto completo del usuario
        from core.supabase import supabase
        user_context = await supabase.get_user_with_context(phone)
        
        # Procesar según tipo de mensaje
        if message_type == "text":
            body = payload.get("body", "")
            logger.info(f"💬 Texto: '{body}'")
            
            # Verificar si es un comando
            if body.startswith('/'):
                from handlers.command_handler import command_handler
                command = body.split()[0].lower()
                result = await command_handler.handle_command(command, body, user_context)
                
                # TODO: Enviar respuesta al usuario via WhatsApp
                logger.info(f"🤖 Comando procesado: {result}")
            else:
                # Procesar mensaje normal con Gemini AI  
                from services.gemini import gemini_service
                result = await gemini_service.process_message(body, user_context)
                
                # TODO: Guardar en database y responder
                logger.info(f"🧠 IA procesada: {result}")
            
        elif message_type == "image":
            caption = payload.get("caption", "")
            logger.info(f"🖼️ Imagen recibida. Caption: '{caption}'")
            
            # TODO: Procesar imagen con Gemini Vision
            # await process_image_message(payload, user_info)
            
        elif message_type in ["audio", "voice"]:
            logger.info(f"🎵 Audio recibido")
            
            # TODO: Transcribir y procesar con Gemini
            # await process_audio_message(payload, user_info)
            
        else:
            logger.info(f"📎 Tipo de mensaje no soportado: {message_type}")
        
        # TODO: Guardar en Supabase
        # await supabase_service.create_entry(entry_data)
        
        logger.info("✅ Mensaje procesado exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")
        # TODO: Enviar mensaje de error al usuario
        # await whatsapp_service.send_message(phone, "❌ Error procesando tu mensaje")