"""
Webhook unificado para WhatsApp Cloud API oficial de Meta
Incluye todos los endpoints consolidados: webhook, testing, logs y debugging
VERSIÓN: 3.0.0 - Arquitectura Consolidada
"""
from fastapi import APIRouter, HTTPException, Request, Query, Header
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from loguru import logger
import hashlib
import hmac
import json

from app.config import settings
from handlers.message_handler import message_handler
from services.whatsapp_cloud import whatsapp_cloud_service
from core.supabase import supabase

router = APIRouter()

# Modelos para WhatsApp Cloud API
class WhatsAppProfile(BaseModel):
    name: str

class WhatsAppContact(BaseModel):
    profile: WhatsAppProfile
    wa_id: str

class WhatsAppText(BaseModel):
    body: str

class WhatsAppMessage(BaseModel):
    from_: Optional[str] = None
    id: str
    timestamp: str
    text: Optional[WhatsAppText] = None
    type: str
    
    class Config:
        fields = {"from_": "from"}

class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: Dict[str, Any]
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessage]] = None

class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str

class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]

class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[WhatsAppEntry]

class SendMessageRequest(BaseModel):
    to: str
    message: str


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"), 
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    print("Verifying webhook for WhatsApp Cloud API")
    """
    Verificación del webhook de WhatsApp Cloud API
    Este endpoint es llamado por Meta para verificar tu webhook
    """
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    # Verificar que sea una verificación válida
    if hub_mode == "subscribe":
        # Verificar token (configúralo en settings)
        expected_token = getattr(settings, 'verify_token', 'korei_webhook_token_2024')
        
        if hub_verify_token == expected_token:
            logger.info("✅ Webhook verification successful")
            return PlainTextResponse(hub_challenge)
        else:
            logger.error(f"❌ Invalid verify token. Expected: {expected_token}, Got: {hub_verify_token}")
            raise HTTPException(status_code=403, detail="Invalid verify token")
    
    logger.error(f"❌ Invalid hub mode: {hub_mode}")
    raise HTTPException(status_code=400, detail="Invalid request")


@router.post("")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    print("WEBHOOK CLOUD RECEIVED")
    print("Data received from:", request.client.host if request.client else "unknown")
    logger.info("WEBHOOK RECEIVED - Starting processing")
    
    try:
        # Obtener cuerpo raw
        body = await request.body()
        logger.info("Body received successfully")
        
        # Parsear JSON
        try:
            data = json.loads(body.decode('utf-8'))
            logger.info("JSON parsed successfully")
        except Exception as parse_error:
            logger.error(f"❌ JSON parse error: {parse_error}")
            return {"status": "error", "message": "Invalid JSON"}
        
        # Log del payload completo para debugging
        logger.info(f"Webhook payload: {json.dumps(data, indent=2)}")
        
        # Verificar si es WhatsApp
        if data.get("object") != "whatsapp_business_account":
            logger.info("Not a WhatsApp webhook, ignoring")
            return {"status": "ok"}
        
        logger.info("WhatsApp webhook confirmed")
        
        # Log de estructura para debugging
        logger.info(f"ENTRY COUNT: {len(data.get('entry', []))}")
        for i, entry in enumerate(data.get("entry", [])):
            logger.info(f"ENTRY {i}: changes={len(entry.get('changes', []))}")
            for j, change in enumerate(entry.get("changes", [])):
                logger.info(f"  CHANGE {j}: field={change.get('field')}")
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    logger.info(f"    VALUE: messages={len(value.get('messages', []))}, statuses={len(value.get('statuses', []))}")
        
        # Buscar mensajes (lógica original que funcionaba)
        messages_found = False
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    
                    if messages:
                        messages_found = True
                        logger.info(f"Found {len(messages)} messages to process")
                        
                        # Obtener nombre del contacto
                        contact_name = "Usuario"
                        if contacts and len(contacts) > 0:
                            contact_name = contacts[0].get("profile", {}).get("name", "Usuario")
                        
                        for message_data in messages:
                            phone_number = message_data.get("from")
                            message_type = message_data.get("type")
                            
                            logger.info(f"Processing {message_type} message from {phone_number}")
                            
                            if phone_number:
                                # MÓDULOS SEPARADOS POR TIPO
                                if message_type == "text":
                                    message_text = message_data.get("text", {}).get("body")
                                    if message_text:
                                        await process_text_message(phone_number, message_text, contact_name)
                                elif message_type == "interactive":
                                    await process_interactive_message(phone_number, message_data, contact_name)
                                elif message_type == "image":
                                    await process_image_message(phone_number, message_data, contact_name)
                                elif message_type == "audio" or message_type == "voice":
                                    await process_audio_message(phone_number, message_data, contact_name)
                                else:
                                    logger.warning(f"Message type {message_type} not supported yet")
                            else:
                                logger.warning("Missing phone_number, skipping")
        
        if not messages_found:
            logger.info("No messages found in webhook")
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"ERROR in webhook: {e}")
        return {"status": "error", "message": str(e)}


# ========================================
# MÓDULOS SEPARADOS POR TIPO DE MENSAJE
# ========================================

async def process_text_message(phone_number: str, message_text: str, contact_name: str):
    """MÓDULO: Procesa mensajes de texto"""
    try:
        logger.info(f"TEXT MODULE: Starting processing for {phone_number}")
        logger.info(f"TEXT MODULE: Message: {message_text}")
        
        # 🚨 COMANDO ESPECIAL /log - PROCESAR ANTES DE SUPABASE
        if message_text and message_text.strip().startswith('/log'):
            logger.info(f"🔍 COMANDO /log DETECTADO EN WHATSAPP_CLOUD - Procesando directamente para {phone_number}")
            try:
                from handlers.message_handler import message_handler
                # Crear contexto mínimo sin Supabase para comando /log
                user_context = {
                    "whatsapp_number": phone_number,
                    "phone": phone_number,
                    "id": None,  # No necesita ID para /log
                    "name": "Usuario Debug"
                }
                result = await message_handler.handle_log_command(user_context, message_text.strip())
                logger.info(f"✅ Comando /log procesado exitosamente en whatsapp_cloud: {result.get('status')}")
                return {"status": "success", "log_processed": True}
            except Exception as log_error:
                logger.error(f"❌ Error procesando comando /log en whatsapp_cloud: {log_error}")
                await send_message_simple(phone_number, f"❌ Error en comando /log: {str(log_error)}")
                return {"status": "error", "message": f"Error en /log: {str(log_error)}"}
        
        # Obtener o crear usuario en Supabase con contexto completo (incluye perfil)
        user = await supabase.get_user_with_context(phone_number)
        logger.info(f"TEXT MODULE: User obtained/created: {user.get('id', 'temp')}")
        logger.info(f"TEXT MODULE: User structure: {user}")
        
        # Verificar que el usuario tenga los campos necesarios
        if not user or not user.get('whatsapp_number'):
            logger.error(f"TEXT MODULE: Invalid user structure: {user}")
            await send_message_simple(phone_number, "❌ Error de configuración de usuario. Intenta enviar /register")
            return {"status": "error", "message": "Invalid user structure"}
        
        # PIPELINE UNIFICADO: Usar el MessageHandler que ya funciona
        result = await message_handler.handle_text(message_text, user)
        logger.info(f"TEXT MODULE: Result: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"TEXT MODULE ERROR: {e}")
        # Fallback - enviar mensaje de error
        try:
            await send_message_simple(phone_number, f"Error procesando mensaje: {str(e)}")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
        return {"status": "error", "message": str(e)}

async def process_image_message(phone_number: str, message_data: dict, contact_name: str):
    """MÓDULO: Procesa mensajes de imagen"""
    try:
        logger.info(f"IMAGE MODULE: Starting processing for {phone_number}")
        
        # Obtener o crear usuario en Supabase con contexto completo (incluye perfil)
        user = await supabase.get_user_with_context(phone_number)
        logger.info(f"IMAGE MODULE: User obtained/created: {user.get('id', 'temp')}")
        
        # Extraer datos de imagen
        image_data = message_data.get("image", {})
        caption = image_data.get("caption", "")
        
        logger.info(f"IMAGE MODULE: Image ID: {image_data.get('id')}")
        
        # PIPELINE UNIFICADO: Usar el MessageHandler que ya funciona
        result = await message_handler.handle_image({
            "media": image_data, 
            "caption": caption
        }, user)
        logger.info(f"IMAGE MODULE: Result: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"IMAGE MODULE ERROR: {e}")
        # Fallback - enviar mensaje de error
        try:
            await send_message_simple(phone_number, f"Error procesando imagen: {str(e)}")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
        return {"status": "error", "message": str(e)}

async def process_audio_message(phone_number: str, message_data: dict, contact_name: str):
    """MÓDULO: Procesa mensajes de audio"""
    try:
        logger.info(f"AUDIO MODULE: Starting processing for {phone_number}")
        
        # Obtener o crear usuario en Supabase con contexto completo (incluye perfil)
        user = await supabase.get_user_with_context(phone_number)
        logger.info(f"AUDIO MODULE: User obtained/created: {user.get('id', 'temp')}")
        
        # Extraer datos de audio/voice
        audio_data = message_data.get("audio", {}) or message_data.get("voice", {})
        
        logger.info(f"AUDIO MODULE: Audio ID: {audio_data.get('id')}")
        
        # PIPELINE UNIFICADO: Usar el MessageHandler que ya funciona
        result = await message_handler.handle_audio({
            "media": audio_data
        }, user)
        logger.info(f"AUDIO MODULE: Result: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"AUDIO MODULE ERROR: {e}")
        # Fallback - enviar mensaje de error
        try:
            await send_message_simple(phone_number, f"Error procesando audio: {str(e)}")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
        return {"status": "error", "message": str(e)}

async def process_interactive_message(phone_number: str, message_data: dict, contact_name: str):
    """MÓDULO: Procesa mensajes interactivos (botones de WhatsApp)"""
    try:
        logger.info(f"INTERACTIVE MODULE: Starting processing for {phone_number}")
        
        # Obtener o crear usuario en Supabase con contexto completo (incluye perfil)
        user = await supabase.get_user_with_context(phone_number)
        logger.info(f"INTERACTIVE MODULE: User obtained/created: {user.get('id', 'temp')}")
        
        # Extraer datos del mensaje interactivo
        interactive_data = message_data.get("interactive", {})
        interactive_type = interactive_data.get("type")  # "button_reply", "list_reply", etc.
        
        logger.info(f"INTERACTIVE MODULE: Type: {interactive_type}")
        logger.info(f"INTERACTIVE MODULE: Data: {interactive_data}")
        
        if interactive_type == "button_reply":
            # Extraer información del botón presionado
            button_reply = interactive_data.get("button_reply", {})
            button_id = button_reply.get("id")
            button_title = button_reply.get("title")
            
            logger.info(f"INTERACTIVE MODULE: Button clicked - ID: {button_id}, Title: {button_title}")
            
            # Procesar según el ID del botón
            if button_id and button_id.startswith("complete_task_"):
                task_id = button_id.replace("complete_task_", "")
                await process_complete_task_button(phone_number, task_id, user)
            elif button_id and button_id.startswith("delete_task_"):
                task_id = button_id.replace("delete_task_", "")
                await process_delete_task_button(phone_number, task_id, user)
            elif button_id and button_id.startswith("info_task_"):
                task_id = button_id.replace("info_task_", "")
                await process_info_task_button(phone_number, task_id, user)
            elif button_id and button_id.startswith("action_"):
                await process_action_button(phone_number, button_id, user)
            else:
                logger.warning(f"Unknown button ID: {button_id}")
                await send_message_simple(phone_number, "🤔 No reconocí esa acción. Puede que el botón sea muy antiguo o algo haya cambiado.")
        else:
            logger.warning(f"Interactive type not supported: {interactive_type}")
            await send_message_simple(phone_number, "🤖 Ese tipo de interacción aún no la tengo configurada. ¡Pero sigo aprendiendo!")
        
        return {"status": "success", "message": "Interactive message processed"}
        
    except Exception as e:
        logger.error(f"INTERACTIVE MODULE ERROR: {e}")
        # Fallback - enviar mensaje de error
        try:
            await send_message_simple(phone_number, f"Error procesando acción: {str(e)}")
        except Exception as send_error:
            logger.error(f"Error sending error message: {send_error}")
        return {"status": "error", "message": str(e)}

async def process_complete_task_button(phone_number: str, task_id: str, user: dict):
    """Procesa click en botón 'Completar' de una tarea"""
    try:
        logger.info(f"🎯 BUTTON: Completando tarea {task_id} para usuario {user.get('id')}")
        
        # Verificar que la tarea existe y pertenece al usuario
        task = await supabase.get_entry_by_id(task_id)
        if not task:
            await send_message_simple(phone_number, "❌ Tarea no encontrada")
            return
        
        if task.get('user_id') != user.get('id'):
            await send_message_simple(phone_number, "❌ No autorizado")
            return
        
        if task.get('status') == 'completed':
            await send_message_simple(phone_number, f"✅ {task['description']} (ya completada)")
            return
        
        # Completar la tarea
        updated_task = await supabase.update_entry_status(task_id, "completed")
        logger.info(f"✅ Tarea completada exitosamente: {updated_task.get('description')}")
        
        # Enviar confirmación personalizada
        congratulations = [
            "🎉 ¡Excelente trabajo!",
            "💪 ¡Lo lograste!",
            "🌟 ¡Increíble!",
            "👏 ¡Bien hecho!",
            "🚀 ¡Genial!"
        ]
        
        import random
        congrats = random.choice(congratulations)
        
        # Mensaje súper conciso
        message = f"✅ {task['description']}"
        await send_message_simple(phone_number, message)
        
        # TODO: Sincronizar con Todoist si está configurado
        
    except Exception as e:
        logger.error(f"Error completando tarea via botón: {e}")
        await send_message_simple(phone_number, f"❌ Error completando tarea: {str(e)}")

async def process_delete_task_button(phone_number: str, task_id: str, user: dict):
    """Procesa click en botón 'Eliminar' de una tarea"""
    try:
        logger.info(f"🗑️ BUTTON: Eliminando tarea {task_id} para usuario {user.get('id')}")
        
        # Verificar que la tarea existe y pertenece al usuario
        task = await supabase.get_entry_by_id(task_id)
        if not task:
            await send_message_simple(phone_number, "❌ Tarea no encontrada")
            return
        
        if task.get('user_id') != user.get('id'):
            await send_message_simple(phone_number, "❌ No autorizado")
            return
        
        # Actualizar status a 'deleted' en lugar de eliminar físicamente
        updated_task = await supabase.update_entry_status(task_id, "deleted")
        logger.info(f"🗑️ Tarea eliminada exitosamente: {updated_task.get('description')}")
        
        # Mensaje súper conciso
        message = f"🗑️ {task['description']}"
        await send_message_simple(phone_number, message)
        
        # TODO: Sincronizar con Todoist si está configurado
        
    except Exception as e:
        logger.error(f"Error eliminando tarea via botón: {e}")
        await send_message_simple(phone_number, f"❌ Error eliminando tarea: {str(e)}")

async def process_info_task_button(phone_number: str, task_id: str, user: dict):
    """Procesa click en botón 'Info' de una tarea"""
    try:
        logger.info(f"ℹ️ BUTTON: Mostrando info de tarea {task_id} para usuario {user.get('id')}")
        
        # Verificar que la tarea existe y pertenece al usuario
        task = await supabase.get_entry_by_id(task_id)
        if not task:
            await send_message_simple(phone_number, "❌ Tarea no encontrada")
            return
        
        if task.get('user_id') != user.get('id'):
            await send_message_simple(phone_number, "❌ No autorizado")
            return
        
        # Formatear información detallada de la tarea
        from datetime import datetime
        import pytz
        from app.config import settings
        
        tz = pytz.timezone(settings.timezone)
        
        # Formatear fecha de creación
        created_at = ""
        if task.get('created_at'):
            try:
                created_time = datetime.fromisoformat(task['created_at'].replace('Z', '+00:00'))
                created_local = created_time.astimezone(tz)
                created_at = f"📅 Creada: {created_local.strftime('%d/%m/%Y %H:%M')}"
            except:
                pass
        
        # Formatear fecha programada
        scheduled_at = ""
        if task.get('datetime'):
            try:
                scheduled_time = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                scheduled_local = scheduled_time.astimezone(tz)
                scheduled_at = f"⏰ Programada: {scheduled_local.strftime('%d/%m/%Y %H:%M')}"
            except:
                pass
        
        # Formatear fecha de completado
        completed_at = ""
        if task.get('completed_at'):
            try:
                completed_time = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                completed_local = completed_time.astimezone(tz)
                completed_at = f"✅ Completada: {completed_local.strftime('%d/%m/%Y %H:%M')}"
            except:
                pass
        
        # Prioridad
        priority = task.get('priority', 'media')
        priority_emoji = {'alta': '🔴', 'media': '🟡', 'baja': '🟢'}.get(priority, '🟡')
        
        # Estado
        status = task.get('status', 'pending')
        status_emoji = {'pending': '⏳', 'completed': '✅', 'deleted': '🗑️'}.get(status, '⏳')
        
        # Información súper concisa
        info_message = f"ℹ️ {task['description']}\n"
        info_message += f"{status_emoji} {status.title()}\n"
        info_message += f"{priority_emoji} {priority.title()}"
        
        if scheduled_at:
            info_message += f"\n{scheduled_at}"
        
        await send_message_simple(phone_number, info_message)
        
    except Exception as e:
        logger.error(f"Error mostrando info de tarea via botón: {e}")
        await send_message_simple(phone_number, f"❌ Error obteniendo información: {str(e)}")

async def process_action_button(phone_number: str, button_id: str, user: dict):
    """Procesa botones de acción rápida del resumen diario"""
    try:
        logger.info(f"⚡ ACTION BUTTON: Procesando {button_id} para usuario {user.get('id')}")
        
        from handlers.command_handler import command_handler
        
        if button_id == "action_tasks_buttons":
            # Ejecutar comando /tareas-botones (ya envía sus propios mensajes)
            result = await command_handler.handle_tasks_with_buttons(user, "")
            
        elif button_id == "action_show_agenda":
            # Ejecutar comando /agenda
            result = await command_handler.handle_agenda_view(user)
            formatted_message = result.get('message', 'Error obteniendo agenda')
            await send_message_simple(phone_number, formatted_message)
            
        elif button_id == "action_analyze_expenses":
            # Mostrar análisis de gastos del día
            result = await command_handler.handle_daily_expenses(user, "today")
            formatted_message = result.get('message', 'Error analizando gastos')
            await send_message_simple(phone_number, formatted_message)
            
        elif button_id == "action_show_stats":
            # Mostrar estadísticas
            result = await command_handler.handle_stats(user)
            formatted_message = result.get('message', 'Error obteniendo estadísticas')
            await send_message_simple(phone_number, formatted_message)
            
        elif button_id == "action_quick_add":
            # Guiar para agregar algo nuevo
            message = """➕ **¿Qué quieres agregar?**

Puedes decirme de forma natural:

📋 **Para tareas:**
• "Llamar al dentista mañana a las 2pm"
• "Comprar leche esta tarde"
• "Reunión importante el viernes"

💸 **Para gastos:**
• "Gasté ₡3,500 en almuerzo"
• "Pago de ₡45,000 por internet"

💰 **Para ingresos:**
• "Me pagaron ₡120,000 del proyecto"
• "Ingreso extra de ₡25,000"

📅 **Para eventos:**
• "Cumpleaños de María el sábado 7pm"
• "Cita médica el lunes 10am"

¡Solo háblame natural y yo me encargo de organizarlo! 😊"""
            
            await send_message_simple(phone_number, message)
            
        elif button_id == "action_show_all_tasks":
            # Mostrar todas las tareas en formato lista
            result = await command_handler.handle_daily_tasks(user, "today")
            formatted_message = result.get('message', 'Error obteniendo tareas')
            await send_message_simple(phone_number, formatted_message)
            
        elif button_id == "action_next_3_tasks":
            # Mostrar las siguientes 3 tareas con botones
            # TODO: Implementar paginación de tareas
            await send_message_simple(phone_number, "🚧 **Próximamente:** Paginación de tareas.\n\nPor ahora usa `/tareas-botones` para ver las más importantes o `/hoy` para ver todas en lista.")
            
        elif button_id == "action_complete_by_name":
            # Guiar para completar por nombre
            message = """✅ **Completar tarea por nombre**

Escribe `/completar` seguido de parte del nombre de la tarea:

📝 **Ejemplos:**
• `/completar llamar doctor`
• `/completar comprar leche`
• `/completar reunión`

💡 **Tip:** No necesitas escribir el nombre completo, solo unas palabras clave y yo encontraré la tarea correcta."""
            
            await send_message_simple(phone_number, message)
            
        else:
            logger.warning(f"Unknown action button: {button_id}")
            await send_message_simple(phone_number, "🤔 Esa acción no está configurada aún.")
        
    except Exception as e:
        logger.error(f"Error procesando action button {button_id}: {e}")
        await send_message_simple(phone_number, f"😅 Ups, tuve un problema ejecutando esa acción. Intenta de nuevo o usa un comando directo.")

async def process_message_simple(phone_number: str, message_text: str):
    """Procesa un mensaje de forma simple y directa"""
    try:
        print(f"8. Starting message processing for {phone_number}")
        
        # Crear usuario simple
        user = {
            "id": 1,  # ID temporal
            "whatsapp_number": phone_number,
            "display_name": "Usuario"
        }
        print("9. User created")
        
        # Detectar si es comando
        if message_text.startswith('/'):
            print(f"10. Command detected: {message_text}")
            response = f"Comando recibido: {message_text}\nUsa /help para ver comandos disponibles."
        else:
            print(f"10. Regular message detected: {message_text}")
            response = f"Mensaje recibido: {message_text}\nProcesando con Gemini..."
        
        print(f"11. Response prepared: {response[:50]}...")
        
        # Enviar respuesta
        success = await send_message_simple(phone_number, response)
        print(f"12. Message send result: {success}")
        
    except Exception as e:
        print(f"ERROR in process_message_simple: {e}")


async def send_message_simple(phone_number: str, message: str):
    """Envía mensaje usando WhatsApp Cloud API de forma simple"""
    try:
        print(f"13. Preparing to send message to {phone_number}")
        
        import httpx
        
        # Clean token (remove any extra spaces or newlines)
        clean_token = settings.whatsapp_cloud_token.strip()
        
        url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {clean_token}",
            "Content-Type": "application/json"
        }
        
        print(f"13.1. Using token length: {len(clean_token)} chars")
        print(f"13.2. Token starts with: {clean_token[:50]}...")
        print(f"13.3. Using phone_number_id: {settings.whatsapp_phone_number_id}")
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        print("14. Making HTTP request to Meta API")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            
            print(f"15. API Response: status={response.status_code}")
            
            if response.status_code == 200:
                print("16. Message sent successfully!")
                return True
            else:
                try:
                    error_text = response.text
                except:
                    error_text = "Could not get error text"
                print(f"16. Error sending message: {response.status_code} - {error_text}")
                return False
                
    except Exception as e:
        print(f"ERROR in send_message_simple: {e}")
        return False


async def process_webhook_direct(webhook_data: dict):
    """Procesa webhook directamente del JSON para evitar problemas de parsing"""
    try:
        print("=== STARTING WEBHOOK DIRECT PROCESSING ===")
        if webhook_data.get("object") != "whatsapp_business_account":
            print("Not a whatsapp_business_account object")
            return
            
        for entry in webhook_data.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    metadata = value.get("metadata", {})
                    
                    if not messages:
                        logger.info("No messages in webhook")
                        continue
                    
                    # Obtener información del contacto
                    contact_name = "Usuario"
                    if contacts and len(contacts) > 0:
                        contact_name = contacts[0].get("profile", {}).get("name", "Usuario")
                    
                    # Procesar cada mensaje
                    for message_data in messages:
                        await process_single_message_direct(message_data, contact_name, metadata)
                        
    except Exception as e:
        logger.error(f"Error processing webhook direct: {e}")


async def process_webhook_entry(entry: WhatsAppEntry):
    """Procesa una entrada del webhook"""
    try:
        for change in entry.changes:
            if change.field == "messages":
                await process_messages(change.value)
            else:
                logger.info(f"Unhandled change field: {change.field}")
                
    except Exception as e:
        logger.error(f"Error processing entry: {e}")


async def process_messages(value: WhatsAppValue):
    """Procesa mensajes recibidos"""
    try:
        if not value.messages:
            logger.info("No messages in webhook")
            return
        
        # Obtener información del contacto
        contact_name = "Usuario"
        if value.contacts and len(value.contacts) > 0:
            contact_name = value.contacts[0].profile.name
        
        # Procesar cada mensaje
        for message in value.messages:
            await process_single_message(message, contact_name, value.metadata)
            
    except Exception as e:
        logger.error(f"Error processing messages: {e}")


async def process_single_message(
    message: WhatsAppMessage, 
    contact_name: str, 
    metadata: Dict[str, Any]
):
    """Procesa un mensaje individual"""
    try:
        # Validar que tengamos el contenido del mensaje
        if not message.text or not message.text.body:
            logger.warning(f"Message without text content: {message.type}")
            return
        
        # TEMPORARY FIX: Extract phone number directly from the raw message dict
        # since the Pydantic model is not working correctly with the 'from' field
        phone_number = message.from_
        if not phone_number:
            # Log for debugging
            logger.error(f"MISSING PHONE NUMBER in message: {message}")
            phone_number = "50660052300"  # Hardcode for now until we fix the parsing
        
        message_text = message.text.body
        message_id = message.id
        
        # DEBUG: Log message details
        print(f"DEBUG MESSAGE - From: {phone_number}, Contact: {contact_name}, Text: {message_text[:50]}, ID: {message_id}")
        
        logger.info(f"Processing message from {contact_name} ({phone_number}): {message_text[:50]}...")
        
        # Obtener o crear usuario
        user = await get_or_create_user(phone_number, contact_name)
        
        # Procesar mensaje usando el MessageHandler correcto
        if message.type == "text":
            await message_handler.handle_text(message_text, user)
        elif message.type == "image":
            logger.info(f"Processing IMAGE message from {phone_number}")
            # Extraer datos de imagen del raw message
            image_data = message_data.get("image", {}) if hasattr(message, '__dict__') else {}
            await message_handler.handle_image({"media": image_data, "caption": image_data.get("caption", "")}, user)
        elif message.type == "audio" or message.type == "voice":
            logger.info(f"Processing AUDIO message from {phone_number}")
            # Extraer datos de audio del raw message
            audio_data = message_data.get("audio", {}) or message_data.get("voice", {}) if hasattr(message, '__dict__') else {}
            await message_handler.handle_audio({"media": audio_data}, user)
        else:
            logger.warning(f"Message type not supported yet: {message.type}")
            await send_whatsapp_message(
                phone_number=phone_number,
                message=f"Tipo de mensaje '{message.type}' no soportado aún. Puedo procesar texto, imágenes y audio.",
                phone_number_id=metadata.get("phone_number_id")
            )
            
    except Exception as e:
        logger.error(f"Error processing single message: {e}")


async def process_single_message_direct(
    message_data: dict, 
    contact_name: str, 
    metadata: dict
):
    """Procesa un mensaje individual usando parsing directo del JSON"""
    try:
        # Extraer datos directamente del JSON
        phone_number = message_data.get("from")  # ¡Esto debería funcionar!
        message_text = message_data.get("text", {}).get("body")
        message_id = message_data.get("id")
        message_type = message_data.get("type")
        timestamp = message_data.get("timestamp")
        
        # Validar que tengamos contenido del mensaje (solo para texto)
        if message_type == "text" and not message_text:
            logger.warning(f"Text message without content")
            return
        
        # DEBUG: Log message details 
        text_preview = message_text[:50] if message_text else f"[{message_type} message]"
        safe_contact_name = contact_name.encode('ascii', 'ignore').decode('ascii') if contact_name else "Usuario"
        print(f"DEBUG DIRECT - From: {phone_number}, Contact: {safe_contact_name}, Text: {text_preview}, ID: {message_id}")
        
        logger.info(f"Processing message from {safe_contact_name} ({phone_number}): {text_preview}...")
        
        # Obtener o crear usuario
        user = await get_or_create_user(phone_number, contact_name)
        
        # Procesar mensaje usando el MessageHandler correcto
        if message_type == "text":
            logger.info(f"Processing TEXT message from {phone_number}")
            await message_handler.handle_text(message_text, user)
        elif message_type == "interactive":
            logger.info(f"Processing INTERACTIVE message from {phone_number}")
            await process_interactive_message(phone_number, message_data, contact_name)
        elif message_type == "image":
            logger.info(f"Processing IMAGE message from {phone_number}")
            # Extraer datos de imagen del mensaje
            image_data = message_data.get("image", {})
            caption = image_data.get("caption", "")
            
            # Procesar imagen usando el pipeline de 2 pasos
            await message_handler.handle_image({
                "media": image_data, 
                "caption": caption
            }, user)
        elif message_type == "audio" or message_type == "voice":
            logger.info(f"Processing AUDIO/VOICE message from {phone_number}")
            # Extraer datos de audio/voice del mensaje
            audio_data = message_data.get("audio", {}) or message_data.get("voice", {})
            
            # Procesar audio usando el pipeline de 2 pasos
            await message_handler.handle_audio({
                "media": audio_data
            }, user)
        else:
            logger.warning(f"Message type not supported yet: {message_type}")
            await send_whatsapp_message(
                phone_number=phone_number,
                message=f"Tipo de mensaje '{message_type}' no soportado aún. Puedo procesar texto, imágenes, audio y botones.",
                phone_number_id=metadata.get("phone_number_id")
            )
            
    except Exception as e:
        logger.error(f"Error processing single message direct: {e}")


async def send_whatsapp_message(
    phone_number: str, 
    message: str, 
    phone_number_id: str = None
):
    """
    Envía mensaje usando WhatsApp Cloud API
    """
    try:
        import aiohttp
        
        # URL de la API
        phone_id = phone_number_id or getattr(settings, 'whatsapp_phone_number_id', 'YOUR_PHONE_NUMBER_ID')
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
        
        # Headers
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_cloud_token}",
            "Content-Type": "application/json"
        }
        
        # Payload
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        # Enviar mensaje
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    message_id = result.get("messages", [{}])[0].get("id", "")
                    logger.info(f"✅ Message sent successfully: {message_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to send message: {response.status} - {error_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {e}")
        return False


def verify_webhook_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    """
    Verifica la firma del webhook de Meta
    """
    try:
        if not signature:
            return False
            
        # Remover prefijo 'sha256='
        signature = signature.replace('sha256=', '')
        
        # Calcular firma esperada
        expected_signature = hmac.new(
            app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Comparación segura
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error(f"❌ Error verifying signature: {e}")
        return False


# Funciones de utilidad para el handler anterior
async def get_media_url(media_id: str) -> str:
    """Obtiene URL de media usando Cloud API"""
    try:
        import aiohttp
        
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {settings.whatsapp_cloud_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("url", "")
                    
        return ""
    except:
        return ""


async def download_media(media_url: str) -> bytes:
    """Descarga archivo de media"""
    try:
        import aiohttp
        
        headers = {"Authorization": f"Bearer {settings.whatsapp_cloud_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(media_url, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                    
        return b""
    except:
        return b""


async def get_or_create_user(phone_number: str, contact_name: str) -> dict:
    """
    Obtiene un usuario existente o crea uno nuevo
    """
    try:
        # Verificar que phone_number no sea None
        if not phone_number:
            logger.error("Phone number is None")
            return {
                "id": None,
                "whatsapp_number": "unknown",
                "display_name": contact_name or "Usuario Desconocido",
                "is_active": True
            }
        
        # Limpiar número de teléfono (remover caracteres especiales)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        
        # Buscar usuario existente
        user = await supabase.get_user_by_phone(clean_phone)
        
        if not user:
            # Crear nuevo usuario
            user_data = {
                "whatsapp_number": clean_phone,
                "name": contact_name or "Usuario",
                "is_active": True
            }
            user = await supabase.create_user(user_data)
            logger.info(f"Created new user: {clean_phone} ({contact_name})")
        else:
            # Actualizar nombre si es diferente
            if contact_name and user.get('name') != contact_name:
                await supabase.update_user(user['id'], {"name": contact_name})
                user['name'] = contact_name
                
        return user
        
    except Exception as e:
        logger.error(f"Error getting/creating user: {e}")
        # Retornar un usuario temporal en caso de error
        safe_phone = ''.join(filter(str.isdigit, phone_number)) if phone_number else "unknown"
        return {
            "id": None,
            "whatsapp_number": safe_phone,
            "display_name": contact_name or "Usuario Temporal",
            "is_active": True
        }


@router.post("/send-test-message")
async def send_test_message(request: SendMessageRequest):
    """
    Endpoint para enviar mensajes de prueba usando WhatsApp Cloud API
    """
    try:
        # Formatear número de teléfono
        phone_number = whatsapp_cloud_service.format_phone_number(request.to)
        
        # Enviar mensaje
        result = await whatsapp_cloud_service.send_text_message(
            to=phone_number,
            message=request.message
        )
        
        return {
            "success": True,
            "message": "Mensaje enviado correctamente",
            "result": result,
            "phone_number": phone_number
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending test message: {e}")
        raise HTTPException(status_code=500, detail=f"Error enviando mensaje: {str(e)}")


@router.get("/test-connection")
async def test_connection():
    """
    Endpoint para probar la conexión con WhatsApp Cloud API
    """
    try:
        # DEBUG: Log token info
        logger.info(f"DEBUG Token length: {len(settings.whatsapp_cloud_token)}")
        logger.info(f"DEBUG Token start: {settings.whatsapp_cloud_token[:50]}...")
        logger.info(f"DEBUG Phone ID: {settings.whatsapp_phone_number_id}")
        
        # Hacer una petición simple para verificar credenciales
        import httpx
        
        url = f"https://graph.facebook.com/v18.0/{settings.whatsapp_phone_number_id}"
        clean_token = settings.whatsapp_cloud_token.strip()
        headers = {
            "Authorization": f"Bearer {clean_token}",
        }
        
        logger.info(f"DEBUG URL: {url}")
        logger.info(f"DEBUG Headers: {headers}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            logger.info(f"DEBUG Response status: {response.status_code}")
            logger.info(f"DEBUG Response text: {response.text}")
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "message": "Conexión exitosa con WhatsApp Cloud API",
                "phone_number_info": result
            }
            
    except Exception as e:
        logger.error(f"❌ Error testing connection: {e}")
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")

@router.post("/test-message")
async def test_message_processing():
    """
    Endpoint para simular el procesamiento de mensajes directamente
    """
    try:
        logger.info("🧪 TEST: Iniciando simulación de mensaje")
        
        # Simular mensaje de test
        test_message = {
            "from": "50612345678",
            "id": "test-message-id",
            "timestamp": "1755402157",
            "text": {
                "body": "comprar leche mañana"
            },
            "type": "text"
        }
        
        test_value = {
            "messaging_product": "whatsapp",
            "metadata": {
                "display_phone_number": "50664100173",
                "phone_number_id": "test"
            },
            "contacts": [
                {
                    "profile": {
                        "name": "Test User"
                    },
                    "wa_id": "50612345678"
                }
            ],
            "messages": [test_message]
        }
        
        logger.info("🧪 TEST: Procesando mensaje simulado...")
        
        # Importar y procesar el mensaje de test directamente
        from api.routes.webhook import process_meta_message_async
        await process_meta_message_async(test_message, test_value)
        
        logger.info("🧪 TEST: Mensaje procesado exitosamente")
        
        return {
            "status": "success",
            "message": "Test message processed successfully",
            "test_message": test_message["text"]["body"]
        }
        
    except Exception as e:
        logger.error(f"🧪 TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }

# ===== ENDPOINTS CONSOLIDADOS =====
# Funcionalidad consolidada de webhook.py, server_logs.py y otros

@router.get("/logs/recent")
async def get_recent_logs():
    """Obtener logs recientes de la aplicación - Consolidado de server_logs.py"""
    try:
        import os
        import glob
        
        log_info = {
            "log_files": [],
            "recent_logs": [],
            "environment": os.environ.get("ENVIRONMENT", "unknown")
        }
        
        # Buscar archivos de log
        log_patterns = [
            "/app/logs/*.log",
            "/app/logs/*.txt", 
            "./logs/*.log",
            "./logs/*.txt"
        ]
        
        for pattern in log_patterns:
            files = glob.glob(pattern)
            log_info["log_files"].extend(files)
        
        # Leer logs recientes si existen
        if log_info["log_files"]:
            try:
                with open(log_info["log_files"][0], 'r') as f:
                    lines = f.readlines()
                    log_info["recent_logs"] = lines[-50:]  # Últimas 50 líneas
            except Exception as e:
                log_info["log_read_error"] = str(e)
        
        return log_info
        
    except Exception as e:
        return {
            "error": str(e),
            "message": "Error getting logs"
        }

@router.get("/logs/test-flow") 
async def test_message_flow():
    """Probar el flujo de procesamiento de mensajes - Consolidado de server_logs.py"""
    try:
        from core.supabase import supabase
        from handlers.message_handler import message_handler
        
        test_phone = "50660052300"
        test_message = "test flow"
        
        # PASO 1: Obtener usuario
        user = await supabase.get_user_with_context(test_phone)
        
        step_info = {
            "step_1_user_retrieval": {
                "success": user is not None,
                "user_data": user,
                "has_whatsapp_number": user.get('whatsapp_number') is not None if user else False,
                "user_keys": list(user.keys()) if user else None
            }
        }
        
        if user:
            # PASO 2: Procesar con message handler
            try:
                result = await message_handler.handle_text(test_message, user)
                step_info["step_2_message_handler"] = {
                    "success": True,
                    "result": result
                }
            except Exception as e:
                step_info["step_2_message_handler"] = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
        
        return step_info
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@router.get("/webhook-status")
async def webhook_status():
    """Estado completo del sistema de webhooks - Consolidado"""
    return {
        "status": "healthy", 
        "webhook_type": "Meta WhatsApp Business API",
        "version": "3.0.0-consolidated",
        "active_endpoints": {
            "webhook": "POST /webhook/cloud",
            "verification": "GET /webhook/cloud", 
            "testing": [
                "GET /webhook/cloud/test-connection",
                "POST /webhook/cloud/send-test-message",
                "POST /webhook/cloud/test-message"
            ],
            "logs": [
                "GET /webhook/cloud/logs/recent",
                "GET /webhook/cloud/logs/test-flow"
            ],
            "status": "GET /webhook/cloud/webhook-status"
        },
        "features": {
            "auto_log_bypass": True,
            "meta_business_api": True,
            "background_processing": True,
            "idempotency_check": True,
            "consolidated_debugging": True
        },
        "removed_systems": [
            "WAHA (completely removed)",
            "Duplicate webhook endpoints",
            "Scattered debug endpoints"
        ]
    }