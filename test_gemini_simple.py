"""
Test simple para capturar JSON de Gemini sin problemas de encoding
"""
import asyncio
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.name_matcher import name_matcher
from services.gemini import gemini_service
from core.supabase import supabase

async def test_gemini_simple():
    """Test simple sin emojis ni caracteres especiales"""
    try:
        print("=" * 50)
        print("TEST: Capturando JSON de Gemini")
        print("=" * 50)
        
        # Usuario test
        test_phone = "50660052300"
        user_context = await supabase.get_user_with_context(test_phone)
        
        # Simular contexto SINPE exacto del problema
        image_context = "Veo una captura de pantalla de una notificacion de transaccion SINPE Movil del Banco de Costa Rica. La notificacion indica que se realizo una Transferencia SINPE Movil a ANDREI ANTONIO VARELA SOLANO por 10,000.00 CRC. Referencia: 2025081715284001625138542. Motivo: Transferencia SINPE."
        
        print("\nContexto de imagen:")
        print(image_context)
        
        # Análisis inteligente
        user_name = "Andrei Varela Solano"  # Hardcoded para evitar encoding
        analysis = name_matcher.analyze_transaction_direction(image_context, user_name)
        
        print(f"\nAnalisis inteligente:")
        print(f"  Tipo: {analysis['type']}")
        print(f"  Confianza: {analysis['confidence']:.1%}")
        
        # Construir mensaje para Gemini
        enhanced_message = f"Informacion extraida de imagen: {image_context}"
        
        if analysis and analysis.get('type'):
            enhanced_message += f"\n\nANALISIS INTELIGENTE DE TRANSACCION:"
            enhanced_message += f"\n- Tipo detectado: {analysis['type'].upper()} (confianza: {analysis['confidence']:.1%})"
            enhanced_message += f"\n- Razonamiento: {', '.join(analysis['reasoning'])}"
        
        print(f"\nMensaje para Gemini:")
        print("-" * 40)
        print(enhanced_message)
        print("-" * 40)
        
        # INTERCEPTAR RESPUESTA DE GEMINI
        original_extract = gemini_service._extract_json
        
        captured_raw = None
        captured_json = None
        
        def intercept_json(text):
            nonlocal captured_raw, captured_json
            captured_raw = text
            
            print(f"\n*** RESPUESTA RAW DE GEMINI ***")
            print(text)
            print("*** FIN RESPUESTA RAW ***")
            
            result = original_extract(text)
            captured_json = result
            
            print(f"\n*** JSON PROCESADO ***")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("*** FIN JSON ***")
            
            return result
        
        gemini_service._extract_json = intercept_json
        
        try:
            # Procesar con Gemini
            fake_image = b"test"
            result = await gemini_service.process_image(fake_image, enhanced_message, user_context)
            
            print(f"\n*** RESULTADO FINAL ***")
            print(f"Tipo final: {result.get('type')}")
            print(f"Descripcion: {result.get('description', '')}")
            print(f"Monto: {result.get('amount')}")
            
            # ANÁLISIS
            print(f"\n*** ANALISIS DEL PROBLEMA ***")
            print(f"Analisis inteligente: {analysis['type']}")
            print(f"Gemini devolvio: {result.get('type')}")
            
            if analysis['type'] == 'ingreso' and result.get('type') == 'gasto':
                print("PROBLEMA ENCONTRADO: Gemini ignora el analisis")
            elif analysis['type'] == result.get('type'):
                print("TODO CORRECTO: Coinciden")
            else:
                print("DISCREPANCIA DETECTADA")
                
        finally:
            gemini_service._extract_json = original_extract
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_simple())