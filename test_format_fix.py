"""
Test para verificar la corrección del formateador
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service
from services.formatters import message_formatter
from core.supabase import supabase

async def test_format_fix():
    """Test para verificar que el formateador funcione correctamente"""
    try:
        print("=" * 50)
        print("TEST: Verificando corrección del formateador")
        print("=" * 50)
        
        # Obtener contexto del usuario
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Simular procesamiento de imagen SINPE
        user_name_full = user_context.get('name', 'Usuario')
        simulated_context = f"""Veo una notificación de transacción SINPE Móvil del Banco de Costa Rica. La notificación indica que se realizó una Transferencia SINPE Móvil a {user_name_full.upper()} por 10,000.00 colones. Motivo: Transferencia SINPE. Ref: 2025081715284001625138542"""
        
        # Procesar con Gemini
        fake_image_data = b"fake_image_data_placeholder"
        result = await gemini_service.process_image(fake_image_data, simulated_context, user_context)
        
        print(f"\nRESULTADO DE GEMINI:")
        print(f"  Tipo: {result.get('type')}")
        print(f"  Descripción: {result.get('description', '')[:80]}...")
        print(f"  Monto: {result.get('amount')}")
        
        # Probar el formateador CORREGIDO
        print(f"\nUSANDO EL MÉTODO CORRECTO:")
        try:
            formatted_message = message_formatter.format_entry_response(result)
            print(f"RESPUESTA FORMATEADA:")
            print("-" * 30)
            print(formatted_message)
            print("-" * 30)
            
            # Verificar que contenga el emoji correcto
            if "💰 Ingreso:" in formatted_message:
                print("SUCCESS: Contiene '💰 Ingreso:' - CORRECTO")
            elif "💸 Gasto:" in formatted_message:
                print("ERROR: Contiene '💸 Gasto:' - INCORRECTO")
            else:
                print("ADVERTENCIA: No contiene emoji de monto específico")
                
        except Exception as format_error:
            print(f"ERROR en formato: {format_error}")
        
        # Probar el método INCORRECTO anterior para confirmar el problema
        print(f"\nUSANDO EL MÉTODO INCORRECTO (para comparar):")
        try:
            # Intentar llamar al método que no existe
            incorrect_result = message_formatter.format_response(result)
            print(f"Resultado método incorrecto: {incorrect_result}")
        except AttributeError as e:
            print(f"CONFIRMADO: El método 'format_response' no existe: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_format_fix())