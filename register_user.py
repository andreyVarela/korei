#!/usr/bin/env python3
"""
Script para registrar usuario en Korei Assistant
"""
import requests
import sys

def register_user(phone_number):
    """Registrar usuario directamente en Supabase"""
    
    # Datos de Supabase - usar variables de entorno en producción
    SUPABASE_URL = "https://your-project.supabase.co"  # Reemplazar con tu URL real
    SUPABASE_KEY = "your_supabase_service_key_here"   # Reemplazar con tu key real
    
    # Headers para Supabase
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Datos del usuario (campos mínimos)
    user_data = {
        "phone": phone_number,
        "name": "Usuario Principal"
    }
    
    print(f"Registrando usuario {phone_number}...")
    
    # Crear usuario
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/users",
        json=user_data,
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        print(f"Usuario {phone_number} registrado exitosamente!")
        print(f"Datos: {response.json()}")
        return True
    else:
        print(f"Error registrando usuario: {response.status_code}")
        print(f"Respuesta: {response.text}")
        return False

if __name__ == "__main__":
    phone = "50660052300"  # Tu número
    
    if register_user(phone):
        print("\nUsuario registrado! Ahora puedes enviar mensajes por WhatsApp.")
        print(f"Numero habilitado: {phone}")
        print("Envia un mensaje para probar.")
    else:
        print("\nError en el registro. Revisa la configuracion.")