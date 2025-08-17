"""
Gestor central de integraciones externas
"""
import asyncio
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from loguru import logger

from core.supabase import supabase
from core.encryption import encrypt_credentials, decrypt_credentials
from .base_integration import BaseIntegration, CalendarIntegration, TaskIntegration
from .google_calendar import GoogleCalendarIntegration
from .todoist_integration import TodoistIntegration


class IntegrationManager:
    """Gestor central para todas las integraciones externas"""
    
    # Registro de integraciones disponibles
    AVAILABLE_INTEGRATIONS = {
        'google_calendar': GoogleCalendarIntegration,
        'todoist': TodoistIntegration,
    }
    
    def __init__(self):
        self.active_integrations: Dict[str, Dict[str, BaseIntegration]] = {}
    
    async def register_user_integration(
        self, 
        user_id: str, 
        service: str, 
        credentials: Dict[str, Any],
        config: Dict[str, Any] = None
    ) -> bool:
        """Registra una nueva integración para un usuario"""
        try:
            logger.info(f"STARTING register_user_integration - User: {user_id}, Service: {service}")
            
            if service not in self.AVAILABLE_INTEGRATIONS:
                logger.error(f"Integration service '{service}' not available")
                return False
            
            integration_class = self.AVAILABLE_INTEGRATIONS[service]
            logger.info(f"CREATING integration instance of {integration_class}")
            integration = integration_class(user_id, credentials)
            logger.info(f"INTEGRATION CREATED, calling authenticate...")
            
            # Intentar autenticar
            auth_result = await integration.authenticate()
            logger.info(f"AUTHENTICATION RESULT: {auth_result}")
            
            if auth_result:
                logger.info(f"AUTHENTICATION SUCCESS, encrypting credentials...")
                # Encriptar credenciales antes de guardar
                encrypted_credentials = encrypt_credentials(credentials)
                logger.info(f"CREDENTIALS ENCRYPTED")
                
                # Guardar en base de datos
                integration_data = {
                    'user_id': user_id,
                    'service': service,
                    'credentials': encrypted_credentials,  # Ahora encriptadas con AES-256
                    'config': config or {},
                    'status': 'active',
                    'created_at': datetime.utcnow().isoformat(),
                    'last_sync': None
                }
                
                logger.info(f"STORING integration in database...")
                await self._store_integration(integration_data)
                logger.info(f"INTEGRATION STORED IN DB")
                
                # Mantener en memoria
                if user_id not in self.active_integrations:
                    self.active_integrations[user_id] = {}
                self.active_integrations[user_id][service] = integration
                
                logger.info(f"FINAL SUCCESS - Registered {service} integration for user {user_id}")
                return True
            else:
                logger.error(f"AUTHENTICATION FAILED for {service} for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"EXCEPTION in register_user_integration {service} for user {user_id}: {e}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return False
    
    async def get_user_integration(self, user_id: str, service: str) -> Optional[BaseIntegration]:
        """Obtiene una integración específica del usuario"""
        try:
            # Verificar si está en memoria
            if (user_id in self.active_integrations and 
                service in self.active_integrations[user_id]):
                return self.active_integrations[user_id][service]
            
            # Cargar desde base de datos
            integration_data = await self._load_integration(user_id, service)
            if integration_data:
                integration_class = self.AVAILABLE_INTEGRATIONS.get(service)
                if integration_class:
                    # Desencriptar credenciales antes de usar
                    try:
                        decrypted_credentials = decrypt_credentials(integration_data['credentials'])
                    except Exception as e:
                        logger.error(f"Error desencriptando credenciales para {service}: {e}")
                        return None
                    
                    integration = integration_class(
                        user_id, 
                        decrypted_credentials
                    )
                    
                    if await integration.authenticate():
                        # Guardar en memoria
                        if user_id not in self.active_integrations:
                            self.active_integrations[user_id] = {}
                        self.active_integrations[user_id][service] = integration
                        return integration
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting integration {service} for user {user_id}: {e}")
            return None
    
    async def get_user_integrations(self, user_id: str) -> List[BaseIntegration]:
        """Obtiene todas las integraciones activas del usuario"""
        integrations = []
        try:
            integration_records = await self._load_user_integrations(user_id)
            
            for record in integration_records:
                service = record['service']
                integration = await self.get_user_integration(user_id, service)
                if integration:
                    integrations.append(integration)
            
            return integrations
            
        except Exception as e:
            logger.error(f"Error getting user integrations for {user_id}: {e}")
            return integrations
    
    async def sync_user_data(self, user_id: str, direction: str = 'both') -> Dict[str, Any]:
        """Sincroniza datos del usuario con todas sus integraciones"""
        results = {
            'success': [],
            'failed': [],
            'imported_items': [],
            'exported_items': []
        }
        
        try:
            integrations = await self.get_user_integrations(user_id)
            
            for integration in integrations:
                service_name = integration.__class__.__name__
                
                try:
                    # Exportar a servicio externo
                    if direction in ['export', 'both']:
                        recent_entries = await self._get_user_recent_entries(user_id)
                        for entry in recent_entries:
                            if await self._should_sync_entry(entry, integration):
                                success = await integration.sync_to_external(entry)
                                if success:
                                    results['exported_items'].append({
                                        'service': service_name,
                                        'entry': entry['description']
                                    })
                    
                    # Importar desde servicio externo
                    if direction in ['import', 'both']:
                        imported = await integration.sync_from_external()
                        for item in imported:
                            # Almacenar en Korei
                            await self._store_imported_entry(user_id, item)
                            results['imported_items'].append({
                                'service': service_name,
                                'item': item['description']
                            })
                    
                    results['success'].append(service_name)
                    
                except Exception as e:
                    logger.error(f"Error syncing {service_name} for user {user_id}: {e}")
                    results['failed'].append({
                        'service': service_name,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in sync_user_data for user {user_id}: {e}")
            return results
    
    async def remove_user_integration(self, user_id: str, service: str) -> bool:
        """Elimina una integración del usuario"""
        try:
            # Remover de memoria
            if (user_id in self.active_integrations and 
                service in self.active_integrations[user_id]):
                integration = self.active_integrations[user_id][service]
                if hasattr(integration, 'close'):
                    await integration.close()
                del self.active_integrations[user_id][service]
            
            # Remover de base de datos
            await self._delete_integration(user_id, service)
            
            logger.info(f"Removed {service} integration for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing integration {service} for user {user_id}: {e}")
            return False
    
    async def _store_integration(self, integration_data: Dict[str, Any]) -> None:
        """Almacena integración en base de datos"""
        try:
            # Nota: Las credenciales deberían estar encriptadas antes de guardar
            supabase._get_client().table("user_integrations").insert(integration_data).execute()
        except Exception as e:
            logger.error(f"Error storing integration: {e}")
            raise
    
    async def _load_integration(self, user_id: str, service: str) -> Optional[Dict[str, Any]]:
        """Carga integración desde base de datos"""
        try:
            result = supabase._get_client().table("user_integrations").select("*").eq(
                "user_id", user_id
            ).eq(
                "service", service
            ).eq(
                "status", "active"
            ).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error loading integration: {e}")
            return None
    
    async def _load_user_integrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Carga todas las integraciones del usuario"""
        try:
            result = supabase._get_client().table("user_integrations").select("*").eq(
                "user_id", user_id
            ).eq(
                "status", "active"
            ).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error loading user integrations: {e}")
            return []
    
    async def _delete_integration(self, user_id: str, service: str) -> None:
        """Elimina integración de base de datos"""
        try:
            supabase._get_client().table("user_integrations").update({
                "status": "deleted"
            }).eq(
                "user_id", user_id
            ).eq(
                "service", service
            ).execute()
        except Exception as e:
            logger.error(f"Error deleting integration: {e}")
            raise
    
    async def _get_user_recent_entries(self, user_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Obtiene entradas recientes del usuario para sincronizar"""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "created_at", cutoff.isoformat()
            ).is_(
                "external_id", "null"  # Solo entradas que no han sido sincronizadas
            ).execute()
            
            return result.data
        except Exception as e:
            logger.error(f"Error getting recent entries: {e}")
            return []
    
    async def _should_sync_entry(self, entry: Dict[str, Any], integration: BaseIntegration) -> bool:
        """Determina si una entrada debe sincronizarse con la integración"""
        entry_type = entry.get('type')
        
        # Eventos -> Calendarios
        if isinstance(integration, CalendarIntegration):
            return entry_type in ['evento', 'recordatorio']
        
        # Tareas -> Apps de tareas
        elif isinstance(integration, TaskIntegration):
            return entry_type in ['tarea']
        
        return False
    
    async def _store_imported_entry(self, user_id: str, item: Dict[str, Any]) -> None:
        """Almacena entrada importada en Korei"""
        try:
            # Verificar que no existe ya
            if item.get('external_id'):
                existing = supabase._get_client().table("entries").select("id").eq(
                    "external_id", item['external_id']
                ).eq(
                    "user_id", user_id
                ).execute()
                
                if existing.data:
                    return  # Ya existe
            
            # Preparar datos
            entry_data = {
                'user_id': user_id,
                'type': item['type'],
                'description': item['description'],
                'datetime': item.get('datetime'),
                'priority': item.get('priority'),
                'status': item.get('status', 'pending'),
                'external_id': item.get('external_id'),
                'external_service': item.get('external_service'),
                'created_at': datetime.utcnow().isoformat()
            }
            
            supabase._get_client().table("entries").insert(entry_data).execute()
            
        except Exception as e:
            logger.error(f"Error storing imported entry: {e}")


# Instancia singleton
integration_manager = IntegrationManager()