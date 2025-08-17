"""
Test del sistema de verificación de usuario y funcionalidades
"""
import asyncio
from core.supabase import supabase
from handlers.message_handler import MessageHandler

async def test_user_verification():
    """Test de verificación de usuario"""
    print("=== TEST VERIFICACIÓN DE USUARIO ===")
    
    message_handler = MessageHandler()
    
    # Usuario de prueba SIN ID (no existe)
    user_no_exist = {
        "whatsapp_number": "50699999999",
        "display_name": "Usuario No Existe"
        # Sin 'id' - simula usuario no encontrado
    }
    
    result = await message_handler.verify_user_and_payment(user_no_exist)
    
    if not result['is_valid']:
        print("[OK] Usuario no encontrado - mensaje correcto")
        print(f"Mensaje: {result['message'][:50]}...")
    else:
        print("[ERROR] Usuario no existente marcado como válido")
    
    # Usuario de prueba CON ID pero sin pago
    # Buscar un usuario real en la DB
    users = supabase._get_client().table("users").select("*").limit(1).execute()
    if users.data:
        test_user = users.data[0]
        
        # Crear contexto de usuario con pago False
        user_no_payment = {
            "id": test_user['id'],
            "whatsapp_number": test_user['whatsapp_number'],
            "display_name": test_user.get('name', 'Usuario')
        }
        
        # Temporalmente desactivar pago
        await supabase.update_user(test_user['id'], {"payment": False})
        
        result = await message_handler.verify_user_and_payment(user_no_payment)
        
        if not result['is_valid'] and "pago" in result['message'].lower():
            print("[OK] Usuario sin pago - mensaje correcto")
            print(f"Mensaje: {result['message'][:50]}...")
        else:
            print("[ERROR] Usuario sin pago no detectado correctamente")
        
        # Restaurar pago
        await supabase.update_user(test_user['id'], {"payment": True})
        
        # Probar con pago activo
        result = await message_handler.verify_user_and_payment(user_no_payment)
        
        if result['is_valid']:
            print("[OK] Usuario con pago - verificación correcta")
        else:
            print("[ERROR] Usuario con pago marcado como inválido")
    
    print("✅ Test de verificación completado")

async def test_commands():
    """Test de comandos"""
    print("\n=== TEST COMANDOS ===")
    
    # Obtener usuario real para pruebas
    users = supabase._get_client().table("users").select("*").limit(1).execute()
    if users.data:
        user_context = users.data[0]
        
        from handlers.command_handler import command_handler
        
        # Test comando /tareas
        print("Probando comando /tareas...")
        result = await command_handler.handle_command("/tareas", "/tareas", user_context)
        
        if result.get('type') in ['daily_tasks', 'daily_tasks_empty']:
            print("[OK] Comando /tareas funciona")
            if result.get('buttons'):
                print(f"[OK] Botones generados: {len(result['buttons'])}")
            else:
                print("[INFO] Sin botones (no hay tareas pendientes)")
        else:
            print(f"[ERROR] Comando /tareas falló: {result}")
        
        # Test comando /eventos
        print("Probando comando /eventos...")
        result = await command_handler.handle_command("/eventos", "/eventos", user_context)
        
        if result.get('type') in ['daily_events', 'daily_events_empty']:
            print("[OK] Comando /eventos funciona")
        else:
            print(f"[ERROR] Comando /eventos falló: {result}")
        
    print("✅ Test de comandos completado")

if __name__ == "__main__":
    asyncio.run(test_user_verification())
    asyncio.run(test_commands())