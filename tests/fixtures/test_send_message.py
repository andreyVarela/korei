#!/usr/bin/env python3
"""
Test envío directo de mensaje usando exactamente la misma configuración
"""
import httpx
import asyncio
from app.config import get_settings

async def test_send_message():
    settings = get_settings()
    token = settings.whatsapp_access_token.strip()
    phone_id = settings.whatsapp_phone_number_id
    
    print(f"Testing message send:")
    print(f"Token: {token[:50]}...")
    print(f"Phone ID: {phone_id}")
    
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": "50660052300",
        "type": "text",
        "text": {"body": "¡Hola! Test directo desde Python - Token del sistema funcionando!"}
    }
    
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                print("SUCCESS: Mensaje enviado!")
            else:
                print("FAILED: Error enviando mensaje")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_send_message())