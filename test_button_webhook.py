"""
Script de prueba para verificar el manejo de botones de WhatsApp
"""
import asyncio
import json
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes.whatsapp_cloud import process_interactive_message, get_or_create_user

async def test_button_interactions():
    """Test completo de interacciones de botones"""
    print("🔧 TEST: Funcionalidad de Botones de WhatsApp")
    print("=" * 50)
    
    # Datos de prueba
    test_phone = "50612345678"
    contact_name = "Usuario Test"
    test_task_id = "test-task-123"  # Cambia por un ID real de tu base de datos
    
    print(f"📱 Teléfono: {test_phone}")
    print(f"👤 Contacto: {contact_name}")
    print(f"🆔 Task ID: {test_task_id}")
    print()
    
    # 1. Test botón "Completar"
    print("✅ 1. TESTEAR BOTÓN COMPLETAR")
    print("-" * 30)
    
    complete_button_data = {
        "from": test_phone,
        "id": "test-msg-complete",
        "timestamp": str(int(datetime.now().timestamp())),
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {
                "id": f"complete_task_{test_task_id}",
                "title": "✅ Completar"
            }
        }
    }
    
    try:
        print(f"📤 Simulando click en botón 'Completar' para tarea {test_task_id}")
        await process_interactive_message(test_phone, complete_button_data, contact_name)
        print("✅ Botón 'Completar' procesado exitosamente")
    except Exception as e:
        print(f"❌ Error en botón 'Completar': {e}")
    
    print()
    
    # 2. Test botón "Info"
    print("ℹ️ 2. TESTEAR BOTÓN INFO")
    print("-" * 30)
    
    info_button_data = {
        "from": test_phone,
        "id": "test-msg-info",
        "timestamp": str(int(datetime.now().timestamp())),
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {
                "id": f"info_task_{test_task_id}",
                "title": "ℹ️ Info"
            }
        }
    }
    
    try:
        print(f"📤 Simulando click en botón 'Info' para tarea {test_task_id}")
        await process_interactive_message(test_phone, info_button_data, contact_name)
        print("✅ Botón 'Info' procesado exitosamente")
    except Exception as e:
        print(f"❌ Error en botón 'Info': {e}")
    
    print()
    
    # 3. Test botón "Eliminar"
    print("🗑️ 3. TESTEAR BOTÓN ELIMINAR")
    print("-" * 30)
    
    delete_button_data = {
        "from": test_phone,
        "id": "test-msg-delete",
        "timestamp": str(int(datetime.now().timestamp())),
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {
                "id": f"delete_task_{test_task_id}",
                "title": "🗑️ Eliminar"
            }
        }
    }
    
    try:
        print(f"📤 Simulando click en botón 'Eliminar' para tarea {test_task_id}")
        await process_interactive_message(test_phone, delete_button_data, contact_name)
        print("✅ Botón 'Eliminar' procesado exitosamente")
    except Exception as e:
        print(f"❌ Error en botón 'Eliminar': {e}")
    
    print()
    
    # 4. Test botón desconocido
    print("❓ 4. TESTEAR BOTÓN DESCONOCIDO")
    print("-" * 30)
    
    unknown_button_data = {
        "from": test_phone,
        "id": "test-msg-unknown",
        "timestamp": str(int(datetime.now().timestamp())),
        "type": "interactive",
        "interactive": {
            "type": "button_reply",
            "button_reply": {
                "id": "unknown_action_123",
                "title": "❓ Desconocido"
            }
        }
    }
    
    try:
        print("📤 Simulando click en botón desconocido")
        await process_interactive_message(test_phone, unknown_button_data, contact_name)
        print("✅ Botón desconocido manejado correctamente")
    except Exception as e:
        print(f"❌ Error en botón desconocido: {e}")
    
    print()

async def test_webhook_parsing():
    """Test del parsing del webhook completo"""
    print("🔧 TEST: Parsing Completo del Webhook")
    print("=" * 40)
    
    # Simular webhook completo de WhatsApp Cloud API
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test-entry-id",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "50664100173",
                                "phone_number_id": "test-phone-id"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Usuario Test"},
                                    "wa_id": "50612345678"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "50612345678",
                                    "id": "test-interactive-msg",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "complete_task_test-task-456",
                                            "title": "✅ Completar"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    print("📊 Payload del webhook:")
    print(json.dumps(webhook_payload, indent=2))
    print()
    
    try:
        from api.routes.whatsapp_cloud import process_webhook_direct
        print("📤 Procesando webhook simulado...")
        await process_webhook_direct(webhook_payload)
        print("✅ Webhook procesado exitosamente")
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE BOTONES DE WHATSAPP")
    print("Para usar este script:")
    print("1. Cambia test_task_id por un ID real de tu base de datos")
    print("2. Asegúrate de que tienes tareas en tu BD")
    print("3. Ejecuta: python test_button_webhook.py")
    print()
    
    # Ejecutar tests
    asyncio.run(test_button_interactions())
    print()
    asyncio.run(test_webhook_parsing())
    
    print("\n✅ Tests completados. Revisa los logs para más detalles.")
    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Usa /tareas-botones en WhatsApp para probar en vivo")
    print("2. Haz click en los botones de las tareas enviadas")
    print("3. Verifica que las tareas se marquen como completadas/eliminadas")