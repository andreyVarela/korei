"""
Verificación simple sin emojis
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service
from services.formatters import message_formatter
from core.supabase import supabase

async def verify_simple():
    """Verificación simple sin emojis"""
    try:
        print("VERIFICACION: Problema SINPE ingreso vs gasto")
        print("=" * 50)
        
        # Usuario test
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Contexto SINPE del problema
        sinpe_context = "Veo una captura de pantalla de una notificacion de transaccion SINPE Movil del Banco de Costa Rica. La notificacion indica que se realizo una Transferencia SINPE Movil a ANDREI ANTONIO VARELA SOLANO por 10,000.00 CRC. Referencia: 2025081715284001625138542. Motivo: Transferencia SINPE."
        
        print(f"\nProcesando contexto SINPE...")
        
        # Procesar con Gemini
        fake_image = b"test"
        result = await gemini_service.process_image(fake_image, sinpe_context, user_context)
        
        print(f"\nGEMINI DEVOLVIO:")
        print(f"  Tipo: {result.get('type')}")
        print(f"  Monto: {result.get('amount')}")
        
        # Formatear con método CORREGIDO
        formatted = message_formatter.format_entry_response(result)
        
        print(f"\nFORMATEADO:")
        print("-" * 30)
        print(formatted.encode('ascii', 'ignore').decode('ascii'))  # Sin caracteres especiales
        print("-" * 30)
        
        # Análisis
        print(f"\nANALISIS:")
        if "Ingreso:" in formatted:
            print("EXITO: Muestra 'Ingreso:' - PROBLEMA RESUELTO")
        elif "Gasto:" in formatted:
            print("ERROR: Muestra 'Gasto:' - PROBLEMA PERSISTE")
        else:
            print("ADVERTENCIA: Formato inesperado")
            
        print(f"\nGemini tipo: {result.get('type')}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_simple())