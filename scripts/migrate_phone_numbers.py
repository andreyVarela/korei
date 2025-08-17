#!/usr/bin/env python3
"""
Migrar números de teléfono quitando @c.us
"""
import asyncio
from core.supabase import supabase

async def migrate_phone_numbers():
    print("=== MIGRAR NÚMEROS DE TELÉFONO ===")
    
    try:
        # Obtener todos los usuarios
        result = supabase._get_client().table("users").select("*").execute()
        users = result.data
        
        print(f"Encontrados {len(users)} usuarios")
        
        updated_count = 0
        for user in users:
            old_number = user['whatsapp_number']
            
            if '@c.us' in old_number:
                # Quitar @c.us
                new_number = old_number.replace('@c.us', '')
                
                # Actualizar en la base de datos
                update_result = supabase._get_client().table("users").update({
                    "whatsapp_number": new_number
                }).eq("id", user['id']).execute()
                
                print(f"Actualizado: {old_number} -> {new_number}")
                updated_count += 1
            else:
                print(f"Ya limpio: {old_number}")
        
        print(f"\nMigración completada. {updated_count} usuarios actualizados.")
        
    except Exception as e:
        print(f"Error en migración: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_phone_numbers())