"""
Test específico para verificar que el audio transcribe correctamente "gasto"
"""
import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gemini import gemini_service

# Usuario de prueba
TEST_USER = {
    "id": "test-user-123",
    "name": "Carlos Rodriguez",
    "whatsapp_number": "50612345678",
    "profile": {
        "occupation": "Desarrollador de software freelance",
        "preferences": {"work_style": "remoto"}
    }
}

async def test_problematic_audio():
    """
    Test del problema específico reportado:
    Usuario dice "gasto" pero se guarda como tarea de "procesar archivo audio"
    """
    print("=== TEST PROBLEMA ESPECÍFICO DE AUDIO ===")
    
    # Simular diferentes variaciones de lo que el usuario podría haber dicho
    test_cases = [
        "Gasté quince mil colones en almuerzo",
        "Tuve un gasto de quince mil colones en comida",
        "Pagué quince mil colones por almuerzo",
        "Compré almuerzo por quince mil colones",
        "Salió quince mil colones el almuerzo",
        "El almuerzo me costó quince mil colones"
    ]
    
    for i, audio_transcription in enumerate(test_cases, 1):
        print(f"\n--- Caso {i}: '{audio_transcription}' ---")
        
        # Simular el pipeline de audio
        enhanced_message = f"Información extraída de audio: {audio_transcription}"
        
        print(f"Mensaje enviado al procesador: {enhanced_message}")
        
        try:
            result = await gemini_service.process_message(enhanced_message, TEST_USER)
            
            # Verificar que se categorice correctamente
            expected_type = "gasto"
            actual_type = result.get('type')
            
            print(f"Tipo detectado: {actual_type}")
            print(f"Descripcion: {result.get('description')}")
            print(f"Monto: {result.get('amount')}")
            
            if actual_type == expected_type:
                print(f"CORRECTO: Se detecto como '{expected_type}'")
            else:
                print(f"ERROR: Se detecto como '{actual_type}', esperaba '{expected_type}'")
                
        except Exception as e:
            print(f"Error procesando: {e}")
        
        print("-" * 50)

async def test_bad_transcription_simulation():
    """
    Test simulando transcripción deficiente que podría causar el problema
    """
    print("\n=== TEST TRANSCRIPCIÓN DEFICIENTE ===")
    
    # Simular transcripciones pobres que podrían confundir al sistema
    bad_transcriptions = [
        "proceso archivo de audio del usuario",  # Lo que reportaste que pasó
        "audio recibido del usuario para procesar",
        "usuario envió audio mensaje",
        "gastos en proceso archivo usuario",  # Mezcla confusa
    ]
    
    for i, bad_transcription in enumerate(bad_transcriptions, 1):
        print(f"\n--- Transcripción mala {i}: '{bad_transcription}' ---")
        
        enhanced_message = f"Información extraída de audio: {bad_transcription}"
        
        try:
            result = await gemini_service.process_message(enhanced_message, TEST_USER)
            
            print(f"Tipo detectado: {result.get('type')}")
            print(f"Descripcion: {result.get('description')}")
            
            # Estas deberían ser rechazadas o manejadas mejor
            if result.get('type') == 'tarea' and 'procesar' in result.get('description', '').lower():
                print("PROBLEMA DETECTADO: Se categorizo como tarea de procesamiento")
            else:
                print("Manejado correctamente")
                
        except Exception as e:
            print(f"Error: {e}")

async def main():
    print("=== TESTING AUDIO TRANSCRIPTION FIXES ===")
    await test_problematic_audio()
    await test_bad_transcription_simulation()
    print("\n=== TEST COMPLETADO ===")
    print("Verifica que los gastos se detecten correctamente y las transcripciones malas se manejen bien")

if __name__ == "__main__":
    asyncio.run(main())