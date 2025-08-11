#!/usr/bin/env python3
"""
Script para probar el webhook de WAHA localmente
"""
import requests
import json
import time
from datetime import datetime

# Configuración
WEBHOOK_URL = "http://localhost:8000/webhook"

def test_text_message():
    """Prueba mensaje de texto"""
    payload = {
        "event": "message",
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_text_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": False,
            "body": "Gasté $25 en almuerzo hoy",
            "type": "text",
            "timestamp": int(time.time()),
            "notifyName": "Usuario Prueba"
        }
    }
    
    print("[TEXT] Enviando mensaje de texto...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_image_message():
    """Prueba mensaje con imagen"""
    payload = {
        "event": "message", 
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_image_{int(time.time())}",
            "from": "50660052300@c.us", 
            "fromMe": False,
            "body": "",
            "type": "image",
            "caption": "Recibo de compra en el supermercado",
            "timestamp": int(time.time()),
            "notifyName": "Usuario Prueba",
            "mediaUrl": "https://example.com/receipt.jpg"
        }
    }
    
    print("[IMAGE] Enviando mensaje con imagen...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_audio_message():
    """Prueba mensaje de audio"""
    payload = {
        "event": "message",
        "session": "default", 
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_audio_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": False,
            "body": "",
            "type": "audio",
            "timestamp": int(time.time()),
            "notifyName": "Usuario Prueba",
            "mediaUrl": "https://example.com/voice_note.ogg"
        }
    }
    
    print("[AUDIO] Enviando mensaje de audio...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_own_message():
    """Prueba mensaje propio (debe ser ignorado)"""
    payload = {
        "event": "message",
        "session": "default",
        "timestamp": int(time.time() * 1000), 
        "payload": {
            "id": f"test_own_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": True,  # Mensaje propio
            "body": "Este mensaje debe ser ignorado",
            "type": "text",
            "timestamp": int(time.time()),
            "notifyName": "Yo"
        }
    }
    
    print("[SKIP] Enviando mensaje propio (debe ignorarse)...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_register_command():
    """Prueba comando /register"""
    payload = {
        "event": "message",
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_register_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": False,
            "body": "/register Soy programador y fotógrafo de bodas, me gusta la tecnología",
            "type": "text",
            "timestamp": int(time.time()),
            "notifyName": "Andrei Varela"
        }
    }
    
    print("[COMMAND] Enviando comando /register...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_profile_command():
    """Prueba comando /profile"""
    payload = {
        "event": "message",
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_profile_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": False,
            "body": "/profile",
            "type": "text",
            "timestamp": int(time.time()),
            "notifyName": "Andrei Varela"
        }
    }
    
    print("[COMMAND] Enviando comando /profile...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_personalized_message():
    """Prueba mensaje que debería usar contexto personal"""
    payload = {
        "event": "message",
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "id": f"test_personal_{int(time.time())}",
            "from": "50660052300@c.us",
            "fromMe": False,
            "body": "Compré una nueva lente para mi cámara por $500",
            "type": "text",
            "timestamp": int(time.time()),
            "notifyName": "Andrei Varela"
        }
    }
    
    print("[PERSONAL] Enviando mensaje con contexto personal...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

def test_status_event():
    """Prueba evento de estado (debe ser ignorado)"""
    payload = {
        "event": "status",
        "session": "default",
        "timestamp": int(time.time() * 1000),
        "payload": {
            "status": "online",
            "from": "5555551234@c.us"
        }
    }
    
    print("[STATUS] Enviando evento de estado (debe ignorarse)...")
    print(f"[OUT] Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"[IN] Respuesta: {response.status_code} - {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    print("[START] Iniciando pruebas del webhook Korei Assistant")
    print(f"[URL] URL: {WEBHOOK_URL}")
    print(f"[TIME] Timestamp: {datetime.now()}")
    print("=" * 60)
    
    try:
        # Verificar que el servidor esté corriendo
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code != 200:
            print("[ERROR] Servidor no está corriendo. Ejecuta: python main.py")
            exit(1)
        
        print("[OK] Servidor está corriendo")
        print("-" * 50)
        
        # Ejecutar todas las pruebas
        test_register_command()
        test_profile_command() 
        test_personalized_message()
        test_text_message()
        test_own_message()
        test_status_event()
        
        print("[OK] Todas las pruebas completadas")
        print("[INFO] Revisa los logs del servidor para ver el procesamiento")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar al servidor.")
        print("[TIP] Asegúrate de que el servidor esté corriendo: python main.py")
    except Exception as e:
        print(f"[ERROR] Error: {e}")