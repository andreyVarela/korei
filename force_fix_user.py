"""
Corrección forzada del usuario
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase

async def force_fix_user():
    """Corrección forzada del usuario"""
    try:
        test_phone = "50660052300"
        
        print("Corrección forzada del usuario...")
        
        # Obtener cliente directo
        client = supabase._get_client()
        
        # Actualizar directamente
        result = client.table("users").update({
            "name": "Andrei Varela Solano"
        }).eq("whatsapp_number", test_phone).execute()
        
        print(f"Resultado update: {result.data}")
        
        # Verificar
        verify = client.table("users").select("name, whatsapp_number").eq("whatsapp_number", test_phone).execute()
        
        if verify.data:
            user = verify.data[0]
            name = user.get('name', '')
            print(f"Nombre verificado: longitud={len(name)}")
            if len(name) > 10:
                print("EXITO: Nombre corregido")
            else:
                print("FALLO: Nombre sigue corrupto")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_fix_user())