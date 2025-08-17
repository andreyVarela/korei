#!/usr/bin/env python3
"""
Test the MessageFormatter functionality
"""
import asyncio
from services.formatters import message_formatter

def test_formatter():
    print("=== TESTING MESSAGE FORMATTER ===")
    
    # Test currency formatting
    print("\n1. Currency formatting:")
    test_amounts = [10000, 250000, 1500.50, 0, None]
    for amount in test_amounts:
        try:
            formatted = message_formatter.format_currency(amount) if amount is not None else "None -> Empty"
            print(f"  {amount} -> {formatted}")
        except Exception as e:
            print(f"  {amount} -> Error: {e}")
    
    # Test date formatting
    print("\n2. Date formatting:")
    test_dates = [
        "2025-08-16T01:22:00",
        "2025-08-16T13:45:30",
        "invalid_date",
        None
    ]
    for date_str in test_dates:
        try:
            formatted = message_formatter.format_date(date_str) if date_str else "None"
            print(f"  {date_str} -> {formatted}")
        except Exception as e:
            print(f"  {date_str} -> Error: {e}")
    
    # Test priority formatting
    print("\n3. Priority formatting:")
    priorities = ['alta', 'media', 'baja', 'none', None, 'invalid']
    for priority in priorities:
        try:
            formatted = message_formatter.format_priority(priority)
            print(f"  {priority} -> {formatted}")
        except Exception as e:
            print(f"  {priority} -> Error: {e}")
    
    # Test entry response formatting
    print("\n4. Entry response formatting:")
    test_result = {
        'type': 'gasto',
        'description': 'Gasto en línea de 10000',
        'amount': 10000,
        'datetime': '2025-08-16T01:22:00',
        'priority': 'media'
    }
    
    try:
        formatted_response = message_formatter.format_entry_response(test_result)
        print(f"Entry response:\n{formatted_response}")
    except Exception as e:
        print(f"Error formatting entry: {e}")
    
    # Test help message
    print("\n5. Help message:")
    try:
        help_msg = message_formatter.format_help_message()
        print(f"Help message length: {len(help_msg)} characters")
        print("First 100 chars:", help_msg[:100])
    except Exception as e:
        print(f"Error formatting help: {e}")
    
    print("\n=== FORMATTER TESTS COMPLETED ===")

if __name__ == "__main__":
    test_formatter()