#!/usr/bin/env python3
"""
Test con usuario existente de Supabase
"""
import asyncio
from handlers.message_handler import message_handler
from core.supabase import supabase

async def test_existing_user():
    print("=== TEST CON USUARIO EXISTENTE ===")
    
    # Usar el número del usuario que vimos en la base de datos
    phone = "50688231184"  # Sin @c.us
    
    try:
        # Obtener usuario existente
        user = await supabase.get_or_create_user(phone, "Ronald")
        print(f"Usuario obtenido:")
        print(f"  ID: {user['id']}")
        print(f"  Número: {user['whatsapp_number']}")
        print(f"  Nombre: {user['display_name']}")
        print()
        
        message = "Gasto 10000 en linea"
        print(f"Procesando: '{message}'")
        
        # Procesar mensaje
        result = await message_handler.handle_text(message, user)
        print(f"Resultado: {result}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    asyncio.run(test_existing_user())