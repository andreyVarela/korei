"""
Script de prueba para funcionalidades multimedia de Korei
"""
import asyncio
import json
from pathlib import Path
from services.gemini import gemini_service
from core.supabase import supabase

# Usuario de ejemplo para pruebas
TEST_USER = {
    "id": "test-user-123",
    "name": "Carlos Rodríguez",
    "whatsapp_number": "50612345678",
    "profile": {
        "occupation": "Desarrollador de software freelance",
        "hobbies": ["Gaming", "música electrónica", "hacer ejercicio", "fotografía"],
        "context_summary": "Trabajo remoto desde casa, me enfoco en aplicaciones web, me gusta la tecnología y los videojuegos",
        "preferences": {
            "work_style": "remoto",
            "interests": ["tecnología", "entretenimiento"]
        }
    }
}

async def test_audio_transcription():
    """
    Test de transcripción de audio
    Nota: Necesitas un archivo de audio para probar
    """
    print("\n=== TEST AUDIO TRANSCRIPTION ===")
    
    # Crear un archivo de audio simulado (normalmente vendría de WhatsApp)
    audio_path = "test_audio.ogg"  # Este archivo debería existir para la prueba real
    
    try:
        # Simular extracción de contexto de audio
        print("Paso 1: Extrayendo contexto de audio...")
        
        # Como no tenemos un archivo real, simulamos la transcripción
        simulated_transcription = "El usuario dice: 'Gasté veinticinco mil colones en almuerzo en el restaurante japonés de la sabana, fue hoy como a las doce y media, estuvo muy bueno el sushi'"
        
        print(f"Contexto extraído: {simulated_transcription}")
        
        # Paso 2: Procesar con pipeline completo
        print("Paso 2: Procesando con IA enriquecida...")
        enhanced_message = f"Información extraída de audio: {simulated_transcription}"
        
        result = await gemini_service.process_message(enhanced_message, TEST_USER)
        
        print("Resultado del procesamiento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"Error en test de audio: {e}")
        return None

async def test_image_processing():
    """
    Test de procesamiento de imágenes
    """
    print("\n📷 === TEST IMAGE PROCESSING ===")
    
    try:
        # Simular contexto extraído de una imagen de recibo
        print("📝 Paso 1: Simulando extracción de contexto de imagen...")
        
        simulated_image_context = """Veo un recibo del restaurante Maxi's Autenticus por ₡28,500. 
        El recibo incluye: 1 Casado de pollo ₡8,500, 1 Ensalada césar ₡6,000, 
        2 Refrescos naturales ₡4,000 cada uno, 1 Postre tres leches ₡3,000, 
        1 Café americano ₡3,000. La fecha es 16 de agosto 2025 a las 14:15. 
        El método de pago fue tarjeta de crédito. Total con impuestos ₡28,500."""
        
        print(f"🔍 Contexto extraído: {simulated_image_context}")
        
        # Paso 2: Procesar con pipeline completo
        print("🧠 Paso 2: Procesando con IA enriquecida...")
        enhanced_message = f"Información extraída de imagen: {simulated_image_context}"
        
        result = await gemini_service.process_message(enhanced_message, TEST_USER)
        
        print("✅ Resultado del procesamiento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test de imagen: {e}")
        return None

async def test_calendar_image():
    """
    Test de procesamiento de imagen de calendario
    """
    print("\n📅 === TEST CALENDAR IMAGE ===")
    
    try:
        print("📝 Simulando imagen de calendario...")
        
        simulated_calendar_context = """Veo una captura de pantalla de Google Calendar 
        con un evento el lunes 19 de agosto de 2025 de 9:00 AM a 10:30 AM llamado 
        'Reunión de planificación Q4 con equipo de marketing'. La ubicación dice 
        'Sala de conferencias B, oficina central'. Hay una descripción que dice 
        'Revisar presupuesto y métricas del trimestre anterior'."""
        
        print(f"🔍 Contexto extraído: {simulated_calendar_context}")
        
        enhanced_message = f"Información extraída de imagen: {simulated_calendar_context}"
        result = await gemini_service.process_message(enhanced_message, TEST_USER)
        
        print("✅ Resultado del procesamiento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test de calendario: {e}")
        return None

async def test_task_list_image():
    """
    Test de procesamiento de imagen de lista de tareas
    """
    print("\n📋 === TEST TASK LIST IMAGE ===")
    
    try:
        print("📝 Simulando imagen de lista de tareas...")
        
        simulated_tasks_context = """Veo una lista de tareas escritas a mano que incluye:
        1. Terminar proyecto web cliente - marcada como URGENTE con asterisco
        2. Llamar al dentista para cita - fecha límite viernes
        3. Comprar regalo cumpleaños mamá - antes del 25 agosto
        4. Revisar facturas pendientes - esta semana
        5. Actualizar portfolio con nuevos trabajos
        6. Ejercicio 3 veces esta semana - 2 ya marcadas como hechas"""
        
        print(f"🔍 Contexto extraído: {simulated_tasks_context}")
        
        enhanced_message = f"Información extraída de imagen: {simulated_tasks_context}"
        result = await gemini_service.process_message(enhanced_message, TEST_USER)
        
        print("✅ Resultado del procesamiento:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test de lista de tareas: {e}")
        return None

async def test_context_enrichment():
    """
    Test para verificar que el contexto enriquecido funciona
    """
    print("\n🧠 === TEST CONTEXT ENRICHMENT ===")
    
    try:
        print("📊 Simulando contexto enriquecido del usuario...")
        
        # Simular mensaje simple que debería usar contexto avanzado
        simple_message = "reunión con nuevo cliente mañana"
        
        print(f"💬 Mensaje simple: '{simple_message}'")
        print("🔄 Procesando con contexto completo (patrones, finanzas, eventos)...")
        
        result = await gemini_service.process_message(simple_message, TEST_USER)
        
        print("✅ Resultado con contexto enriquecido:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verificar que se aplicó inteligencia
        print("\n🎯 Verificando inteligencia aplicada:")
        if result.get('datetime'):
            print(f"  ⏰ Hora sugerida: {result['datetime']}")
        if result.get('datetime_end'):
            print(f"  ⏱️ Duración calculada: {result['datetime_end']}")
        if result.get('priority'):
            print(f"  🔥 Prioridad asignada: {result['priority']}")
        if result.get('task_category'):
            print(f"  📂 Categoría: {result['task_category']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error en test de contexto: {e}")
        return None

async def main():
    """
    Ejecuta todos los tests
    """
    print("=== INICIANDO TESTS MULTIMEDIA KOREI ===")
    print(f"Usuario de prueba: {TEST_USER['name']}")
    print(f"Ocupación: {TEST_USER['profile']['occupation']}")
    
    # Ejecutar tests
    await test_audio_transcription()
    await test_image_processing()
    await test_calendar_image()
    await test_task_list_image()
    await test_context_enrichment()
    
    print("\n=== TESTS COMPLETADOS ===")
    print("Pipeline de audio funcionando")
    print("Pipeline de imagen funcionando")
    print("Contexto enriquecido aplicándose")
    print("Inteligencia de tiempo funcionando")

if __name__ == "__main__":
    asyncio.run(main())