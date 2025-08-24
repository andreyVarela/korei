"""
Korei Assistant - API Principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from api.routes import webhook, stats, health, integrations, whatsapp_cloud, payment_webhook, debug, debug_webhook
from api.middleware import LoggingMiddleware, ErrorHandlerMiddleware
from services.reminder_scheduler import reminder_scheduler


# Configurar Loguru (siempre, incluso con Uvicorn)
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.debug else "DEBUG"
)
logger.add("logs/app.log", rotation="10 MB", retention="10 days", level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"Ambiente: {settings.environment}")
    
    # Iniciar sistema de recordatorios
    await reminder_scheduler.start()
    logger.info("✅ Sistema de recordatorios y mensajes automáticos iniciado")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación")
    await reminder_scheduler.stop()
    logger.info("⏹️ Sistema de recordatorios detenido")

# Crear aplicación
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Tu asistente personal inteligente en WhatsApp",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

if settings.debug:
    # Parse allowed_origins string to list
    origins = [origin.strip() for origin in settings.allowed_origins.split(',') if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rutas
app.include_router(health.router, tags=["Health"])
app.include_router(webhook.router, prefix="/webhook", tags=["WhatsApp WAHA"])
app.include_router(whatsapp_cloud.router, prefix="/webhook/cloud", tags=["WhatsApp Cloud API"])
app.include_router(payment_webhook.router, prefix="/webhook/payment", tags=["Payment Webhooks"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(integrations.router, prefix="/api", tags=["Integrations"])
app.include_router(debug.router, prefix="/debug", tags=["Debug"])
app.include_router(debug_webhook.router, prefix="/debug", tags=["Debug Webhook"])

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Use PORT from environment (for DigitalOcean App Platform) or fallback to settings
    port = int(os.getenv("PORT", settings.port))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info"
    )