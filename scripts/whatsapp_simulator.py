#!/usr/bin/env python3
"""
Simulador de WhatsApp para testing - Usa el flujo completo existente
"""
import asyncio
from datetime import datetime
from handlers.message_handler import message_handler
from core.supabase import supabase

class WhatsAppSimulator:
    def __init__(self):
        self.phone = "50660052300@c.us"  # Número del usuario real en la BD
        self.user_id = "3a0c145f-ac71-4eb8-bda4-95dff3c7919c"  # ID fijo para testing
        self.user_context = None
        
    async def initialize(self):
        """Inicializa el simulador obteniendo el contexto del usuario"""
        try:
            print(">> Inicializando simulador...")
            
            # Obtener o crear usuario con contexto completo (igual que en webhook)
            self.user_context = await supabase.get_user_with_context(self.phone)
            
            print(f">> Usuario inicializado:")
            print(f"   Teléfono: {self.phone}")
            print(f"   Nombre: {self.user_context.get('name')}")
            print(f"   ID: {self.user_context.get('id')}")
            
            if self.user_context.get('profile', {}).get('occupation'):
                print(f"   Ocupación: {self.user_context['profile']['occupation']}")
                
            return True
            
        except Exception as e:
            print(f"XX Error inicializando: {e}")
            return False
    
    async def send_text_message(self, message: str):
        """Simula envío de mensaje de texto - Usa el handler completo"""
        try:
            print(f"\n>> Enviando: '{message}'")
            print(">> Procesando...")
            
            # Detectar si es un comando
            if message.startswith('/'):
                return await self.handle_command(message)
            
            # Usar exactamente el mismo handler que usa WhatsApp
            result = await message_handler.handle_text(message, self.user_context)
            
            if result['status'] == 'success':
                print(f">> Procesado exitosamente!")
                print(f"   Entry ID: {result.get('entry_id')}")
                
                # Mostrar cómo se vería la respuesta en WhatsApp
                print("\n>> Respuesta que se enviaría por WhatsApp:")
                print("   " + "-" * 40)
                # Note: La respuesta ya se envió en el handler (modo mock)
                print("   [Ver arriba en los logs MOCK]")
                print("   " + "-" * 40)
            else:
                print(f"XX Error: {result.get('message')}")
                
            return result
            
        except Exception as e:
            print(f"XX Error simulando mensaje: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_command(self, message: str):
        """Maneja comandos especiales como /register, /profile"""
        try:
            from handlers.command_handler import command_handler
            
            # Extraer comando
            command = message.split()[0] if message.strip() else ""
            
            print(f">> Comando detectado: {command}")
            
            # Usar el mismo handler que usa el webhook
            result = await command_handler.handle_command(command, message, self.user_context)
            
            if result.get('error'):
                print(f"XX Error: {result['error']}")
            else:
                print(f">> Comando procesado exitosamente!")
                print(f"   Tipo: {result.get('type', 'unknown')}")
                
                # Mostrar la respuesta que se enviaría
                print("\n>> Respuesta que se enviaría por WhatsApp:")
                print("   " + "-" * 50)
                try:
                    message_text = result.get('message', 'Sin mensaje')
                    # Reemplazar caracteres problemáticos
                    message_text = message_text.encode('ascii', 'ignore').decode('ascii')
                    print(f"   {message_text}")
                except Exception as e:
                    print(f"   [Mensaje contiene caracteres especiales: {len(result.get('message', ''))} chars]")
                print("   " + "-" * 50)
                
                # Si es registro exitoso, actualizar el contexto del usuario
                if result.get('type') == 'registration_success' and result.get('profile'):
                    print(">> Actualizando contexto local del usuario...")
                    self.user_context['profile'] = result['profile']
            
            return result
            
        except Exception as e:
            print(f"XX Error procesando comando: {e}")
            return {"error": str(e)}
    
    async def show_stats(self):
        """Muestra estadísticas del usuario"""
        try:
            stats = await supabase.get_user_stats(self.user_context['id'])
            
            print("\n>> ESTADÍSTICAS:")
            print(f"   Total entradas: {stats.get('total_entries', 0)}")
            print(f"   Gastos: ${stats.get('gastos', 0):.2f}")
            print(f"   Ingresos: ${stats.get('ingresos', 0):.2f}")
            print(f"   Balance: ${stats.get('balance', 0):.2f}")
            print(f"   Tareas pendientes: {stats.get('pending_tasks', 0)}")
            
            if stats.get('by_type'):
                print("\n>> Por tipo:")
                for tipo, count in stats['by_type'].items():
                    print(f"   {tipo}: {count}")
                    
        except Exception as e:
            print(f"XX Error obteniendo stats: {e}")

async def main():
    """Función principal del simulador"""
    import sys
    
    print("=" * 60)
    print(">> WHATSAPP SIMULATOR - Korei Assistant")
    print("=" * 60)
    print("Simula el flujo completo: Mensaje -> Handler -> Gemini -> Supabase")
    print("\nComandos:")
    print("  'salir' - Terminar")
    print("  'stats' - Ver estadísticas")
    print("\nEjemplos de mensajes:")
    print("  'Compré café por $5'")
    print("  'Tengo reunión mañana a las 3pm'")
    print("  'Recordar llamar al doctor'")
    print("-" * 60)
    
    # Inicializar simulador
    simulator = WhatsAppSimulator()
    
    if not await simulator.initialize():
        print("XX No se pudo inicializar el simulador")
        return
    
    # Para testing, ejecutar mensajes predefinidos cuando se pasa argumento
    import sys
    run_tests = len(sys.argv) > 1 and sys.argv[1] == '--test'
    
    if run_tests or not sys.stdin.isatty():
        print("\n>> Modo de prueba. Ejecutando mensajes predefinidos...")
        test_messages = [
            "/register",  # Ver si pide el perfil
            "/register Soy desarrollador de software, me gusta la música electrónica, los videojuegos y hacer ejercicio. Trabajo remoto y me enfoco en aplicaciones web.",
            "/profile",  # Ver el perfil creado
            "Compré café por $5",
            "Tengo reunión mañana a las 3pm",
            "stats"
        ]
        
        for message in test_messages:
            print(f"\n>> Mensaje: {message}")
            if message.lower() == 'stats':
                await simulator.show_stats()
            else:
                await simulator.send_text_message(message)
            
            # Pausa pequeña entre mensajes para mejor legibilidad
            import asyncio
            await asyncio.sleep(1)
        
        print("\n>> Pruebas completadas!")
        return
    
    print("\n>> Simulador listo! Escribe mensajes como si fuera WhatsApp:")
    
    # Loop principal para modo interactivo
    while True:
        try:
            message = input("\n>> Mensaje: ").strip()
            
            if message.lower() in ['salir', 'exit', 'quit']:
                print(">> ¡Hasta luego!")
                break
                
            if message.lower() == 'stats':
                await simulator.show_stats()
                continue
                
            if not message:
                continue
            
            # Simular el mensaje usando el handler completo
            await simulator.send_text_message(message)
            
        except KeyboardInterrupt:
            print("\n>> ¡Hasta luego!")
            break
        except EOFError:
            print("\n>> Entrada terminada. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"XX Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())