"""
Verificar y corregir el nombre de usuario en la base de datos
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase

async def check_and_fix_user():
    """Verificar y corregir el nombre de usuario corrupto"""
    try:
        test_phone = "50660052300"
        
        print("Verificando usuario en la base de datos...")
        user = await supabase.get_user_by_phone(test_phone)
        
        if user:
            print(f"User ID: {user.get('id')}")
            print(f"Phone: {user.get('whatsapp_number')}")
            print(f"Name length: {len(user.get('name', ''))}")
            print(f"Display name length: {len(user.get('display_name', ''))}")
            
            # Si el nombre está corrupto, corregirlo
            current_name = user.get('name', '')
            # Detectar emojis u otros caracteres especiales
            has_emoji = any(ord(char) > 127 for char in current_name) if current_name else True
            if has_emoji or current_name == 'Usuario' or not current_name:
                print("\nCorrigiendo nombre corrupto...")
                
                # Actualizar con el nombre correcto
                correct_name = "Andrei Varela Solano"
                
                client = supabase._get_client()
                result = client.table("users").update({
                    "name": correct_name
                }).eq("whatsapp_number", test_phone).execute()
                
                if result.data:
                    print(f"Nombre corregido a: {correct_name}")
                else:
                    print("Error actualizando nombre")
            else:
                print("Nombre esta correcto")
                
        else:
            print("Usuario no encontrado")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_fix_user())