"""
Manejador principal de mensajes
"""
from typing import Dict, Any
import os
import tempfile
from loguru import logger

from core.supabase import supabase
from services.whatsapp import whatsapp_service
from services.gemini import gemini_service

class MessageHandler:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    async def handle_text(self, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes de texto"""
        try:
            # Mostrar que estamos escribiendo
            await whatsapp_service.send_typing(user['whatsapp_number'])
            
            # Procesar con Gemini
            result = await gemini_service.process_message(message, user)
            
            # Guardar en base de datos
            entry_data = {
                **result,
                "user_id": user['id']
            }
            
            entry = await supabase.create_entry(entry_data)
            
            # Enviar confirmación
            response = whatsapp_service.format_response(result)
            await whatsapp_service.send_message(
                user['whatsapp_number'], 
                response
            )
            
            return {"status": "success", "entry_id": entry['id']}
            
        except Exception as e:
            logger.error(f"Error procesando texto: {e}")
            
            await whatsapp_service.send_message(
                user['whatsapp_number'],
                "❌ Hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
            )
            
            return {"status": "error", "message": str(e)}
    
    async def handle_audio(self, message_data: Dict[str, Any], 
                          user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes de audio usando Gemini directamente"""
        try:
            await whatsapp_service.send_typing(user['whatsapp_number'])
            
            # Descargar audio
            media_url = message_data.get('media', {}).get('url')
            if not media_url:
                raise ValueError("No se encontró URL del audio")
            
            audio_data = await whatsapp_service.download_media(media_url)
            
            # Guardar temporalmente
            temp_path = os.path.join(self.temp_dir, f"audio_{user['id']}.ogg")
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # Procesar con Gemini (que transcribe y procesa)
            result = await gemini_service.process_audio(temp_path, user)
            
            # Guardar en base de datos
            entry_data = {
                **result,
                "user_id": user['id']
            }
            
            # También guardar log del audio
            audio_log = {
                "user_id": user['id'],
                "original_audio_url": media_url,
                "transcribed_text": result.get('description', ''),
                "storage_path": None  # Podríamos subirlo a Supabase Storage
            }
            
            await supabase.client.table("voice_logs").insert(audio_log).execute()
            
            entry = await supabase.create_entry(entry_data)
            
            # Limpiar archivo temporal
            os.remove(temp_path)
            
            # Enviar confirmación
            response = "🎤 Audio procesado:\n\n"
            response += whatsapp_service.format_response(result)
            
            await whatsapp_service.send_message(
                user['whatsapp_number'], 
                response
            )
            
            return {"status": "success", "entry_id": entry['id']}
            
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            
            await whatsapp_service.send_message(
                user['whatsapp_number'],
                "❌ No pude procesar tu audio. Por favor, intenta de nuevo."
            )
            
            return {"status": "error", "message": str(e)}
    
    async def handle_image(self, message_data: Dict[str, Any], 
                          user: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa imágenes con Gemini Vision"""
        try:
            await whatsapp_service.send_typing(user['whatsapp_number'])
            
            # Descargar imagen
            media_url = message_data.get('media', {}).get('url')
            if not media_url:
                raise ValueError("No se encontró URL de la imagen")
            
            image_data = await whatsapp_service.download_media(media_url)
            
            # Contexto adicional del mensaje
            caption = message_data.get('caption', '')
            
            # Procesar con Gemini Vision
            result = await gemini_service.process_image(
                image_data, 
                caption, 
                user
            )
            
            # Guardar en base de datos
            entry_data = {
                **result,
                "user_id": user['id']
            }
            
            # Subir imagen a Supabase Storage (opcional)
            # image_url = await supabase.upload_media(
            #     image_data, 
            #     f"image_{entry_data['id']}.jpg",
            #     "image/jpeg"
            # )
            
            entry = await supabase.create_entry(entry_data)
            
            # Enviar confirmación
            response = "📷 Imagen procesada:\n\n"
            response += whatsapp_service.format_response(result)
            
            await whatsapp_service.send_message(
                user['whatsapp_number'], 
                response
            )
            
            return {"status": "success", "entry_id": entry['id']}
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            
            await whatsapp_service.send_message(
                user['whatsapp_number'],
                "❌ No pude procesar tu imagen. Por favor, intenta de nuevo."
            )
            
            return {"status": "error", "message": str(e)}

# Singleton
message_handler = MessageHandler()