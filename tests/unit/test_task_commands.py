"""
Tests para los nuevos comandos de gestión de tareas
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import pytz
from unittest.mock import AsyncMock, MagicMock, patch

from handlers.command_handler import CommandHandler
from app.config import settings

@pytest.fixture
def command_handler():
    """Fixture del command handler"""
    return CommandHandler()

@pytest.fixture
def mock_user_context():
    """Mock del contexto de usuario"""
    return {
        "id": "test-user-123",
        "whatsapp_number": "50612345678",
        "name": "Usuario Test",
        "profile": {
            "occupation": "Developer",
            "hobbies": ["coding", "gaming"]
        }
    }

@pytest.fixture
def mock_task_data():
    """Mock de datos de tareas"""
    tz = pytz.timezone(settings.timezone)
    now = datetime.now(tz)
    
    return [
        {
            "id": "task-1",
            "type": "tarea",
            "description": "Llamar al doctor",
            "datetime": now.isoformat(),
            "status": "pending",
            "priority": "alta"
        },
        {
            "id": "task-2", 
            "type": "tarea",
            "description": "Comprar leche",
            "datetime": now.isoformat(),
            "status": "pending",
            "priority": "media"
        },
        {
            "id": "task-3",
            "type": "tarea", 
            "description": "Reunión equipo",
            "datetime": now.isoformat(),
            "status": "completed",
            "priority": "alta"
        }
    ]

class TestTodayCommand:
    """Tests para el comando /today"""
    
    @pytest.mark.asyncio
    async def test_today_with_tasks(self, command_handler, mock_user_context, mock_task_data):
        """Test /today con tareas existentes"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock de la respuesta de Supabase
            mock_result = MagicMock()
            mock_result.data = mock_task_data
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_today_summary(mock_user_context)
            
            assert result["type"] == "today_summary"
            assert "Resumen de Hoy" in result["message"]
            assert "TAREAS (3)" in result["message"]
            assert "Llamar al doctor" in result["message"]
            assert "Comprar leche" in result["message"]
            assert result["has_pending_tasks"] == True
            assert len(result["buttons"]) > 0
    
    @pytest.mark.asyncio
    async def test_today_empty(self, command_handler, mock_user_context):
        """Test /today sin actividad"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock de respuesta vacía
            mock_result = MagicMock()
            mock_result.data = []
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_today_summary(mock_user_context)
            
            assert result["type"] == "today_empty"
            assert "Sin actividad registrada" in result["message"]
            assert result["buttons"] == []

class TestCompleteTaskCommand:
    """Tests para el comando /completar"""
    
    @pytest.mark.asyncio
    async def test_complete_task_success(self, command_handler, mock_user_context, mock_task_data):
        """Test completar tarea exitosamente"""
        with patch('core.supabase.supabase._get_client') as mock_client, \
             patch('core.supabase.supabase.update_entry_status') as mock_update:
            
            # Mock búsqueda de tareas
            mock_result = MagicMock()
            mock_result.data = [mock_task_data[0]]  # Solo la primera tarea
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
            
            # Mock actualización exitosa
            mock_update.return_value = mock_task_data[0]
            
            result = await command_handler.handle_complete_task("/completar doctor", mock_user_context)
            
            assert result["type"] == "task_completed"
            assert "Tarea completada!" in result["message"]
            assert "Llamar al doctor" in result["message"]
            mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, command_handler, mock_user_context):
        """Test completar tarea no encontrada"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock sin resultados
            mock_result = MagicMock()
            mock_result.data = []
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_complete_task("/completar nonexistent", mock_user_context)
            
            assert result["type"] == "no_pending_tasks"
            assert "No tienes tareas pendientes" in result["message"]
    
    @pytest.mark.asyncio
    async def test_complete_task_multiple_matches(self, command_handler, mock_user_context, mock_task_data):
        """Test con múltiples tareas que coinciden"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock múltiples resultados que coinciden
            mock_result = MagicMock()
            mock_result.data = mock_task_data[:2]  # Dos tareas pendientes
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_complete_task("/completar a", mock_user_context)
            
            # Debería encontrar múltiples coincidencias por la letra 'a'
            assert result["type"] in ["task_completed", "multiple_tasks_found", "task_not_found"]

class TestTomorrowCommand:
    """Tests para el comando /tomorrow"""
    
    @pytest.mark.asyncio
    async def test_tomorrow_with_tasks(self, command_handler, mock_user_context):
        """Test /tomorrow con tareas"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock tareas para mañana
            tz = pytz.timezone(settings.timezone)
            tomorrow = datetime.now(tz) + timedelta(days=1)
            
            tomorrow_tasks = [
                {
                    "id": "task-tomorrow-1",
                    "type": "tarea",
                    "description": "Reunión importante",
                    "datetime": tomorrow.isoformat(),
                    "status": "pending",
                    "priority": "alta"
                }
            ]
            
            mock_result = MagicMock()
            mock_result.data = tomorrow_tasks
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_tomorrow_summary(mock_user_context)
            
            assert result["type"] == "tomorrow_summary"
            assert "Mañana -" in result["message"]
            assert "TAREAS (1)" in result["message"]
            assert "Reunión importante" in result["message"]

class TestAgendaCommand:
    """Tests para el comando /agenda"""
    
    @pytest.mark.asyncio
    async def test_agenda_view(self, command_handler, mock_user_context):
        """Test vista de agenda semanal"""
        with patch('core.supabase.supabase._get_client') as mock_client:
            # Mock entradas de la semana
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            week_entries = [
                {
                    "id": "entry-1",
                    "type": "tarea",
                    "description": "Tarea de hoy",
                    "datetime": now.isoformat(),
                    "status": "pending",
                    "priority": "media"
                },
                {
                    "id": "entry-2",
                    "type": "evento",
                    "description": "Evento de mañana", 
                    "datetime": (now + timedelta(days=1)).isoformat(),
                    "status": "pending"
                }
            ]
            
            mock_result = MagicMock()
            mock_result.data = week_entries
            mock_client.return_value.table.return_value.select.return_value.eq.return_value.in_.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value = mock_result
            
            result = await command_handler.handle_agenda_view(mock_user_context)
            
            assert result["type"] == "agenda_view"
            assert "Agenda Semanal" in result["message"]
            assert "*(HOY)*" in result["message"]
            assert "*(MAÑANA)*" in result["message"]
            assert result["stats"]["total_tasks"] == 1
            assert result["stats"]["total_events"] == 1

class TestTaskCommandsIntegration:
    """Tests de integración para comandos de tareas"""
    
    @pytest.mark.asyncio
    async def test_command_routing(self, command_handler, mock_user_context):
        """Test que los comandos se enrutan correctamente"""
        
        # Test comando /today
        with patch.object(command_handler, 'handle_today_summary') as mock_today:
            mock_today.return_value = {"type": "today_summary", "message": "test"}
            
            result = await command_handler.handle_command("/today", "", mock_user_context)
            mock_today.assert_called_once_with(mock_user_context)
        
        # Test comando /hoy (alias en español)
        with patch.object(command_handler, 'handle_today_summary') as mock_today:
            mock_today.return_value = {"type": "today_summary", "message": "test"}
            
            result = await command_handler.handle_command("/hoy", "", mock_user_context)
            mock_today.assert_called_once_with(mock_user_context)
        
        # Test comando /completar
        with patch.object(command_handler, 'handle_complete_task') as mock_complete:
            mock_complete.return_value = {"type": "task_completed", "message": "test"}
            
            result = await command_handler.handle_command("/completar", "/completar test", mock_user_context)
            mock_complete.assert_called_once_with("/completar test", mock_user_context)

if __name__ == "__main__":
    pytest.main([__file__])