"""
Test simple del flujo real sin problemas de encoding
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.message_handler import message_handler
from core.supabase import supabase

async def test_simple_flow():
    """Test simple del flujo"""
    print("TESTING REAL MESSAGE FLOW")
    print("="*30)
    
    # Obtener usuario con Todoist
    result = supabase._get_client().table("user_integrations").select(
        "user_id"
    ).eq("service", "todoist").eq("status", "active").execute()
    
    if not result.data:
        print("NO USERS WITH TODOIST CONFIGURED")
        print("This explains why tasks are not saved to Todoist")
        
        # Mostrar usuarios sin encoding issues
        users_result = supabase._get_client().table("users").select(
            "id, whatsapp_number"
        ).execute()
        
        print(f"\nUsers in system: {len(users_result.data)}")
        for i, user in enumerate(users_result.data, 1):
            print(f"{i}. User ID: {user['id']}")
            print(f"   Phone: {user.get('whatsapp_number', 'No phone')}")
            
            # Check integrations
            integrations = supabase._get_client().table("user_integrations").select(
                "service, status"
            ).eq("user_id", user['id']).execute()
            
            if integrations.data:
                services = [f"{i['service']}" for i in integrations.data]
                print(f"   Integrations: {', '.join(services)}")
            else:
                print(f"   Integrations: NONE")
        
        return
    
    user_id = result.data[0]['user_id']
    print(f"Testing with user ID: {user_id}")
    
    # Obtener usuario completo
    user_result = supabase._get_client().table("users").select("*").eq("id", user_id).execute()
    user = user_result.data[0] if user_result.data else {'id': user_id}
    
    # Test con mensaje simple
    test_message = "comprar pan para la casa"
    print(f"Test message: '{test_message}'")
    
    try:
        # Procesar mensaje
        result = await message_handler.handle_text(test_message, user)
        
        print(f"Handler result status: {result.get('status')}")
        
        if result.get('status') == 'success':
            entry_id = result.get('entry_id')
            print(f"Entry ID: {entry_id}")
            
            if entry_id:
                # Verificar entrada
                entry = supabase._get_client().table("entries").select("*").eq("id", entry_id).execute()
                
                if entry.data:
                    entry_data = entry.data[0]
                    print(f"Entry description: {entry_data['description']}")
                    print(f"Entry type: {entry_data['type']}")
                    
                    external_id = entry_data.get('external_id')
                    external_service = entry_data.get('external_service')
                    
                    print(f"External ID: {external_id if external_id else 'NONE'}")
                    print(f"External service: {external_service if external_service else 'NONE'}")
                    
                    if external_id and external_service == 'todoist':
                        print("SUCCESS: Task saved to Todoist!")
                    else:
                        print("ISSUE: Task NOT saved to Todoist")
        else:
            print(f"Handler failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_flow())