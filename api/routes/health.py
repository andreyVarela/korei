# -*- coding: utf-8 -*-
"""
Health check endpoints para monitoreo
"""
from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint basico de salud del servicio
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now().isoformat(),
        "timezone": settings.timezone
    }

@router.get("/health/detailed")  
async def detailed_health_check() -> Dict[str, Any]:
    """
    Health check detallado con verificaciones de servicios
    """
    checks = {
        "api": "healthy",
        "database": "unknown",
        "whatsapp_api": "unknown", 
        "gemini_ai": "unknown"
    }
    
    # Verificar configuracion basica
    config_ok = all([
        settings.supabase_url and settings.supabase_url != "https://tuproyecto.supabase.co",
        settings.gemini_api_key and settings.gemini_api_key.startswith("AIza"),
        settings.waha_api_key and settings.waha_api_key != "tu_waha_key"
    ])
    
    overall_status = "healthy" if config_ok else "degraded"
    
    return {
        "status": overall_status,
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat(),
        "checks": checks,
        "config_valid": config_ok
    }