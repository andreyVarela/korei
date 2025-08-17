"""
Manejador principal de mensajes
"""
from typing import Dict, Any, List
import os
import tempfile
from datetime import datetime
from loguru import logger

from core.supabase import supabase
from services.whatsapp import whatsapp_service
from services.whatsapp_cloud import whatsapp_cloud_service
from services.gemini import gemini_service
from handlers.command_handler import command_handler
from services.reminder_scheduler import reminder_scheduler

class MessageHandler:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    async def verify_user_and_payment(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica que el usuario exista y tenga el pago al día
        
        Returns:
            Dict con is_valid (bool) y message (str)
        """
        try:
            # Verificar si el usuario tiene ID (significa que existe en la DB)
            if not user.get('id'):
                return {
                    'is_valid': False,
                    'message': "❌ **Usuario no encontrado**\n\n🔒 Para usar Korei Assistant necesitas estar registrado.\n\n💬 Contacta al administrador para obtener acceso."
                }
            
            # Obtener datos completos del usuario desde la base de datos
            try:
                user_data = await supabase.get_user_by_id(user['id'])
                if not user_data:
                    return {
                        'is_valid': False,
                        'message': "❌ **Usuario no encontrado en la base de datos**\n\n💬 Contacta al administrador para verificar tu cuenta."
                    }
                
                # Verificar estado de pago
                payment_status = user_data.get('payment', False)
                if not payment_status:
                    return {
                        'is_valid': False,
                        'message': "💳 **Pago pendiente**\n\n❌ Tu suscripción no está al día.\n\n💰 Para continuar usando Korei Assistant, actualiza tu pago.\n\n📞 Contacta al administrador para más información."
                    }
                
                # Usuario válido y con pago al día
                return {
                    'is_valid': True,
                    'message': "Usuario válido"
                }
                
            except Exception as db_error:
                logger.error(f"Error verificando usuario en DB: {db_error}")
                return {
                    'is_valid': False,
                    'message': "❌ **Error de sistema**\n\nNo se pudo verificar tu cuenta. Intenta de nuevo en unos minutos."
                }
                
        except Exception as e:
            logger.error(f"Error en verify_user_and_payment: {e}")
            return {
                'is_valid': False,
                'message': "❌ **Error de sistema**\n\nOcurrió un error verificando tu cuenta."
            }
    
    async def handle_text(self, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes de texto"""
        try:
            # VERIFICACIÓN DE USUARIO Y PAGO
            user_verification = await self.verify_user_and_payment(user)
            if not user_verification['is_valid']:
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=user_verification['message']
                )
                return {"status": "error", "message": user_verification['message']}
            
            # Detectar si es un comando
            if message.strip().startswith('/'):
                return await self.handle_command(message.strip(), user)
            
            # FILTRO INTELIGENTE: Detectar intención antes de procesar con Gemini
            intent_result = await self.detect_user_intent(message, user)
            if intent_result['should_handle_directly']:
                return intent_result
            
            # Procesar con Gemini solo si es contenido real
            result = await gemini_service.process_message(message, user)
            
            # NUEVA FUNCIONALIDAD: Revisar disponibilidad ANTES de crear evento
            if result.get('type') == 'evento' and user.get('id'):
                logger.info(f"AVAILABILITY-CHECK: Detectado evento, revisando disponibilidad...")
                try:
                    from services.integrations.integration_manager import integration_manager
                    
                    # Obtener integración de Google Calendar del usuario
                    google_integration = await integration_manager.get_user_integration(
                        user['id'], 'google_calendar'
                    )
                    
                    if google_integration:
                        # Revisar disponibilidad en Google Calendar
                        availability_result = await self.check_calendar_availability(
                            google_integration, result
                        )
                        
                        if availability_result['has_conflict']:
                            # HAY CONFLICTO - No crear evento, avisar al usuario
                            conflict_response = self.format_conflict_response(
                                availability_result['conflicts'], result
                            )
                            
                            send_result = await whatsapp_cloud_service.send_text_message(
                                to=user['whatsapp_number'], 
                                message=conflict_response
                            )
                            
                            return {"status": "conflict", "message": "Conflicto de horario detectado"}
                        
                        else:
                            logger.info(f"AVAILABILITY-CHECK: Horario disponible, procediendo...")
                    else:
                        logger.info(f"AVAILABILITY-CHECK: Usuario no tiene Google Calendar, creando sin verificar")
                        
                except Exception as availability_error:
                    logger.error(f"AVAILABILITY-CHECK ERROR: {availability_error}")
                    # Si falla la verificación, continuar normalmente
            
            # Guardar en base de datos si hay ID de usuario válido
            entry = None
            if user.get('id'):
                entry_data = {
                    **result,
                    "user_id": user['id']
                }
                # Si es tarea o recordatorio, intentar crear primero en Todoist
                if result.get('type') in ['tarea', 'recordatorio']:
                    try:
                        from services.integrations.integration_manager import integration_manager
                        from services.integrations.todoist_integration import select_optimal_project
                        todoist_integration = await integration_manager.get_user_integration(user['id'], 'todoist')
                        if todoist_integration:
                            projects = await todoist_integration.get_projects()
                            user_context = user.get('profile', {})
                            optimal_project = select_optimal_project(projects, user_context, message)
                            if optimal_project:
                                entry_data['project_id'] = optimal_project['id']
                                entry_data['project_name'] = optimal_project['name']
                            else:
                                entry_data['project_id'] = todoist_integration.default_project_id
                            todoist_id = await todoist_integration.create_task(entry_data)
                            if todoist_id:
                                entry_data['external_id'] = todoist_id
                                entry_data['external_service'] = 'todoist'
                                logger.info(f"TODOIST: Tarea/recordatorio creado en Todoist con ID {todoist_id}")
                    except Exception as todoist_error:
                        logger.error(f"TODOIST ERROR: {todoist_error}")
                entry = await supabase.create_entry(entry_data)
                # Programar recordatorio si es de tipo recordatorio
                if result.get('type') == 'recordatorio' and entry:
                    logger.info(f"REMINDER: Detectado recordatorio, programando...")
                    try:
                        reminder_data = {**result, 'id': entry['id']}
                        job_id = await reminder_scheduler.schedule_reminder(reminder_data, user)
                        if job_id:
                            logger.info(f"REMINDER: Programado exitosamente con ID {job_id}")
                        else:
                            logger.warning(f"REMINDER: No se pudo programar")
                    except Exception as reminder_error:
                        logger.error(f"REMINDER ERROR: {reminder_error}")
                # Sincronización automática con Google Calendar (solo si no hubo conflicto)
                if entry and result.get('type') == 'evento':
                    logger.info(f"AUTO-SYNC: Creando evento en Google Calendar...")
                    try:
                        from services.integrations.integration_manager import integration_manager
                        google_integration = await integration_manager.get_user_integration(
                            user['id'], 'google_calendar'
                        )
                        if google_integration:
                            google_event_id = await google_integration.sync_to_external(result)
                            if google_event_id:
                                logger.info(f"AUTO-SYNC: Evento sincronizado exitosamente con Google Calendar. ID: {google_event_id}")
                                await supabase.update_entry(entry['id'], {
                                    'external_service': 'google_calendar',
                                    'external_id': google_event_id
                                })
                            else:
                                logger.warning(f"AUTO-SYNC: Falló la sincronización con Google Calendar")
                        else:
                            logger.info(f"AUTO-SYNC: Usuario no tiene Google Calendar conectado")
                    except Exception as sync_error:
                        logger.error(f"AUTO-SYNC ERROR: {sync_error}")
            
            # Enviar respuesta usando WhatsApp Cloud API
            response = whatsapp_service.format_response(result)
            
            # Log response details
            logger.info("=" * 50)
            logger.info("SENDING RESPONSE:")
            logger.info(f"  To: {user['whatsapp_number']}")
            logger.info(f"  Message Length: {len(response)} chars")
            logger.info(f"  Response: {response[:100]}...")
            logger.info("=" * 50)
            
            send_result = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'], 
                message=response
            )
            
            # Log send result
            logger.info("=" * 50)
            logger.info("SEND RESULT:")
            logger.info(f"  Success: {send_result}")
            logger.info("=" * 50)
            
            return {"status": "success", "entry_id": entry.get('id') if entry else None}
            
        except Exception as e:
            logger.error(f"Error procesando texto: {e}")
            
            from services.formatters import message_formatter
            error_message = message_formatter.format_error_message(str(e))
            await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=error_message
            )
            
            return {"status": "error", "message": str(e)}
    
    async def handle_command(self, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa comandos especiales"""
        try:
            # Extraer comando (primera palabra que empieza con /)
            parts = message.split()
            command = parts[0].lower()
            
            print(f"DEBUG COMMAND: {command} from user {user.get('whatsapp_number', 'unknown')}")
            
            # Procesar comando
            result = await command_handler.handle_command(command, message, user)
            
            # Obtener mensaje de respuesta
            response_message = result.get('message', 'Comando procesado')
            
            # DEBUG: Print command response
            print("=" * 30)
            print("COMMAND RESPONSE:")
            print(f"  Command: {command}")
            print(f"  Type: {result.get('type', 'unknown')}")
            print(f"  Message Length: {len(response_message)} chars")
            print("=" * 30)
            
            # Enviar respuesta - usar botones si están disponibles
            if result.get('buttons') and result.get('has_pending'):
                send_result = await whatsapp_cloud_service.send_interactive_message(
                    to=user['whatsapp_number'],
                    body_text=response_message,
                    buttons=result['buttons']
                )
            else:
                send_result = await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response_message
                )
            
            print(f"Command send result: {send_result}")
            
            return {"status": "success", "command": command, "result": result}
            
        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            
            from services.formatters import message_formatter
            error_message = message_formatter.format_error_message("comando")
            await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=error_message
            )
            
            return {"status": "error", "message": str(e)}
    
    async def handle_audio(self, message_data: Dict[str, Any], 
                          user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes de audio usando pipeline de dos pasos"""
        try:
            # VERIFICACIÓN DE USUARIO Y PAGO
            user_verification = await self.verify_user_and_payment(user)
            if not user_verification['is_valid']:
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=user_verification['message']
                )
                return {"status": "error", "message": user_verification['message']}
                
            await whatsapp_service.send_typing(user['whatsapp_number'])
            
            # DEBUG: Ver estructura exacta del mensaje
            logger.info(f"AUDIO-DEBUG: message_data structure: {message_data}")
            
            # Descargar audio desde WhatsApp Cloud API (igual que imágenes)
            media_info = message_data.get('media', {})
            media_id = media_info.get('id')
            
            logger.info(f"AUDIO-DEBUG: media_info: {media_info}")
            logger.info(f"AUDIO-DEBUG: media_id: {media_id}")
            
            if not media_id:
                raise ValueError("No se encontró ID del audio")
            
            logger.info(f"AUDIO-DOWNLOAD: Getting media URL for ID: {media_id}")
            
            # Obtener URL del archivo desde WhatsApp Cloud API
            from api.routes.whatsapp_cloud import get_media_url, download_media
            media_url = await get_media_url(media_id)
            
            if not media_url:
                raise ValueError("No se pudo obtener URL del audio")
                
            logger.info(f"AUDIO-DOWNLOAD: Downloading from URL: {media_url[:50]}...")
            
            # Descargar archivo
            audio_data = await download_media(media_url)
            
            if not audio_data:
                raise ValueError("No se pudo descargar el audio")
            
            # Guardar temporalmente
            temp_path = os.path.join(self.temp_dir, f"audio_{user['id']}.ogg")
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # PASO 1: Extraer contexto del audio con Gemini (REAL)
            logger.info(f"AUDIO-STEP1: Iniciando transcripción real con Gemini")
            logger.info(f"AUDIO-STEP1: Archivo temporal: {temp_path}")
            logger.info(f"AUDIO-STEP1: Usuario: {user.get('name', 'Unknown')}")
            
            try:
                logger.info(f"AUDIO-STEP1: Llamando gemini_service.extract_audio_context...")
                audio_context = await gemini_service.extract_audio_context(temp_path, user)
                logger.info(f"AUDIO-SUCCESS: Transcripción exitosa!")
                logger.info(f"AUDIO-CONTEXT: {audio_context[:200]}...")
            except Exception as e:
                logger.error(f"AUDIO-ERROR: Error en transcripción real: {e}")
                logger.error(f"AUDIO-ERROR: Tipo de error: {type(e).__name__}")
                import traceback
                logger.error(f"AUDIO-ERROR: Traceback: {traceback.format_exc()}")
                audio_context = "Usuario envió un mensaje de audio que no se pudo transcribir completamente."
            
            # PASO 2: Procesar contexto extraído a través del pipeline enriquecido
            logger.info(f"AUDIO-STEP2: Procesando contexto extraído con pipeline completo")
            enhanced_message = f"Información extraída de audio: {audio_context}"
            
            # Usar el pipeline completo de procesamiento (con contexto financiero, eventos, etc.)
            result = await gemini_service.process_message(enhanced_message, user)
            logger.info(f"AUDIO-RESULT: {result}")
            
            # NUEVA FUNCIONALIDAD: Revisar disponibilidad ANTES de crear evento (igual que imágenes)
            if result.get('type') == 'evento' and user.get('id'):
                logger.info(f"AUDIO-AVAILABILITY: Detectado evento en audio, revisando disponibilidad...")
                try:
                    from services.integrations.integration_manager import integration_manager
                    
                    # Obtener integración de Google Calendar del usuario
                    google_integration = await integration_manager.get_user_integration(
                        user['id'], 'google_calendar'
                    )
                    
                    if google_integration:
                        # Revisar disponibilidad en Google Calendar
                        availability_result = await self.check_calendar_availability(
                            google_integration, result
                        )
                        
                        if availability_result['has_conflict']:
                            # HAY CONFLICTO - No crear evento, avisar al usuario
                            conflict_response = self.format_conflict_response(
                                availability_result['conflicts'], result
                            )
                            
                            # Agregar nota sobre audio procesado
                            audio_processed_msg = f"🎤 **Audio procesado exitosamente**\n\n{audio_context[:150]}...\n\n{conflict_response}"
                            
                            send_result = await whatsapp_cloud_service.send_text_message(
                                to=user['whatsapp_number'], 
                                message=audio_processed_msg
                            )
                            
                            return {"status": "conflict", "message": "Conflicto de horario detectado en audio"}
                        
                        else:
                            logger.info(f"AUDIO-AVAILABILITY: Horario disponible, procediendo...")
                    else:
                        logger.info(f"AUDIO-AVAILABILITY: Usuario no tiene Google Calendar, creando sin verificar")
                        
                except Exception as availability_error:
                    logger.error(f"AUDIO-AVAILABILITY ERROR: {availability_error}")
                    # Si falla la verificación, continuar normalmente
            
            # Guardar en base de datos si hay ID de usuario válido
            entry = None
            if user.get('id'):
                entry_data = {
                    **result,
                    "user_id": user['id']
                }
                entry = await supabase.create_entry(entry_data)
                
                # También guardar log del audio (TEMPORAL: DESHABILITADO)
                # audio_log = {
                #     "user_id": user['id'],
                #     "original_audio_url": media_url,
                #     "transcribed_text": audio_context[:500]
                # }
                # await supabase.client.table("voice_logs").insert(audio_log).execute()
                logger.info(f"AUDIO-LOG: Saltando guardado de voice_logs temporalmente")
                
                # Sincronización automática con Google Calendar (solo si no hubo conflicto)
                if entry and result.get('type') == 'evento':
                    logger.info(f"AUDIO-AUTO-SYNC: Creando evento en Google Calendar...")
                    try:
                        from services.integrations.integration_manager import integration_manager
                        
                        # Obtener integración de Google Calendar del usuario
                        google_integration = await integration_manager.get_user_integration(
                            user['id'], 'google_calendar'
                        )
                        
                        if google_integration:
                            # Sincronizar este evento específico
                            google_event_id = await google_integration.sync_to_external(result)
                            if google_event_id:
                                logger.info(f"AUDIO-AUTO-SYNC: Evento sincronizado exitosamente con Google Calendar. ID: {google_event_id}")
                                # Actualizar la entrada con external_id real
                                await supabase.update_entry(entry['id'], {
                                    'external_service': 'google_calendar',
                                    'external_id': google_event_id
                                })
                            else:
                                logger.warning(f"AUDIO-AUTO-SYNC: Falló la sincronización con Google Calendar")
                        else:
                            logger.info(f"AUDIO-AUTO-SYNC: Usuario no tiene Google Calendar conectado")
                            
                    except Exception as sync_error:
                        logger.error(f"AUDIO-AUTO-SYNC ERROR: {sync_error}")
            
            # Limpiar archivo temporal
            os.remove(temp_path)
            
            # RESPUESTA SIMPLIFICADA (FUNCIONAL)
            response = f"🎤 **Audio recibido y procesado:**\n\n"
            response += whatsapp_service.format_response(result)
            
            # Log response details
            logger.info("=== AUDIO PROCESSING COMPLETE ===")
            logger.info(f"Context extracted: {audio_context[:200]}...")
            logger.info(f"Final result: {result}")
            logger.info("=" * 50)
            
            send_result = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'], 
                message=response
            )
            
            return {"status": "success", "entry_id": entry.get('id') if entry else None, "audio_context": audio_context}
            
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            
            from services.formatters import message_formatter
            error_message = f"❌ No pude procesar tu audio.\n\n💡 {message_formatter.format_error_message('audio')}"
            await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=error_message
            )
            
            return {"status": "error", "message": str(e)}
    
    async def handle_image(self, message_data: Dict[str, Any], 
                          user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa imágenes con Gemini Vision usando pipeline de dos pasos"""
        try:
            # VERIFICACIÓN DE USUARIO Y PAGO
            user_verification = await self.verify_user_and_payment(user)
            if not user_verification['is_valid']:
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=user_verification['message']
                )
                return {"status": "error", "message": user_verification['message']}
                
            await whatsapp_service.send_typing(user['whatsapp_number'])
            
            # Descargar imagen desde WhatsApp Cloud API
            media_info = message_data.get('media', {})
            media_id = media_info.get('id')
            
            if not media_id:
                raise ValueError("No se encontró ID de la imagen")
            
            logger.info(f"IMAGE-DOWNLOAD: Getting media URL for ID: {media_id}")
            
            # Obtener URL del archivo desde WhatsApp Cloud API
            from api.routes.whatsapp_cloud import get_media_url, download_media
            media_url = await get_media_url(media_id)
            
            if not media_url:
                raise ValueError("No se pudo obtener URL de la imagen")
                
            logger.info(f"IMAGE-DOWNLOAD: Downloading from URL: {media_url[:50]}...")
            
            # Descargar archivo
            image_data = await download_media(media_url)
            
            if not image_data:
                raise ValueError("No se pudo descargar la imagen")
            
            # Contexto adicional del mensaje (caption)
            caption = message_data.get('caption', '')
            
            # PASO 1: Extraer contexto de la imagen con Gemini Vision
            logger.info(f"IMAGE-STEP1: Extrayendo contexto de imagen para usuario {user.get('whatsapp_number')}")
            image_context = await gemini_service.extract_image_context(image_data, user)
            logger.info(f"IMAGE-CONTEXT: {image_context[:200]}...")
            
            # PASO 2: Procesar contexto extraído a través del pipeline enriquecido
            logger.info(f"IMAGE-STEP2: Procesando contexto extraído con pipeline completo")
            enhanced_message = f"Información extraída de imagen: {image_context}"
            if caption:
                enhanced_message += f"\nContexto adicional del usuario: {caption}"
            
            # Usar el pipeline completo de procesamiento (con contexto financiero, eventos, etc.)
            result = await gemini_service.process_message(enhanced_message, user)
            logger.info(f"IMAGE-RESULT: {result}")
            
            # NUEVA FUNCIONALIDAD: Revisar disponibilidad ANTES de crear evento (igual que texto)
            if result.get('type') == 'evento' and user.get('id'):
                logger.info(f"IMAGE-AVAILABILITY: Detectado evento en imagen, revisando disponibilidad...")
                try:
                    from services.integrations.integration_manager import integration_manager
                    
                    # Obtener integración de Google Calendar del usuario
                    google_integration = await integration_manager.get_user_integration(
                        user['id'], 'google_calendar'
                    )
                    
                    if google_integration:
                        # Revisar disponibilidad en Google Calendar
                        availability_result = await self.check_calendar_availability(
                            google_integration, result
                        )
                        
                        if availability_result['has_conflict']:
                            # HAY CONFLICTO - No crear evento, avisar al usuario
                            conflict_response = self.format_conflict_response(
                                availability_result['conflicts'], result
                            )
                            
                            # Agregar nota sobre imagen procesada
                            image_processed_msg = f"📷 **Imagen procesada exitosamente**\n\n{image_context[:150]}...\n\n{conflict_response}"
                            
                            send_result = await whatsapp_cloud_service.send_text_message(
                                to=user['whatsapp_number'], 
                                message=image_processed_msg
                            )
                            
                            return {"status": "conflict", "message": "Conflicto de horario detectado en imagen"}
                        
                        else:
                            logger.info(f"IMAGE-AVAILABILITY: Horario disponible, procediendo...")
                    else:
                        logger.info(f"IMAGE-AVAILABILITY: Usuario no tiene Google Calendar, creando sin verificar")
                        
                except Exception as availability_error:
                    logger.error(f"IMAGE-AVAILABILITY ERROR: {availability_error}")
                    # Si falla la verificación, continuar normalmente
            
            # Guardar en base de datos si hay ID de usuario válido
            entry = None
            if user.get('id'):
                entry_data = {
                    **result,
                    "user_id": user['id']
                }
                entry = await supabase.create_entry(entry_data)
                
                # Sincronización automática con Google Calendar (solo si no hubo conflicto)
                if entry and result.get('type') == 'evento':
                    logger.info(f"IMAGE-AUTO-SYNC: Creando evento en Google Calendar...")
                    try:
                        from services.integrations.integration_manager import integration_manager
                        
                        # Obtener integración de Google Calendar del usuario
                        google_integration = await integration_manager.get_user_integration(
                            user['id'], 'google_calendar'
                        )
                        
                        if google_integration:
                            # Sincronizar este evento específico
                            google_event_id = await google_integration.sync_to_external(result)
                            if google_event_id:
                                logger.info(f"IMAGE-AUTO-SYNC: Evento sincronizado exitosamente con Google Calendar. ID: {google_event_id}")
                                # Actualizar la entrada con external_id real
                                await supabase.update_entry(entry['id'], {
                                    'external_service': 'google_calendar',
                                    'external_id': google_event_id
                                })
                            else:
                                logger.warning(f"IMAGE-AUTO-SYNC: Falló la sincronización con Google Calendar")
                        else:
                            logger.info(f"IMAGE-AUTO-SYNC: Usuario no tiene Google Calendar conectado")
                            
                    except Exception as sync_error:
                        logger.error(f"IMAGE-AUTO-SYNC ERROR: {sync_error}")
            
            # Subir imagen a Supabase Storage (opcional para el futuro)
            # image_url = await supabase.upload_media(
            #     image_data, 
            #     f"image_{entry['id'] if entry else 'unknown'}.jpg",
            #     "image/jpeg"
            # )
            
            # Enviar confirmación usando WhatsApp Cloud API
            response = f"📷 **Imagen procesada exitosamente:**\n\n"
            response += f"🔍 **Contexto extraído:** {image_context[:100]}...\n\n"
            response += whatsapp_service.format_response(result)
            
            # Log response details
            logger.info("=== IMAGE PROCESSING COMPLETE ===")
            logger.info(f"Context extracted: {image_context[:200]}...")
            logger.info(f"Final result: {result}")
            logger.info("=" * 50)
            
            send_result = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'], 
                message=response
            )
            
            return {"status": "success", "entry_id": entry.get('id') if entry else None, "image_context": image_context}
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            
            from services.formatters import message_formatter
            error_message = f"❌ No pude procesar tu imagen.\n\n💡 {message_formatter.format_error_message('imagen')}"
            await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=error_message
            )
            
            return {"status": "error", "message": str(e)}
    
    async def check_calendar_availability(self, google_integration, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica disponibilidad en Google Calendar antes de crear evento"""
        try:
            logger.info(f"AVAILABILITY: Checking calendar for event: {event_data.get('description')}")
            
            # Obtener fecha y hora del evento
            event_datetime = event_data.get('datetime')
            if not event_datetime:
                logger.warning(f"AVAILABILITY: No datetime found, assuming no conflict")
                return {"has_conflict": False, "conflicts": []}
            
            # Convertir string a datetime si es necesario
            if isinstance(event_datetime, str):
                try:
                    from datetime import datetime
                    event_datetime = datetime.fromisoformat(event_datetime.replace('Z', '+00:00'))
                except:
                    logger.warning(f"AVAILABILITY: Invalid datetime format: {event_datetime}")
                    return {"has_conflict": False, "conflicts": []}
            
            # Definir ventana de búsqueda (1 hora antes y después)
            from datetime import timedelta
            start_check = event_datetime - timedelta(minutes=30)
            end_check = event_datetime + timedelta(hours=1, minutes=30)  # Duración típica + buffer
            
            logger.info(f"AVAILABILITY: Checking window {start_check} to {end_check}")
            
            # Obtener eventos existentes en esa ventana
            if not google_integration.service:
                await google_integration.authenticate()
            
            events_result = google_integration.service.events().list(
                calendarId=google_integration.calendar_id,
                timeMin=start_check.isoformat(),
                timeMax=end_check.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            existing_events = events_result.get('items', [])
            logger.info(f"AVAILABILITY: Found {len(existing_events)} existing events in window")
            
            conflicts = []
            
            for existing_event in existing_events:
                start_info = existing_event.get('start', {})
                end_info = existing_event.get('end', {})
                
                # Procesar evento con hora específica
                if start_info.get('dateTime'):
                    try:
                        from datetime import datetime
                        existing_start = datetime.fromisoformat(start_info['dateTime'].replace('Z', '+00:00'))
                        existing_end = datetime.fromisoformat(end_info['dateTime'].replace('Z', '+00:00'))
                        
                        # Verificar solapamiento
                        # Nuevo evento dura 1 hora por defecto
                        new_end = event_datetime + timedelta(hours=1)
                        
                        # Hay conflicto si:
                        # - El nuevo evento empieza antes de que termine el existente Y
                        # - El nuevo evento termina después de que empiece el existente
                        if (event_datetime < existing_end and new_end > existing_start):
                            conflicts.append({
                                "title": existing_event.get('summary', 'Evento sin título'),
                                "start": existing_start.strftime("%H:%M"),
                                "end": existing_end.strftime("%H:%M"),
                                "date": existing_start.strftime("%Y-%m-%d")
                            })
                            
                    except Exception as dt_error:
                        logger.warning(f"AVAILABILITY: Error parsing existing event datetime: {dt_error}")
                        continue
            
            has_conflict = len(conflicts) > 0
            logger.info(f"AVAILABILITY: Result - Has conflict: {has_conflict}, Conflicts: {len(conflicts)}")
            
            return {
                "has_conflict": has_conflict,
                "conflicts": conflicts
            }
            
        except Exception as e:
            logger.error(f"AVAILABILITY ERROR: {e}")
            # En caso de error, asumir que no hay conflicto para no bloquear
            return {"has_conflict": False, "conflicts": []}
    
    def format_conflict_response(self, conflicts: List[Dict[str, Any]], event_data: Dict[str, Any]) -> str:
        """Formatea mensaje de conflicto de horario para el usuario"""
        try:
            response = "⚠️ *Conflicto de Horario Detectado*\n\n"
            response += f"El evento '{event_data.get('description')}' tiene conflictos:\n\n"
            
            for i, conflict in enumerate(conflicts, 1):
                response += f"{i}. *{conflict['title']}*\n"
                response += f"   📅 {conflict['date']}\n"
                response += f"   🕐 {conflict['start']} - {conflict['end']}\n\n"
            
            response += "💡 *Opciones:*\n"
            response += "• Elige otra hora para tu evento\n"
            response += "• Envía el mensaje de nuevo con hora diferente\n"
            response += "• Usa '/calendar' para ver tu agenda completa\n\n"
            response += "🔄 *No se creó el evento* para evitar conflictos."
            
            return response
            
        except Exception as e:
            logger.error(f"CONFLICT-FORMAT ERROR: {e}")
            return "⚠️ Se detectó un conflicto de horario. Por favor, elige otra hora para tu evento."

    async def detect_user_intent(self, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta la intención del usuario para evitar procesar saludos/comandos como tareas
        Retorna: {should_handle_directly: bool, response: str, type: str}
        """
        try:
            message_lower = message.lower().strip()
            
            # 1. SALUDOS SIMPLES - Responder directamente
            greetings = [
                'hola', 'hello', 'hi', 'hey', 'buenas', 'buenos días', 'buenas tardes', 
                'buenas noches', 'good morning', 'good afternoon', 'good evening',
                'qué tal', 'como estas', 'como estás', 'how are you', 'saludos'
            ]
            
            if any(greeting == message_lower for greeting in greetings):
                logger.info(f"INTENT: Saludo detectado - {message}")
                
                # Respuesta simple sin emojis para evitar problemas de encoding
                response = f"Hola! Soy Korei, tu asistente personal. En que te puedo ayudar hoy?"
                
                # Enviar respuesta
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response
                )
                
                return {
                    'should_handle_directly': True,
                    'status': 'handled',
                    'type': 'greeting',
                    'message': 'Saludo procesado'
                }
            
            # 2. COMANDOS SIN SLASH - Redirigir a comando handler
            command_words = {
                'help': '/help', 'ayuda': '/help',
                'stats': '/stats', 'estadisticas': '/stats', 'estadísticas': '/stats',
                'hoy': '/hoy', 'today': '/hoy',
                'mañana': '/mañana', 'tomorrow': '/mañana',
                'agenda': '/agenda', 'schedule': '/agenda',
                'tareas': '/tareas', 'tasks': '/tareas',
                'profile': '/profile', 'perfil': '/perfil'
            }
            
            if message_lower in command_words:
                logger.info(f"🎯 INTENT: Comando sin slash detectado - {message} -> {command_words[message_lower]}")
                return await self.handle_command(command_words[message_lower], user)
            
            # 3. PREGUNTAS SIMPLES - Responder directamente sin crear entrada
            simple_questions = [
                '¿qué tal?', 'que tal?', 'como va todo', 'cómo va todo',
                'how is it going', 'whats up', 'what\'s up', 'qué pasa',
                'que pasa', 'todo bien', '¿todo bien?', 'como estas',
                'cómo estás', 'how are you doing'
            ]
            
            if any(q in message_lower for q in simple_questions):
                logger.info(f"INTENT: Pregunta simple detectada - {message}")
                
                response = "Todo excelente! En que te puedo ayudar hoy?"
                
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response
                )
                
                return {
                    'should_handle_directly': True,
                    'status': 'handled',
                    'type': 'simple_question',
                    'message': 'Pregunta simple respondida'
                }
            
            # 4. AGRADECIMIENTOS - Responder cordialmente
            thanks = [
                'gracias', 'thanks', 'thank you', 'muchas gracias', 'perfecto gracias',
                'ok gracias', 'excelente gracias', 'genial gracias', 'perfect thanks'
            ]
            
            if any(thank in message_lower for thank in thanks):
                logger.info(f"INTENT: Agradecimiento detectado - {message}")
                
                responses = [
                    "De nada!", 
                    "Un placer ayudarte!",
                    "Para eso estoy!",
                    "Siempre a tu disposicion!"
                ]
                
                import random
                response = random.choice(responses)
                
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response
                )
                
                return {
                    'should_handle_directly': True,
                    'status': 'handled',
                    'type': 'thanks',
                    'message': 'Agradecimiento respondido'
                }
            
            # 5. MENSAJES MUY CORTOS Y AMBIGUOS - Pedir clarificación
            if len(message_lower) <= 2 or message_lower in ['ok', 'si', 'sí', 'no', 'bien', 'mal', 'mmm', 'ahh', 'ohh']:
                logger.info(f"INTENT: Mensaje muy corto/ambiguo - {message}")
                
                response = "Podrias ser mas especifico? Dime que necesitas y te ayudo."
                
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response
                )
                
                return {
                    'should_handle_directly': True,
                    'status': 'handled',
                    'type': 'ambiguous',
                    'message': 'Mensaje ambiguo, pidiendo clarificación'
                }
            
            # 6. EMOJIS SOLOS - Responder de forma amigable
            if all(ord(char) > 127 for char in message.strip()) and len(message.strip()) <= 10:  # Solo emojis/símbolos
                logger.info(f"INTENT: Solo emojis detectados - {message}")
                
                response = "Entendido!"
                
                await whatsapp_cloud_service.send_text_message(
                    to=user['whatsapp_number'],
                    message=response
                )
                
                return {
                    'should_handle_directly': True,
                    'status': 'handled',
                    'type': 'emoji_only',
                    'message': 'Emoji respondido'
                }
            
            # 7. Si llegamos aquí, es contenido real que debe procesarse con Gemini
            logger.info(f"INTENT: Contenido real detectado, enviando a Gemini - {message[:50]}...")
            return {
                'should_handle_directly': False,
                'type': 'real_content'
            }
            
        except Exception as e:
            logger.error(f"Error en detect_user_intent: {e}")
            # En caso de error, procesar normalmente con Gemini
            return {
                'should_handle_directly': False,
                'type': 'fallback'
            }

# Singleton
message_handler = MessageHandler()