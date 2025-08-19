#!/usr/bin/env python3
"""
🧪 TEST ALL COMMANDS - Korei Assistant
Prueba sistemática de todos los comandos disponibles
"""
import asyncio
import json
from typing import Dict, Any
from handlers.command_handler import CommandHandler

class CommandTester:
    def __init__(self):
        self.command_handler = CommandHandler()
        self.test_user = {
            "id": "test-user-001",
            "whatsapp_number": "50660052300",
            "name": "Test User",
            "registration_date": "2025-08-18",
            "is_premium": False,
            "timezone": "America/Costa_Rica"
        }
        
        # Lista de todos los comandos disponibles
        self.commands_to_test = [
            "/register",
            "/registro", 
            "/profile",
            "/perfil",
            "/help",
            "/ayuda",
            "/stats",
            "/estadisticas",
            "/tareas",
            "/tasks",
            "/tareas-hoy",
            "/tasks-today",
            "/tareas-mañana", 
            "/tasks-tomorrow",
            "/eventos",
            "/events",
            "/eventos-hoy",
            "/events-today",
            "/eventos-mañana",
            "/events-tomorrow",
            "/gastos",
            "/expenses",
            "/gastos-hoy",
            "/expenses-today",
            "/ingresos",
            "/income",
            "/ingresos-hoy", 
            "/income-today",
            "/resumen-mes",
            "/monthly-summary",
            "/tips-finanzas",
            "/financial-tips",
            "/analisis-gastos",
            "/spending-analysis",
            "/hola",
            "/hello",
            "/inicio",
            "/recordatorio",
            "/reminder",
            "/proyectos",
            "/projects"
        ]

    async def test_command(self, command: str) -> Dict[str, Any]:
        """Prueba un comando específico"""
        try:
            print(f"Testing command: {command}")
            
            # Simular el comando
            result = await self.command_handler.handle_command(
                command=command,
                message=command,
                user_context=self.test_user
            )
            
            print(f"   SUCCESS: {result.get('type', 'unknown')}")
            print(f"   Message: {result.get('message', '')[:100]}...")
            return {
                "command": command,
                "status": "success",
                "type": result.get('type'),
                "message_length": len(result.get('message', ''))
            }
            
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            return {
                "command": command,
                "status": "error", 
                "error": str(e)
            }

    async def test_all_commands(self):
        """Prueba todos los comandos disponibles"""
        print("STARTING COMMAND TESTING")
        print("=" * 50)
        
        results = []
        successful_commands = 0
        failed_commands = 0
        
        for command in self.commands_to_test:
            result = await self.test_command(command)
            results.append(result)
            
            if result["status"] == "success":
                successful_commands += 1
            else:
                failed_commands += 1
            
            # Pausa entre comandos
            await asyncio.sleep(0.1)
        
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print(f"Successful commands: {successful_commands}")
        print(f"Failed commands: {failed_commands}")
        print(f"Success rate: {(successful_commands/len(self.commands_to_test)*100):.1f}%")
        
        if failed_commands > 0:
            print("\nFAILED COMMANDS:")
            for result in results:
                if result["status"] == "error":
                    print(f"   ERROR {result['command']}: {result['error']}")
        
        return results

async def main():
    """Función principal de prueba"""
    tester = CommandTester()
    results = await tester.test_all_commands()
    
    # Guardar resultados
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to test_results.json")

if __name__ == "__main__":
    asyncio.run(main())