"""
Test para verificar que las tareas se crean en el proyecto correcto de Todoist
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import message_handler
from core.supabase import supabase

async def test_project_assignment():
    """Test de asignación de proyectos"""
    print("TESTING PROJECT ASSIGNMENT IN TODOIST")
    print("="*40)
    
    # Obtener usuario con Todoist
    result = supabase._get_client().table("user_integrations").select(
        "user_id"
    ).eq("service", "todoist").eq("status", "active").execute()
    
    if not result.data:
        print("ERROR: No users with Todoist configured")
        return
    
    user_id = result.data[0]['user_id']
    user_result = supabase._get_client().table("users").select("*").eq("id", user_id).execute()
    user = user_result.data[0] if user_result.data else {'id': user_id}
    
    print(f"Testing with user: {user_id}")
    
    # Test con diferentes tipos de tareas para proyectos específicos
    test_cases = [
        {
            "message": "necesito hacer presentación para el trabajo mañana",
            "expected_project": "trabajo",
            "description": "Tarea de trabajo"
        },
        {
            "message": "comprar leche y pan en el supermercado",
            "expected_project": "personal", 
            "description": "Tarea personal/compras"
        },
        {
            "message": "leer libro de programación",
            "expected_project": "personal",
            "description": "Tarea de aprendizaje/personal"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"Message: '{test_case['message']}'")
        print(f"Expected project: {test_case['expected_project']}")
        
        try:
            # Procesar mensaje
            result = await message_handler.handle_text(test_case['message'], user)
            
            if result.get('status') == 'success':
                entry_id = result.get('entry_id')
                
                if entry_id:
                    # Verificar entrada en BD
                    entry = supabase._get_client().table("entries").select("*").eq("id", entry_id).execute()
                    
                    if entry.data:
                        entry_data = entry.data[0]
                        project_name = entry_data.get('project_name', 'NO PROJECT')
                        external_id = entry_data.get('external_id')
                        
                        print(f"RESULT:")
                        print(f"  Project assigned: {project_name}")
                        print(f"  Todoist ID: {external_id}")
                        
                        if project_name.lower() == test_case['expected_project']:
                            print(f"  SUCCESS: Correct project assignment!")
                        else:
                            print(f"  ISSUE: Expected '{test_case['expected_project']}', got '{project_name}'")
                    else:
                        print(f"  ERROR: Entry not found in database")
                else:
                    print(f"  ERROR: No entry_id returned")
            else:
                print(f"  ERROR: Message handler failed: {result}")
                
        except Exception as e:
            print(f"  ERROR: {e}")
        
        # Pausa entre tests
        await asyncio.sleep(2)

if __name__ == "__main__":
    print("Testing if tasks are created in the correct Todoist projects")
    print("This will test the project selection algorithm")
    print()
    
    asyncio.run(test_project_assignment())