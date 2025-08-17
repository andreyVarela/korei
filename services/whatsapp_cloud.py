"""
Servicio para WhatsApp Cloud API
"""
import httpx
import json
from typing import Optional, Dict, Any
from loguru import logger
from app.config import settings


class WhatsAppCloudService:
    """Servicio para interactuar con WhatsApp Cloud API"""
    
    def __init__(self):
        pass  # Initialize empty, get fresh settings each time
    
    def _get_headers(self):
        """Get fresh headers with current token"""
        from app.config import get_settings
        current_settings = get_settings()
        clean_token = current_settings.whatsapp_access_token.strip()
        return {
            "Authorization": f"Bearer {clean_token}",
            "Content-Type": "application/json"
        }
    
    def _get_base_url(self):
        """Get fresh base URL with current settings"""
        from app.config import get_settings
        current_settings = get_settings()
        return f"https://graph.facebook.com/v18.0/{current_settings.whatsapp_phone_number_id}"
    
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto usando WhatsApp Cloud API
        
        Args:
            to: Número de teléfono del destinatario (con código de país)
            message: Mensaje a enviar
            
        Returns:
            Respuesta de la API
        """
        url = f"{self._get_base_url()}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        try:
            logger.info(f"Enviando mensaje a {to}: {message[:50]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Mensaje enviado exitosamente. Message ID: {result.get('messages', [{}])[0].get('id', 'unknown')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP al enviar mensaje: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            raise
    
    async def send_interactive_message(self, to: str, body_text: str, buttons: list) -> Dict[str, Any]:
        """
        Envía un mensaje interactivo con botones usando WhatsApp Cloud API
        
        Args:
            to: Número de teléfono del destinatario
            body_text: Texto principal del mensaje
            buttons: Lista de botones [{"id": "btn1", "title": "Texto del botón"}]
            
        Returns:
            Respuesta de la API
        """
        url = f"{self._get_base_url()}/messages"
        
        # Formatear botones según especificación de WhatsApp Cloud API
        button_components = []
        for i, button in enumerate(buttons[:3]):  # Máximo 3 botones
            button_components.append({
                "type": "reply",
                "reply": {
                    "id": button.get("id", f"btn_{i}"),
                    "title": button.get("title", "Botón")[:20]  # Máximo 20 caracteres
                }
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual", 
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": button_components
                }
            }
        }
        
        try:
            logger.info(f"Enviando mensaje interactivo a {to} con {len(buttons)} botones")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Mensaje interactivo enviado exitosamente. Message ID: {result.get('messages', [{}])[0].get('id', 'unknown')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP al enviar mensaje interactivo: {e.response.status_code} - {e.response.text}")
            # Fallback: enviar como mensaje de texto normal
            logger.info("Fallback: enviando como mensaje de texto normal")
            fallback_text = body_text + "\n\n" + "\n".join([f"• {btn['title']}" for btn in buttons])
            return await self.send_text_message(to, fallback_text)
        except Exception as e:
            logger.error(f"Error al enviar mensaje interactivo: {str(e)}")
            # Fallback: enviar como mensaje de texto normal  
            fallback_text = body_text + "\n\n" + "\n".join([f"• {btn['title']}" for btn in buttons])
            return await self.send_text_message(to, fallback_text)
    
    async def send_template_message(self, to: str, template_name: str, language_code: str = "es") -> Dict[str, Any]:
        """
        Envía un mensaje de template usando WhatsApp Cloud API
        
        Args:
            to: Número de teléfono del destinatario
            template_name: Nombre del template aprobado
            language_code: Código del idioma (default: es)
            
        Returns:
            Respuesta de la API
        """
        url = f"{self._get_base_url()}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        try:
            logger.info(f"Enviando template '{template_name}' a {to}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Template enviado exitosamente. Message ID: {result.get('messages', [{}])[0].get('id', 'unknown')}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP al enviar template: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error al enviar template: {str(e)}")
            raise
    
    def format_phone_number(self, phone: str) -> str:
        """
        Formatea un número de teléfono para WhatsApp Cloud API
        
        Args:
            phone: Número de teléfono
            
        Returns:
            Número formateado
        """
        # Remover caracteres especiales
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Si no empieza con código de país, asumir Costa Rica (+506)
        if not clean_phone.startswith('506') and len(clean_phone) == 8:
            clean_phone = '506' + clean_phone
        
        return clean_phone

    async def send_task_with_buttons(self, to: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía una tarea específica con botones de acción
        
        Args:
            to: Número de teléfono
            task: Diccionario con datos de la tarea
            
        Returns:
            Respuesta de la API
        """
        from datetime import datetime
        import pytz
        from app.config import settings
        
        # Formatear información de la tarea
        description = task.get('description', 'Tarea sin descripción')
        priority = task.get('priority', 'media')
        task_id = task.get('id', '')
        
        # Formatear fecha si existe
        datetime_str = ""
        if task.get('datetime'):
            try:
                tz = pytz.timezone(settings.timezone)
                task_time = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                task_time_local = task_time.astimezone(tz)
                datetime_str = f"\n⏰ {task_time_local.strftime('%H:%M')}"
            except:
                pass
        
        # Emoji de prioridad
        priority_emoji = {
            'alta': '🔴',
            'media': '🟡', 
            'baja': '🟢'
        }.get(priority, '🟡')
        
        # Formatear mensaje
        message_text = f"📋 **TAREA**\n\n{priority_emoji} {description}{datetime_str}"
        
        # Crear botones de acción
        buttons = [
            {
                "id": f"complete_task_{task_id}",
                "title": "✅ Completar"
            },
            {
                "id": f"delete_task_{task_id}", 
                "title": "🗑️ Eliminar"
            },
            {
                "id": f"info_task_{task_id}",
                "title": "ℹ️ Info"
            }
        ]
        
        return await self.send_interactive_message(to, message_text, buttons)

    async def send_multiple_tasks(self, to: str, tasks: list, send_individually: bool = True, max_individual: int = 3) -> list:
        """
        Envía múltiples tareas de forma inteligente - primeras 3 con botones, resto en resumen
        
        Args:
            to: Número de teléfono
            tasks: Lista de tareas (ya ordenadas por prioridad/fecha)
            send_individually: Si True, envía las primeras tareas en mensajes separados
            max_individual: Máximo de tareas a enviar individualmente (default: 3)
            
        Returns:
            Lista de respuestas de la API
        """
        import asyncio
        from datetime import datetime
        import pytz
        from app.config import settings
        
        results = []
        total_tasks = len(tasks)
        
        if total_tasks == 0:
            return results
        
        # Determinar cuántas tareas enviar individualmente
        tasks_to_send_individual = min(max_individual, total_tasks)
        remaining_tasks = max(0, total_tasks - tasks_to_send_individual)
        
        if send_individually and total_tasks > 0:
            # Mensaje inicial súper conciso
            if total_tasks == 1:
                header_text = f"📋 Tu tarea:"
            elif total_tasks <= 3:
                header_text = f"📋 Tus {total_tasks} tareas:"
            else:
                header_text = f"📋 Tareas prioritarias ({tasks_to_send_individual}/{total_tasks}):"
            
            await self.send_text_message(to, header_text)
            
            # Pequeña pausa antes de enviar tareas
            await asyncio.sleep(1)
            
            # Enviar solo las tareas prioritarias individualmente
            priority_tasks = tasks[:tasks_to_send_individual]
            
            for i, task in enumerate(priority_tasks):
                try:
                    # Pausa entre mensajes para evitar rate limiting
                    if i > 0:
                        await asyncio.sleep(0.8)
                    
                    result = await self.send_task_with_buttons(to, task)
                    results.append({
                        "task_id": task.get('id'),
                        "description": task.get('description', '')[:30] + "...",
                        "success": "error" not in result,
                        "result": result,
                        "sent_individually": True
                    })
                    
                    logger.info(f"📤 Tarea individual enviada: {task.get('description', 'Sin descripción')[:40]}...")
                    
                except Exception as e:
                    logger.error(f"Error enviando tarea individual {task.get('id', 'unknown')}: {e}")
                    results.append({
                        "task_id": task.get('id'),
                        "description": task.get('description', 'Error'),
                        "success": False,
                        "error": str(e),
                        "sent_individually": True
                    })
            
            # Si hay tareas adicionales, enviar resumen con opciones
            if remaining_tasks > 0:
                await asyncio.sleep(1.5)
                await self.send_remaining_tasks_summary(to, tasks[tasks_to_send_individual:], remaining_tasks)
            
            # Solo mensaje final si hay tareas restantes importantes
            if remaining_tasks > 5:  # Solo si hay muchas más
                await asyncio.sleep(1)
                footer_text = f"💡 {remaining_tasks} tareas más en `/hoy`"
                await self.send_text_message(to, footer_text)
                
        else:
            # Enviar resumen simple
            task_list = "\n".join([
                f"• {task.get('description', 'Sin descripción')}" 
                for task in tasks
            ])
            
            summary_text = f"📋 **TAREAS PENDIENTES ({len(tasks)})**\n\n{task_list}\n\n💡 Usa `/completar [tarea]` para marcar como completada"
            
            result = await self.send_text_message(to, summary_text)
            results.append({"type": "summary", "result": result})
        
        return results
    
    async def send_remaining_tasks_summary(self, to: str, remaining_tasks: list, count: int):
        """Envía resumen conciso de tareas restantes"""
        try:
            # Solo enviar si hay muchas tareas restantes (4+)
            if count < 4:
                return
                
            from datetime import datetime
            import pytz
            from app.config import settings
            
            tz = pytz.timezone(settings.timezone)
            
            # Mostrar solo las primeras 3 del resto
            preview_tasks = remaining_tasks[:3]
            summary_text = f"📝 Otras {count} tareas:\n"
            
            for i, task in enumerate(preview_tasks, 1):
                # Solo mostrar descripción, sin tanto detalle
                desc = task['description']
                if len(desc) > 25:
                    desc = desc[:25] + "..."
                summary_text += f"• {desc}\n"
            
            if count > 3:
                summary_text += f"• ... y {count - 3} más"
            
            # Solo botón para ver todas, no más opciones
            buttons = [{"id": "action_show_all_tasks", "title": "📋 Ver Todas"}]
            
            await self.send_interactive_message(to, summary_text, buttons)
            
        except Exception as e:
            logger.error(f"Error enviando resumen de tareas restantes: {e}")


# Instancia global del servicio
whatsapp_cloud_service = WhatsAppCloudService()