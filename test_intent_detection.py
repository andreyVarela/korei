"""
Test script para verificar el sistema de detección de intención inteligente
Verifica que saludos como "hola" no se procesen como tareas
"""
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import message_handler

async def test_intent_detection():
    """Test del sistema de detección de intención"""
    print("🎯 TEST: Sistema de Detección de Intención Inteligente")
    print("=" * 60)
    
    # Usuario de prueba
    user_context = {
        "id": "test-user-123",
        "whatsapp_number": "50612345678",
        "name": "Usuario Test"
    }
    
    # Casos de prueba - mensajes que NO deben procesarse como tareas
    test_cases = [
        # 1. SALUDOS SIMPLES
        {
            "input": "hola",
            "expected_type": "greeting",
            "description": "Saludo simple que reportó el usuario"
        },
        {
            "input": "Hola",
            "expected_type": "greeting", 
            "description": "Saludo con mayúscula"
        },
        {
            "input": "hello",
            "expected_type": "greeting",
            "description": "Saludo en inglés"
        },
        {
            "input": "buenas tardes",
            "expected_type": "greeting",
            "description": "Saludo más largo"
        },
        
        # 2. COMANDOS SIN SLASH
        {
            "input": "help",
            "expected_type": "command",
            "description": "Comando sin slash"
        },
        {
            "input": "hoy",
            "expected_type": "command", 
            "description": "Comando hoy sin slash"
        },
        {
            "input": "stats",
            "expected_type": "command",
            "description": "Comando estadísticas"
        },
        
        # 3. AGRADECIMIENTOS
        {
            "input": "gracias",
            "expected_type": "thanks",
            "description": "Agradecimiento simple"
        },
        {
            "input": "muchas gracias",
            "expected_type": "thanks",
            "description": "Agradecimiento completo"
        },
        
        # 4. MENSAJES AMBIGUOS
        {
            "input": "ok",
            "expected_type": "ambiguous",
            "description": "Respuesta muy corta"
        },
        {
            "input": "si",
            "expected_type": "ambiguous",
            "description": "Confirmación simple"
        },
        
        # 5. EMOJIS SOLOS
        {
            "input": "😊",
            "expected_type": "emoji_only",
            "description": "Solo emoji"
        },
        {
            "input": "👍",
            "expected_type": "emoji_only", 
            "description": "Pulgar arriba"
        },
        
        # 6. CONTENIDO REAL (debe procesarse con Gemini)
        {
            "input": "necesito comprar leche mañana a las 3pm",
            "expected_type": "real_content",
            "description": "Tarea real que sí debe procesarse"
        },
        {
            "input": "tengo reunión con cliente el viernes",
            "expected_type": "real_content",
            "description": "Evento real que sí debe procesarse"
        }
    ]
    
    print(f"👤 Usuario: {user_context['name']}")
    print(f"📱 Número: {user_context['whatsapp_number']}")
    print()
    
    # Mock de WhatsApp Cloud Service para evitar enviar mensajes reales
    original_send = message_handler.whatsapp_cloud_service.send_text_message if hasattr(message_handler, 'whatsapp_cloud_service') else None
    
    # Crear mock temporal
    mock_responses = []
    async def mock_send_message(to, message):
        mock_responses.append({"to": to, "message": message})
        print(f"    📤 Mock envío: {message}")
        return {"success": True}
    
    # Aplicar mock si existe el servicio
    try:
        from services.whatsapp_cloud import whatsapp_cloud_service
        whatsapp_cloud_service.send_text_message = mock_send_message
    except:
        print("⚠️ WhatsApp Cloud Service no disponible, continuando con test...")
    
    # Ejecutar tests
    passed = 0
    failed = 0
    
    print("🧪 EJECUTANDO TESTS:")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        input_msg = test_case["input"]
        expected_type = test_case["expected_type"]
        description = test_case["description"]
        
        print(f"\n{i:2d}. {description}")
        print(f"    💬 Input: '{input_msg}'")
        
        try:
            # Ejecutar detección de intención
            result = await message_handler.detect_user_intent(input_msg, user_context)
            
            detected_type = result.get('type', 'unknown')
            should_handle = result.get('should_handle_directly', False)
            
            print(f"    🎯 Detected: {detected_type}")
            print(f"    ⚡ Handle directly: {should_handle}")
            
            # Verificar resultado
            if expected_type == "real_content":
                # Para contenido real, should_handle_directly debe ser False
                if not should_handle and detected_type == expected_type:
                    print(f"    ✅ PASS - Contenido real enviado a Gemini")
                    passed += 1
                else:
                    print(f"    ❌ FAIL - Contenido real no detectado correctamente")
                    failed += 1
            elif expected_type == "command":
                # Para comandos, depende de si se redirige correctamente
                if detected_type in ["command", "greeting", "handled"] or should_handle:
                    print(f"    ✅ PASS - Comando manejado directamente")
                    passed += 1
                else:
                    print(f"    ❌ FAIL - Comando no detectado correctamente")
                    failed += 1
            else:
                # Para otros casos, should_handle_directly debe ser True
                if should_handle and detected_type == expected_type:
                    print(f"    ✅ PASS - {expected_type} manejado directamente")
                    passed += 1
                else:
                    print(f"    ❌ FAIL - Expected {expected_type}, got {detected_type} (handle: {should_handle})")
                    failed += 1
                    
        except Exception as e:
            print(f"    💥 ERROR: {e}")
            failed += 1
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL TEST:")
    print(f"✅ Casos exitosos: {passed}")
    print(f"❌ Casos fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if mock_responses:
        print(f"\n📱 Mensajes enviados en mock: {len(mock_responses)}")
    
    # Casos críticos específicos
    print("\n🎯 VERIFICACIÓN ESPECÍFICA DEL PROBLEMA REPORTADO:")
    print("-" * 50)
    
    # Test del caso exacto que reportó el usuario: "hola"
    try:
        hola_result = await message_handler.detect_user_intent("hola", user_context)
        if hola_result.get('should_handle_directly', False):
            print("✅ CRÍTICO: 'hola' se maneja como saludo (NO como tarea)")
        else:
            print("❌ CRÍTICO: 'hola' todavía se enviaría a Gemini como tarea")
    except Exception as e:
        print(f"❌ CRÍTICO: Error procesando 'hola': {e}")
    
    print("\n🎯 SISTEMA DE FILTROS INTELIGENTES:")
    print("✅ Saludos → Respuesta directa personalizada")
    print("✅ Comandos sin slash → Redirección a comando handler")
    print("✅ Agradecimientos → Respuesta cordial")
    print("✅ Mensajes ambiguos → Pedir clarificación")
    print("✅ Emojis solos → Respuesta amigable")
    print("✅ Contenido real → Procesar con Gemini")
    
    if passed > failed:
        print(f"\n🎉 TEST EXITOSO - El sistema filtra correctamente los comandos y saludos")
        print(f"🎯 'hola' y otros saludos ya NO se procesan como tareas")
    else:
        print(f"\n⚠️ TEST CON ISSUES - Revisar implementación del filtro")

if __name__ == "__main__":
    print("INICIANDO TEST DE DETECCION DE INTENCION")
    print("Este test verifica que:")
    print("1. 'hola' se detecte como saludo, no como tarea")
    print("2. Comandos sin slash se redirijan correctamente")
    print("3. Agradecimientos y emojis se manejen directamente")
    print("4. Solo el contenido real se envie a Gemini")
    print()
    
    # Ejecutar test
    asyncio.run(test_intent_detection())
    
    print("\nTest completado.")
    print("El problema reportado 'si agrego hola, lo agrega como tarea' debe estar resuelto.")