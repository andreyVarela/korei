"""
Rutas para webhooks de WhatsApp usando WAHA
"""
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Dict, Any


router = APIRouter()

# Endpoint para WhatsApp Cloud API (Meta)
@router.get("/meta")
async def meta_webhook_verify(request: Request):
    """
    Verificación de webhook para WhatsApp Cloud API (Meta)
    Meta envía un GET con los parámetros:
    - hub.mode
    - hub.challenge
    - hub.verify_token
    """
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    # Cambia este token por el que configuraste en Meta
    VERIFY_TOKEN = "TU_TOKEN_VERIFICACION"
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return JSONResponse(content=challenge)
    return JSONResponse(content="Invalid verification", status_code=403)

@router.post("/meta")
async def meta_webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """
    Recibe mensajes y eventos de WhatsApp Cloud API (Meta)
    Documentación: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples/
    """
    try:
        data = await request.json()
        logger.info(f"📥 Webhook Meta recibido: {data}")
        # Procesar cada entry
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    # Idempotencia: verificar si ya procesamos este mensaje
                    message_id = message.get("id")
                    if message_id:
                        from core.supabase import supabase
                        try:
                            existing = supabase._get_client().table("entries").select("id").eq(
                                "id_meta", message_id
                            ).execute()
                            if existing.data:
                                logger.info(f"⚠️ Mensaje duplicado ignorado: {message_id}")
                                continue
                        except Exception as e:
                            logger.warning(f"Error verificando idempotencia Meta: {e}")
                    # Procesar en background
                    background_tasks.add_task(
                        process_meta_message_async,
                        message,
                        value
                    )
        return {"status": "accepted"}
    except Exception as e:
        logger.error(f"❌ Error en webhook Meta: {e}")
        return {"status": "error", "message": str(e)}

async def handle_button_interaction(button_id: str, user_context: dict):
    """
    Maneja las interacciones con botones
    """
    try:
        if button_id.startswith("complete_task_"):
            # Extraer ID de la tarea
            task_id = button_id.replace("complete_task_", "")
            
            # Marcar tarea como completada
            from core.supabase import supabase
            await supabase.update_entry(task_id, {"status": "completed"})
            
            # Obtener datos de la tarea para confirmación
            task_data = await supabase.get_entry_by_id(task_id)
            task_description = task_data.get('description', 'Tarea') if task_data else 'Tarea'
            
            # Enviar confirmación
            from services.whatsapp_cloud import whatsapp_cloud_service
            confirmation_message = f"✅ **Tarea completada**\n\n📝 {task_description}\n\n🎉 ¡Bien hecho!"
            
            await whatsapp_cloud_service.send_text_message(
                to=user_context['whatsapp_number'],
                message=confirmation_message
            )
            
            # Si hay integración con Todoist, marcar allí también
            if task_data and task_data.get('external_service') == 'todoist':
                external_id = task_data.get('external_id')
                if external_id:
                    try:
                        from services.integrations.integration_manager import integration_manager
                        todoist_integration = await integration_manager.get_user_integration(
                            user_context['id'], 'todoist'
                        )
                        if todoist_integration:
                            await todoist_integration.complete_task(external_id)
                            logger.info(f"TODOIST: Tarea {external_id} marcada como completada")
                    except Exception as todoist_error:
                        logger.error(f"TODOIST ERROR: {todoist_error}")
            
            logger.info(f"✅ Tarea {task_id} completada por botón")
            
        else:
            logger.warning(f"Botón no reconocido: {button_id}")
            
    except Exception as e:
        logger.error(f"Error manejando interacción de botón: {e}")

async def process_meta_message_async(message: dict, value: dict):
    """
    Procesa mensaje de WhatsApp Cloud API (Meta) de forma asíncrona
    """

    try:
        message_id = message.get("id", "unknown")
        phone = message.get("from", "")
        message_type = message.get("type", "text")
        timestamp = message.get("timestamp", 0)
        logger.info(f"📱 Procesando mensaje Meta de {phone}")
        logger.info(f"🆔 ID: {message_id} | Tipo: {message_type}")
        from core.supabase import supabase
        # Buscar usuario existente
        user = await supabase.get_user_by_phone(phone)
        body = message.get("text", {}).get("body", "") if message_type == "text" else None
        # Si no existe el usuario
        if not user:
            logger.info(f"🔍 Usuario no encontrado para {phone}")
            # Verificar si el mensaje es para registrarse (ejemplo: comando /registrar)
            # Verificar comandos de registro
            registration_commands = ["/registrar", "/register", "/registro"]
            is_registration = message_type == "text" and body and any(body.strip().lower().startswith(cmd) for cmd in registration_commands)
            if is_registration:
                logger.info(f"✅ Detectado comando de registro: {body}")
                # RESPUESTA INMEDIATA SIN COMPLICACIONES
                try:
                    from services.whatsapp_cloud import whatsapp_cloud_service
                    simple_response = f"🔄 **Registro detectado**\n\nTu número: {phone}\nComando: {body}\n\n✅ Sistema funcionando correctamente!"
                    
                    await whatsapp_cloud_service.send_text_message(
                        to=phone,
                        message=simple_response
                    )
                    logger.info(f"✅ Respuesta simple enviada a {phone}")
                except Exception as simple_error:
                    logger.error(f"❌ Error en respuesta simple: {simple_error}")
            else:
                logger.info(f"⏭️ Usuario no existe y no es registro. Ignorando mensaje Meta de {phone}")
                return  # No responde ni procesa
        else:
            # Si el usuario existe y tiene el pago activo, procesar normalmente
            if user.get("payment") == True:
                user_context = await supabase.get_user_with_context(phone)
                if message_type == "text":
                    logger.info(f"💬 Texto: '{body}'")
                    if body.startswith('/'):
                        from handlers.command_handler import command_handler
                        command = body.split()[0].lower()
                        result = await command_handler.handle_command(command, body, user_context)
                        logger.info(f"🤖 Comando procesado Meta: {result}")
                    else:
                        from services.gemini import gemini_service
                        result = await gemini_service.process_message(body, user_context)
                        logger.info(f"🧠 IA procesada Meta: {result}")
                elif message_type == "image":
                    logger.info(f"🖼️ Imagen recibida Meta")
                    # TODO: Procesar imagen con Gemini Vision
                elif message_type in ["audio", "voice"]:
                    logger.info(f"🎵 Audio recibido Meta")
                    # TODO: Transcribir y procesar con Gemini
                elif message_type == "interactive":
                    logger.info(f"🔘 Mensaje interactivo recibido Meta")
                    # Manejar respuesta de botón
                    interactive_data = message.get("interactive", {})
                    if interactive_data.get("type") == "button_reply":
                        button_reply = interactive_data.get("button_reply", {})
                        button_id = button_reply.get("id", "")
                        
                        logger.info(f"🔘 Botón presionado: {button_id}")
                        
                        # Procesar acción del botón
                        await handle_button_interaction(button_id, user_context)
                else:
                    logger.info(f"📎 Tipo de mensaje no soportado Meta: {message_type}")
                # TODO: Guardar en Supabase
                logger.info("✅ Mensaje Meta procesado exitosamente")
            else:
                logger.info(f"⏭️ Usuario {phone} no tiene pago activo (payment={user.get('payment')}). Ignorando mensaje.")
                return
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje Meta: {e}")
        # TODO: Enviar mensaje de error al usuario

@router.get("/test")
async def webhook_test():
    """
    Endpoint de prueba que también testa WhatsApp
    """
    test_phone = "50699999999"
    debug_info = {"steps": [], "errors": []}
    
    try:
        debug_info["steps"].append("1. Testing WhatsApp service...")
        from services.whatsapp_cloud import whatsapp_cloud_service
        debug_info["steps"].append("✅ WhatsApp service imported")
        
        debug_info["steps"].append("2. Getting headers and config...")
        headers = whatsapp_cloud_service._get_headers()
        base_url = whatsapp_cloud_service._get_base_url()
        debug_info["steps"].append(f"✅ Headers: {bool(headers.get('Authorization'))}")
        debug_info["steps"].append(f"✅ Base URL: {base_url}")
        
        debug_info["steps"].append("3. Attempting to send test message...")
        try:
            result = await whatsapp_cloud_service.send_text_message(
                to=test_phone,
                message="🧪 Test message from endpoint"
            )
            debug_info["steps"].append(f"✅ Message sent: {result}")
        except Exception as wa_error:
            debug_info["errors"].append(f"❌ WhatsApp error: {str(wa_error)}")
        
    except Exception as e:
        debug_info["errors"].append(f"❌ General error: {str(e)}")
    
    return {
        "status": "webhook_ready",
        "service": "Korei Assistant UPDATED v2.1", 
        "webhook_url": "https://korei.duckdns.org/webhook/cloud",
        "ready_for": ["message", "status", "presence"],
        "timestamp": "2025-08-21 06:30:00",
        "debug": debug_info
    }

@router.get("/simulate-register")
async def simulate_register():
    """Simula exactamente el flujo de registro para ver dónde falla"""
    test_phone = "50699999999"
    errors = []
    steps = []
    
    try:
        steps.append("1. Importando supabase...")
        from core.supabase import supabase
        steps.append("✅ Supabase importado")
        
        steps.append("2. Verificando si usuario existe...")
        user = await supabase.get_user_by_phone(test_phone)
        steps.append(f"✅ Usuario existente: {bool(user)}")
        
        if not user:
            steps.append("3. Usuario no existe, creando usuario básico...")
            try:
                basic_user = await supabase.get_or_create_user(test_phone, "Usuario")
                steps.append(f"✅ Usuario creado: {basic_user}")
            except Exception as e:
                errors.append(f"❌ Error creando usuario: {e}")
                steps.append(f"❌ Falló creación de usuario: {e}")
                
            steps.append("4. Obteniendo contexto...")
            try:
                user_context = await supabase.get_user_with_context(test_phone)
                steps.append(f"✅ Contexto: ID={user_context.get('id')}, phone={user_context.get('whatsapp_number')}")
            except Exception as e:
                errors.append(f"❌ Error obteniendo contexto: {e}")
                steps.append(f"❌ Falló contexto: {e}")
                user_context = {"id": None, "whatsapp_number": test_phone}
                
            if user_context.get('id'):
                steps.append("5. Ejecutando comando de registro...")
                try:
                    from handlers.command_handler import command_handler
                    result = await command_handler.handle_command("/register", "/register", user_context)
                    steps.append(f"✅ Comando ejecutado: {result.get('type', 'unknown')}")
                except Exception as e:
                    errors.append(f"❌ Error en comando: {e}")
                    steps.append(f"❌ Falló comando: {e}")
            else:
                errors.append("❌ Usuario sin ID válido")
                steps.append("❌ No se puede ejecutar comando sin ID de usuario")
        else:
            steps.append("3. Usuario ya existe, saltando creación...")
            
        return {
            "status": "simulation_complete",
            "test_phone": test_phone,
            "steps": steps,
            "errors": errors,
            "error_count": len(errors)
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "simulation_failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "steps": steps,
            "errors": errors
        }

@router.get("/debug-registrar")
async def debug_registrar():
    """
    Endpoint para debug del proceso de registro
    """
    try:
        test_phone = "50688888888"
        debug_steps = []
        
        from core.supabase import supabase
        
        # Paso 1: Verificar si usuario existe
        debug_steps.append("🧪 PASO 1: Verificando si usuario existe...")
        try:
            user = await supabase.get_user_by_phone(test_phone)
            debug_steps.append(f"✅ Usuario existente: {user}")
        except Exception as e1:
            debug_steps.append(f"❌ Error verificando usuario: {e1}")
            user = None
        
        # Paso 2: Intentar obtener contexto
        debug_steps.append("🧪 PASO 2: Obteniendo contexto...")
        try:
            user_context = await supabase.get_user_with_context(test_phone)
            debug_steps.append(f"✅ Contexto obtenido: {user_context}")
        except Exception as e2:
            debug_steps.append(f"❌ Error obteniendo contexto: {e2}")
            user_context = {"whatsapp_number": test_phone, "id": None, "name": "Usuario"}
        
        # Paso 3: Intentar comando de registro
        debug_steps.append("🧪 PASO 3: Ejecutando comando de registro...")
        try:
            from handlers.command_handler import command_handler
            result = await command_handler.handle_command("/registrar", "/registrar", user_context)
            debug_steps.append(f"✅ Resultado del comando: {result}")
        except Exception as e3:
            debug_steps.append(f"❌ Error ejecutando comando: {e3}")
            import traceback
            debug_steps.append(f"❌ Traceback: {traceback.format_exc()}")
            result = None
        
        return {
            "status": "debug_complete",
            "test_phone": test_phone,
            "user_exists": bool(user),
            "debug_steps": debug_steps,
            "final_user_context": user_context,
            "command_result": result
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

@router.post("/test-image-internal")
async def test_image_internal():
    """
    Endpoint de prueba interno para verificar el procesamiento de imágenes
    """
    try:
        from core.supabase import supabase
        
        # Usuario de prueba
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Simular payload
        payload = {
            "id": "test_internal_123",
            "type": "image",
            "from": f"{test_phone}@c.us",
            "caption": ""
        }
        
        # Ejecutar procesamiento
        await process_image_message(payload, user_context, "")
        
        return {
            "status": "success",
            "message": "Procesamiento de imagen completado",
            "check_logs": "Revisa los logs del servidor para ver el resultado"
        }
        
    except Exception as e:
        logger.error(f"Error en test interno: {e}")
        return {
            "status": "error",
            "message": str(e)
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
            
            # Procesar imagen con análisis inteligente
            await process_image_message(payload, user_context, caption)
            
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

async def process_image_message(payload: Dict[str, Any], user_context: Dict[str, Any], caption: str = ""):
    """Procesa mensajes de imagen desde WAHA"""
    try:
        # Simular descarga de imagen (por ahora)
        # En WAHA, necesitarías hacer una llamada para descargar la imagen
        # Para testing, voy a crear datos de imagen simulados
        
        logger.info(f"🖼️ Procesando imagen para usuario {user_context.get('whatsapp_number', 'unknown')}")
        
        # TESTING: Simular procesamiento de imagen con contexto real
        # En el futuro, esto descargaría la imagen real desde WAHA
        
        # Simular el contexto extraído de imagen SINPE (genérico para cualquier usuario)
        user_name_full = user_context.get('name', 'Usuario')
        simulated_context = f"""Veo una notificación de transacción SINPE Móvil del Banco de Costa Rica. La notificación indica que se realizó una Transferencia SINPE Móvil a {user_name_full.upper()} por 10,000.00 colones. Motivo: Transferencia SINPE. Ref: 2025081715284001625138542"""
        
        fake_image_data = b"fake_image_data_placeholder"
        
        # TESTING: Llamar directamente a gemini con el contexto simulado
        from services.gemini import gemini_service
        result = await gemini_service.process_image(fake_image_data, simulated_context, user_context)
        
        logger.info(f"🖼️ Imagen procesada: tipo={result.get('type')}, desc={result.get('description', '')[:50]}...")
        
        # DEBUG CRÍTICO: Interceptar el resultado completo de Gemini
        logger.info(f"🔍 DEBUG GEMINI RESULT COMPLETO: {result}")
        
        # Formatear y enviar respuesta
        from services.formatters import message_formatter
        logger.info(f"🔍 Formateando respuesta con tipo: {result.get('type')}")
        response_message = message_formatter.format_entry_response(result)
        logger.info(f"📝 Respuesta formateada: {response_message[:100]}...")
        
        from services.whatsapp_cloud import whatsapp_cloud_service
        await whatsapp_cloud_service.send_text_message(
            to=user_context['whatsapp_number'],
            message=response_message
        )
        
        # Guardar en base de datos
        if user_context.get('id'):
            from core.supabase import supabase
            entry_data = {
                **result,
                "user_id": user_context['id']
            }
            entry = await supabase.create_entry(entry_data)
            logger.info(f"🖼️ Entrada guardada en BD: {entry.get('id') if entry else 'error'}")
        
        logger.info(f"🖼️ Imagen procesada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error procesando imagen: {e}")
        
        # Enviar mensaje de error
        from services.whatsapp_cloud import whatsapp_cloud_service
        await whatsapp_cloud_service.send_text_message(
            to=user_context['whatsapp_number'],
            message="❌ No pude procesar tu imagen. 💡 😅 Perdón, no pude procesar eso correctamente. 💡 Puedes intentar de nuevo o escribir /help si necesitas una mano. ¡Estoy aquí para ayudarte!"
        )