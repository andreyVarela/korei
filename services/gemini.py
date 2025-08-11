"""
Servicio Gemini que maneja TODO: texto, audio e imágenes
"""
import google.generativeai as genai
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import pytz
from loguru import logger
from app.config import settings
import PIL.Image
import io
import asyncio
from functools import wraps

def with_timeout(timeout_seconds: int = 30):
    """Decorator para agregar timeout a métodos síncronos de Gemini"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Ejecutar función síncrona en thread pool con timeout
                return await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, lambda: func(*args, **kwargs)
                    ),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"Timeout en {func.__name__} después de {timeout_seconds}s")
                raise TimeoutError(f"Gemini tardó más de {timeout_seconds} segundos")
        return wrapper
    return decorator

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        
        # Modelo para texto
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Modelo para multimodal (imágenes + texto)
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.tz = pytz.timezone(settings.timezone)
        
    async def process_message(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensaje de texto"""
        try:
            current_time = datetime.now(self.tz)
            
            prompt = self._build_prompt(message, user_context, current_time)
            
            # Aplicar timeout de 30 segundos
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.model.generate_content(prompt)
                ),
                timeout=30.0
            )
            
            return self._extract_json(response.text)
            
        except asyncio.TimeoutError:
            logger.error("Timeout procesando mensaje con Gemini")
            return self._get_fallback_response(f"Timeout procesando: {message[:50]}...")
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            return self._get_fallback_response(message)
    
    async def process_audio(self, audio_path: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa audio directamente con Gemini
        Gemini 1.5 Pro puede procesar audio directamente!
        """
        try:
            # Cargar archivo de audio
            audio_file = genai.upload_file(path=audio_path)
            
            current_time = datetime.now(self.tz)
            
            prompt = f"""
            Transcribe este audio y luego procésalo según estas instrucciones:
            
            CONTEXTO:
            - Usuario: {user_context.get('name', 'Usuario')}
            - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
            
            {self._get_base_instructions()}
            
            Devuelve ÚNICAMENTE el JSON estructurado.
            """
            
            # Aplicar timeout de 45 segundos (audio tarda más)
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.model.generate_content([prompt, audio_file])
                ),
                timeout=45.0
            )
            
            # Limpiar archivo temporal
            genai.delete_file(audio_file.name)
            
            return self._extract_json(response.text)
            
        except asyncio.TimeoutError:
            logger.error("Timeout procesando audio con Gemini")
            return self._get_fallback_response("Audio procesado (timeout)")
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            return self._get_fallback_response("Audio procesado")
    
    async def process_image(self, image_data: bytes, context: str = "", 
                          user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa imagen con Gemini Vision
        """
        try:
            # Convertir bytes a imagen PIL
            image = PIL.Image.open(io.BytesIO(image_data))
            
            current_time = datetime.now(self.tz)
            
            prompt = f"""
            Analiza esta imagen y procésala según el contexto.
            
            CONTEXTO:
            - Usuario: {user_context.get('name', 'Usuario') if user_context else 'Usuario'}
            - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
            - Contexto adicional: {context}
            
            IDENTIFICAR:
            1. Si es un recibo/factura: extrae el monto total y descripción
            2. Si es un calendario/agenda: extrae eventos y fechas
            3. Si es una captura con texto: extrae la información relevante
            
            {self._get_base_instructions()}
            
            Devuelve ÚNICAMENTE el JSON estructurado.
            """
            
            # Aplicar timeout de 30 segundos
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.vision_model.generate_content([prompt, image])
                ),
                timeout=30.0
            )
            
            return self._extract_json(response.text)
            
        except asyncio.TimeoutError:
            logger.error("Timeout procesando imagen con Gemini")
            return self._get_fallback_response("Imagen analizada (timeout)")
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            return self._get_fallback_response("Imagen analizada")
    
    def _build_prompt(self, message: str, user_context: Dict[str, Any], 
                     current_time: datetime) -> str:
        """Construye prompt para texto"""
        
        # Extraer información del perfil
        profile = user_context.get('profile', {})
        name = user_context.get('name', 'Usuario')
        occupation = profile.get('occupation', '')
        hobbies = profile.get('hobbies', [])
        context_summary = profile.get('context_summary', '')
        
        # Construir contexto personal
        personal_context = ""
        if occupation:
            personal_context += f"- Ocupación: {occupation}\n        "
        if hobbies:
            personal_context += f"- Hobbies: {', '.join(hobbies)}\n        "
        if context_summary:
            personal_context += f"- Contexto personal: {context_summary}\n        "
        
        return f"""
        Eres Korei, un asistente personal inteligente que conoce a {name} y se adapta a su estilo de vida.
        
        INFORMACIÓN DEL USUARIO:
        - Nombre: {name}
        {personal_context}
        
        CONTEXTO TEMPORAL:
        - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
        - Día de la semana: {current_time.strftime('%A')}
        
        MENSAJE A PROCESAR:
        "{message}"
        
        INSTRUCCIONES:
        - Usa el contexto personal para dar respuestas más relevantes
        - Si conoces la ocupación, ajusta sugerencias (ej: "reunión" puede ser trabajo)
        - Si conoces hobbies, relaciona gastos/eventos con ellos
        - Mantén el tono personal y familiar
        
        {self._get_base_instructions()}
        
        JSON:"""
    
    def _get_base_instructions(self) -> str:
        """Instrucciones base para todos los prompts"""
        return """
        INSTRUCCIONES:
        1. Analiza el contenido y determina el tipo correcto
        2. Extrae TODA la información relevante
        3. Genera fechas relativas correctamente (hoy, mañana, próximo lunes, etc.)
        4. Para gastos/ingresos, extrae el monto numérico
        5. Devuelve ÚNICAMENTE un objeto JSON válido
        
        TIPOS DISPONIBLES:
        - gasto: Compras, pagos, cualquier salida de dinero
        - ingreso: Salario, cobros, entrada de dinero  
        - evento: Citas, reuniones, actividades con hora específica
        - tarea: Actividades por hacer, con o sin fecha límite
        - recordatorio: Alertas simples para recordar algo
        
        ESTRUCTURA JSON REQUERIDA:
        {
            "type": "string",
            "description": "string",
            "amount": number o null,
            "datetime": "YYYY-MM-DDTHH:MM:SS-06:00",
            "datetime_end": "YYYY-MM-DDTHH:MM:SS-06:00",
            "priority": "alta|media|baja",
            "recurrence": "none|daily|weekly|monthly|yearly",
            "calendary": boolean,
            "remember": "YYYY-MM-DDTHH:MM:SS-06:00" o null,
            "task_category": "Trabajo|Personal|Ocio" o null,
            "status": "pending|completed|cancelled"
        }
        """
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extrae JSON de la respuesta"""
        try:
            # Limpiar respuesta
            text = text.strip()
            
            # Buscar JSON
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            
            raise ValueError("No se encontró JSON válido")
            
        except Exception as e:
            logger.error(f"Error extrayendo JSON: {e}")
            raise
    
    def _get_fallback_response(self, description: str) -> Dict[str, Any]:
        """Respuesta por defecto"""
        now = datetime.now(self.tz)
        
        return {
            "type": "recordatorio",
            "description": description[:100],
            "datetime": now.isoformat(),
            "datetime_end": (now + timedelta(minutes=30)).isoformat(),
            "status": "pending",
            "calendary": False,
            "recurrence": "none",
            "priority": "media",
            "amount": None,
            "task_category": None,
            "remember": None
        }

# Singleton
gemini_service = GeminiService()