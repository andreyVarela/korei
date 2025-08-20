#!/usr/bin/env python3
import sys
sys.path.append("/app")
from core.supabase import SupabaseService

# Crear servicio
service = SupabaseService()
phone = "50660052300"

print("Registrando usuario...")

try:
    user_data = {"phone": phone, "name": "Usuario Principal"}
    result = service.create_user(user_data)
    print("Usuario creado exitosamente!")
except Exception as e:
    print(f"Error: {e}")
    try:
        user = service.get_user_by_phone(phone)
        if user:
            print("Usuario ya existe")
        else:
            print("Usuario no existe")
    except Exception as e2:
        print(f"Error buscando: {e2}")