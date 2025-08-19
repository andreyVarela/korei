"""
Cliente Supabase mejorado con manejo de errores
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pytz
from loguru import logger
from app.config import settings

class SupabaseService:
    def __init__(self):
        self.client: Optional[Client] = None
        self.tz = pytz.timezone(settings.timezone)
        
    def _get_client(self) -> Client:
        """Lazy initialization del cliente Supabase"""
        if self.client is None:
            try:
                self.client = create_client(
                    settings.supabase_url,
                    settings.supabase_service_key
                )
                logger.info("Cliente Supabase inicializado")
            except Exception as e:
                logger.warning(f"No se pudo conectar a Supabase: {e}")
                raise
        return self.client
        
    # Usuario methods
    async def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Busca usuario por teléfono - compatible con ambos formatos"""
        try:
            # Limpiar número
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Intentar buscar con número limpio primero (nuevo formato)
            result = self._get_client().table("users").select("*").eq(
                "whatsapp_number", clean_phone
            ).execute()
            
            if result.data:
                return result.data[0]
            
            # Si no encuentra, intentar con formato @c.us (formato legacy)
            legacy_phone = f"{clean_phone}@c.us"
            result = self._get_client().table("users").select("*").eq(
                "whatsapp_number", legacy_phone
            ).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error buscando usuario: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Busca usuario por ID"""
        try:
            result = self._get_client().table("users").select("*").eq(
                "id", user_id
            ).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error buscando usuario por ID: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea nuevo usuario"""
        try:
            # Usar las columnas correctas del esquema
            clean_data = {
                "whatsapp_number": user_data.get("whatsapp_number"),
                "name": user_data.get("name", user_data.get("display_name", "Usuario")),
                "created_at": datetime.now(self.tz).isoformat()
            }
            
            result = self._get_client().table("users").insert(clean_data).execute()
            logger.info(f"Nuevo usuario creado: {clean_data.get('whatsapp_number')}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza usuario"""
        try:
            result = self._get_client().table("users").update(update_data).eq(
                "id", user_id
            ).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}")
            raise
    
    async def get_or_create_user(self, phone: str, name: str = None) -> Dict[str, Any]:
        """Obtiene o crea usuario - compatible con formato WhatsApp Cloud API"""
        try:
            # Limpiar número (viene limpio desde WhatsApp Cloud API)
            clean_phone = ''.join(filter(str.isdigit, phone))
            
            # Buscar usuario existente (busca en ambos formatos)
            user = await self.get_user_by_phone(clean_phone)
            
            if user:
                # Convertir a formato esperado por message_handler
                return {
                    "id": user["id"],
                    "whatsapp_number": clean_phone,  # Siempre limpio para WhatsApp Cloud API
                    "display_name": user.get("name", "Usuario"),
                    "is_active": True
                }
            
            # Crear nuevo usuario (formato limpio para WhatsApp Cloud API)
            new_user = {
                "whatsapp_number": clean_phone,  # Sin @c.us para nuevos usuarios
                "name": name or f"Usuario {clean_phone[-4:]}",
            }
            
            created_user = await self.create_user(new_user)
            
            # Convertir a formato esperado
            return {
                "id": created_user["id"],
                "whatsapp_number": clean_phone,  # Limpio para compatibilidad
                "display_name": created_user.get("name", "Usuario"),
                "is_active": True
            }
            
        except Exception as e:
            logger.error(f"Error en get_or_create_user: {e}")
            raise
    
    # Entry methods
    def _validate_task_category(self, category: str) -> str:
        """Valida y mapea categorías de tareas a valores válidos del enum"""
        if not category:
            return None
            
        # Categorías válidas en la base de datos
        valid_categories = ["Trabajo", "Personal", "Ocio"]
        
        # Si ya es válida, devolverla
        if category in valid_categories:
            return category
            
        # Mapeo de categorías comunes a válidas
        category_mapping = {
            "Transporte": "Personal",
            "Alimentación": "Personal", 
            "Comida": "Personal",
            "Entretenimiento": "Ocio",
            "Diversión": "Ocio",
            "Deporte": "Personal",
            "Ejercicio": "Personal",
            "Salud": "Personal",
            "Médico": "Personal",
            "Educación": "Personal",
            "Estudio": "Personal",
            "Familia": "Personal",
            "Compras": "Personal",
            "Casa": "Personal",
            "Hogar": "Personal",
            "Negocios": "Trabajo",
            "Empresa": "Trabajo",
            "Oficina": "Trabajo",
            "Proyecto": "Trabajo",
            "Reunión": "Trabajo",
            "Cine": "Ocio",
            "Música": "Ocio",
            "Viaje": "Personal",
            "Vacaciones": "Ocio"
        }
        
        # Intentar mapear
        mapped = category_mapping.get(category)
        if mapped:
            logger.info(f"CATEGORY_MAPPING: '{category}' -> '{mapped}'")
            return mapped
            
        # Si no se puede mapear, usar "Personal" como default
        logger.warning(f"CATEGORY_UNKNOWN: '{category}' -> 'Personal' (default)")
        return "Personal"

    async def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una entrada"""
        try:
            # Validar y mapear categoría de tarea si existe
            if 'task_category' in entry_data and entry_data['task_category']:
                entry_data['task_category'] = self._validate_task_category(entry_data['task_category'])
            
            # Asegurar timestamps
            if 'created_at' not in entry_data:
                entry_data['created_at'] = datetime.now(self.tz).isoformat()
                
            result = self._get_client().table("entries").insert(entry_data).execute()
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creando entrada: {e}")
            raise
    
    async def update_entry(self, entry_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una entrada"""
        try:
            # Asegurar timestamp de actualización
            update_data['updated_at'] = datetime.now(self.tz).isoformat()
                
            result = self._get_client().table("entries").update(update_data).eq(
                "id", entry_id
            ).execute()
            
            if result.data:
                return result.data[0]
            else:
                raise ValueError(f"No se encontró entrada con ID: {entry_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando entrada {entry_id}: {e}")
            raise
    
    async def update_entry_status(self, entry_id: str, new_status: str) -> Dict[str, Any]:
        """Actualiza específicamente el estado de una entrada"""
        try:
            logger.info(f"🔄 Iniciando actualización de estado: entry_id={entry_id}, new_status={new_status}")
            
            now = datetime.now(self.tz)
            
            # Crear datos de actualización básicos
            update_data = {
                'status': new_status
            }
            
            # Si se marca como completada, agregar timestamp de completado
            if new_status == 'completed':
                update_data['completed_at'] = now.isoformat()
                logger.info(f"📅 Agregando completed_at: {update_data['completed_at']}")
            
            # Intentar agregar updated_at solo si existe la columna
            try:
                # Test si updated_at existe haciendo una query simple
                test_result = self._get_client().table("entries").select("updated_at").limit(1).execute()
                update_data['updated_at'] = now.isoformat()
                logger.info(f"📅 Agregando updated_at: {update_data['updated_at']}")
            except Exception as col_error:
                logger.warning(f"⚠️ Columna updated_at no existe, continuando sin ella: {col_error}")
            
            logger.info(f"📝 Datos a actualizar: {update_data}")
            
            result = self._get_client().table("entries").update(update_data).eq(
                "id", entry_id
            ).execute()
            
            logger.info(f"📊 Resultado de Supabase: {result}")
            
            if result.data:
                logger.info(f"✅ Entrada {entry_id} marcada como {new_status} exitosamente")
                return result.data[0]
            else:
                logger.error(f"❌ No se encontró entrada con ID: {entry_id} o no se actualizó")
                raise ValueError(f"No se encontró entrada con ID: {entry_id}")
            
        except Exception as e:
            logger.error(f"💥 Error actualizando status de entrada {entry_id}: {e}")
            logger.error(f"💥 Tipo de error: {type(e)}")
            raise
    
    async def get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene una entrada por ID"""
        try:
            result = self._get_client().table("entries").select("*").eq(
                "id", entry_id
            ).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error obteniendo entrada por ID: {e}")
            return None
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas del usuario"""
        try:
            # Stats del mes actual
            now = datetime.now(self.tz)
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            
            # Obtener todas las entries del mes
            entries = self._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", month_start.isoformat()
            ).execute()
            
            # Calcular estadísticas
            stats = {
                "total_entries": len(entries.data),
                "by_type": {},
                "gastos": 0,
                "ingresos": 0,
                "balance": 0,
                "pending_tasks": 0
            }
            
            for entry in entries.data:
                # Contar por tipo
                entry_type = entry['type']
                stats['by_type'][entry_type] = stats['by_type'].get(entry_type, 0) + 1
                
                # Sumar montos
                if entry_type == 'gasto' and entry.get('amount'):
                    stats['gastos'] += float(entry['amount'])
                elif entry_type == 'ingreso' and entry.get('amount'):
                    stats['ingresos'] += float(entry['amount'])
                
                # Contar tareas pendientes
                if entry_type == 'tarea' and entry['status'] == 'pending':
                    stats['pending_tasks'] += 1
            
            stats['balance'] = stats['ingresos'] - stats['gastos']
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {}
    
    # Media storage
    async def upload_media(self, file_data: bytes, filename: str, 
                          content_type: str) -> str:
        """Sube archivo a Supabase Storage"""
        try:
            path = f"{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            
            self._get_client().storage.from_("korei-media").upload(
                path,
                file_data,
                {"content-type": content_type}
            )
            
            # Obtener URL pública
            url = self._get_client().storage.from_("korei-media").get_public_url(path)
            return url
            
        except Exception as e:
            logger.error(f"Error subiendo archivo: {e}")
            raise
    
    # Búsquedas avanzadas
    async def search_entries(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Busca entries por texto"""
        try:
            result = self._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).ilike(
                "description", f"%{query}%"
            ).order(
                "datetime", desc=True
            ).limit(10).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error buscando entries: {e}")
            return []
    
    # Recordatorios
    async def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Obtiene recordatorios pendientes para enviar"""
        try:
            now = datetime.now(self.tz)
            
            result = self._get_client().table("entries").select(
                "*, users!inner(whatsapp_number, name)"
            ).lte(
                "datetime_remember", now.isoformat()
            ).eq(
                "status", "pending"
            ).in_(
                "type", ["recordatorio", "tarea", "evento"]
            ).execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios: {e}")
            return []
    
    # User Profile methods
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Obtiene perfil completo del usuario"""
        try:
            result = self._get_client().table("user_profiles").select("*").eq(
                "user_id", user_id
            ).execute()
            
            if result.data:
                return result.data[0]
            
            # Si no tiene perfil, crear uno básico
            return {
                "user_id": user_id,
                "occupation": None,
                "hobbies": [],
                "context_summary": None,
                "preferences": {}
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo perfil: {e}")
            return {}
    
    async def create_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea o actualiza perfil de usuario"""
        try:
            # Verificar si ya existe
            existing = self._get_client().table("user_profiles").select("id").eq(
                "user_id", user_id
            ).execute()
            
            if existing.data:
                # Actualizar existente
                result = self._get_client().table("user_profiles").update(
                    profile_data
                ).eq("user_id", user_id).execute()
            else:
                # Crear nuevo
                profile_data["user_id"] = user_id
                result = self._get_client().table("user_profiles").insert(
                    profile_data
                ).execute()
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error creando/actualizando perfil: {e}")
            raise
    
    async def update_user_context(self, user_id: str, context_summary: str) -> None:
        """Actualiza el resumen de contexto del usuario"""
        try:
            self._get_client().table("user_profiles").update({
                "context_summary": context_summary
            }).eq("user_id", user_id).execute()
            
            logger.info(f"Contexto actualizado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error actualizando contexto: {e}")
    
    async def get_spending_patterns(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Obtiene patrones de gasto de los últimos N días"""
        try:
            cutoff_date = (datetime.now(self.tz) - timedelta(days=days))
            
            result = self._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "gasto"
            ).gte(
                "datetime", cutoff_date.isoformat()
            ).order("datetime", desc=True).execute()
            
            expenses = result.data
            
            # Análisis de patrones
            patterns = {
                "total_amount": sum(float(e.get('amount', 0)) for e in expenses),
                "average_per_day": 0,
                "by_category": {},
                "by_day_of_week": {},
                "by_hour": {},
                "common_descriptions": {},
                "largest_expenses": []
            }
            
            if expenses:
                patterns["average_per_day"] = patterns["total_amount"] / days
                
                # Análisis por categoría
                for exp in expenses:
                    cat = exp.get('category', 'Sin categoría')
                    patterns["by_category"][cat] = patterns["by_category"].get(cat, 0) + float(exp.get('amount', 0))
                
                # Análisis temporal
                for exp in expenses:
                    if exp.get('datetime'):
                        dt = datetime.fromisoformat(exp['datetime'].replace('Z', '+00:00'))
                        day_name = dt.strftime('%A')
                        hour = dt.hour
                        
                        patterns["by_day_of_week"][day_name] = patterns["by_day_of_week"].get(day_name, 0) + 1
                        patterns["by_hour"][hour] = patterns["by_hour"].get(hour, 0) + 1
                
                # Descripciones comunes
                for exp in expenses:
                    desc = exp.get('description', '').lower()
                    patterns["common_descriptions"][desc] = patterns["common_descriptions"].get(desc, 0) + 1
                
                # Gastos más grandes
                patterns["largest_expenses"] = sorted(expenses, key=lambda x: float(x.get('amount', 0)), reverse=True)[:10]
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error obteniendo patrones de gasto: {e}")
            return {}
    
    async def get_financial_context_summary(self, user_id: str) -> Dict[str, Any]:
        """Genera un resumen de contexto financiero para IA"""
        try:
            # Obtener datos de múltiples períodos
            now = datetime.now(self.tz)
            
            # Último mes
            last_month = now - timedelta(days=30)
            result_month = self._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", last_month.isoformat()
            ).execute()
            
            # Últimos 3 meses para tendencias
            last_3_months = now - timedelta(days=90)
            result_3_months = self._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", last_3_months.isoformat()
            ).execute()
            
            entries_month = result_month.data
            entries_3_months = result_3_months.data
            
            context = {
                "monthly_summary": {
                    "total_entries": len(entries_month),
                    "total_gastos": sum(float(e.get('amount', 0)) for e in entries_month if e['type'] == 'gasto'),
                    "total_ingresos": sum(float(e.get('amount', 0)) for e in entries_month if e['type'] == 'ingreso'),
                    "avg_expense": 0,
                    "most_frequent_categories": {}
                },
                "spending_trends": {
                    "is_increasing": False,
                    "trend_percentage": 0,
                    "seasonal_patterns": {}
                },
                "behavioral_insights": {
                    "preferred_spending_times": {},
                    "common_expense_types": {},
                    "financial_discipline_score": 0  # 0-10 basado en patrones
                }
            }
            
            gastos_month = [e for e in entries_month if e['type'] == 'gasto']
            gastos_3_months = [e for e in entries_3_months if e['type'] == 'gasto']
            
            if gastos_month:
                context["monthly_summary"]["avg_expense"] = context["monthly_summary"]["total_gastos"] / len(gastos_month)
                
                # Categorías más frecuentes
                cat_counts = {}
                for gasto in gastos_month:
                    cat = gasto.get('category', 'Sin categoría')
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
                
                context["monthly_summary"]["most_frequent_categories"] = dict(
                    sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                )
            
            # Análisis de tendencias
            if len(gastos_3_months) >= 30:  # Suficientes datos
                # Comparar primer mes vs último mes de los 3 meses
                first_month_expenses = [e for e in gastos_3_months if 
                                      datetime.fromisoformat(e['datetime'].replace('Z', '+00:00')) < 
                                      (last_3_months + timedelta(days=30))]
                last_month_expenses = gastos_month
                
                first_total = sum(float(e.get('amount', 0)) for e in first_month_expenses)
                last_total = sum(float(e.get('amount', 0)) for e in last_month_expenses)
                
                if first_total > 0:
                    trend_pct = ((last_total - first_total) / first_total) * 100
                    context["spending_trends"]["trend_percentage"] = trend_pct
                    context["spending_trends"]["is_increasing"] = trend_pct > 5  # 5% threshold
            
            return context
            
        except Exception as e:
            logger.error(f"Error generando contexto financiero: {e}")
            return {}
    
    async def store_ai_insight(self, user_id: str, insight_type: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """Almacena insights generados por IA para referencia futura"""
        try:
            insight_data = {
                "user_id": user_id,
                "insight_type": insight_type,  # 'financial_tip', 'spending_pattern', 'recommendation'
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.now(self.tz).isoformat(),
                "relevance_score": 1.0  # Para futuro ranking
            }
            
            # Crear tabla si no existe (esto sería mejor en migración)
            self._get_client().table("ai_insights").insert(insight_data).execute()
            
        except Exception as e:
            logger.warning(f"Error almacenando insight de IA: {e}")  # No critical
    
    async def get_recent_ai_insights(self, user_id: str, insight_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene insights recientes de IA para contexto"""
        try:
            query = self._get_client().table("ai_insights").select("*").eq("user_id", user_id)
            
            if insight_type:
                query = query.eq("insight_type", insight_type)
            
            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data
            
        except Exception as e:
            logger.warning(f"Error obteniendo insights de IA: {e}")
            return []
    
    async def get_user_with_context(self, phone: str) -> Dict[str, Any]:
        """Obtiene usuario con toda su información de contexto"""
        try:
            # Obtener o crear usuario
            user = await self.get_or_create_user(phone)
            
            # Obtener perfil
            profile = await self.get_user_profile(user["id"])
            
            # Combinar información
            return {
                "id": user["id"],
                "phone": phone,
                "whatsapp_number": phone,  # Para compatibilidad con message_handler
                "name": user.get("display_name", user.get("name", "Usuario")),
                "profile": {
                    "occupation": profile.get("occupation"),
                    "hobbies": profile.get("hobbies", []),
                    "context_summary": profile.get("context_summary"),
                    "preferences": profile.get("preferences", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo contexto completo: {e}")
            return {}

# Instancia singleton
supabase = SupabaseService()