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
    
    # Debug: Print current working directory and .env file existence
    print(f"🔍 Current working directory: {os.getcwd()}")
    env_path = os.path.join(os.getcwd(), '.env')
    print(f"🔍 Looking for .env at: {env_path}")
    print(f"🔍 .env file exists: {os.path.exists(env_path)}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
            print(f"🔍 .env file content preview (first 200 chars): {env_content[:200]}...")
    
    load_dotenv(override=True)  # This forces reload
    
    # Debug: Print some non-sensitive environment variables
    print(f"🔍 Environment: {os.getenv('ENVIRONMENT', 'NOT_SET')}")
    print(f"🔍 SUPABASE_URL set: {'YES' if os.getenv('SUPABASE_URL') else 'NO'}")
    print(f"🔍 SUPABASE_SERVICE_KEY set: {'YES' if os.getenv('SUPABASE_SERVICE_KEY') else 'NO'}")
    print(f"🔍 WHATSAPP_ACCESS_TOKEN set: {'YES' if os.getenv('WHATSAPP_ACCESS_TOKEN') else 'NO'}")
    
    return Settings()

# Create fresh instance every time
settings = get_settings()