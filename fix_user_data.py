"""
Script para verificar y corregir datos del usuario en BD
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.supabase import supabase

async def fix_user_data():
    """Verificar y corregir datos del usuario"""
    try:
        print("VERIFICANDO DATOS DEL USUARIO...")
        
        test_phone = "50660052300"
        
        # 1. Verificar datos actuales
        print(f"\n1. Datos actuales del usuario {test_phone}:")
        
        user_data = supabase._get_client().table("users").select("*").eq(
            "whatsapp_number", test_phone
        ).execute()
        
        if user_data.data:
            user = user_data.data[0]
            print(f"ID: {user.get('id')}")
            name_value = user.get('name', 'Sin nombre')
            print(f"Telefono: {user.get('whatsapp_number')}")
            print(f"Plan: {user.get('plan_type', 'Sin plan')}")
            print(f"Nombre tiene caracteres especiales: {len(name_value)} chars")
            
            # 2. Corregir nombre (forzar actualizacion)
            current_name = user.get('name', '')
            print(f"Actualizando nombre...")
            
            # Forzar actualizacion del nombre
            if True:  # Siempre actualizar
                print(f"\n2. Corrigiendo nombre del usuario...")
                
                correct_name = "Andrei Varela Solano"
                
                update_result = supabase._get_client().table("users").update({
                    "name": correct_name
                }).eq("id", user['id']).execute()
                
                if update_result.data:
                    print(f"SUCCESS: Nombre actualizado a '{correct_name}'")
                else:
                    print(f"ERROR: No se pudo actualizar el nombre")
            else:
                print(f"\n2. Nombre ya esta correcto: '{current_name}'")
        else:
            print(f"ERROR: Usuario no encontrado en la BD")
        
        # 3. Verificar datos finales
        print(f"\n3. Verificando datos finales...")
        
        final_context = await supabase.get_user_with_context(test_phone)
        final_name = final_context.get('name', 'Sin nombre')
        
        print(f"Nombre final: '{final_name}'")
        
        if final_name == "Andrei Varela Solano":
            print("SUCCESS: Datos del usuario corregidos correctamente")
        else:
            print(f"ERROR: Nombre aun incorrecto: '{final_name}'")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_user_data())