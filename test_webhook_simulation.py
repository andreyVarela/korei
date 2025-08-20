"""
Simular exactamente el proceso de webhook de imagen para probar la corrección
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes.webhook import process_image_message
from core.supabase import supabase

async def test_webhook_simulation():
    """Simular webhook de imagen exactamente como en el código real"""
    try:
        print("=" * 50)
        print("TEST: Simulando webhook de imagen completo")
        print("=" * 50)
        
        # Obtener contexto del usuario
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        print(f"Usuario: {user_context.get('name', 'Usuario')}")
        print(f"ID: {user_context.get('id', 'Sin ID')}")
        print(f"Tel: {user_context.get('whatsapp_number', 'Sin telefono')}")
        
        # Simular payload de imagen (como viene de WAHA)
        payload = {
            "id": "test_message_id_12345",
            "timestamp": 1692289720,
            "from": f"{test_phone}@c.us",
            "type": "image",
            "caption": "",
            "notifyName": "Test User"
        }
        
        print(f"\nPayload simulado:")
        print(f"  ID: {payload['id']}")
        print(f"  Tipo: {payload['type']}")
        print(f"  De: {payload['from']}")
        
        # Ejecutar el proceso completo de imagen
        print(f"\nEjecutando process_image_message...")
        
        await process_image_message(payload, user_context, "")
        
        print(f"\nProceso completado exitosamente!")
        print(f"Revisa los logs del servidor para ver:")
        print(f"  1. Tipo devuelto por Gemini")
        print(f"  2. Mensaje formateado")
        print(f"  3. Respuesta enviada")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_webhook_simulation())