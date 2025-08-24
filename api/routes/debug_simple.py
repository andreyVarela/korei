"""
Endpoint SIMPLE para debugging directo
"""
from fastapi import APIRouter
from core.supabase import supabase
import json

router = APIRouter()

@router.get("/check-user/{phone}")
async def check_user_exists(phone: str):
    """Verificar si usuario existe en la base de datos"""
    try:
        # Probar get_user_by_phone directamente
        user = await supabase.get_user_by_phone(phone)
        
        return {
            "phone": phone,
            "user_exists": user is not None,
            "user_data": user,
            "user_keys": list(user.keys()) if user else None
        }
        
    except Exception as e:
        return {
            "phone": phone,
            "error": str(e),
            "user_exists": False
        }

@router.get("/test-supabase")
async def test_supabase_connection():
    """Probar conexión básica a Supabase"""
    try:
        # Hacer query simple
        result = supabase._get_client().table("users").select("count").execute()
        
        return {
            "supabase_connected": True,
            "users_count": len(result.data) if result.data else 0,
            "connection_working": True
        }
        
    except Exception as e:
        return {
            "supabase_connected": False,
            "error": str(e),
            "connection_working": False
        }

@router.post("/simulate-webhook")
async def simulate_message_processing():
    """Simular procesamiento de mensaje paso a paso"""
    try:
        phone = "50660052300"
        message = "hola"
        
        # PASO 1: Verificar usuario
        user = await supabase.get_user_with_context(phone)
        
        # PASO 2: Log detallado
        result = {
            "step": "user_context",
            "phone": phone,
            "user_retrieved": user is not None,
            "user_data": user,
            "has_whatsapp_number": user.get('whatsapp_number') is not None if user else False,
            "has_phone": user.get('phone') is not None if user else False,
            "has_id": user.get('id') is not None if user else False
        }
        
        if user and user.get('whatsapp_number'):
            # PASO 3: Probar message handler (solo si el usuario está bien)
            from handlers.message_handler import message_handler
            handler_result = await message_handler.handle_text(message, user)
            result["message_handler_result"] = handler_result
        
        return result
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }