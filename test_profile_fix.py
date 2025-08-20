#!/usr/bin/env python3
"""
Test del fix del comando /profile
"""
import asyncio
from core.supabase import supabase
from handlers.command_handler import CommandHandler

async def test_profile_fix():
    """Prueba si el comando /profile funciona con el fix"""
    try:
        print("Testing profile fix...")
        
        # Número de teléfono de prueba (el tuyo)
        phone_number = "50660052300"
        
        # Obtener usuario con contexto completo
        print("1. Getting user with context...")
        user = await supabase.get_user_with_context(phone_number)
        print(f"   User: {user}")
        
        # Verificar si tiene perfil
        profile = user.get("profile", {})
        print(f"2. Profile: {profile}")
        
        # Probar comando /profile
        print("3. Testing /profile command...")
        command_handler = CommandHandler()
        result = await command_handler.handle_profile(user)
        print(f"   Result type: {result.get('type')}")
        print(f"   Message: {result.get('message', '')[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_profile_fix())
    print(f"\nFinal result: {result.get('type', 'unknown')}")