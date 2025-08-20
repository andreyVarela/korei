#!/usr/bin/env python3
"""
Test script to debug image processing step by step
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import MessageHandler
from core.supabase import supabase
from services.formatters import message_formatter

async def test_image_processing():
    """Test the complete image processing flow step by step"""
    
    print("=" * 60)
    print("INICIANDO DEBUG DE PROCESAMIENTO DE IMÁGENES")
    print("=" * 60)
    
    # Mock user data (simulate a registered user) - use valid UUID format
    mock_user = {
        'id': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        'whatsapp_number': '+50688888888',
        'name': 'Test User',
        'is_premium': True,
        'has_access': True,
        'profile': {'name': 'Test User', 'occupation': 'Developer'}
    }
    
    # Mock image data (simulate SINPE transaction image)
    mock_image_data = {
        'id': 'test-image-123',
        'media_url': 'https://example.com/test-image.jpg',
        'mime_type': 'image/jpeg',
        'sha256': 'abc123',
        'file_size': 150000
    }
    
    print(f"STEP 1: Inicializando MessageHandler")
    handler = MessageHandler()
    
    print(f"STEP 2: Verificando usuario mock: {mock_user['whatsapp_number']}")
    
    try:
        print(f"STEP 3: Verificando acceso del usuario...")
        user_verification = await handler.verify_user_and_payment(mock_user)
        print(f"STEP 3 RESULT: Valid={user_verification.get('is_valid', False)}")
        
        if not user_verification['is_valid']:
            print("ERROR: Usuario no valido")
            print(f"Detalles de error: {user_verification.get('message', 'Sin mensaje')}")
            return
            
        print(f"OK STEP 3 PASSED: Usuario verificado correctamente")
        
        print(f"STEP 4: Simulando procesamiento de imagen...")
        
        # Test the format_entry_response function directly
        print(f"STEP 5: Probando formato de respuesta...")
        
        # Mock Gemini response (similar to what we'd get from a SINPE transaction)
        mock_gemini_result = {
            "type": "expense",
            "description": "Compra en DELTA MORAVIA SAN JOSE CR - SINPE Móvil",
            "amount": 10000.00,
            "datetime": "2025-08-18T22:30:00",
            "priority": "medium",
            "category": "purchases",
            "merchant": "DELTA MORAVIA SAN JOSE CR",
            "transaction_id": "123456789",
            "payment_method": "SINPE Móvil"
        }
        
        print(f"STEP 6: Resultado mock de Gemini: {mock_gemini_result}")
        
        try:
            print(f"STEP 7: Intentando formatear respuesta...")
            formatted_response = message_formatter.format_entry_response(mock_gemini_result)
            print(f"STEP 7 SUCCESS: Respuesta formateada: {len(formatted_response)} caracteres")
            print(f"RESPUESTA PREVIEW: {formatted_response[:200]}...")
            
        except Exception as format_error:
            print(f"ERROR STEP 7: Error al formatear respuesta: {format_error}")
            import traceback
            traceback.print_exc()
            return
            
        print(f"STEP 8: Simulando guardado en base de datos...")
        
        # Test database save operation
        try:
            entry_data = {
                "user_id": mock_user['id'],
                "type": mock_gemini_result["type"],
                "description": mock_gemini_result["description"],
                "amount": mock_gemini_result["amount"],
                "datetime": mock_gemini_result["datetime"],
                "category": mock_gemini_result.get("category", "general"),
                "priority": mock_gemini_result.get("priority", "medium"),
                "created_by": "whatsapp_image"
            }
            
            print(f"STEP 8A: Datos a guardar: {entry_data}")
            
            # Note: We're not actually saving to avoid test data pollution
            print(f"STEP 8B: OK Simulacion de guardado exitosa (no se guardo realmente)")
            
        except Exception as db_error:
            print(f"ERROR STEP 8: Error en simulacion de base de datos: {db_error}")
            import traceback
            traceback.print_exc()
            
        print(f"STEP 9: OK PROCESAMIENTO COMPLETO EXITOSO")
        print(f"Respuesta final seria: {formatted_response}")
        
    except Exception as e:
        print(f"ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("DEBUG COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_image_processing())