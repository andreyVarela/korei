"""
Integración con Google Calendar
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pytz
from loguru import logger

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    Flow = None
    Request = None
    Credentials = None
    build = None
    logger.warning("Google Calendar dependencies not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

from .base_integration import CalendarIntegration
from app.config import settings


class GoogleCalendarIntegration(CalendarIntegration):
    """Integración con Google Calendar"""
    
    # Scopes necesarios para Google Calendar
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, user_id: str, credentials: Dict[str, Any]):
        super().__init__(user_id, credentials)
        self.service = None
        self.calendar_id = 'primary'  # Calendario principal por defecto
        
        if not GOOGLE_AVAILABLE:
            logger.error("Google Calendar integration not available - missing dependencies")
    
    async def authenticate(self) -> bool:
        """Autentica usando OAuth2 con Google"""
        try:
            logger.info(f"GOOGLE AUTH START - User: {self.user_id}")
            logger.info(f"GOOGLE AVAILABLE: {GOOGLE_AVAILABLE}")
            logger.info(f"CREDENTIALS KEYS: {list(self.credentials.keys())}")
            
            if not GOOGLE_AVAILABLE:
                logger.error(f"GOOGLE NOT AVAILABLE")
                return False
                
            # Crear credenciales desde los datos almacenados
            creds = None
            if self.credentials.get('token'):  # Buscar 'token' que es el access_token
                logger.info(f"TOKEN FOUND, creating credentials...")
                try:
                    creds = Credentials.from_authorized_user_info(
                        self.credentials, self.SCOPES
                    )
                    logger.info(f"CREDENTIALS CREATED: valid={creds.valid if creds else None}")
                except Exception as cred_error:
                    logger.error(f"ERROR CREATING CREDENTIALS: {cred_error}")
                    return False
            else:
                logger.error(f"NO TOKEN in credentials, available keys: {list(self.credentials.keys())}")
                return False
            
            # Si no hay credenciales válidas, necesitamos OAuth flow
            if not creds or not creds.valid:
                logger.info(f"CREDENTIALS NOT VALID - expired: {creds.expired if creds else None}")
                if creds and creds.expired and creds.refresh_token:
                    logger.info(f"ATTEMPTING TOKEN REFRESH...")
                    creds.refresh(Request())
                    logger.info(f"TOKEN REFRESHED")
                else:
                    # Esto requeriría un flow web completo
                    logger.warning(f"User {self.user_id} needs to complete OAuth flow")
                    return False
            
            # Crear servicio de Calendar API
            logger.info(f"BUILDING CALENDAR SERVICE...")
            self.service = build('calendar', 'v3', credentials=creds)
            self.is_connected = True
            logger.info(f"CALENDAR SERVICE BUILT SUCCESSFULLY")
            
            # Actualizar credenciales si se refrescaron
            if creds.to_json() != self.credentials.get('token'):
                self.credentials['token'] = creds.to_json()
            
            return True
            
        except Exception as e:
            logger.error(f"EXCEPTION in Google Calendar authenticate for user {self.user_id}: {e}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return False
    
    async def test_connection(self) -> bool:
        """Prueba la conexión obteniendo info del calendario"""
        try:
            if not self.service:
                return False
                
            # Intentar obtener información del calendario principal
            calendar = self.service.calendars().get(calendarId=self.calendar_id).execute()
            logger.info(f"Connected to Google Calendar: {calendar.get('summary')}")
            return True
            
        except Exception as e:
            logger.error(f"Google Calendar connection test failed: {e}")
            return False
    
    async def create_event(self, event_data: Dict[str, Any]) -> str:
        """Crea un evento en Google Calendar"""
        try:
            if not self.service:
                await self.authenticate()
            
            # Convertir datos de Korei a formato Google Calendar
            google_event = self._korei_to_google_event(event_data)
            
            # Crear evento
            event = self.service.events().insert(
                calendarId=self.calendar_id, 
                body=google_event
            ).execute()
            
            event_id = event.get('id')
            logger.info(f"Created Google Calendar event: {event_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {e}")
            raise
    
    async def update_event(self, event_id: str, event_data: Dict[str, Any]) -> bool:
        """Actualiza un evento existente"""
        try:
            if not self.service:
                await self.authenticate()
            
            google_event = self._korei_to_google_event(event_data)
            
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=google_event
            ).execute()
            
            logger.info(f"Updated Google Calendar event: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Google Calendar event {event_id}: {e}")
            return False
    
    async def delete_event(self, event_id: str) -> bool:
        """Elimina un evento"""
        try:
            if not self.service:
                await self.authenticate()
            
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted Google Calendar event: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Google Calendar event {event_id}: {e}")
            return False
    
    async def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Obtiene eventos próximos"""
        try:
            if not self.service:
                await self.authenticate()
            
            # Configurar rango de fechas
            now = datetime.utcnow()
            end_time = now + timedelta(days=days_ahead)
            
            # Obtener eventos
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convertir a formato Korei
            korei_events = []
            for event in events:
                korei_event = self._google_to_korei_event(event)
                korei_events.append(korei_event)
            
            return korei_events
            
        except Exception as e:
            logger.error(f"Error getting Google Calendar events: {e}")
            return []
    
    async def sync_to_external(self, data: Dict[str, Any]) -> str:
        """Sincroniza evento de Korei a Google Calendar"""
        try:
            if data.get('type') == 'evento':
                event_id = await self.create_event(data)
                if event_id:
                    logger.info(f"SYNC SUCCESS: Created Google Calendar event {event_id}")
                    return event_id
                else:
                    logger.error(f"SYNC FAILED: No event ID returned")
                    return None
            else:
                logger.info(f"SYNC SKIPPED: Not an event type ({data.get('type')})")
                return None
            
        except Exception as e:
            logger.error(f"Error syncing to Google Calendar: {e}")
            return None
    
    async def sync_from_external(self) -> List[Dict[str, Any]]:
        """Importa eventos desde Google Calendar"""
        try:
            events = await self.get_upcoming_events(30)  # Próximos 30 días
            self.last_sync = datetime.utcnow()
            return events
            
        except Exception as e:
            logger.error(f"Error syncing from Google Calendar: {e}")
            return []
    
    def _korei_to_google_event(self, korei_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte evento de Korei a formato Google Calendar"""
        event = {
            'summary': korei_data.get('description', 'Evento desde Korei'),
            'description': f"Creado desde Korei\n\n{korei_data.get('description', '')}",
            'start': {},
            'end': {},
        }
        
        # Configurar fecha y hora
        event_datetime = korei_data.get('datetime')
        if event_datetime:
            if isinstance(event_datetime, str):
                event_datetime = datetime.fromisoformat(event_datetime.replace('Z', '+00:00'))
            
            # Evento con hora específica
            event['start']['dateTime'] = event_datetime.isoformat()
            event['end']['dateTime'] = (event_datetime + timedelta(hours=1)).isoformat()
            event['start']['timeZone'] = settings.timezone
            event['end']['timeZone'] = settings.timezone
        else:
            # Evento de todo el día
            today = datetime.now().date()
            event['start']['date'] = today.isoformat()
            event['end']['date'] = (today + timedelta(days=1)).isoformat()
        
        # Recordatorios
        if korei_data.get('priority') == 'alta':
            event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 60},
                    {'method': 'popup', 'minutes': 15},
                ],
            }
        
        return event
    
    def _google_to_korei_event(self, google_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte evento de Google Calendar a formato Korei"""
        korei_event = {
            'type': 'evento',
            'description': google_event.get('summary', 'Evento importado'),
            'external_id': google_event.get('id'),
            'external_service': 'google_calendar',
            'status': 'pending'
        }
        
        # Extraer fecha/hora
        start = google_event.get('start', {})
        if start.get('dateTime'):
            # Evento con hora
            korei_event['datetime'] = start['dateTime']
        elif start.get('date'):
            # Evento de todo el día
            korei_event['datetime'] = f"{start['date']}T09:00:00"
        
        # Descripción adicional si existe
        if google_event.get('description'):
            korei_event['description'] += f" - {google_event['description'][:100]}"
        
        return korei_event


# Función helper para crear flujo OAuth
def create_oauth_flow(redirect_uri: str) -> Flow:
    """Crea un flujo OAuth para Google Calendar"""
    if not GOOGLE_AVAILABLE:
        raise ImportError("Google dependencies not available")
    
    # Estas credenciales deben estar en variables de entorno
    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=GoogleCalendarIntegration.SCOPES,
        redirect_uri=redirect_uri
    )
    
    return flow