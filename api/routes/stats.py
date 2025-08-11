# -*- coding: utf-8 -*-
"""
Rutas para estadisticas
"""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/")
async def get_stats() -> Dict[str, Any]:
    """
    Endpoint basico de estadisticas
    """
    return {
        "status": "ok",
        "total_users": 0,
        "total_messages": 0,
        "version": "2.0.0"
    }

@router.get("/users")
async def get_user_stats() -> Dict[str, Any]:
    """
    Estadisticas de usuarios
    """
    return {
        "active_users": 0,
        "new_users_today": 0,
        "total_users": 0
    }