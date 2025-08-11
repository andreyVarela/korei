"""
Schemas para validacion de datos con Pydantic
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """Tipos de mensaje soportados"""
    text = "text"
    image = "image"
    audio = "audio"
    voice = "voice"
    document = "document"

class EntryType(str, Enum):
    """Tipos de entrada que puede procesar Gemini"""
    gasto = "gasto"
    ingreso = "ingreso"
    tarea = "tarea"
    evento = "evento" 
    recordatorio = "recordatorio"

class Priority(str, Enum):
    """Niveles de prioridad"""
    alta = "alta"
    media = "media"
    baja = "baja"

class Status(str, Enum):
    """Estados de tareas/eventos"""
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

# WAHA Webhook Schemas
class WAHAPayload(BaseModel):
    """Payload de webhook WAHA"""
    id: str
    timestamp: int
    from_: str = Field(alias="from")
    fromMe: bool = False
    body: Optional[str] = None
    type: MessageType = MessageType.text
    notifyName: Optional[str] = None
    caption: Optional[str] = None
    
    class Config:
        extra = 'forbid'  # Rechazar campos extra
        allow_population_by_field_name = True

class WAHAWebhook(BaseModel):
    """Estructura completa del webhook WAHA"""
    event: str
    session: str = "default"
    payload: WAHAPayload
    
    class Config:
        extra = 'forbid'

# User Profile Schemas  
class UserProfileCreate(BaseModel):
    """Datos para crear perfil de usuario"""
    name: str = Field(..., min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    hobbies: List[str] = Field(default_factory=list, max_items=10)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    timezone: Optional[str] = "America/Costa_Rica"
    
    class Config:
        extra = 'forbid'

class UserProfileUpdate(BaseModel):
    """Actualizar perfil existente"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    occupation: Optional[str] = Field(None, max_length=200)
    hobbies: Optional[List[str]] = Field(None, max_items=10)
    preferences: Optional[Dict[str, Any]] = None
    context_summary: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        extra = 'forbid'

class UserProfileResponse(BaseModel):
    """Respuesta con perfil de usuario"""
    id: str
    user_id: str
    name: str
    occupation: Optional[str] = None
    hobbies: List[str] = []
    context_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Gemini Response Schemas
class GeminiEntryResponse(BaseModel):
    """Respuesta estructurada de Gemini"""
    type: EntryType
    description: str = Field(..., min_length=1, max_length=500)
    amount: Optional[float] = Field(None, ge=0)
    datetime: str  # ISO format
    datetime_end: Optional[str] = None  # ISO format
    priority: Priority = Priority.media
    recurrence: str = "none"
    calendary: bool = False
    remember: Optional[str] = None  # ISO format
    task_category: Optional[str] = Field(None, max_length=50)
    status: Status = Status.pending
    
    class Config:
        extra = 'forbid'

# Entry Database Schemas
class EntryCreate(BaseModel):
    """Crear nueva entrada en DB"""
    user_id: str
    id_waha: Optional[str] = None  # Para idempotencia
    type: EntryType
    description: str
    amount: Optional[float] = None
    datetime: str
    datetime_end: Optional[str] = None
    priority: Priority = Priority.media
    status: Status = Status.pending
    
    class Config:
        extra = 'forbid'

class EntryResponse(BaseModel):
    """Respuesta de entrada desde DB"""
    id: str
    user_id: str
    type: EntryType
    description: str
    amount: Optional[float] = None
    datetime: datetime
    status: Status
    created_at: datetime