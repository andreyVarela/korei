#!/usr/bin/env python3
"""
Simple test to check the format_entry_response function directly
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_format_response():
    """Test the format_entry_response function directly"""
    
    print("=" * 60)
    print("PRUEBA SIMPLE DE FORMATO DE RESPUESTA")
    print("=" * 60)
    
    try:
        from services.formatters import message_formatter
        
        # Mock Gemini response (similar to what we'd get from a SINPE transaction)
        mock_gemini_result = {
            "type": "expense",
            "description": "Compra en DELTA MORAVIA SAN JOSE CR - SINPE Movil",
            "amount": 10000.00,
            "datetime": "2025-08-18T22:30:00",
            "priority": "medium",
            "category": "purchases",
            "merchant": "DELTA MORAVIA SAN JOSE CR",
            "transaction_id": "123456789",
            "payment_method": "SINPE Movil"
        }
        
        print(f"STEP 1: Datos de entrada:")
        for key, value in mock_gemini_result.items():
            print(f"  {key}: {value}")
        
        print(f"\nSTEP 2: Intentando formatear respuesta...")
        
        # Test the format function directly
        formatted_response = message_formatter.format_entry_response(mock_gemini_result)
        
        print(f"STEP 3: SUCCESS!")
        print(f"Longitud de respuesta: {len(formatted_response)} caracteres")
        print(f"\nSTEP 4: Respuesta formateada:")
        print("-" * 40)
        print(formatted_response)
        print("-" * 40)
        
        print(f"\nTEST COMPLETO: OK")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_format_response()