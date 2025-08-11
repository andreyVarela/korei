"""
Korei Assistant - API Principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from api.routes import webhook, stats, health
from api.middleware import LoggingMiddleware, ErrorHandlerMiddleware

# Configurar Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO" if not settings.debug else "DEBUG"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    logger.info(f"🚀 Iniciando {settings.app_name} v{settings.app_version}")
    logger.info(f"📍 Ambiente: {settings.environment}")
    
    # Aquí puedes inicializar conexiones, cargar modelos, etc.
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación")

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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rutas
app.include_router(health.router, tags=["Health"])
app.include_router(webhook.router, prefix="/webhook", tags=["WhatsApp"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )