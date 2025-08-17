#!/usr/bin/env python3
"""
Test con formato de WhatsApp Cloud API
"""
import asyncio
from handlers.message_handler import message_handler
from core.supabase import supabase

async def test_cloud_api_format():
    print("=== TEST FORMATO WHATSAPP CLOUD API ===")
    
    # Número como viene desde WhatsApp Cloud API (limpio)
    phone = "50660052300"  # Tu número real, como viene de Meta
    
    try:
        # Obtener/crear usuario
        user = await supabase.get_or_create_user(phone, "Andrei")
        print(f"Usuario obtenido/creado:")
        print(f"  ID: {user['id']}")
        print(f"  Número: {user['whatsapp_number']}")
        print(f"  Nombre: {user['display_name']}")
        print()
        
        message = "Gasto 10000 en linea"
        print(f"Procesando: '{message}'")
        
        # Procesar mensaje
        result = await message_handler.handle_text(message, user)
        print(f"Resultado final: {result}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    asyncio.run(test_cloud_api_format())