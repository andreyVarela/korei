#!/usr/bin/env python3
"""
Verificar esquema actual de Supabase
"""
import asyncio
from core.supabase import supabase

async def check_schema():
    print("=== VERIFICAR ESQUEMA SUPABASE ===")
    
    try:
        # Intentar obtener un usuario existente para ver las columnas
        result = supabase._get_client().table("users").select("*").limit(1).execute()
        
        if result.data:
            print("Columnas encontradas en users:")
            for column in result.data[0].keys():
                print(f"  - {column}")
            print()
            print("Ejemplo de usuario:")
            print(result.data[0])
        else:
            print("No hay usuarios en la tabla")
            
            # Intentar insertar uno para ver qué columnas acepta
            print("Probando inserción para detectar columnas...")
            try:
                test_result = supabase._get_client().table("users").insert({
                    "whatsapp_number": "test123"
                }).execute()
                print(f"Inserción exitosa: {test_result.data}")
            except Exception as e:
                print(f"Error en inserción: {e}")
                
    except Exception as e:
        print(f"Error consultando schema: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())