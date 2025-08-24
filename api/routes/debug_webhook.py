"""
Endpoint de debugging para webhook - SOLO PARA DESARROLLO
"""
from fastapi import APIRouter, Request
from typing import Dict, Any
import json
from loguru import logger

from core.supabase import supabase
from handlers.message_handler import message_handler

router = APIRouter()

@router.post("/debug-webhook")
async def debug_webhook_processing(request: Request):
    """
    Endpoint para debuggear exactamente qué pasa en el procesamiento del webhook
    """
    try:
        # Obtener el payload
        payload = await request.json()
        
        logger.info("=== DEBUG WEBHOOK START ===")
        logger.info(f"Payload received: {json.dumps(payload, indent=2)}")
        
        # Extraer información del mensaje
        if payload.get("object") != "whatsapp_business_account":
            return {"error": "Not a WhatsApp webhook"}
        
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                if change.get("field") == "messages":
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    contacts = value.get("contacts", [])
                    
                    if messages:
                        message_data = messages[0]  # Primer mensaje
                        phone_number = message_data.get("from")
                        message_text = message_data.get("text", {}).get("body")
                        
                        logger.info(f"DEBUG: Phone number extracted: {phone_number}")
                        logger.info(f"DEBUG: Message text: {message_text}")
                        
                        # PASO 1: Probar get_user_with_context
                        try:
                            user = await supabase.get_user_with_context(phone_number)
                            logger.info(f"DEBUG: User from supabase: {json.dumps(user, indent=2, default=str)}")
                            
                            # Verificar campos específicos
                            has_id = user.get('id') is not None
                            has_phone = user.get('phone') is not None
                            has_whatsapp_number = user.get('whatsapp_number') is not None
                            
                            logger.info(f"DEBUG: User validation - ID: {has_id}, phone: {has_phone}, whatsapp_number: {has_whatsapp_number}")
                            
                            # PASO 2: Probar message_handler
                            try:
                                result = await message_handler.handle_text(message_text, user)
                                logger.info(f"DEBUG: Message handler result: {json.dumps(result, indent=2, default=str)}")
                                
                                return {
                                    "success": True,
                                    "phone_number": phone_number,
                                    "user": user,
                                    "result": result,
                                    "message": "Processing successful"
                                }
                                
                            except Exception as handler_error:
                                logger.error(f"DEBUG: Message handler error: {handler_error}")
                                import traceback
                                logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
                                
                                return {
                                    "success": False,
                                    "phone_number": phone_number,
                                    "user": user,
                                    "error": str(handler_error),
                                    "traceback": traceback.format_exc(),
                                    "step": "message_handler"
                                }
                                
                        except Exception as supabase_error:
                            logger.error(f"DEBUG: Supabase error: {supabase_error}")
                            import traceback
                            logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
                            
                            return {
                                "success": False,
                                "phone_number": phone_number,
                                "error": str(supabase_error),
                                "traceback": traceback.format_exc(),
                                "step": "supabase"
                            }
        
        return {"error": "No messages found in webhook"}
        
    except Exception as e:
        logger.error(f"DEBUG: General error: {e}")
        import traceback
        logger.error(f"DEBUG: Traceback: {traceback.format_exc()}")
        
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "step": "general"
        }

@router.get("/debug-user/{phone}")
async def debug_user_creation(phone: str):
    """
    Debug específico para creación de usuario
    """
    try:
        logger.info(f"=== DEBUG USER CREATION FOR {phone} ===")
        
        # Probar get_user_with_context paso a paso
        user = await supabase.get_user_with_context(phone)
        
        return {
            "success": True,
            "phone": phone,
            "user": user,
            "user_type": type(user).__name__,
            "user_keys": list(user.keys()) if isinstance(user, dict) else None
        }
        
    except Exception as e:
        logger.error(f"DEBUG USER ERROR: {e}")
        import traceback
        
        return {
            "success": False,
            "phone": phone,
            "error": str(e),
            "traceback": traceback.format_exc()
        }