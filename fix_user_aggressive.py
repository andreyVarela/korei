"""
Corrección agresiva del usuario
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase

async def fix_user_aggressive():
    """Corrección agresiva del usuario"""
    try:
        print("=== CORRECCIÓN AGRESIVA ===")
        
        test_phone = "50660052300"
        correct_name = "Andrei Varela Solano"
        
        client = supabase._get_client()
        
        # 1. Verificar estado actual
        print("1. ESTADO ACTUAL:")
        current = client.table("users").select("id, name").eq("whatsapp_number", test_phone).execute()
        if current.data:
            user = current.data[0]
            user_id = user['id']
            current_name = user['name']
            print(f"   ID: {user_id}")
            print(f"   Nombre actual longitud: {len(current_name)}")
        
        # 2. Update por ID (más específico)
        print("2. ACTUALIZANDO POR ID...")
        update_result = client.table("users").update({
            "name": correct_name
        }).eq("id", user_id).execute()
        
        print(f"   Filas afectadas: {len(update_result.data)}")
        
        # 3. Verificar inmediatamente
        print("3. VERIFICACIÓN INMEDIATA:")
        verify = client.table("users").select("name").eq("id", user_id).execute()
        if verify.data:
            new_name = verify.data[0]['name']
            new_length = len(new_name)
            print(f"   Nueva longitud: {new_length}")
            
            if new_length == len(correct_name):
                print("   SUCCESS: Nombre actualizado correctamente")
            else:
                print("   FAILED: Nombre no se actualizó")
                
                # 4. Intentar con DELETE + INSERT
                print("4. MÉTODO DRÁSTICO - DELETE + INSERT:")
                
                # Obtener datos completos del usuario
                full_user = client.table("users").select("*").eq("id", user_id).execute()
                user_data = full_user.data[0]
                
                # Eliminar
                client.table("users").delete().eq("id", user_id).execute()
                print("   Usuario eliminado")
                
                # Recrear con nombre correcto
                user_data['name'] = correct_name
                new_user = client.table("users").insert(user_data).execute()
                print("   Usuario recreado")
                
                if new_user.data:
                    print("   SUCCESS: Usuario recreado con nombre correcto")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_user_aggressive())