"""
Test final del workflow completo - Sin emojis para Windows
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
import pytz

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.integrations.todoist_integration import select_optimal_project

async def test_final_workflow():
    """Test del workflow completo sin emojis"""
    print("=== TEST WORKFLOW FINAL COMPLETO ===")
    
    # Datos de prueba
    mock_projects = [
        {"id": "1", "name": "Personal", "color": "blue"},
        {"id": "2", "name": "Trabajo", "color": "red"},
        {"id": "3", "name": "Casa", "color": "green"},
        {"id": "4", "name": "Compras", "color": "yellow"}
    ]
    
    # Test cases
    test_cases = [
        {
            "text": "comprar leche manana", 
            "expected_project": "Personal"
        },
        {
            "text": "reunion con el equipo",
            "expected_project": "Trabajo"
        },
        {
            "text": "limpiar la casa",
            "expected_project": "Casa"
        }
    ]
    
    print(f"Procesando {len(test_cases)} casos de prueba...")
    print("-" * 50)
    
    success_count = 0
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. Tarea: '{case['text']}'")
        
        try:
            # Simular selección de proyecto
            selected_project = select_optimal_project(
                mock_projects, 
                {}, 
                case['text']
            )
            
            if selected_project:
                project_name = selected_project.get('name')
                project_id = selected_project.get('id')
                print(f"   [OK] Proyecto: {project_name} (ID: {project_id})")
                
                # Verificar que es el proyecto esperado
                if project_name == case['expected_project']:
                    print(f"   [CORRECTO] Seleccion correcta!")
                    success_count += 1
                else:
                    print(f"   [ADVERTENCIA] Esperado: {case['expected_project']}, obtuvo: {project_name}")
            else:
                print(f"   [ERROR] No se selecciono proyecto")
                
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        
        print()
    
    print("=== TEST DE ESTRUCTURA DE DATOS PARA BD ===")
    
    # Test estructura de datos que se enviaría a la BD
    test_entry_data = {
        "type": "tarea",
        "description": "comprar leche manana",
        "amount": 0,
        "datetime": (datetime.now(pytz.UTC) + timedelta(days=1)).isoformat(),
        "priority": "media",
        "task_category": "personal",
        "project_id": "1",
        "project_name": "Personal"
    }
    
    print("Estructura de datos para BD:")
    for key, value in test_entry_data.items():
        print(f"  {key}: {value}")
    
    print()
    print("=== RESUMEN ===")
    print(f"Tests exitosos: {success_count}/{len(test_cases)}")
    print(f"Sistema funcionando: {'SI' if success_count == len(test_cases) else 'PARCIAL'}")
    
    print()
    print("PROXIMOS PASOS:")
    print("1. Ejecutar migraciones en Supabase:")
    print("   - ALTER TABLE entries ADD COLUMN project_id VARCHAR(255);")
    print("   - ALTER TABLE entries ADD COLUMN project_name VARCHAR(255);")
    print("2. Probar mensaje real: 'recordarme comprar leche manana'")
    print("3. Verificar que se guarde en BD con campos de proyecto")
    print("4. El sistema deberia funcionar sin errores!")

if __name__ == "__main__":
    asyncio.run(test_final_workflow())