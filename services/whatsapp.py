"""
Servicio para WhatsApp usando WAHA API
"""
import aiohttp
from typing import Dict, Any, Optional
from loguru import logger
from app.config import settings

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.waha_api_url
        self.api_key = settings.waha_api_key
        self.session_name = settings.waha_session
        
    async def send_message(self, to: str, message: str) -> bool:
        """
        Envía mensaje de texto
        """
        try:
            # Si WAHA no está configurado, solo log
            if self.api_key == "tu_waha_key_aqui":
                logger.info(f"[MOCK] Mensaje a {to}: {message}")
                return True
                
            url = f"{self.base_url}/api/sendText"
            payload = {
                "session": self.session_name,
                "chatId": f"{to}@c.us",
                "text": message
            }
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Mensaje enviado a {to}")
                        return True
                    else:
                        logger.error(f"Error enviando mensaje: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error en send_message: {e}")
            return False
    
    async def send_image(self, to: str, image_url: str, caption: str = "") -> bool:
        """
        Envía imagen con caption
        """
        try:
            if self.api_key == "tu_waha_key_aqui":
                logger.info(f"[MOCK] Imagen a {to}: {caption}")
                return True
                
            url = f"{self.base_url}/api/sendImage"
            payload = {
                "session": self.session_name,
                "chatId": f"{to}@c.us",
                "file": {"url": image_url},
                "caption": caption
            }
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error enviando imagen: {e}")
            return False
    
    async def download_media(self, message_id: str) -> Optional[bytes]:
        """
        Descarga media de WhatsApp
        """
        try:
            if self.api_key == "tu_waha_key_aqui":
                logger.info(f"[MOCK] Descarga media: {message_id}")
                return b"mock_media_data"
                
            url = f"{self.base_url}/api/files/{message_id}"
            
            headers = {"X-API-KEY": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
                    
        except Exception as e:
            logger.error(f"Error descargando media: {e}")
            return None
    
    def is_configured(self) -> bool:
        """
        Verifica si WAHA está configurado
        """
        return self.api_key != "tu_waha_key_aqui"

# Instancia singleton
whatsapp_service = WhatsAppService()