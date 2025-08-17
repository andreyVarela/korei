"""
Simple test para verificar que 'hola' no se procese como tarea
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import message_handler

async def test_hola_intent():
    """Test específico para el problema reportado: 'hola' como tarea"""
    print("TEST: Verificar que 'hola' no se procese como tarea")
    print("=" * 50)
    
    # Usuario de prueba
    user_context = {
        "id": "test-user-123",
        "whatsapp_number": "50612345678",
        "name": "Usuario Test"
    }
    
    # Mock para evitar envíos reales
    mock_responses = []
    async def mock_send_message(to, message):
        mock_responses.append({"to": to, "message": message})
        print(f"Mock response sent: {message}")
        return {"success": True}
    
    # Aplicar mock
    try:
        from services.whatsapp_cloud import whatsapp_cloud_service
        whatsapp_cloud_service.send_text_message = mock_send_message
    except Exception as e:
        print(f"Warning: Could not mock WhatsApp service: {e}")
    
    # TEST PRINCIPAL: ¿'hola' se detecta como saludo?
    print("\n1. Testing 'hola' input...")
    result = await message_handler.detect_user_intent("hola", user_context)
    
    print(f"Result type: {result.get('type', 'unknown')}")
    print(f"Should handle directly: {result.get('should_handle_directly', False)}")
    
    if result.get('should_handle_directly', False):
        print("SUCCESS: 'hola' se maneja como saludo (NO como tarea)")
        print("El problema reportado por el usuario ESTA RESUELTO")
    else:
        print("FAILED: 'hola' se enviaria a Gemini como tarea")
        print("El problema reportado por el usuario AUN EXISTE")
    
    # Test casos adicionales críticos
    test_cases = ["Hola", "hello", "help", "gracias", "ok"]
    
    print(f"\n2. Testing additional cases...")
    for case in test_cases:
        result = await message_handler.detect_user_intent(case, user_context)
        handled = result.get('should_handle_directly', False)
        print(f"'{case}' -> handled directly: {handled}")
    
    # Test contenido real
    print(f"\n3. Testing real content (should go to Gemini)...")
    real_content = "necesito comprar leche mañana"
    result = await message_handler.detect_user_intent(real_content, user_context)
    handled = result.get('should_handle_directly', False)
    print(f"'{real_content}' -> handled directly: {handled}")
    if not handled:
        print("GOOD: Real content will be processed by Gemini")
    else:
        print("ISSUE: Real content was filtered incorrectly")
    
    print(f"\nMock responses generated: {len(mock_responses)}")
    for i, response in enumerate(mock_responses, 1):
        print(f"{i}. {response['message']}")

if __name__ == "__main__":
    print("SIMPLE INTENT DETECTION TEST")
    print("Verificando el problema específico del usuario:")
    print("'si agrego hola, lo agrega como tarea'")
    print()
    
    asyncio.run(test_hola_intent())