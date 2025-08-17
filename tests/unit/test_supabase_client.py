#!/usr/bin/env python3
"""
Script para probar conexión con Supabase
"""
import asyncio
from core.supabase import supabase

async def test_supabase():
    """Prueba conexión básica con Supabase"""
    try:
        print(">> Probando conexión con Supabase...")
        
        # Obtener o crear usuario de prueba
        phone = "+50612345678"
        user = await supabase.get_or_create_user(phone, "Usuario Test")
        
        print(f">> Usuario obtenido/creado:")
        print(f"   ID: {user.get('id')}")
        print(f"   Nombre: {user.get('name')}")
        print(f"   Teléfono: {user.get('whatsapp_number')}")
        
        # Crear entrada de prueba
        entry_data = {
            "user_id": user['id'],
            "type": "gasto",
            "description": "Café de prueba",
            "amount": 5.0,
            "datetime": "2025-08-11T10:00:00-06:00",
            "priority": "baja",
            "status": "completed"
        }
        
        print("\n>> Creando entrada de prueba...")
        entry = await supabase.create_entry(entry_data)
        
        print(f">> Entrada creada:")
        print(f"   ID: {entry.get('id')}")
        print(f"   Tipo: {entry.get('type')}")
        print(f"   Descripción: {entry.get('description')}")
        print(f"   Monto: ${entry.get('amount')}")
        
        # Obtener estadísticas
        print("\n>> Obteniendo estadísticas del usuario...")
        stats = await supabase.get_user_stats(user['id'])
        
        print(f">> Estadísticas:")
        print(f"   Total entradas: {stats.get('total_entries')}")
        print(f"   Gastos: ${stats.get('gastos')}")
        print(f"   Ingresos: ${stats.get('ingresos')}")
        print(f"   Balance: ${stats.get('balance')}")
        
        return True
        
    except Exception as e:
        print(f"XX Error: {e}")
        return False

async def main():
    print("=== Test Supabase ===\n")
    
    success = await test_supabase()
    
    if success:
        print("\n>> ¡Conexión exitosa con Supabase!")
    else:
        print("\n>> Error conectando con Supabase")
        print("Verifica las credenciales en .env")

if __name__ == "__main__":
    asyncio.run(main())