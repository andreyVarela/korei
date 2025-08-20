#!/usr/bin/env python3
"""
Simple Command Test - Test command functionality without Unicode printing
"""
import asyncio
import json
from typing import Dict, Any
from handlers.command_handler import CommandHandler

async def test_commands():
    """Test essential commands functionality"""
    command_handler = CommandHandler()
    
    # Use a valid UUID for testing  
    test_user = {
        "id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID
        "whatsapp_number": "50660052300",
        "name": "Test User",
        "registration_date": "2025-08-18",
        "is_premium": False,
        "timezone": "America/Costa_Rica"
    }
    
    # Test essential commands
    commands_to_test = [
        "/help",
        "/profile", 
        "/stats",
        "/tasks",
        "/events",
        "/expenses",
        "/income",
        "/hello"
    ]
    
    results = {}
    
    for command in commands_to_test:
        try:
            result = await command_handler.handle_command(
                command=command,
                message=command,
                user_context=test_user
            )
            
            # Check if command executed successfully (has type and message)
            if result.get('type') and result.get('message'):
                results[command] = {
                    "status": "SUCCESS",
                    "type": result.get('type'),
                    "has_message": len(result.get('message', '')) > 0
                }
                print(f"{command}: SUCCESS - {result.get('type')}")
            else:
                results[command] = {
                    "status": "FAILED", 
                    "error": "No type or message in response"
                }
                print(f"{command}: FAILED - No response data")
                
        except Exception as e:
            results[command] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"{command}: ERROR - {str(e)}")
    
    # Summary
    successful = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
    total = len(results)
    
    print(f"\nSUMMARY: {successful}/{total} commands working ({successful/total*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(test_commands())
    
    # Save results
    with open("command_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to command_test_results.json")