# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Development mode with hot reload
python main.py

# Production mode using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Using Docker
docker-compose up --build
```

### Testing
```bash
# Run all tests with coverage
coverage run -m pytest

# Generate coverage report
coverage xml

# Run specific test files
pytest tests/api/test_webhook.py
pytest tests/services/test_gemini.py
```

### Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Update dependencies (manually edit requirements.txt)
```

## Architecture Overview

Korei Assistant is a WhatsApp-based AI assistant that processes messages, audio, and images using Google's Gemini AI. The application follows a FastAPI-based microservices architecture with the following key components:

### Core Architecture
- **FastAPI Application**: Main HTTP server handling webhooks and API endpoints
- **WAHA Integration**: WhatsApp HTTP API for message handling
- **Supabase Backend**: Database and storage for user data and entries
- **Gemini AI Service**: Multi-modal AI processing (text, audio, images)

### Key Components

#### Message Flow
1. WhatsApp → WAHA → Webhook endpoint (`api/routes/webhook.py`)
2. Background task processing via `MessageHandler` (`handlers/message_handler.py`)
3. AI processing through `GeminiService` (`services/gemini.py`)
4. Database storage via Supabase client (`core/supabase.py`)
5. Response sent back through WhatsApp service

#### Service Layer
- **`services/gemini.py`**: Handles all AI processing (text, audio transcription, image analysis)
- **`services/whatsapp.py`**: WhatsApp API integration and message formatting
- **`services/audio.py`**: Audio processing utilities
- **`services/image.py`**: Image processing utilities
- **`services/scheduler.py`**: Task scheduling and reminders

#### Data Models
- User management and entry tracking via Supabase
- Structured JSON responses from Gemini with fields: type, description, amount, datetime, priority, etc.
- Support for tasks, expenses, income, events, and reminders

### Configuration
- Environment-based configuration using Pydantic Settings (`app/config.py`)
- Required environment variables: Supabase credentials, WAHA API details, Gemini API key
- Timezone-aware processing (defaults to America/Costa_Rica)

### Media Processing
- **Audio**: Direct processing with Gemini 1.5 Pro (transcription + analysis)
- **Images**: Gemini Vision for OCR, receipt parsing, and content analysis
- Temporary file handling with automatic cleanup

### Error Handling
- Comprehensive error handling with Loguru logging
- Custom middleware for error tracking (`api/middleware.py`)
- Fallback responses for AI processing failures

## Development Notes

### Adding New Message Types
1. Add handler method in `MessageHandler` class
2. Update webhook routing in `api/routes/webhook.py`
3. Extend Gemini service if AI processing is needed

### Database Schema
- Users table with WhatsApp phone numbers and metadata
- Entries table for all processed content (tasks, expenses, events)
- Voice logs table for audio processing history

### AI Processing
- Gemini models: `gemini-1.5-pro` for text/audio, `gemini-1.5-flash` for images
- Structured JSON output with strict schema validation
- Context-aware processing with user information and timestamps

### Testing Structure
- API tests in `tests/api/`
- Service tests in `tests/services/`
- Handler tests in `tests/test_handlers.py`
- Configuration in `tests/conftest.py`