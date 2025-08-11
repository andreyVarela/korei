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
    async def get_or_create_user(self, phone: str, name: str = None) -> Dict[str, Any]:
        """Obtiene o crea usuario"""
        try:
            # Buscar usuario existente
            result = self._get_client().table("users").select("*").eq(
                "whatsapp_number", phone
            ).execute()
            
            if result.data:
                return result.data[0]
            
            # Crear nuevo usuario
            new_user = {
                "whatsapp_number": phone,
                "name": name or f"Usuario {phone[-4:]}",
                "created_at": datetime.now(self.tz).isoformat()
            }
            
            result = self._get_client().table("users").insert(new_user).execute()
            logger.info(f"Nuevo usuario creado: {phone}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error en get_or_create_user: {e}")
            raise
    
    # Entry methods
    async def create_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una entrada"""
        try:
            # Asegurar timestamps
            if 'created_at' not in entry_data:
                entry_data['created_at'] = datetime.now(self.tz).isoformat()
                
            result = self._get_client().table("entries").insert(entry_data).execute()
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error creando entrada: {e}")
            raise
    
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
                "name": user.get("name", "Usuario"),
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