"""
Servicio Gemini que maneja TODO: texto, audio e imágenes
"""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
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
            
            prompt = await self._build_prompt(message, user_context, current_time)
            
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
    
    async def extract_audio_context(self, audio_path: str, user_context: Dict[str, Any] = None) -> str:
        """
        Extrae contexto de un archivo de audio sin procesarlo directamente
        """
        try:
            logger.info(f"GEMINI-AUDIO: Iniciando transcripción de {audio_path}")
            
            # Verificar que el archivo existe
            import pathlib
            import os
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Archivo de audio no encontrado: {audio_path}")
            
            # Verificar tamaño del archivo
            file_size = os.path.getsize(audio_path)
            logger.info(f"GEMINI-AUDIO: Tamaño del archivo: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError("Archivo de audio está vacío")
            
            # Cargar archivo de audio usando la API actualizada
            logger.info(f"GEMINI-AUDIO: Subiendo archivo a Gemini...")
            audio_file = genai.upload_file(pathlib.Path(audio_path))
            logger.info(f"GEMINI-AUDIO: Archivo subido exitosamente. ID: {audio_file.name}")
            
            # También leer para debugging
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            logger.info(f"GEMINI-AUDIO: Archivo leído para debug. Tamaño: {len(audio_data)} bytes")
            
            current_time = datetime.now(self.tz)
            
            prompt = f"""
            TRANSCRIBE este audio con MÁXIMA PRECISIÓN. Este es un usuario de Costa Rica que habla ESPAÑOL.
            
            CONTEXTO DEL USUARIO:
            - Nombre: {user_context.get('name', 'Usuario') if user_context else 'Usuario'}
            - País: Costa Rica (español costarricense)
            - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
            
            VOCABULARIO COMÚN ESPERADO (COSTA RICA):
            - "gasto", "gasté", "gastó" = expense/spent money
            - "colones" = Costa Rican currency
            - "plata", "dinero" = money
            - "pagué", "pago" = I paid/payment
            - "almuerzo", "desayuno", "cena" = meals
            - "compré", "compra" = I bought/purchase
            - "trabajo", "reunión", "cita" = work/meeting/appointment
            - "mañana", "hoy", "ayer" = tomorrow/today/yesterday
            
            INSTRUCCIONES DE TRANSCRIPCIÓN:
            1. Transcribe EXACTAMENTE lo que se dice en ESPAÑOL
            2. Presta especial atención a palabras de FINANZAS y DINERO
            3. Si el audio menciona cantidades, números o montos, transcríbelos con precisión
            4. Si menciona "gasté", "compré", "pagué" - esto es MUY IMPORTANTE
            5. Si no entiendes una palabra, escribe [inaudible] pero continúa con el resto
            6. Mantén el acento y expresiones costarricenses
            
            FORMATO DE RESPUESTA:
            - Responde SOLO con la transcripción directa
            - NO agregues explicaciones ni formato JSON
            - NO categorices ni analices, solo transcribe
            - Ejemplo: "Gasté veinticinco mil colones en almuerzo en el restaurante de la esquina ayer"
            
            TRANSCRIPCIÓN DEL AUDIO:
            """
            
            # Aplicar timeout de 45 segundos (audio tarda más)
            logger.info(f"GEMINI-AUDIO: Enviando prompt a Gemini con timeout de 45s...")
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.model.generate_content([prompt, audio_file])
                ),
                timeout=45.0
            )
            
            logger.info(f"GEMINI-AUDIO: Respuesta recibida de Gemini")
            
            # Limpiar archivo temporal de Gemini
            try:
                genai.delete_file(audio_file.name)
                logger.info(f"GEMINI-AUDIO: Archivo temporal limpiado")
            except Exception as cleanup_error:
                logger.warning(f"GEMINI-AUDIO: Error limpiando archivo temporal: {cleanup_error}")
            
            transcription = response.text.strip()
            logger.info(f"GEMINI-AUDIO: Transcripción exitosa: {transcription[:100]}...")
            return transcription
            
        except asyncio.TimeoutError:
            logger.error("Timeout extrayendo contexto de audio")
            return "Audio recibido pero no se pudo procesar por timeout."
        except Exception as e:
            logger.error(f"Error extrayendo contexto de audio: {e}")
            return "Audio recibido pero no se pudo transcribir el contenido."

    async def process_audio(self, audio_path: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa audio usando el pipeline de dos pasos
        """
        try:
            # Paso 1: Extraer contexto/transcripción del audio
            audio_context = await self.extract_audio_context(audio_path, user_context)
            
            # Paso 2: Procesar el contexto extraído a través del pipeline normal
            enhanced_message = f"Información extraída de audio: {audio_context}"
            
            # Usar el pipeline completo de procesamiento de mensajes
            return await self.process_message(enhanced_message, user_context)
            
        except Exception as e:
            logger.error(f"Error en pipeline de audio: {e}")
            return self._get_fallback_response("Audio procesado")
    
    async def extract_image_context(self, image_data: bytes, user_context: Dict[str, Any] = None) -> str:
        """
        Extrae contexto de una imagen sin procesarla directamente
        """
        try:
            # Convertir bytes a imagen PIL
            image = PIL.Image.open(io.BytesIO(image_data))
            
            current_time = datetime.now(self.tz)
            
            prompt = f"""
            Analiza esta imagen y extrae ÚNICAMENTE el contexto/información visible.
            NO proceses la información ni la estructures en JSON.
            
            CONTEXTO:
            - Usuario: {user_context.get('name', 'Usuario') if user_context else 'Usuario'}
            - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
            
            INSTRUCCIONES:
            1. Describe QUÉ VES en la imagen de forma textual y natural
            2. Si es un recibo/factura: extrae montos, establecimiento, fecha, productos
            3. Si es una captura de pantalla: describe el contenido y texto visible
            4. Si es un calendario/agenda: menciona fechas, eventos, horarios
            5. Si es una lista de tareas: enumera las tareas visibles
            6. Si es una conversación: resume el contenido principal
            7. Si contiene texto: transcribe el texto importante
            
            IMPORTANTE:
            - Responde en español natural
            - NO uses formato JSON
            - NO categorices como gasto/ingreso/evento aún
            - Solo describe lo que ves de forma clara y completa
            - Incluye todos los detalles relevantes (montos, fechas, nombres, etc.)
            
            Ejemplo de respuesta:
            "Veo un recibo del restaurante La Fortuna por ₡15,000. El recibo incluye: 1 Casado completo ₡8,500, 1 Refresco natural ₡2,500, 1 Postre tres leches ₡4,000. La fecha es 15 de agosto 2025 a las 13:45. El método de pago fue efectivo."
            
            RESPUESTA:
            """
            
            # Aplicar timeout de 30 segundos
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: self.vision_model.generate_content([prompt, image])
                ),
                timeout=30.0
            )
            
            return response.text.strip()
            
        except asyncio.TimeoutError:
            logger.error("Timeout extrayendo contexto de imagen")
            return "Imagen recibida pero no se pudo procesar por timeout."
        except Exception as e:
            logger.error(f"Error extrayendo contexto de imagen: {e}")
            return "Imagen recibida pero no se pudo extraer el contexto."

    async def process_image(self, image_data: bytes, context: str = "", 
                          user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Procesa imagen con Gemini Vision usando el pipeline de dos pasos
        """
        try:
            # Paso 1: Extraer contexto de la imagen
            image_context = await self.extract_image_context(image_data, user_context)
            
            # Paso 2: ANÁLISIS INTELIGENTE DE TRANSACCIONES
            transaction_analysis = None
            if user_context and user_context.get('name'):
                from services.name_matcher import name_matcher
                
                logger.error(f"🔥 CRITICAL - USER NAME FOR ANALYSIS: '{user_context['name']}'")
                logger.error(f"🔥 CRITICAL - IMAGE CONTEXT: '{image_context}'")
                
                # Analizar si es una transacción financiera
                transaction_analysis = name_matcher.analyze_transaction_direction(
                    image_context, 
                    user_context['name']
                )
                
                logger.error(f"🔥 CRITICAL - TRANSACTION_ANALYSIS: {transaction_analysis}")
            
            # Paso 3: Construir mensaje mejorado para Gemini
            enhanced_message = f"Información extraída de imagen: {image_context}"
            if context:
                enhanced_message += f"\nContexto adicional: {context}"
            
            # Agregar análisis inteligente si existe
            if transaction_analysis and transaction_analysis.get('type'):
                confidence = transaction_analysis.get('confidence', 0)
                reasoning = transaction_analysis.get('reasoning', [])
                
                enhanced_message += f"\n\nANÁLISIS INTELIGENTE DE TRANSACCIÓN:"
                enhanced_message += f"\n- Tipo detectado: {transaction_analysis['type'].upper()} (confianza: {confidence:.1%})"
                enhanced_message += f"\n- Razonamiento: {', '.join(reasoning)}"
                
                if transaction_analysis.get('found_names'):
                    enhanced_message += f"\n- Nombres encontrados: {transaction_analysis['found_names']}"
            
            # Usar el pipeline normal de procesamiento de mensajes
            logger.error(f"🔥 CRITICAL - ENHANCED MESSAGE TO GEMINI: {enhanced_message}")
            result = await self.process_message(enhanced_message, user_context)
            logger.error(f"🔥 CRITICAL - GEMINI FINAL RESULT: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error en pipeline de imagen: {e}")
            return self._get_fallback_response("Imagen procesada")
    
    async def _build_prompt(self, message: str, user_context: Dict[str, Any], 
                           current_time: datetime) -> str:
        """Construye prompt enriquecido para texto"""
        
        # Extraer información del perfil
        profile = user_context.get('profile', {})
        name = user_context.get('name', 'Usuario')
        user_id = user_context.get('id')
        occupation = profile.get('occupation', '')
        hobbies = profile.get('hobbies', [])
        context_summary = profile.get('context_summary', '')
        preferences = profile.get('preferences', {})
        
        # Construir contexto personal
        personal_context = ""
        if occupation:
            personal_context += f"- Ocupación: {occupation}\n        "
        if hobbies:
            personal_context += f"- Hobbies: {', '.join(hobbies)}\n        "
        if context_summary:
            personal_context += f"- Contexto personal: {context_summary}\n        "
        
        # Obtener contexto enriquecido si hay user_id
        financial_context = ""
        upcoming_events = ""
        spending_patterns = ""
        user_preferences = ""
        
        if user_id:
            try:
                # Importar aquí para evitar circular imports
                from core.supabase import supabase
                
                # 1. Contexto financiero reciente (últimos 7 días)
                financial_data = await self._get_recent_financial_context(supabase, user_id, current_time)
                if financial_data:
                    financial_context = f"""
        CONTEXTO FINANCIERO RECIENTE (últimos 7 días):
        - Gastos totales: ₡{financial_data.get('total_gastos', 0):,.0f}
        - Promedio diario: ₡{financial_data.get('promedio_diario', 0):,.0f}
        - Categorías principales: {', '.join(financial_data.get('categorias_principales', []))}
        - Último gasto: {financial_data.get('ultimo_gasto', 'N/A')}
        """
                
                # 2. Eventos próximos (próximos 3 días)
                events_data = await self._get_upcoming_events_context(supabase, user_id, current_time)
                if events_data:
                    upcoming_events = f"""
        EVENTOS PRÓXIMOS (próximos 3 días):
        {chr(10).join([f"- {event}" for event in events_data[:5]])}
        """
                
                # 3. Patrones de gasto (último mes)
                patterns_data = await self._get_spending_patterns_context(supabase, user_id)
                if patterns_data:
                    spending_patterns = f"""
        PATRONES DE GASTO (último mes):
        - Días de mayor gasto: {', '.join(patterns_data.get('dias_frecuentes', []))}
        - Horarios comunes: {', '.join(patterns_data.get('horarios_comunes', []))}
        - Categorías frecuentes: {', '.join(patterns_data.get('categorias_frecuentes', []))}
        """
                
                # 4. Preferencias del usuario
                if preferences:
                    user_preferences = f"""
        PREFERENCIAS DEL USUARIO:
        - Estilo de trabajo: {preferences.get('work_style', 'No especificado')}
        - Intereses principales: {', '.join(preferences.get('interests', []))}
        """
                    
            except Exception as e:
                logger.warning(f"Error obteniendo contexto enriquecido: {e}")
        
        return f"""
        Eres Korei, un asistente personal inteligente que conoce profundamente a {name} y se adapta a su estilo de vida y patrones.
        
        INFORMACIÓN DEL USUARIO:
        - Nombre: {name}
        {personal_context}{user_preferences}
        
        CONTEXTO TEMPORAL:
        - Fecha/Hora actual: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (Costa Rica, UTC-6)
        - Día de la semana: {current_time.strftime('%A')}
        {financial_context}{upcoming_events}{spending_patterns}
        MENSAJE A PROCESAR:
        "{message}"
        
        INSTRUCCIONES AVANZADAS:
        - Usa TODOS los contextos para dar respuestas más precisas y personalizadas
        - Si conoces patrones de gasto, sugiere categorías coherentes con su comportamiento
        - Si hay eventos próximos, considera conflictos de horario al asignar fechas
        - Ajusta las horas sugeridas según sus patrones temporales habituales
        - Para gastos, considera si está dentro de sus patrones normales o es atípico
        - Si conoces su trabajo remoto/presencial, ajusta sugerencias de ubicación
        - Relaciona nuevos gastos/eventos con sus hobbies e intereses conocidos
        - Mantén el tono personal y familiar, pero profesional
        
        INSTRUCCIONES ESPECIALES PARA AUDIO TRANSCRITO:
        - Si el mensaje incluye "Información extraída de audio:", analiza el contenido transcrito cuidadosamente
        - Presta atención especial a palabras clave financieras en español: "gasté", "pagué", "compré", "costó"
        - Cuando veas transcripciones de audio, busca patrones de habla coloquial costarricense
        - Si la transcripción menciona dinero o pagos, el tipo DEBE ser "gasto" o "ingreso"
        - No categorices audio transcrito como "tarea" a menos que claramente se refiera a algo por hacer
        
        FILTROS ANTI-ERROR PARA AUDIO:
        - Si la transcripción contiene "proceso archivo", "procesar audio", "audio del usuario" sin contexto real, clasifica como "recordatorio" con descripción "Audio recibido sin contenido claro"
        - NUNCA categorices como "tarea" transcripciones que hablen de procesar archivos técnicos
        - Si no hay contenido real en la transcripción, devuelve tipo "recordatorio" en lugar de "tarea"
        
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
        5. INTELIGENCIA DE TIEMPO: Si no se especifica hora, analiza la complejidad y asigna duración inteligente
        6. Devuelve ÚNICAMENTE un objeto JSON válido
        
        TIPOS DISPONIBLES:
        - gasto: Compras, pagos, cualquier salida de dinero
        - ingreso: Salario, cobros, entrada de dinero  
        - evento: Citas, reuniones, actividades con hora específica
        - tarea: Actividades por hacer, con o sin fecha límite
        - recordatorio: Alertas simples para recordar algo
        
        PALABRAS CLAVE PARA IDENTIFICACIÓN DE TIPOS (ESPAÑOL COSTA RICA):
        GASTO: "gasté", "pagué", "compré", "costó", "salió", "invertí", "gastó", "dinero", "colones", "plata", "caro", "barato", "precio", "debitaron", "se debita"
        INGRESO: "gané", "cobré", "recibí", "me pagaron", "ingreso", "salario", "bono", "ganancia", "comisión", "pago", "sueldo", "depositaron", "se deposita", "transferencia recibida"
        
        LÓGICA INTELIGENTE PARA COMPROBANTES BANCARIOS/SINPE/FACTURAS:
        - Usuario propietario: {user_context.get('name', '')} | Tel: {user_context.get('whatsapp_number', '')}
        
        **CONTEXTO DE ASISTENTE PERSONAL CRÍTICO:**
        El usuario envía imágenes por WhatsApp para documentar SUS transacciones financieras.
        Si el usuario envía una imagen de transferencia, está registrando una transacción que LE AFECTA:
        
        - Si la imagen muestra "Transferencia SINPE Móvil A [USUARIO]" → SIEMPRE es INGRESO para el usuario
        - Si la imagen muestra "Transferencia SINPE Móvil DE [USUARIO]" → SIEMPRE es GASTO para el usuario  
        - Si la imagen muestra "se debitaron de [OTRA PERSONA]" pero el destino es el USUARIO → es INGRESO para el usuario
        - PRIORIDAD: El análisis inteligente previo tiene MÁXIMA PRIORIDAD sobre indicadores literales
        
        REGLAS CRÍTICAS PARA DETECTAR INGRESO vs GASTO:
        
        1. **ANÁLISIS DE NOMBRES (MUY IMPORTANTE)**:
           - BUSCA nombres de personas en el texto de la imagen
           - COMPARA con el nombre del usuario (ignorar mayúsculas/minúsculas y nombres medios)
           - Ejemplos de matching fuzzy:
             * "NOMBRE COMPLETO USUARIO" = "Nombre Usuario" ✅ MATCH
             * "MARIA JOSE GONZALEZ RUIZ" = "Maria Gonzalez" ✅ MATCH  
             * "JUAN CARLOS PEREZ MORA" = "Juan Perez" ✅ MATCH
             * Ignore diferencias en mayúsculas, acentos y nombres medios
        
        2. **PATRONES ESPECÍFICOS DE SINPE MÓVIL**:
           • "Transferencia SINPE Móvil A [NOMBRE]" = INGRESO si [NOMBRE] es el usuario
           • "Transferencia SINPE Móvil DE [NOMBRE]" = GASTO si [NOMBRE] es el usuario
           • "enviaste a [NOMBRE]" = GASTO (el usuario envió)
           • "recibiste de [NOMBRE]" = INGRESO (el usuario recibió)
           • "Ref: XXXX" = típico de SINPE, analizar dirección cuidadosamente
        
        3. **INDICADORES DE INGRESO (dinero que RECIBE el usuario)**:
           • "se acreditó", "se depositó", "recibió transferencia"
           • Usuario aparece como DESTINATARIO/RECEPTOR
           • Su nombre en "PARA:", "A:", "DESTINATARIO:", "RECEPTOR:"
           • "cobro", "ingreso", "pago recibido"
        
        4. **INDICADORES DE GASTO (dinero que ENVÍA el usuario)**:
           • "se debitó", "se descontó", "envió transferencia" 
           • Usuario aparece como EMISOR/REMITENTE
           • Su nombre en "DE:", "DESDE:", "REMITENTE:", "EMISOR:"
           • FACTURAS/RECIBOS/TICKETS = siempre GASTO
           • "pago", "compra", "gasto"
        
        5. **EJEMPLOS ESPECÍFICOS**:
           📥 INGRESO: "💸 Transferencia SINPE Móvil a [NOMBRE_USUARIO] por 10000.00 CRC"
           📤 GASTO: "💸 Transferencia SINPE Móvil de [NOMBRE_USUARIO] por 5000.00 CRC"
           📤 GASTO: "Factura Restaurant La Fortuna - Total: ₡15,000"
           📥 INGRESO: "Depósito a cuenta - Salario Enero - ₡850,000"
           📥 INGRESO: "Recibo SINPE: María Pérez te envió ₡25,000"
           📤 GASTO: "Pago realizado a SuperMercado XYZ - Total: ₡12,500"
        EVENTO: "reunión", "cita", "junta", "meeting", "evento", "conferencia", "visita", "llamada", "videollamada", "zoom", "teams"
        TAREA: "tengo que", "debo", "necesito", "hay que", "pendiente", "hacer", "completar", "terminar", "acabar", "finalizar"
        RECORDATORIO: "recordar", "no olvidar", "acordarme", "anotar", "apuntar", "nota mental", "recordatorio"
        PLAN: "planear", "planifico", "voy a", "quiero", "me gustaría", "pensar", "considerar", "idea", "proyecto"
        
        LÓGICA INTELIGENTE DE TIEMPO:
        Cuando NO se especifica hora exacta, analiza la complejidad y asigna duración:
        
        EVENTOS CORTOS (30 min - 1 hora):
        • Llamadas telefónicas
        • Citas médicas rápidas  
        • Reuniones de check-in
        • Compras rápidas
        → datetime_end: +30 min a +1 hora
        
        EVENTOS MEDIANOS (1-3 horas):
        • Reuniones de trabajo
        • Citas con clientes
        • Almuerzos de negocios
        • Consultas médicas
        • Clases/cursos
        → datetime_end: +1 a +3 horas
        
        EVENTOS LARGOS (3-8 horas):
        • Workshops/talleres
        • Conferencias
        • Viajes largos
        • Jornadas de trabajo
        • Eventos sociales grandes
        → datetime_end: +3 a +8 horas
        
        EVENTOS TODO EL DÍA:
        • Vacaciones
        • Días libres
        • Conferencias de múltiples días
        • Mudanzas
        • Eventos familiares grandes
        → Usar formato de fecha completa sin hora específica
        
        HORAS PREDETERMINADAS INTELIGENTES:
        Si solo menciona "mañana" o "hoy" sin hora:
        • Reuniones de trabajo → 09:00 o 14:00
        • Citas médicas → 10:00 o 15:00  
        • Almuerzos → 12:00-13:00
        • Llamadas → 10:00 o 16:00
        • Eventos sociales → 19:00 o 20:00
        
        ESTRUCTURA JSON REQUERIDA:
        {
            "type": "string",
            "description": "string",
            "amount": number o null,
            "datetime": "YYYY-MM-DDTHH:MM:SS-06:00",
            "datetime_end": "YYYY-MM-DDTHH:MM:SS-06:00",
            "priority": "alta|media|baja",
            "recurrence": "none|daily|weekly|monthly|yearly",
            "task_category": "Trabajo|Personal|Ocio" o null (NUNCA uses "Sin categoría"),
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
            "recurrence": "none",
            "priority": "media",
            "amount": None,
            "task_category": None,
        }
    
    async def _get_recent_financial_context(self, supabase, user_id: str, current_time: datetime) -> Dict[str, Any]:
        """Obtiene contexto financiero de los últimos 7 días"""
        try:
            seven_days_ago = current_time - timedelta(days=7)
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "gasto"
            ).gte(
                "datetime", seven_days_ago.isoformat()
            ).order("datetime", desc=True).execute()
            
            gastos = result.data
            if not gastos:
                return None
            
            total_gastos = sum(float(g.get('amount') or 0) for g in gastos)
            promedio_diario = total_gastos / 7
            
            # Categorías más frecuentes
            categorias = {}
            for gasto in gastos:
                cat = gasto.get('category', 'Sin categoría')
                categorias[cat] = categorias.get(cat, 0) + 1
            
            categorias_principales = sorted(categorias.keys(), key=lambda x: categorias[x], reverse=True)[:3]
            
            # Último gasto
            ultimo_gasto = f"₡{float(gastos[0].get('amount') or 0):,.0f} - {gastos[0].get('description', '')}" if gastos else "N/A"
            
            return {
                "total_gastos": total_gastos,
                "promedio_diario": promedio_diario,
                "categorias_principales": categorias_principales,
                "ultimo_gasto": ultimo_gasto
            }
            
        except Exception as e:
            logger.warning(f"Error obteniendo contexto financiero: {e}")
            return None
    
    async def _get_upcoming_events_context(self, supabase, user_id: str, current_time: datetime) -> List[str]:
        """Obtiene eventos próximos (próximos 3 días)"""
        try:
            three_days_ahead = current_time + timedelta(days=3)
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).in_(
                "type", ["evento", "tarea", "recordatorio"]
            ).gte(
                "datetime", current_time.isoformat()
            ).lte(
                "datetime", three_days_ahead.isoformat()
            ).order("datetime").execute()
            
            events = result.data
            if not events:
                return []
            
            formatted_events = []
            for event in events[:5]:  # Máximo 5 eventos
                event_time = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                day_name = event_time.strftime('%A')
                time_str = event_time.strftime('%H:%M')
                formatted_events.append(f"{day_name} {time_str}: {event['description']}")
            
            return formatted_events
            
        except Exception as e:
            logger.warning(f"Error obteniendo eventos próximos: {e}")
            return []
    
    async def _get_spending_patterns_context(self, supabase, user_id: str) -> Dict[str, Any]:
        """Obtiene patrones de gasto del último mes"""
        try:
            one_month_ago = datetime.now(self.tz) - timedelta(days=30)
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "gasto"
            ).gte(
                "datetime", one_month_ago.isoformat()
            ).execute()
            
            gastos = result.data
            if not gastos:
                return None
            
            # Análisis de días
            dias_gasto = {}
            horarios_gasto = {}
            categorias_gasto = {}
            
            for gasto in gastos:
                if gasto.get('datetime'):
                    dt = datetime.fromisoformat(gasto['datetime'].replace('Z', '+00:00'))
                    day_name = dt.strftime('%A')
                    hour = dt.hour
                    
                    dias_gasto[day_name] = dias_gasto.get(day_name, 0) + 1
                    
                    # Agrupar horarios
                    if 6 <= hour < 12:
                        horario = "Mañana (6-12h)"
                    elif 12 <= hour < 18:
                        horario = "Tarde (12-18h)"
                    elif 18 <= hour < 24:
                        horario = "Noche (18-24h)"
                    else:
                        horario = "Madrugada (0-6h)"
                    
                    horarios_gasto[horario] = horarios_gasto.get(horario, 0) + 1
                
                # Categorías
                cat = gasto.get('category', 'Sin categoría')
                categorias_gasto[cat] = categorias_gasto.get(cat, 0) + 1
            
            # Top 3 de cada uno
            dias_frecuentes = sorted(dias_gasto.keys(), key=lambda x: dias_gasto[x], reverse=True)[:3]
            horarios_comunes = sorted(horarios_gasto.keys(), key=lambda x: horarios_gasto[x], reverse=True)[:2]
            categorias_frecuentes = sorted(categorias_gasto.keys(), key=lambda x: categorias_gasto[x], reverse=True)[:3]
            
            # Traducir días al español
            day_translation = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            dias_frecuentes = [day_translation.get(day, day) for day in dias_frecuentes]
            
            return {
                "dias_frecuentes": dias_frecuentes,
                "horarios_comunes": horarios_comunes,
                "categorias_frecuentes": categorias_frecuentes
            }
            
        except Exception as e:
            logger.warning(f"Error obteniendo patrones de gasto: {e}")
            return None

# Singleton
gemini_service = GeminiService()