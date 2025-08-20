#!/usr/bin/env python3
"""
Test to validate that format_entry_response works correctly
"""
import sys
import os
import json

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_format_validation():
    """Test that the format_entry_response function works correctly"""
    
    print("=" * 60)
    print("VALIDACION DE FORMATO DE RESPUESTA")
    print("=" * 60)
    
    try:
        from services.formatters import message_formatter
        
        # Mock Gemini response (similar to what we'd get from a SINPE transaction)
        test_data = {
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
        
        print("STEP 1: Datos de entrada preparados")
        print("STEP 2: Probando format_entry_response...")
        
        # Test the format function directly
        formatted_response = message_formatter.format_entry_response(test_data)
        
        # Validation checks
        success = True
        errors = []
        
        # Check that we got a string response
        if not isinstance(formatted_response, str):
            success = False
            errors.append(f"Esperaba string, obtuve {type(formatted_response)}")
        
        # Check that the response has content
        if len(formatted_response) == 0:
            success = False
            errors.append("Respuesta vacia")
        
        # Always save response to file first to check content
        with open("test_response_output.txt", "w", encoding="utf-8") as f:
            f.write(formatted_response)
        print("Respuesta guardada en: test_response_output.txt")
        
        # Check that response contains expected elements
        expected_elements = ["10000", "DELTA", "expense"]
        for element in expected_elements:
            if element not in formatted_response:
                success = False
                errors.append(f"Falta elemento esperado: {element}")
        
        print("STEP 3: Validaciones completadas")
        
        if success:
            print("RESULTADO: SUCCESS")
            print(f"Longitud de respuesta: {len(formatted_response)} caracteres")
            print("Contiene todos los elementos esperados")
            
        else:
            print("RESULTADO: ERROR")
            for error in errors:
                print(f"  - {error}")
            print(f"Contenido real (primeros 100 chars):")
            # Show safe ASCII version of first 100 characters
            safe_content = ''.join(c if ord(c) < 128 else '?' for c in formatted_response[:100])
            print(f"  '{safe_content}'")
        
        return success
        
    except Exception as e:
        print(f"ERROR CRITICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_format_validation()
    print("=" * 60)
    print(f"TEST FINAL: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)