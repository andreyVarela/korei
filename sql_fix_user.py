"""
Corrección SQL directa del usuario
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase

async def sql_fix_user():
    """Corrección SQL directa"""
    try:
        print("Corrección SQL directa...")
        
        client = supabase._get_client()
        
        # Update directo
        client.table("users").update({
            "name": "Andrei Varela Solano"
        }).eq("whatsapp_number", "50660052300").execute()
        
        print("Update ejecutado")
        
        # Verificar longitud
        verify = client.table("users").select("name").eq("whatsapp_number", "50660052300").execute()
        
        if verify.data:
            name_length = len(verify.data[0].get('name', ''))
            print(f"Nueva longitud del nombre: {name_length}")
            
            if name_length > 10:
                print("SUCCESS: Nombre corregido")
            else:
                print("FAILED: Nombre sigue corrupto")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(sql_fix_user())