"""
Endpoints para gestión de integraciones externas
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger

from services.integrations.integration_manager import integration_manager
from services.integrations.google_calendar import create_oauth_flow
from core.supabase import supabase

router = APIRouter(tags=["integrations"])


class IntegrationRequest(BaseModel):
    service: str
    credentials: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


class SyncRequest(BaseModel):
    direction: str = "both"  # 'import', 'export', 'both'


@router.get("/available")
async def get_available_integrations():
    """Lista integraciones disponibles"""
    return {
        "integrations": [
            {
                "service": "google_calendar",
                "name": "Google Calendar",
                "type": "calendar",
                "auth_type": "oauth2",
                "description": "Sincroniza eventos con Google Calendar"
            },
            {
                "service": "todoist", 
                "name": "Todoist",
                "type": "tasks",
                "auth_type": "api_token",
                "description": "Sincroniza tareas con Todoist"
            }
        ]
    }


@router.get("/oauth/{service}/start")
async def start_oauth_flow(
    request: Request,
    service: str,
    user_id: str = Query(...),
    redirect_url: Optional[str] = Query(None)
):
    """Inicia flujo OAuth para integraciones"""
    try:
        if service == "google_calendar":
            # Crear flujo OAuth usando BASE_URL de settings
            from app.config import settings
            callback_url = f"{settings.base_url}/api/oauth/google_calendar/callback"
            flow = create_oauth_flow(str(callback_url))
            
            # Generar URL de autorización
            auth_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=f"{user_id}|{redirect_url or ''}"  # Incluir user_id en state
            )
            
            return RedirectResponse(url=auth_url)
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth not supported for service: {service}"
            )
            
    except Exception as e:
        logger.error(f"Error starting OAuth flow for {service}: {e}")
        raise HTTPException(status_code=500, detail="Error starting OAuth flow")


@router.get("/oauth/google_calendar/callback")
async def google_calendar_oauth_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None)
):
    """Callback para OAuth de Google Calendar"""
    try:
        logger.info(f"CALLBACK RECEIVED - Code: {code[:20]}..., State: {state}, Error: {error}")
        
        if error:
            logger.error(f"OAuth error: {error}")
            return {"error": f"OAuth authorization failed: {error}"}
        
        # Extraer user_id del state
        state_parts = state.split('|')
        user_id = state_parts[0]
        redirect_url = state_parts[1] if len(state_parts) > 1 and state_parts[1] else None
        logger.info(f"EXTRACTED - User ID: {user_id}, Redirect URL: {redirect_url}")
        
        # Completar flujo OAuth
        callback_url = str(request.url).split('?')[0]  # URL sin parámetros
        logger.info(f"CALLBACK URL: {callback_url}")
        
        flow = create_oauth_flow(callback_url)
        logger.info(f"FLOW CREATED")
        
        flow.fetch_token(code=code)
        logger.info(f"TOKEN FETCHED")
        
        # Obtener credenciales en el formato correcto
        import json
        token_data = json.loads(flow.credentials.to_json())
        logger.info(f"TOKEN DATA: {token_data}")
        
        # SOLUCION: Agregar los scopes que faltan
        credentials = {
            **token_data,  # access_token, refresh_token, etc.
            'client_id': flow.client_config['client_id'],
            'client_secret': flow.client_config['client_secret'],
            'scopes': ['https://www.googleapis.com/auth/calendar']  # ¡ESTO FALTABA!
        }
        logger.info(f"CREDENTIALS FINAL: {credentials}")
        
        # Registrar integración
        logger.info(f"CALLING register_user_integration...")
        success = await integration_manager.register_user_integration(
            user_id=user_id,
            service="google_calendar",
            credentials=credentials,
            config={"calendar_id": "primary"}
        )
        logger.info(f"REGISTRATION RESULT: {success}")
        
        if success:
            message = "✅ Google Calendar conectado exitosamente"
            logger.info(f"SUCCESS: {message}")
            if redirect_url:
                return RedirectResponse(url=f"{redirect_url}?status=success&message={message}")
            return {"status": "success", "message": message}
        else:
            message = "❌ Error conectando Google Calendar"
            logger.error(f"FAILED: {message}")
            if redirect_url:
                return RedirectResponse(url=f"{redirect_url}?status=error&message={message}")
            return {"status": "error", "message": message}
            
    except Exception as e:
        logger.error(f"Error in Google Calendar OAuth callback: {e}")
        message = f"Error en OAuth: {str(e)}"
        if 'redirect_url' in locals() and redirect_url:
            return RedirectResponse(url=f"{redirect_url}?status=error&message={message}")
        return {"status": "error", "message": message}


@router.post("/connect")
async def connect_integration(
    user_id: str,
    integration: IntegrationRequest
):
    """Conecta una integración (para servicios con API key)"""
    try:
        success = await integration_manager.register_user_integration(
            user_id=user_id,
            service=integration.service,
            credentials=integration.credentials,
            config=integration.config
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Integración {integration.service} conectada exitosamente"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to authenticate integration"
            )
            
    except Exception as e:
        logger.error(f"Error connecting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_integrations(user_id: str):
    """Obtiene las integraciones activas del usuario"""
    try:
        integrations = await integration_manager.get_user_integrations(user_id)
        
        integration_list = []
        for integration in integrations:
            status = integration.get_integration_status()
            integration_list.append({
                "service": status["service"],
                "is_connected": status["is_connected"],
                "last_sync": status["last_sync"]
            })
        
        return {"integrations": integration_list}
        
    except Exception as e:
        logger.error(f"Error getting user integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/{user_id}")
async def sync_user_integrations(
    user_id: str,
    sync_request: SyncRequest
):
    """Sincroniza datos del usuario con sus integraciones"""
    try:
        results = await integration_manager.sync_user_data(
            user_id=user_id,
            direction=sync_request.direction
        )
        
        return {
            "status": "completed",
            "results": results,
            "message": f"Sincronización completada. Exportados: {len(results['exported_items'])}, Importados: {len(results['imported_items'])}"
        }
        
    except Exception as e:
        logger.error(f"Error syncing user integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/user/{user_id}/{service}")
async def disconnect_integration(user_id: str, service: str):
    """Desconecta una integración específica"""
    try:
        success = await integration_manager.remove_user_integration(user_id, service)
        
        if success:
            return {
                "status": "success",
                "message": f"Integración {service} desconectada"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to disconnect integration"
            )
            
    except Exception as e:
        logger.error(f"Error disconnecting integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{user_id}/{service}")
async def test_integration(user_id: str, service: str):
    """Prueba una integración específica"""
    try:
        integration = await integration_manager.get_user_integration(user_id, service)
        
        if not integration:
            raise HTTPException(
                status_code=404,
                detail="Integration not found"
            )
        
        is_working = await integration.test_connection()
        
        return {
            "service": service,
            "is_working": is_working,
            "message": "Conexión exitosa" if is_working else "Error de conexión"
        }
        
    except Exception as e:
        logger.error(f"Error testing integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))