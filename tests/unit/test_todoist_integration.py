"""
Test del sistema inteligente de asignación de proyectos de Todoist
"""
import asyncio
from services.integrations.todoist_integration import select_optimal_project

def test_project_selection():
    """Test de selección de proyectos con datos simulados"""
    print("=== TEST SISTEMA DE PROYECTOS INTELIGENTE ===")
    
    # Proyectos simulados de Todoist
    mock_projects = [
        {"id": "1", "name": "Personal", "color": "blue"},
        {"id": "2", "name": "Trabajo", "color": "red"},
        {"id": "3", "name": "Casa", "color": "green"},
        {"id": "4", "name": "Compras", "color": "yellow"},
        {"id": "5", "name": "Salud", "color": "purple"},
        {"id": "6", "name": "Finanzas", "color": "orange"},
        {"id": "7", "name": "Proyectos Tech", "color": "teal"},
        {"id": "8", "name": "Inbox", "color": "gray"}
    ]
    
    # Casos de prueba
    test_cases = [
        "comprar leche mañana",
        "reunión con el equipo de desarrollo",
        "pagar factura de electricidad",
        "cita médica viernes",
        "limpiar la casa",
        "programar nueva funcionalidad",
        "hacer ejercicio",
        "llamar a mamá",
        "revisar presupuesto mensual",
        "comprar ingredientes para la cena",
        "deadline del proyecto",
        "organizar documentos"
    ]
    
    user_context = {}  # Contexto vacío para este test
    
    print("Probando asignación inteligente de proyectos:")
    print("-" * 60)
    
    for i, task in enumerate(test_cases, 1):
        print(f"{i:2d}. Tarea: '{task}'")
        
        selected_project = select_optimal_project(mock_projects, user_context, task)
        
        if selected_project:
            project_name = selected_project.get('name', 'Sin nombre')
            project_id = selected_project.get('id', '')
            print(f"    → Proyecto: {project_name} (ID: {project_id})")
        else:
            print(f"    → No se pudo seleccionar proyecto")
        
        print()
    
    print("=" * 60)
    print("Test completado. Revisa los logs para ver el análisis detallado.")

def test_edge_cases():
    """Test de casos especiales"""
    print("\n=== TEST CASOS ESPECIALES ===")
    
    mock_projects = [
        {"id": "1", "name": "Mi Proyecto Personal", "color": "blue"},
        {"id": "2", "name": "Desarrollo Web", "color": "red"},
        {"id": "3", "name": "📱 Apps Móviles", "color": "green"}
    ]
    
    edge_cases = [
        "",  # Texto vacío
        "   ",  # Solo espacios
        "xyz abc def",  # Sin palabras clave reconocibles
        "desarrollo web app móvil",  # Múltiples coincidencias
        "COMPRAR PERSONAL",  # Mayúsculas
        "development programming code"  # Inglés
    ]
    
    user_context = {}
    
    for case in edge_cases:
        print(f"Caso: '{case}'")
        selected = select_optimal_project(mock_projects, user_context, case)
        if selected:
            print(f"  → {selected.get('name')}")
        else:
            print(f"  → Sin selección")
        print()

if __name__ == "__main__":
    test_project_selection()
    test_edge_cases()