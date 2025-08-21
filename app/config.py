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
    debug: bool = True
    environment: str = "development"
    port: int = 8000
    timezone: str = "America/Costa_Rica"
    log_level: str = "INFO"
    
    # Supabase
    supabase_url: str
    supabase_service_key: str  # Service role key
    supabase_anon_key: Optional[str] = None  # Optional anon key
    
    # WhatsApp (WAHA) - Legacy
    waha_api_url: Optional[str] = None
    waha_api_key: Optional[str] = None
    waha_session: str = "default"
    
    # WhatsApp Cloud API
    whatsapp_access_token: str  # Access token
    whatsapp_verify_token: str  # Verify token
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_webhook_secret: Optional[str] = None
    
    @property
    def whatsapp_cloud_token(self) -> str:
        """Alias for whatsapp_access_token for backward compatibility"""
        return self.whatsapp_access_token
    
    # AI Services
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # Security
    api_key: Optional[str] = None
    secret_key: Optional[str] = None  # JWT secret key (made optional)
    allowed_origins: str = "*"  # Single string for simplicity
    
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
        case_sensitive=False,
        extra="ignore"
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