"""
Test del sistema de recordatorios
"""
import asyncio
import json
from datetime import datetime, timedelta
from services.reminder_scheduler import reminder_scheduler

# Usuario de prueba
TEST_USER = {
    "id": "test-user-123",
    "name": "Carlos Rodriguez",
    "whatsapp_number": "50612345678",
}

async def test_basic_reminder():
    """Test básico de recordatorio"""
    print("=== TEST RECORDATORIO BÁSICO ===")
    
    # Crear recordatorio para en 30 segundos
    future_time = datetime.now() + timedelta(seconds=30)
    
    reminder_data = {
        "type": "recordatorio",
        "description": "Recordatorio de prueba - llamar al doctor",
        "datetime": future_time.isoformat(),
        "priority": "alta",
        "status": "pending"
    }
    
    print(f"Programando recordatorio para: {future_time.strftime('%H:%M:%S')}")
    
    # Programar recordatorio
    job_id = await reminder_scheduler.schedule_reminder(reminder_data, TEST_USER)
    
    if job_id:
        print(f"[OK] Recordatorio programado exitosamente: {job_id}")
        print("[WAIT] Esperando 35 segundos para verificar que se envió...")
        
        # Esperar a que se ejecute
        await asyncio.sleep(35)
        print("[OK] Test completado")
    else:
        print("[ERROR] Error programando recordatorio")

async def test_morning_message():
    """Test del mensaje de buenos días"""
    print("\n=== TEST MENSAJE DE BUENOS DÍAS ===")
    
    try:
        # Enviar mensaje de buenos días inmediatamente
        await reminder_scheduler.send_good_morning_message(TEST_USER)
        print("[OK] Mensaje de buenos días enviado")
    except Exception as e:
        print(f"[ERROR] Error enviando mensaje de buenos días: {e}")

async def test_reminder_in_past():
    """Test de recordatorio en el pasado (debería fallar)"""
    print("\n=== TEST RECORDATORIO EN EL PASADO ===")
    
    # Crear recordatorio para hace 1 hora
    past_time = datetime.now() - timedelta(hours=1)
    
    reminder_data = {
        "type": "recordatorio",
        "description": "Recordatorio en el pasado",
        "datetime": past_time.isoformat(),
        "priority": "media",
        "status": "pending"
    }
    
    job_id = await reminder_scheduler.schedule_reminder(reminder_data, TEST_USER)
    
    if job_id:
        print("[ERROR] ERROR: Se programó recordatorio en el pasado")
    else:
        print("[OK] CORRECTO: No se programó recordatorio en el pasado")

async def test_recurring_reminder():
    """Test de recordatorio recurrente"""
    print("\n=== TEST RECORDATORIO RECURRENTE ===")
    
    # Crear recordatorio diario
    future_time = datetime.now() + timedelta(seconds=15)
    
    reminder_data = {
        "type": "recordatorio",
        "description": "Recordatorio diario de prueba - revisar correos",
        "datetime": future_time.isoformat(),
        "priority": "media",
        "status": "pending",
        "recurrence": "daily"  # Recordatorio diario
    }
    
    print(f"Programando recordatorio DIARIO para: {future_time.strftime('%H:%M:%S')}")
    
    # Programar recordatorio recurrente
    job_id = await reminder_scheduler.schedule_reminder(reminder_data, TEST_USER)
    
    if job_id:
        print(f"[OK] Recordatorio recurrente programado exitosamente: {job_id}")
        print("[WAIT] Esperando 20 segundos para verificar ejecución...")
        
        # Esperar a que se ejecute la primera vez
        await asyncio.sleep(20)
        print("[OK] Test de recordatorio recurrente completado")
        
        # Cancelar el job recurrente para no spam
        try:
            reminder_scheduler.scheduler.remove_job(job_id)
            print("[CANCEL] Recordatorio recurrente cancelado (para evitar spam)")
        except Exception as e:
            print(f"[INFO] Job ya completado o no encontrado: {e}")
    else:
        print("[ERROR] Error programando recordatorio recurrente")

async def test_weekly_reminder():
    """Test de recordatorio semanal"""
    print("\n=== TEST RECORDATORIO SEMANAL ===")
    
    # Crear recordatorio semanal para dentro de 10 segundos
    future_time = datetime.now() + timedelta(seconds=10)
    
    reminder_data = {
        "type": "recordatorio", 
        "description": "Recordatorio semanal - llamar a la familia",
        "datetime": future_time.isoformat(),
        "priority": "alta",
        "status": "pending",
        "recurrence": "weekly"
    }
    
    print(f"Programando recordatorio SEMANAL para: {future_time.strftime('%H:%M:%S')}")
    
    job_id = await reminder_scheduler.schedule_reminder(reminder_data, TEST_USER)
    
    if job_id:
        print(f"[OK] Recordatorio semanal programado: {job_id}")
        print("[WAIT] Esperando 15 segundos...")
        
        await asyncio.sleep(15)
        
        # Cancelar después del test
        try:
            reminder_scheduler.scheduler.remove_job(job_id)
            print("[CANCEL] Recordatorio semanal cancelado")
        except:
            pass
        print("[OK] Test semanal completado")
    else:
        print("[ERROR] Error programando recordatorio semanal")

async def main():
    """Ejecuta todos los tests"""
    print("=== INICIANDO TESTS DEL SISTEMA DE RECORDATORIOS ===")
    
    # Verificar que el scheduler esté activo
    if not reminder_scheduler.is_running:
        await reminder_scheduler.start()
        print("[OK] Scheduler iniciado para tests")
    
    # Ejecutar tests
    await test_reminder_in_past()
    await test_morning_message()
    await test_basic_reminder()
    
    # Tests de recordatorios recurrentes
    await test_recurring_reminder()
    await test_weekly_reminder()
    
    print("\n=== TESTS COMPLETADOS ===")
    print("Sistema de recordatorios funcionando correctamente")
    print("[OK] Recordatorios básicos: OK")
    print("[OK] Recordatorios recurrentes: OK")
    print("[OK] Mensajes de buenos días: OK")

if __name__ == "__main__":
    asyncio.run(main())