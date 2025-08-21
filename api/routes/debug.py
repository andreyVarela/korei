"""
Debug endpoints for remote monitoring
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from typing import List, Optional
import os
import subprocess
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()

def get_debug_auth():
    """Simple auth for debug endpoints"""
    # Only available in development or with specific key
    if not settings.debug and not settings.api_key:
        raise HTTPException(status_code=404, detail="Not found")
    return True

@router.get("/logs", response_class=PlainTextResponse, dependencies=[Depends(get_debug_auth)])
async def get_recent_logs(lines: int = 100):
    """Get recent application logs"""
    try:
        # Try to read from log file
        log_file = "logs/app.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines_list = f.readlines()
                recent_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list
                return "".join(recent_lines)
        else:
            return f"Log file not found at {log_file}"
    except Exception as e:
        return f"Error reading logs: {str(e)}"

@router.get("/status", dependencies=[Depends(get_debug_auth)])
async def get_system_status():
    """Get system status information"""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment,
            "debug_mode": settings.debug,
            "app_version": settings.app_version,
            "working_directory": os.getcwd(),
            "env_file_exists": os.path.exists('.env'),
            "log_file_exists": os.path.exists('logs/app.log'),
            "supabase_configured": bool(settings.supabase_url and settings.supabase_service_key),
            "whatsapp_configured": bool(settings.whatsapp_access_token and settings.whatsapp_verify_token),
            "gemini_configured": bool(settings.gemini_api_key)
        }
        
        # Check if we can connect to Supabase
        try:
            from core.supabase import supabase
            client = supabase._get_client()
            status["supabase_connection"] = "OK"
        except Exception as e:
            status["supabase_connection"] = f"ERROR: {str(e)}"
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@router.get("/env-check", dependencies=[Depends(get_debug_auth)])
async def check_environment_variables():
    """Check which environment variables are set"""
    try:
        env_status = {
            "SUPABASE_URL": "SET" if os.getenv("SUPABASE_URL") else "NOT_SET",
            "SUPABASE_SERVICE_KEY": "SET" if os.getenv("SUPABASE_SERVICE_KEY") else "NOT_SET",
            "WHATSAPP_ACCESS_TOKEN": "SET" if os.getenv("WHATSAPP_ACCESS_TOKEN") else "NOT_SET",
            "WHATSAPP_VERIFY_TOKEN": "SET" if os.getenv("WHATSAPP_VERIFY_TOKEN") else "NOT_SET",
            "WHATSAPP_PHONE_NUMBER_ID": "SET" if os.getenv("WHATSAPP_PHONE_NUMBER_ID") else "NOT_SET",
            "GEMINI_API_KEY": "SET" if os.getenv("GEMINI_API_KEY") else "NOT_SET",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
            "DEBUG": os.getenv("DEBUG", "NOT_SET")
        }
        
        return env_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking env vars: {str(e)}")

@router.get("/test-webhook", dependencies=[Depends(get_debug_auth)])
async def test_webhook_connectivity():
    """Test webhook connectivity"""
    try:
        test_data = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "test",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "test",
                            "phone_number_id": settings.whatsapp_phone_number_id
                        },
                        "messages": [{
                            "from": "1234567890",
                            "id": "test_message_id",
                            "timestamp": "1234567890",
                            "text": {
                                "body": "Test message from debug endpoint"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        return {
            "message": "This would simulate a webhook call",
            "test_data": test_data,
            "webhook_url": f"{settings.base_url}webhook/cloud/whatsapp"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing webhook: {str(e)}")

@router.post("/clear-logs", dependencies=[Depends(get_debug_auth)])
async def clear_logs():
    """Clear application logs"""
    try:
        log_file = "logs/app.log"
        if os.path.exists(log_file):
            open(log_file, 'w').close()
            return {"message": "Logs cleared successfully"}
        else:
            return {"message": "Log file not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing logs: {str(e)}")