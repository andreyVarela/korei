"""
Pytest configuration and fixtures for Korei Assistant tests
"""
import pytest
import asyncio
from typing import AsyncGenerator
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_user_data():
    """Mock user data for testing"""
    return {
        "id": "test-user-123",
        "whatsapp_number": "5057890123",
        "payment": True,
        "name": "Test User",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def mock_webhook_payload():
    """Mock WAHA webhook payload"""
    return {
        "event": "message",
        "session": "default",
        "payload": {
            "id": "msg_123",
            "from": "5057890123@c.us",
            "body": "Test message",
            "type": "text",
            "timestamp": 1640995200,
            "fromMe": False
        }
    }

@pytest.fixture
def mock_gemini_response():
    """Mock Gemini AI response"""
    return {
        "type": "tarea",
        "description": "Test task",
        "amount": 0,
        "datetime": "2024-01-01T10:00:00",
        "priority": "media",
        "recurrence": "none",
        "calendary": False,
        "task_category": "personal"
    }