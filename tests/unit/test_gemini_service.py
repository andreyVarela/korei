#!/usr/bin/env python3
"""
Script simple para probar Gemini desde terminal
"""
import asyncio
import sys
from services.gemini import gemini_service

async def test_gemini():
    """Prueba básica de Gemini"""
    print(">> Probando conexión con Gemini...")
    
    # Contexto de usuario básico para las pruebas
    user_context = {
        "name": "Test User",
        "profile": {
            "occupation": "Desarrollador",
            "hobbies": ["programación", "café"],
            "context_summary": "Le gusta la tecnología y trabajar en proyectos"
        }
    }
    
    try:
        # Mensaje de prueba
        test_message = "Compré café por $5 en Starbucks esta mañana"
        
        print(f">> Procesando: {test_message}")
        result = await gemini_service.process_message(test_message, user_context)
        
        print(">> Respuesta de Gemini:")
        print(f"   Tipo: {result.get('type')}")
        print(f"   Descripción: {result.get('description')}")
        print(f"   Monto: {result.get('amount')}")
        print(f"   Fecha: {result.get('datetime')}")
        print(f"   Prioridad: {result.get('priority')}")
        
        return True
        
    except Exception as e:
        print(f"XX Error: {e}")
        return False

async def interactive_mode():
    """Modo interactivo para probar mensajes"""
    print("\n>> Modo interactivo - Envía mensajes a Gemini")
    print("Escribe 'salir' para terminar\n")
    
    user_context = {
        "name": "Usuario Test",
        "profile": {
            "occupation": "Desarrollador", 
            "hobbies": ["programación", "café", "videojuegos"],
            "context_summary": "Desarrollador que trabaja desde casa"
        }
    }
    
    while True:
        try:
            message = input(">> Tu mensaje: ").strip()
            
            if message.lower() in ['salir', 'exit', 'quit']:
                print(">> ¡Hasta luego!")
                break
                
            if not message:
                continue
                
            print(">> Procesando...")
            result = await gemini_service.process_message(message, user_context)
            
            print("\n>> Resultado:")
            print(f"   Tipo: {result.get('type')}")
            print(f"   Descripción: {result.get('description')}")
            if result.get('amount'):
                print(f"   Monto: ${result.get('amount')}")
            print(f"   Fecha: {result.get('datetime')}")
            print(f"   Prioridad: {result.get('priority')}")
            if result.get('task_category'):
                print(f"   Categoría: {result.get('task_category')}")
            print()
            
        except KeyboardInterrupt:
            print("\n>> ¡Hasta luego!")
            break
        except Exception as e:
            print(f"XX Error: {e}\n")

async def main():
    print(">> Korei - Test de Gemini\n")
    
    # Primero probar conexión básica
    if await test_gemini():
        print("\n>> Conexión exitosa con Gemini!")
        
        # Preguntar si quiere modo interactivo
        response = input("\n¿Quieres probar el modo interactivo? (s/n): ").strip().lower()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            await interactive_mode()
    else:
        print("\n>> No se pudo conectar con Gemini")
        print("Verifica tu GEMINI_API_KEY en el archivo .env")

if __name__ == "__main__":
    asyncio.run(main())