"""
ADHD Plan Generator
Creates specialized plans for ADHD users with dual language support
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from loguru import logger

class ADHDPlanGenerator:
    """Generador de planes específicos para ADHD"""
    
    # Principios de diseño basados en investigación ADHD
    ADHD_DESIGN_PRINCIPLES = {
        'max_task_duration': 25,  # Máximo 25 minutos por tarea
        'break_frequency': 5,     # Descanso cada 5 tareas
        'reward_frequency': 3,    # Recompensa cada 3 tareas
        'reminder_interval': 15,  # Recordatorio cada 15 minutos
        'flexibility_buffer': 0.3 # 30% de buffer para días difíciles
    }
    
    def __init__(self, language_style: str = "natural"):
        """
        Initialize with language style
        
        Args:
            language_style: "neural" or "natural"
        """
        self.language_style = language_style
        from .language_formatter import ADHDLanguageFormatter
        self.formatter = ADHDLanguageFormatter(language_style)
    
    async def create_morning_routine(self, complexity: str, user_context: dict) -> dict:
        """Crea rutina matutina ADHD-friendly"""
        
        if complexity == 'simple' or complexity == 'basica':
            tasks = self._get_simple_morning_tasks()
            plan_name = "Rutina Matutina Básica" if self.language_style == "natural" else "MORNING_PROTOCOL_BASIC"
        else:  # completa o compleja
            tasks = self._get_complete_morning_tasks()
            plan_name = "Rutina Matutina Completa" if self.language_style == "natural" else "MORNING_PROTOCOL_FULL"
        
        return self._build_adhd_plan(
            name=plan_name,
            tasks=tasks,
            plan_type="rutina_matutina",
            user_context=user_context
        )
    
    def _get_simple_morning_tasks(self) -> List[Dict[str, Any]]:
        """Tareas simples para rutina matutina"""
        
        if self.language_style == "neural":
            return [
                {'task': 'WAKEUP_PROTOCOL::disable_snooze', 'description': 'Activar consciencia sin delay', 'duration': 1, 'reward': 'system_boot'},
                {'task': 'HYDRATION_MODULE::execute', 'description': 'Optimizar hidratación neural', 'duration': 1, 'reward': 'biological_boost'},
                {'task': 'SENSORY_REFRESH::face_protocol', 'description': 'Activar sensores faciales', 'duration': 2, 'reward': 'alertness_increase'},
                {'task': 'APPEARANCE_OPTIMIZATION::auto_dress', 'description': 'Configurar apariencia diaria', 'duration': 5, 'reward': 'confidence_boost'},
                {'task': 'FUEL_INTAKE::morning_nutrition', 'description': 'Cargar combustible cerebral', 'duration': 10, 'reward': 'energy_stabilization'},
                {'task': 'MEDICATION_PROTOCOL::if_applicable', 'description': 'Ejecutar protocolo farmacológico', 'duration': 1, 'reward': 'neural_optimization'},
                {'task': 'PRIORITY_SCAN::daily_targets', 'description': 'Scanear objetivos del día', 'duration': 5, 'reward': 'clarity_enhancement'}
            ]
        else:
            return [
                {'task': 'Levantarse sin snooze', 'description': 'Un pequeño acto de amor propio', 'duration': 1, 'reward': 'momentum'},
                {'task': 'Tomar un vaso de agua', 'description': 'Despertar tu cuerpo gentilmente', 'duration': 1, 'reward': 'bienestar'},
                {'task': 'Lavarse la cara', 'description': 'Sentir la frescura que te despierta', 'duration': 2, 'reward': 'claridad'},
                {'task': 'Vestirse con ropa cómoda', 'description': 'Elegir comodidad sobre perfección', 'duration': 5, 'reward': 'confianza'},
                {'task': 'Desayunar algo nutritivo', 'description': 'Nutrir tu cerebro maravilloso', 'duration': 10, 'reward': 'energía'},
                {'task': 'Tomar medicación (si aplica)', 'description': 'Cuidar tu bienestar mental', 'duration': 1, 'reward': 'autocuidado'},
                {'task': 'Revisar 3 prioridades del día', 'description': 'Enfocar tu mente brillante', 'duration': 5, 'reward': 'propósito'}
            ]
    
    def _get_complete_morning_tasks(self) -> List[Dict[str, Any]]:
        """Tareas completas para rutina matutina"""
        
        basic_tasks = self._get_simple_morning_tasks()
        
        if self.language_style == "neural":
            additional_tasks = [
                {'task': 'EXERCISE_MODULE::light_activation', 'description': 'Activar sistemas cardiovasculares', 'duration': 10, 'reward': 'endorphin_release'},
                {'task': 'MEDITATION_PROTOCOL::mindfulness_v2', 'description': 'Calibrar sistema de atención', 'duration': 5, 'reward': 'focus_enhancement'},
                {'task': 'WORKSPACE_OPTIMIZATION::environment_prep', 'description': 'Configurar entorno productivo', 'duration': 5, 'reward': 'efficiency_boost'},
                {'task': 'COMMUNICATION_CHECK::message_scan', 'description': 'Procesar comunicaciones prioritarias', 'duration': 3, 'reward': 'connectivity'}
            ]
        else:
            additional_tasks = [
                {'task': 'Movimiento ligero', 'description': 'Despertar tu cuerpo con cariño', 'duration': 10, 'reward': 'vitalidad'},
                {'task': 'Respiración consciente', 'description': 'Conectar contigo mismo', 'duration': 5, 'reward': 'calma'},
                {'task': 'Organizar espacio de trabajo', 'description': 'Crear un ambiente que te apoye', 'duration': 5, 'reward': 'orden'},
                {'task': 'Revisar mensajes importantes', 'description': 'Mantenerte conectado', 'duration': 3, 'reward': 'conexión'}
            ]
        
        return basic_tasks + additional_tasks
    
    async def create_attention_management_plan(self, attention_span: str, user_context: dict) -> dict:
        """Crea plan de gestión de atención personalizado"""
        
        # Configuración basada en capacidad de atención
        if attention_span in ['corta', 'short']:
            work_blocks = 15
            break_duration = 5
            sessions_per_day = 8
            plan_name = "Atención Corta - Intensiva" if self.language_style == "natural" else "ATTENTION_PROTOCOL_SHORT"
        elif attention_span in ['media', 'medium']:
            work_blocks = 25
            break_duration = 5
            sessions_per_day = 6
            plan_name = "Atención Media - Balanceada" if self.language_style == "natural" else "ATTENTION_PROTOCOL_MEDIUM"
        else:  # larga, long
            work_blocks = 45
            break_duration = 15
            sessions_per_day = 4
            plan_name = "Atención Extendida - Profunda" if self.language_style == "natural" else "ATTENTION_PROTOCOL_EXTENDED"
        
        # Crear sesiones de trabajo a lo largo del día
        optimal_hours = user_context.get('peak_attention_hours', [9, 10, 11, 14, 15, 16])
        
        tasks = []
        for i in range(sessions_per_day):
            hour = optimal_hours[i % len(optimal_hours)]
            
            # Tarea de trabajo enfocado
            if self.language_style == "neural":
                focus_task = {
                    'task': f'FOCUS_SESSION_#{i+1:02d}',
                    'description': f'Sesión de trabajo concentrado por {work_blocks} minutos',
                    'duration': work_blocks,
                    'time': f'{hour:02d}:00',
                    'type': 'focus_session',
                    'reward': 'cognitive_boost'
                }
            else:
                focus_task = {
                    'task': f'Sesión de Enfoque #{i+1}',
                    'description': f'Tiempo para brillar: {work_blocks} minutos de concentración pura',
                    'duration': work_blocks,
                    'time': f'{hour:02d}:00',
                    'type': 'focus_session',
                    'reward': 'satisfacción'
                }
            
            tasks.append(focus_task)
            
            # Descanso después de cada sesión (excepto la última)
            if i < sessions_per_day - 1:
                if self.language_style == "neural":
                    break_task = {
                        'task': f'RECOVERY_CYCLE_#{i+1:02d}',
                        'description': f'Descanso activo de {break_duration} min - recharge neural systems',
                        'duration': break_duration,
                        'time': f'{hour:02d}:{work_blocks:02d}',
                        'type': 'active_break',
                        'reward': 'system_refresh'
                    }
                else:
                    break_task = {
                        'task': f'Descanso Reparador #{i+1}',
                        'description': f'{break_duration} min para recargar: muévete, respira, hidrata',
                        'duration': break_duration,
                        'time': f'{hour:02d}:{work_blocks:02d}',
                        'type': 'active_break',
                        'reward': 'renovación'
                    }
                
                tasks.append(break_task)
        
        return self._build_adhd_plan(
            name=plan_name,
            tasks=tasks,
            plan_type="atencion",
            user_context=user_context
        )
    
    async def create_dopamine_regulation_plan(self, plan_type: str, user_context: dict) -> dict:
        """Crea plan para regular dopamina naturalmente"""
        
        if plan_type in ['boost', 'quick']:
            tasks = self._get_dopamine_boost_tasks()
            plan_name = "Boost de Energía Rápido" if self.language_style == "natural" else "DOPAMINE_BOOST_PROTOCOL"
        else:  # regulation, sustained
            tasks = self._get_dopamine_regulation_tasks()
            plan_name = "Regulación de Dopamina" if self.language_style == "natural" else "DOPAMINE_REGULATION_SYSTEM"
        
        return self._build_adhd_plan(
            name=plan_name,
            tasks=tasks,
            plan_type="dopamina",
            user_context=user_context
        )
    
    def _get_dopamine_boost_tasks(self) -> List[Dict[str, Any]]:
        """Tareas para boost rápido de dopamina"""
        
        if self.language_style == "neural":
            return [
                {'task': 'MOVEMENT_ACTIVATION::light_exercise', 'duration': 5, 'dopamine_boost': 'high'},
                {'task': 'AUDIO_STIMULATION::energizing_frequency', 'duration': 3, 'dopamine_boost': 'medium'},
                {'task': 'MICRO_ACHIEVEMENT::unlock_completion', 'duration': 2, 'dopamine_boost': 'accomplishment'},
                {'task': 'NUTRITION_OPTIMIZATION::protein_hydration', 'duration': 3, 'dopamine_boost': 'biological'},
                {'task': 'BREATHING_ENHANCEMENT::oxygen_boost', 'duration': 2, 'dopamine_boost': 'oxygenation'},
                {'task': 'SOCIAL_CONNECTION::brief_interaction', 'duration': 5, 'dopamine_boost': 'social_reward'},
                {'task': 'ORGANIZATION_PROTOCOL::micro_tidying', 'duration': 10, 'dopamine_boost': 'order_satisfaction'}
            ]
        else:
            return [
                {'task': 'Movimiento energizante (5 min)', 'description': 'Despertar tu cuerpo y mente', 'duration': 5, 'dopamine_boost': 'high'},
                {'task': 'Música que te emocione', 'description': 'Dejar que el ritmo eleve tu ánimo', 'duration': 3, 'dopamine_boost': 'medium'},
                {'task': 'Una tarea súper fácil', 'description': 'Ganar momentum con una victoria rápida', 'duration': 2, 'dopamine_boost': 'accomplishment'},
                {'task': 'Hidratarte + snack saludable', 'description': 'Nutrir tu cerebro con amor', 'duration': 3, 'dopamine_boost': 'biological'},
                {'task': 'Respiración energizante', 'description': 'Oxigenar tu mente brillante', 'duration': 2, 'dopamine_boost': 'oxygenation'},
                {'task': 'Contacto social breve', 'description': 'Conectar con alguien especial', 'duration': 5, 'dopamine_boost': 'social_reward'},
                {'task': 'Organizar algo pequeño', 'description': 'Crear orden en tu espacio', 'duration': 10, 'dopamine_boost': 'order_satisfaction'}
            ]
    
    def _get_dopamine_regulation_tasks(self) -> List[Dict[str, Any]]:
        """Tareas para regulación sostenida de dopamina"""
        
        if self.language_style == "neural":
            return [
                {'task': 'MORNING_PROTOCOL::dopamine_optimization', 'duration': 30, 'type': 'routine'},
                {'task': 'CREATIVE_EXPRESSION::artistic_output', 'duration': 20, 'type': 'creative'},
                {'task': 'SKILL_BUILDING::progressive_learning', 'duration': 25, 'type': 'growth'},
                {'task': 'NATURE_INTERFACE::outdoor_connection', 'duration': 15, 'type': 'restoration'},
                {'task': 'GRATITUDE_PROCESSING::positive_recognition', 'duration': 5, 'type': 'mindfulness'},
                {'task': 'ACHIEVEMENT_TRACKING::progress_visualization', 'duration': 10, 'type': 'motivation'}
            ]
        else:
            return [
                {'task': 'Rutina matutina consciente', 'description': 'Comenzar el día con intención', 'duration': 30, 'type': 'routine'},
                {'task': 'Momento creativo', 'description': 'Expresar tu creatividad única', 'duration': 20, 'type': 'creative'},
                {'task': 'Aprender algo nuevo', 'description': 'Alimentar tu curiosidad natural', 'duration': 25, 'type': 'growth'},
                {'task': 'Tiempo en la naturaleza', 'description': 'Conectar con el mundo exterior', 'duration': 15, 'type': 'restoration'},
                {'task': 'Momento de gratitud', 'description': 'Reconocer lo bueno en tu vida', 'duration': 5, 'type': 'mindfulness'},
                {'task': 'Celebrar tu progreso', 'description': 'Reconocer hasta dónde has llegado', 'duration': 10, 'type': 'motivation'}
            ]
    
    async def create_crisis_plan(self, crisis_type: str, user_context: dict) -> dict:
        """Crea plan de crisis para días difíciles"""
        
        if crisis_type in ['overwhelm', 'overflow']:
            tasks = self._get_overwhelm_crisis_tasks()
            plan_name = "Plan Anti-Overwhelm" if self.language_style == "natural" else "OVERFLOW_RECOVERY_PROTOCOL"
        elif crisis_type in ['executive', 'dysfunction']:
            tasks = self._get_executive_crisis_tasks()
            plan_name = "Apoyo Función Ejecutiva" if self.language_style == "natural" else "EXECUTIVE_RECOVERY_SYSTEM"
        else:  # general
            tasks = self._get_general_crisis_tasks()
            plan_name = "Plan de Día Difícil" if self.language_style == "natural" else "GENERAL_CRISIS_PROTOCOL"
        
        return self._build_adhd_plan(
            name=plan_name,
            tasks=tasks,
            plan_type="crisis",
            user_context=user_context,
            is_crisis=True
        )
    
    def _get_general_crisis_tasks(self) -> List[Dict[str, Any]]:
        """Tareas esenciales para crisis general"""
        
        if self.language_style == "neural":
            return [
                {'task': 'BREATHING_STABILIZATION::emergency_calm', 'duration': 2, 'priority': 'critical'},
                {'task': 'HYDRATION_EMERGENCY::water_intake', 'duration': 1, 'priority': 'critical'},
                {'task': 'NUTRITION_MINIMUM::basic_fuel', 'duration': 5, 'priority': 'essential'},
                {'task': 'SUPPORT_CONNECTION::human_contact', 'duration': 10, 'priority': 'recovery'},
                {'task': 'MICRO_WIN::tiny_accomplishment', 'duration': 2, 'priority': 'momentum'}
            ]
        else:
            return [
                {'task': 'Respirar profundamente por 2 min', 'description': 'Esto no es una emergencia. Solo respira.', 'duration': 2, 'priority': 'critical'},
                {'task': 'Tomar agua', 'description': 'Tu cuerpo te necesita hidratado', 'duration': 1, 'priority': 'critical'},
                {'task': 'Comer algo, lo que sea', 'description': 'Nutrir tu cerebro, sin juzgar', 'duration': 5, 'priority': 'essential'},
                {'task': 'Hablar con alguien querido', 'description': 'No tienes que hacer esto solo', 'duration': 10, 'priority': 'recovery'},
                {'task': 'Una cosa súper pequeña', 'description': 'Cualquier micro-paso cuenta', 'duration': 2, 'priority': 'momentum'}
            ]
    
    def _get_overwhelm_crisis_tasks(self) -> List[Dict[str, Any]]:
        """Tareas específicas para overwhelm"""
        
        if self.language_style == "neural":
            return [
                {'task': 'SYSTEM_PAUSE::full_stop_5min', 'duration': 5, 'type': 'emergency_break'},
                {'task': 'SENSORY_GROUNDING::5_4_3_2_1_protocol', 'duration': 3, 'type': 'grounding'},
                {'task': 'BRAIN_DUMP::data_extraction', 'duration': 10, 'type': 'cognitive_unload'},
                {'task': 'PRIORITY_FILTER::select_one_target', 'duration': 5, 'type': 'focus_narrowing'},
                {'task': 'TASK_SUSPENSION::defer_non_critical', 'duration': 2, 'type': 'load_reduction'}
            ]
        else:
            return [
                {'task': 'Parar todo por 5 minutos', 'description': 'Permítete una pausa total', 'duration': 5, 'type': 'emergency_break'},
                {'task': 'Técnica 5-4-3-2-1', 'description': '5 cosas que ves, 4 que tocas, 3 que oyes...', 'duration': 3, 'type': 'grounding'},
                {'task': 'Vaciar tu mente en papel', 'description': 'Escribe todo lo que te preocupa', 'duration': 10, 'type': 'cognitive_unload'},
                {'task': 'Elegir SOLO 1 cosa para hoy', 'description': 'Una sola prioridad, nada más', 'duration': 5, 'type': 'focus_narrowing'},
                {'task': 'Posponer el resto', 'description': 'El mundo no se va a acabar', 'duration': 2, 'type': 'load_reduction'}
            ]
    
    def _get_executive_crisis_tasks(self) -> List[Dict[str, Any]]:
        """Tareas para disfunción ejecutiva"""
        
        if self.language_style == "neural":
            return [
                {'task': 'EXTERNAL_STRUCTURE::timer_activation', 'duration': 1, 'type': 'scaffolding'},
                {'task': 'TASK_DECOMPOSITION::micro_breakdown', 'duration': 5, 'type': 'simplification'},
                {'task': 'ENVIRONMENT_OPTIMIZATION::distraction_removal', 'duration': 3, 'type': 'setup'},
                {'task': 'BODY_DOUBLING::virtual_companion', 'duration': 0, 'type': 'support'},
                {'task': 'REWARD_PRELOADING::dopamine_scheduling', 'duration': 2, 'type': 'motivation'}
            ]
        else:
            return [
                {'task': 'Poner un timer', 'description': 'Dejar que el tiempo te guíe', 'duration': 1, 'type': 'scaffolding'},
                {'task': 'Dividir en pasos micro', 'description': 'Hacer todo súper simple', 'duration': 5, 'type': 'simplification'},
                {'task': 'Limpiar distracciones', 'description': 'Crear un espacio que te apoye', 'duration': 3, 'type': 'setup'},
                {'task': 'Buscar compañía virtual', 'description': 'Trabajar "con" alguien más', 'duration': 0, 'type': 'support'},
                {'task': 'Planear tu recompensa', 'description': 'Decidir cómo celebrarás', 'duration': 2, 'type': 'motivation'}
            ]
    
    def _build_adhd_plan(self, name: str, tasks: List[Dict[str, Any]], plan_type: str, 
                        user_context: dict, is_crisis: bool = False) -> dict:
        """Construye plan con características específicas de ADHD"""
        
        # Adaptar horarios a patrones del usuario
        optimal_start = user_context.get('peak_attention_hours', [9])[0] if not is_crisis else datetime.now().hour
        
        plan_tasks = []
        current_time = datetime.now().replace(hour=optimal_start, minute=0, second=0, microsecond=0)
        
        for i, task in enumerate(tasks):
            # Tiempo específico o progresivo
            if 'time' in task:
                task_time = datetime.now().replace(
                    hour=int(task['time'].split(':')[0]),
                    minute=int(task['time'].split(':')[1]),
                    second=0,
                    microsecond=0
                )
            else:
                # Para crisis, empezar inmediatamente
                if is_crisis:
                    task_time = datetime.now() + timedelta(minutes=sum(t.get('duration', 0) for t in tasks[:i]))
                else:
                    task_time = current_time + timedelta(minutes=sum(t.get('duration', 0) for t in tasks[:i]))
            
            plan_task = {
                'title': task['task'],
                'description': task.get('description', task['task']),
                'datetime': task_time.isoformat(),
                'duration_minutes': task.get('duration', 5),
                'priority': 'alta' if is_crisis else 'media',
                'category': 'ADHD',
                'reward_type': task.get('reward', 'completion'),
                'adhd_specific': True,
                'crisis_mode': is_crisis
            }
            plan_tasks.append(plan_task)
        
        return {
            'id': str(uuid.uuid4()),
            'name': name,
            'type': plan_type,
            'adhd_optimized': True,
            'language_style': self.language_style,
            'tasks': plan_tasks,
            'crisis_mode': is_crisis,
            'total_duration': sum(task.get('duration', 5) for task in tasks),
            'task_count': len(plan_tasks)
        }