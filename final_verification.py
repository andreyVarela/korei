"""
Verificación final del problema reportado por el usuario
"""
import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service
from services.formatters import message_formatter
from core.supabase import supabase

async def final_verification():
    """Verificación final paso a paso del problema reportado"""
    print("=" * 60)
    print("VERIFICACION FINAL: Problema reportado por el usuario")
    print("=" * 60)
    
    try:
        # PASO 1: Recrear el contexto EXACTO del usuario
        print("\nPASO 1: Recreando contexto exacto del usuario")
        
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # El contexto exacto que ve el usuario según su reporte
        exact_context = """🔍 *Contexto extraído:* Veo una captura de pantalla de una notificación de transacción SINPE Móvil del Banco de Costa Rica. La notificación indica que se realizó una Transferencia SINPE Móvil a ANDREI ANTONIO VARELA SOLANO por 10,000.00 CRC. Referencia: 2025081715284001625138542. Motivo: Transferencia SINPE."""
        
        print(f"Contexto del usuario: {exact_context}")
        
        # PASO 2: Procesar con Gemini (sin interceptar para ver resultado real)
        print("\nPASO 2: Procesando con Gemini...")
        
        fake_image = b"test_data"
        result = await gemini_service.process_image(fake_image, exact_context, user_context)
        
        print(f"RESULTADO DE GEMINI:")
        print(f"  Tipo: {result.get('type')}")
        print(f"  Descripcion: {result.get('description', '')}") 
        print(f"  Monto: {result.get('amount')}")
        print(f"  Categoria: {result.get('category', 'Sin categoria')}")
        
        # PASO 3: Usar el formateador CORREGIDO
        print(f"\nPASO 3: Formateando con método CORREGIDO...")
        
        formatted_message = message_formatter.format_entry_response(result)
        
        print(f"MENSAJE FORMATEADO:")
        print("=" * 40)
        print(formatted_message)
        print("=" * 40)
        
        # PASO 4: Análisis del resultado vs problema reportado
        print(f"\nPASO 4: ANÁLISIS vs PROBLEMA REPORTADO")
        
        user_reported_seeing = "💸 Gasto: ₡10.000"
        should_see = "💰 Ingreso: ₡10.000"
        
        print(f"Usuario reportó ver: '{user_reported_seeing}'")
        print(f"Debería ver: '{should_see}'")
        
        if "💰 Ingreso:" in formatted_message:
            print("✅ PROBLEMA RESUELTO: Ahora muestra '💰 Ingreso:' correctamente")
        elif "💸 Gasto:" in formatted_message:
            print("❌ PROBLEMA PERSISTE: Aún muestra '💸 Gasto:' incorrectamente")
        else:
            print("⚠️ RESULTADO INESPERADO: No contiene emoji de monto esperado")
        
        # PASO 5: Verificar el JSON completo
        print(f"\nPASO 5: JSON COMPLETO PARA DEPURACIÓN")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(final_verification())