"""
Configuración usando Pydantic Settings para validación
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from functools import lru_cache
from pydantic import field_validator

class Settings(BaseSettings):
    # App
    app_name: str = "Korei Assistant"
    app_version: str = "2.0.0"
    debug: bool = True
    environment: str = "development"
    port: int = 8000
    timezone: str = "America/Costa_Rica"
    
    # Supabase
    supabase_url: str
    supabase_key: str  # Service role key (was supabase_service_key)
    
    # WhatsApp (WAHA) - Legacy
    waha_api_url: Optional[str] = None
    waha_api_key: Optional[str] = None
    waha_session: str = "default"
    
    # WhatsApp Cloud API
    whatsapp_cloud_token: str  # Access token (was whatsapp_access_token)
    verify_token: str  # Verify token (was whatsapp_verify_token)
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_webhook_secret: Optional[str] = None
    
    # AI Services
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # Security
    api_key: Optional[str] = None
    secret_key: str  # JWT secret key
    allowed_origins: List[str] = ["*"]  # Will be parsed from comma-separated string
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse comma-separated string into list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Optional webhook URL (for documentation/testing)
    webhook_url: Optional[str] = None
    
    # Configuración de integraciones
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    base_url: str = "http://localhost:8000/"
    encryption_master_key: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

def get_settings() -> Settings:
    """Get settings (no cache in development)"""
    # Force reload .env file
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)  # This forces reload
    return Settings()

# Create fresh instance every time
settings = get_settings()