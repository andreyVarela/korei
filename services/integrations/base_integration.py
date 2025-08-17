"""
Clase base para todas las integraciones externas
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class BaseIntegration(ABC):
    """Clase base para integraciones con servicios externos"""
    
    def __init__(self, user_id: str, credentials: Dict[str, Any]):
        self.user_id = user_id
        self.credentials = credentials
        self.is_connected = False
        self.last_sync = None
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """Autentica la conexión con el servicio"""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Prueba que la conexión funcione"""
        pass
    
    @abstractmethod
    async def sync_to_external(self, data: Dict[str, Any]) -> bool:
        """Sincroniza datos desde Korei al servicio externo"""
        pass
    
    @abstractmethod
    async def sync_from_external(self) -> List[Dict[str, Any]]:
        """Importa datos del servicio externo a Korei"""
        pass
    
    async def refresh_credentials(self) -> bool:
        """Refresca credenciales si es necesario (OAuth)"""
        return True
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Obtiene estado de la integración"""
        return {
            "service": self.__class__.__name__,
            "user_id": self.user_id,
            "is_connected": self.is_connected,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None
        }


class CalendarIntegration(BaseIntegration):
    """Clase base para integraciones de calendario"""
    
    @abstractmethod
    async def create_event(self, event_data: Dict[str, Any]) -> str:
        """Crea un evento en el calendario externo"""
        pass
    
    @abstractmethod
    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """Actualiza un evento existente"""
        pass
    
    @abstractmethod
    async def delete_event(self, event_id: str) -> bool:
        """Elimina un evento"""
        pass
    
    @abstractmethod
    async def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Obtiene eventos próximos"""
        pass


class TaskIntegration(BaseIntegration):
    """Clase base para integraciones de tareas"""
    
    @abstractmethod
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Crea una tarea en el servicio externo"""
        pass
    
    @abstractmethod
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Actualiza una tarea existente"""
        pass
    
    @abstractmethod
    async def complete_task(self, task_id: str) -> bool:
        """Marca una tarea como completada"""
        pass
    
    @abstractmethod
    async def get_tasks(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene tareas del servicio"""
        pass