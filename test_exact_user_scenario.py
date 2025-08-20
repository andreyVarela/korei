"""
Test exacto del escenario del usuario
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service
from services.formatters import message_formatter
from core.supabase import supabase

async def test_exact_scenario():
    """Test del escenario exacto del usuario"""
    try:
        print("TEST: Escenario exacto del usuario")
        print("=" * 50)
        
        # Usuario real
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Contexto exacto que reportó el usuario
        exact_context = "Veo una captura de pantalla de una notificacion de transaccion SINPE Movil del Banco de Costa Rica. Transferencia SINPE Movil a ANDREI ANTONIO VARELA SOLANO por 10,000.00 CRC. Ref: 2025081715284001625138542. Motivo: Transferencia SINPE."
        
        print("1. Procesando imagen con contexto exacto...")
        
        # Simular datos de imagen
        fake_image_data = b"fake_image_data"
        
        # Usar el método exacto del pipeline de imagen
        result = await gemini_service.process_image(fake_image_data, exact_context, user_context)
        
        print("2. RESULTADO DE GEMINI:")
        print(f"   Tipo: {result.get('type')}")
        print(f"   Descripcion: {result.get('description', '')}")
        print(f"   Monto: {result.get('amount')}")
        print()
        
        print("3. FORMATEANDO RESPUESTA...")
        formatted_response = message_formatter.format_entry_response(result)
        
        print("4. RESPUESTA FORMATEADA:")
        # Limpiar caracteres especiales para mostrar
        clean_response = formatted_response.encode('ascii', 'ignore').decode('ascii')
        print(clean_response)
        print()
        
        print("5. ANÁLISIS:")
        if result.get('type') == 'ingreso':
            print("   Gemini clasifico como: INGRESO (CORRECTO)")
            if "Ingreso:" in formatted_response:
                print("   Formato muestra: INGRESO (CORRECTO)")
                print("   CONCLUSION: El sistema funciona correctamente")
            else:
                print("   Formato muestra: GASTO (PROBLEMA EN FORMATEADOR)")
        else:
            print("   Gemini clasifico como: GASTO (PROBLEMA EN GEMINI)")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_exact_scenario())