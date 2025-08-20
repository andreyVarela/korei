"""
Test con análisis de texto directo (simulando análisis inteligente funcionando)
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service
from services.formatters import message_formatter
from services.name_matcher import name_matcher
from core.supabase import supabase

async def test_text_analysis():
    """Test procesando directamente como texto con análisis inteligente"""
    try:
        print("TEST: Procesamiento directo como texto con analisis inteligente")
        print("=" * 60)
        
        # Usuario test
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        user_name = "Andrei Varela Solano"  # Hardcoded para evitar encoding
        
        # Contexto SINPE exacto
        sinpe_context = "Veo una captura de pantalla de una notificacion de transaccion SINPE Movil del Banco de Costa Rica. La notificacion indica que se realizo una Transferencia SINPE Movil a ANDREI ANTONIO VARELA SOLANO por 10,000.00 CRC. Referencia: 2025081715284001625138542. Motivo: Transferencia SINPE."
        
        print(f"\nContexto SINPE:")
        print(sinpe_context)
        
        # STEP 1: Análisis inteligente manual
        print(f"\nSTEP 1: Ejecutando analisis inteligente...")
        analysis = name_matcher.analyze_transaction_direction(sinpe_context, user_name)
        
        print(f"Analisis inteligente:")
        print(f"  Tipo: {analysis['type']}")
        print(f"  Confianza: {analysis['confidence']:.1%}")
        print(f"  Razonamiento: {analysis['reasoning']}")
        
        # STEP 2: Construir mensaje con análisis para Gemini
        enhanced_message = f"Informacion extraida de imagen: {sinpe_context}"
        
        if analysis and analysis.get('type'):
            enhanced_message += f"\n\nANALISIS INTELIGENTE DE TRANSACCION:"
            enhanced_message += f"\n- Tipo detectado: {analysis['type'].upper()} (confianza: {analysis['confidence']:.1%})"
            enhanced_message += f"\n- Razonamiento: {', '.join(analysis['reasoning'])}"
        
        print(f"\nSTEP 2: Mensaje con analisis para Gemini:")
        print("-" * 40)
        print(enhanced_message)
        print("-" * 40)
        
        # STEP 3: Procesar con Gemini como TEXTO (no imagen)
        print(f"\nSTEP 3: Procesando con Gemini como TEXTO...")
        result = await gemini_service.process_message(enhanced_message, user_context)
        
        print(f"\nGEMINI RESULTADO:")
        print(f"  Tipo: {result.get('type')}")
        print(f"  Monto: {result.get('amount')}")
        
        # STEP 4: Formatear
        print(f"\nSTEP 4: Formateando...")
        formatted = message_formatter.format_entry_response(result)
        
        print(f"RESULTADO FORMATEADO:")
        print("-" * 30)
        print(formatted.encode('ascii', 'ignore').decode('ascii'))
        print("-" * 30)
        
        # STEP 5: Análisis final
        print(f"\nSTEP 5: VERIFICACION FINAL")
        print(f"Analisis inteligente: {analysis['type']}")
        print(f"Gemini devolvio: {result.get('type')}")
        
        if analysis['type'] == 'ingreso' and result.get('type') == 'ingreso':
            print("EXITO: Todo el pipeline funciona correctamente")
        elif analysis['type'] == 'ingreso' and result.get('type') == 'gasto':
            print("PROBLEMA: Gemini ignora el analisis inteligente")
        else:
            print(f"CASO INESPERADO: {analysis['type']} -> {result.get('type')}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_text_analysis())