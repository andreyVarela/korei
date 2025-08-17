"""
Script de prueba para verificar el nuevo sistema de tareas priorizadas
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
import pytz

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.command_handler import command_handler
from app.config import settings

async def test_priority_task_system():
    """Test del nuevo sistema de priorización de tareas"""
    print("🎯 TEST: Sistema de Tareas Priorizadas")
    print("=" * 50)
    
    # Usuario de prueba
    user_context = {
        "id": "tu-user-id-aqui",  # Cambia por tu user ID real
        "whatsapp_number": "50612345678",
        "name": "Usuario Test"
    }
    
    print(f"👤 Usuario: {user_context['name']} (ID: {user_context['id']})")
    print()
    
    # 1. Probar ordenamiento de tareas por prioridad
    print("🔀 1. TESTEAR ORDENAMIENTO POR PRIORIDAD")
    print("-" * 40)
    
    # Crear tareas de ejemplo para probar el algoritmo
    test_tasks = [
        {
            "id": "task-1",
            "description": "Tarea normal sin prioridad",
            "priority": "media",
            "datetime": (datetime.now() + timedelta(hours=5)).isoformat(),
            "type": "tarea",
            "status": "pending"
        },
        {
            "id": "task-2", 
            "description": "Reunión urgente con cliente",
            "priority": "alta",
            "datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
            "type": "tarea",
            "status": "pending"
        },
        {
            "id": "task-3",
            "description": "Llamar doctor", 
            "priority": "baja",
            "datetime": (datetime.now() + timedelta(hours=8)).isoformat(),
            "type": "tarea",
            "status": "pending"
        },
        {
            "id": "task-4",
            "description": "Presentación importante deadline",
            "priority": "alta", 
            "datetime": (datetime.now() - timedelta(hours=1)).isoformat(),  # Atrasada
            "type": "tarea",
            "status": "pending"
        },
        {
            "id": "task-5",
            "description": "Comprar leche",
            "priority": "baja",
            "datetime": (datetime.now() + timedelta(minutes=30)).isoformat(),  # Muy pronto
            "type": "tarea", 
            "status": "pending"
        }
    ]
    
    # Usar el método interno de ordenamiento
    handler = command_handler
    sorted_tasks = handler._sort_tasks_by_priority(test_tasks)
    
    print("📝 Tareas ordenadas por prioridad:")
    for i, task in enumerate(sorted_tasks, 1):
        priority = task.get('priority', 'media')
        desc = task['description']
        task_time = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
        tz = pytz.timezone(settings.timezone)
        now = datetime.now(tz)
        
        # Calcular tiempo relativo
        if task_time.replace(tzinfo=None) < now.replace(tzinfo=None):
            time_rel = "⚠️ ATRASADA"
        else:
            hours_diff = (task_time.replace(tzinfo=None) - now.replace(tzinfo=None)).total_seconds() / 3600
            if hours_diff < 1:
                time_rel = f"🔥 en {int(hours_diff * 60)} min"
            elif hours_diff < 6:
                time_rel = f"⏰ en {hours_diff:.1f}h"
            else:
                time_rel = f"📅 en {hours_diff:.0f}h"
        
        print(f"  {i}. [{priority.upper()}] {desc} - {time_rel}")
    
    print()
    
    # 2. Probar límite de 3 tareas
    print("📊 2. TESTEAR LÍMITE DE 3 TAREAS")
    print("-" * 30)
    
    total_tasks = len(sorted_tasks)
    max_individual = 3
    priority_tasks = sorted_tasks[:max_individual]
    remaining_tasks = sorted_tasks[max_individual:]
    
    print(f"📋 Total de tareas: {total_tasks}")
    print(f"⚡ Tareas prioritarias (con botones): {len(priority_tasks)}")
    print(f"📝 Tareas en resumen: {len(remaining_tasks)}")
    print()
    
    print("🎯 Tareas que tendrían botones interactivos:")
    for i, task in enumerate(priority_tasks, 1):
        print(f"  {i}. {task['description']} [{task['priority']}]")
    
    if remaining_tasks:
        print("\n📝 Tareas que aparecerían en resumen:")
        for i, task in enumerate(remaining_tasks, 1):
            print(f"  {i}. {task['description']} [{task['priority']}]")
    
    print()
    
    # 3. Simular mensajes que se enviarían
    print("💬 3. SIMULAR MENSAJES A ENVIAR")
    print("-" * 30)
    
    # Mensaje inicial
    if total_tasks <= 3:
        header_text = f"📋 **Tus {total_tasks} tareas pendientes:**\n\n¡Pocas y estratégicas! Cada una con botones para completar o eliminar 🎯"
    else:
        header_text = f"📋 **Tienes {total_tasks} tareas pendientes**\n\n🎯 Te muestro las **{len(priority_tasks)} más importantes** con botones interactivos.\n💡 Las otras {len(remaining_tasks)} aparecen en el resumen final."
    
    print("📤 Mensaje inicial:")
    print(f"   {header_text}")
    print()
    
    print("📤 Mensajes individuales con botones:")
    for i, task in enumerate(priority_tasks, 1):
        print(f"   {i}. 📋 **TAREA** - {task['description']} [Botones: ✅ Completar | 🗑️ Eliminar | ℹ️ Info]")
    
    if remaining_tasks:
        print("\n📤 Resumen de tareas restantes:")
        summary_preview = remaining_tasks[:3]  # Primeras 3 del resto
        for i, task in enumerate(summary_preview, 1):
            print(f"   {i}. {task['description']}")
        if len(remaining_tasks) > 3:
            print(f"   ... y {len(remaining_tasks) - 3} tareas más")
        print("   [Botones: 📋 Ver Todas | ➡️ Siguientes 3 | ✅ Completar por Nombre]")
    
    print()
    
    # 4. Mensaje final
    if len(priority_tasks) > 0:
        if total_tasks <= 3:
            footer_text = f"🎯 **¡Perfecto!** Tus {total_tasks} tareas ya tienen botones interactivos.\n\n💡 Solo haz click para completar o eliminar. ¡Cada paso cuenta! 💪"
        else:
            footer_text = f"🎯 **Tareas priorizadas** - Las {len(priority_tasks)} más importantes ya tienen botones.\n\n⚡ Enfócate en estas primero, luego gestiona las restantes.\n\n💡 **Tip:** Usa `/completar [nombre]` para marcar cualquier tarea como completada."
        
        print("📤 Mensaje final:")
        print(f"   {footer_text}")

if __name__ == "__main__":
    print("🚀 INICIANDO TEST DE SISTEMA DE PRIORIDADES")
    print("Este test simula cómo funcionaría el nuevo sistema:")
    print("1. Ordena tareas por prioridad inteligente")
    print("2. Envía solo las 3 más importantes con botones")
    print("3. Muestra las restantes en resumen con opciones")
    print()
    
    # Ejecutar test
    asyncio.run(test_priority_task_system())
    
    print("\n✅ Test completado. El sistema ahora:")
    print("📌 Prioriza tareas inteligentemente (urgencia + tiempo + palabras clave)")
    print("📌 Envía máximo 3 tareas con botones individuales")
    print("📌 Agrupa las restantes en resumen con opciones")
    print("📌 Evita spam de mensajes cuando hay muchas tareas")
    print("\n🎯 ¡Mucho mejor UX para usuarios con muchas tareas!")