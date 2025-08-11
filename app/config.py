"""
Configuración usando Pydantic Settings para validación
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Korei Assistant"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "development"
    port: int = 8000
    timezone: str = "America/Costa_Rica"
    
    # Supabase
    supabase_url: str = "https://ejemplo.supabase.co"
    supabase_anon_key: str = "ejemplo_key"
    supabase_service_key: str = "ejemplo_key"
    
    # WhatsApp (WAHA)
    waha_api_url: str = "http://localhost:3000"
    waha_api_key: str
    waha_session: str = "default"
    
    # AI Services
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # Security
    api_key: Optional[str] = None
    allowed_origins: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

@lru_cache()
def get_settings() -> Settings:
    """Cache settings untuk performa"""
    return Settings()

settings = get_settings()