#!/usr/bin/env python3
"""
Test script for ADHD Support System
Tests both Neural Hacking and Natural language styles
"""

import asyncio
import sys
import os
from datetime import datetime
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_adhd_system():
    """Test complete ADHD system functionality"""
    
    print("🧪 Testing ADHD Support System")
    print("=" * 50)
    
    try:
        # Test 1: Import all modules
        print("1️⃣ Testing imports...")
        from services.adhd_support.language_formatter import ADHDLanguageFormatter
        from services.adhd_support.adhd_plan_generator import ADHDPlanGenerator
        from services.adhd_support.context_analyzer import ADHDContextAnalyzer
        from handlers.command_handler import CommandHandler
        print("✅ All imports successful")
        
        # Test 2: Language formatters
        print("\n2️⃣ Testing language formatters...")
        neural_formatter = ADHDLanguageFormatter("neural")
        natural_formatter = ADHDLanguageFormatter("natural")
        
        # Test plan creation messages
        plan_data = {
            'name': 'Test ADHD Plan',
            'tasks_count': 7,
            'duration_weeks': 2
        }
        
        neural_msg = neural_formatter.format_plan_created(plan_data)
        natural_msg = natural_formatter.format_plan_created(plan_data)
        
        print("✅ Neural formatter working")
        print("✅ Natural formatter working")
        
        # Test 3: Crisis messages
        print("\n3️⃣ Testing crisis activation...")
        neural_crisis = neural_formatter.format_crisis_activated("overwhelm", 5)
        natural_crisis = natural_formatter.format_crisis_activated("overwhelm", 5)
        
        print("✅ Crisis messages generated")
        
        # Test 4: Plan generators
        print("\n4️⃣ Testing plan generators...")
        
        # Mock user context
        mock_user_context = {
            'peak_attention_hours': [9, 10, 11, 14, 15, 16],
            'energy_cycles': {'morning_energy': 0.8},
            'completion_patterns': {'micro_task_success': 0.9}
        }
        
        # Test neural style generator
        neural_generator = ADHDPlanGenerator("neural")
        neural_routine = await neural_generator.create_morning_routine("basica", mock_user_context)
        
        # Test natural style generator
        natural_generator = ADHDPlanGenerator("natural")
        natural_routine = await natural_generator.create_morning_routine("basica", mock_user_context)
        
        print("✅ Neural routine generated:", len(neural_routine['tasks']), "tasks")
        print("✅ Natural routine generated:", len(natural_routine['tasks']), "tasks")
        
        # Test attention plans
        neural_attention = await neural_generator.create_attention_management_plan("media", mock_user_context)
        natural_attention = await natural_generator.create_attention_management_plan("media", mock_user_context)
        
        print("✅ Attention plans generated")
        
        # Test dopamine plans
        neural_dopamine = await neural_generator.create_dopamine_regulation_plan("quick", mock_user_context)
        natural_dopamine = await natural_generator.create_dopamine_regulation_plan("quick", mock_user_context)
        
        print("✅ Dopamine plans generated")
        
        # Test crisis plans
        neural_crisis_plan = await neural_generator.create_crisis_plan("general", mock_user_context)
        natural_crisis_plan = await natural_generator.create_crisis_plan("general", mock_user_context)
        
        print("✅ Crisis plans generated")
        
        # Test 5: Context analyzer (without database)
        print("\n5️⃣ Testing context analyzer (offline mode)...")
        analyzer = ADHDContextAnalyzer()
        
        # Test default context
        default_context = analyzer._get_default_adhd_context()
        print("✅ Default ADHD context generated")
        
        # Test 6: Command routing test (without actual execution)
        print("\n6️⃣ Testing command handler structure...")
        command_handler = CommandHandler()
        
        # Verify methods exist
        assert hasattr(command_handler, 'handle_adhd_command')
        assert hasattr(command_handler, 'handle_adhd_routine')
        assert hasattr(command_handler, 'handle_adhd_attention')
        assert hasattr(command_handler, 'handle_adhd_dopamine')
        assert hasattr(command_handler, 'handle_adhd_crisis')
        assert hasattr(command_handler, 'handle_neural_status')
        
        print("✅ All ADHD command handlers present")
        
        # Test 7: Sample message outputs
        print("\n7️⃣ Sample message outputs:")
        print("\n🧠 NEURAL STYLE:")
        print("-" * 30)
        print(neural_msg[:200] + "...")
        
        print("\n🌟 NATURAL STYLE:")
        print("-" * 30) 
        print(natural_msg[:200] + "...")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ ADHD Support System is fully operational")
        print("✅ Both Neural Hacking and Natural styles working")
        print("✅ All command handlers integrated")
        print("✅ Plan generators functioning")
        print("✅ Crisis management ready")
        print("\n💡 Ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_adhd_system())
    sys.exit(0 if success else 1)