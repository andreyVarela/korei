#!/usr/bin/env python3
"""
Script para probar la aplicación Korei Assistant
"""
import asyncio
import httpx
import json
from app.config import settings

async def test_app():
    """Prueba todos los endpoints importantes"""
    base_url = "http://localhost:8000"
    
    print("=== PROBANDO KOREI ASSISTANT ===")
    print(f"Base URL: {base_url}")
    print(f"WhatsApp Token length: {len(settings.whatsapp_access_token)}")
    print(f"Phone Number ID: {settings.whatsapp_phone_number_id}")
    print()
    
    async with httpx.AsyncClient() as client:
        # 1. Health check
        print("1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   OK Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
        print()
        
        # 2. Test webhook verification
        print("2. Testing webhook verification...")
        try:
            response = await client.get(
                f"{base_url}/webhook/cloud",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "test123",
                    "hub.verify_token": settings.whatsapp_verify_token
                }
            )
            print(f"   OK Status: {response.status_code}")
            print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
        print()
        
        # 3. Test WhatsApp connection
        print("3. Testing WhatsApp connection...")
        try:
            response = await client.get(f"{base_url}/webhook/test-connection")
            if response.status_code == 200:
                print(f"   OK WhatsApp API connected!")
                print(f"   Response: {response.json()}")
            else:
                print(f"   WARNING Status: {response.status_code}")
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
        print()
        
        # 4. Test send message
        print("4. Testing send message...")
        try:
            payload = {
                "to": "50660052300",
                "message": "Prueba desde script de testing - Korei Assistant funcionando!"
            }
            response = await client.post(
                f"{base_url}/webhook/send-test-message",
                json=payload
            )
            if response.status_code == 200:
                print(f"   OK Message sent successfully!")
                print(f"   Response: {response.json()}")
            else:
                print(f"   ERROR Status: {response.status_code}")
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
        print()
        
        # 5. Test webhook processing (simulate WhatsApp message)
        print("5. Testing webhook message processing...")
        try:
            webhook_payload = {
                "object": "whatsapp_business_account",
                "entry": [
                    {
                        "id": "709752851834150",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {
                                        "display_phone_number": "50660052300",
                                        "phone_number_id": "765691039959515"
                                    },
                                    "contacts": [
                                        {
                                            "profile": {"name": "Test User"},
                                            "wa_id": "50660052300"
                                        }
                                    ],
                                    "messages": [
                                        {
                                            "from": "50660052300",
                                            "id": f"test_message_{asyncio.get_event_loop().time()}",
                                            "timestamp": "1734307200",
                                            "text": {"body": "Gasté $50 en almuerzo hoy"},
                                            "type": "text"
                                        }
                                    ]
                                },
                                "field": "messages"
                            }
                        ]
                    }
                ]
            }
            
            response = await client.post(
                f"{base_url}/webhook/cloud",
                json=webhook_payload
            )
            print(f"   OK Webhook Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ERROR: {e}")
        print()

if __name__ == "__main__":
    # Verificar que el servidor esté corriendo
    print("=== INICIANDO PRUEBAS DE KOREI ASSISTANT ===")
    print("Servidor deberia estar corriendo en localhost:8000")
    print()
    
    asyncio.run(test_app())