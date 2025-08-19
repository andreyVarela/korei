"""
ADHD Context Analyzer
Analyzes user patterns to optimize ADHD support plans
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import statistics
from loguru import logger

class ADHDContextAnalyzer:
    """Analiza patrones específicos de ADHD en el comportamiento del usuario"""
    
    async def analyze_adhd_patterns(self, user_id: str) -> dict:
        """Analiza patrones completos de ADHD del usuario"""
        
        try:
            # Obtener datos de los últimos 60 días para análisis profundo
            from core.supabase import supabase
            entries = await supabase.get_user_entries(user_id, days=60)
            
            if not entries:
                # Si no hay datos, usar defaults seguros
                return self._get_default_adhd_context()
            
            analysis = {
                'user_id': user_id,
                'analysis_date': datetime.now().isoformat(),
                'data_points': len(entries),
                'attention_patterns': self._analyze_attention_spans(entries),
                'energy_cycles': self._analyze_energy_fluctuations(entries),
                'completion_patterns': self._analyze_task_completion_by_size(entries),
                'time_of_day_performance': self._analyze_peak_hours(entries),
                'hyperfocus_indicators': self._detect_hyperfocus_sessions(entries),
                'overwhelm_triggers': self._identify_overwhelm_patterns(entries),
                'dopamine_activities': self._track_mood_boosting_tasks(entries),
                'executive_function_load': self._assess_executive_function(entries)
            }
            
            # Calcular recomendaciones basadas en el análisis
            analysis['recommendations'] = self._generate_adhd_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing ADHD patterns for user {user_id}: {e}")
            return self._get_default_adhd_context()
    
    def _get_default_adhd_context(self) -> dict:
        """Contexto por defecto seguro para usuarios nuevos"""
        return {
            'attention_patterns': {
                'average_focus_duration': 20,
                'optimal_session_length': 25,
                'peak_attention_hours': [9, 10, 11],
                'attention_variability': 15
            },
            'energy_cycles': {
                'morning_energy': 0.8,
                'afternoon_energy': 0.6,
                'evening_energy': 0.4,
                'energy_consistency': 0.5
            },
            'completion_patterns': {
                'micro_task_success': 0.85,
                'medium_task_success': 0.65,
                'large_task_success': 0.35,
                'overall_completion_rate': 0.7
            },
            'recommendations': {
                'optimal_task_duration': 15,
                'break_frequency': 'every_3_tasks',
                'reward_frequency': 'every_task',
                'crisis_support_level': 'medium'
            }
        }
    
    def _analyze_attention_spans(self, entries: List[dict]) -> dict:
        """Analiza capacidad de atención y patrones de concentración"""
        
        task_durations = []
        completion_times = []
        
        for entry in entries:
            if entry.get('completed_at') and entry.get('created_at'):
                # Calcular duración de la tarea
                created = datetime.fromisoformat(entry['created_at'])
                completed = datetime.fromisoformat(entry['completed_at'])
                duration_minutes = (completed - created).total_seconds() / 60
                
                # Filtrar duraciones realistas (5 min a 4 horas)
                if 5 <= duration_minutes <= 240:
                    task_durations.append(duration_minutes)
                    
                    # Hora del día de completación
                    completion_times.append(completed.hour)
        
        if not task_durations:
            return {
                'average_focus_duration': 25,
                'optimal_session_length': 25,
                'peak_attention_hours': [9, 10, 11],
                'attention_variability': 10
            }
        
        avg_duration = statistics.mean(task_durations)
        variability = statistics.stdev(task_durations) if len(task_durations) > 1 else 10
        
        # Encontrar horas pico basadas en completaciones exitosas
        peak_hours = self._find_peak_hours(completion_times)
        
        # Calcular duración óptima de sesión (ligeramente menor al promedio)
        optimal_session = max(15, min(45, int(avg_duration * 0.9)))
        
        return {
            'average_focus_duration': round(avg_duration, 1),
            'optimal_session_length': optimal_session,
            'peak_attention_hours': peak_hours,
            'attention_variability': round(variability, 1),
            'total_samples': len(task_durations)
        }
    
    def _find_peak_hours(self, completion_times: List[int]) -> List[int]:
        """Encuentra las horas del día con más completaciones exitosas"""
        
        if not completion_times:
            return [9, 10, 11]  # Default morning hours
        
        # Contar completaciones por hora
        hour_counts = {}
        for hour in completion_times:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Ordenar por frecuencia y tomar las top 3-5 horas
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, count in sorted_hours[:5]]
        
        # Asegurar al menos 3 horas y en orden
        if len(peak_hours) < 3:
            peak_hours.extend([9, 10, 11])
        
        return sorted(list(set(peak_hours)))[:5]
    
    def _analyze_energy_fluctuations(self, entries: List[dict]) -> dict:
        """Analiza patrones de energía a lo largo del día y semana"""
        
        morning_completions = 0  # 6-12
        afternoon_completions = 0  # 12-18
        evening_completions = 0  # 18-24
        total_completions = 0
        
        weekday_completions = 0
        weekend_completions = 0
        
        for entry in entries:
            if entry.get('completed_at'):
                completed_dt = datetime.fromisoformat(entry['completed_at'])
                hour = completed_dt.hour
                weekday = completed_dt.weekday()
                
                total_completions += 1
                
                # Análisis por tiempo del día
                if 6 <= hour < 12:
                    morning_completions += 1
                elif 12 <= hour < 18:
                    afternoon_completions += 1
                elif 18 <= hour <= 24 or hour < 6:
                    evening_completions += 1
                
                # Análisis por día de la semana
                if weekday < 5:  # Lunes a Viernes
                    weekday_completions += 1
                else:  # Sábado y Domingo
                    weekend_completions += 1
        
        if total_completions == 0:
            return {
                'morning_energy': 0.8,
                'afternoon_energy': 0.6,
                'evening_energy': 0.4,
                'weekday_performance': 0.7,
                'weekend_performance': 0.5,
                'energy_consistency': 0.5
            }
        
        # Calcular porcentajes de energía
        morning_ratio = morning_completions / total_completions
        afternoon_ratio = afternoon_completions / total_completions
        evening_ratio = evening_completions / total_completions
        
        weekday_ratio = weekday_completions / total_completions if total_completions > 0 else 0.7
        weekend_ratio = weekend_completions / total_completions if total_completions > 0 else 0.3
        
        # Calcular consistencia (menos variabilidad = más consistencia)
        energy_values = [morning_ratio, afternoon_ratio, evening_ratio]
        consistency = 1 - (statistics.stdev(energy_values) if len(energy_values) > 1 else 0.3)
        
        return {
            'morning_energy': round(morning_ratio, 2),
            'afternoon_energy': round(afternoon_ratio, 2),
            'evening_energy': round(evening_ratio, 2),
            'weekday_performance': round(weekday_ratio, 2),
            'weekend_performance': round(weekend_ratio, 2),
            'energy_consistency': round(max(0, min(1, consistency)), 2)
        }
    
    def _analyze_task_completion_by_size(self, entries: List[dict]) -> dict:
        """Analiza tasa de completación según el tamaño/complejidad de las tareas"""
        
        # Clasificar tareas por duración estimada o palabras en descripción
        micro_tasks = []  # < 15 min o descripción corta
        medium_tasks = []  # 15-60 min o descripción media
        large_tasks = []  # > 60 min o descripción larga
        
        for entry in entries:
            description = entry.get('description', '')
            status = entry.get('status', 'pending')
            
            # Clasificar por longitud de descripción como proxy de complejidad
            desc_length = len(description.split())
            
            task_data = {
                'status': status,
                'completed': status == 'completed',
                'description_length': desc_length
            }
            
            if desc_length <= 3:
                micro_tasks.append(task_data)
            elif desc_length <= 8:
                medium_tasks.append(task_data)
            else:
                large_tasks.append(task_data)
        
        def calculate_success_rate(tasks):
            if not tasks:
                return 0.0
            completed = sum(1 for task in tasks if task['completed'])
            return completed / len(tasks)
        
        micro_success = calculate_success_rate(micro_tasks)
        medium_success = calculate_success_rate(medium_tasks)
        large_success = calculate_success_rate(large_tasks)
        
        total_tasks = len(entries)
        completed_tasks = len([e for e in entries if e.get('status') == 'completed'])
        overall_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.7
        
        return {
            'micro_task_success': round(micro_success, 2),
            'medium_task_success': round(medium_success, 2),
            'large_task_success': round(large_success, 2),
            'overall_completion_rate': round(overall_rate, 2),
            'micro_task_count': len(micro_tasks),
            'medium_task_count': len(medium_tasks),
            'large_task_count': len(large_tasks),
            'preference_insight': self._analyze_task_preferences(micro_success, medium_success, large_success)
        }
    
    def _analyze_task_preferences(self, micro: float, medium: float, large: float) -> str:
        """Analiza preferencias de tipo de tarea"""
        
        if micro > 0.8 and medium < 0.6:
            return "strong_micro_preference"
        elif medium > micro and medium > large:
            return "balanced_medium_preference" 
        elif large > 0.6:
            return "hyperfocus_capable"
        elif micro > medium > large:
            return "decreasing_with_complexity"
        else:
            return "variable_pattern"
    
    def _detect_hyperfocus_sessions(self, entries: List[dict]) -> dict:
        """Detecta patrones de hiperfoco"""
        
        # Agrupar completaciones por día
        daily_completions = {}
        
        for entry in entries:
            if entry.get('completed_at'):
                completed_dt = datetime.fromisoformat(entry['completed_at'])
                date_key = completed_dt.date()
                
                if date_key not in daily_completions:
                    daily_completions[date_key] = []
                daily_completions[date_key].append(entry)
        
        hyperfocus_sessions = []
        high_productivity_days = 0
        
        for date, day_entries in daily_completions.items():
            task_count = len(day_entries)
            
            # Detectar días de alta productividad (posible hiperfoco)
            if task_count >= 8:  # 8+ tareas en un día
                high_productivity_days += 1
                hyperfocus_sessions.append({
                    'date': date.isoformat(),
                    'tasks_completed': task_count,
                    'type': 'high_productivity',
                    'intensity': min(100, task_count * 10)
                })
            
            # Detectar sesiones de trabajo concentrado (muchas tareas en pocas horas)
            if task_count >= 5:
                times = [datetime.fromisoformat(e['completed_at']).hour for e in day_entries]
                if max(times) - min(times) <= 4:  # Todas en 4 horas o menos
                    hyperfocus_sessions.append({
                        'date': date.isoformat(),
                        'tasks_completed': task_count,
                        'hours_span': max(times) - min(times),
                        'type': 'concentrated_session',
                        'intensity': task_count * 15
                    })
        
        return {
            'hyperfocus_frequency': len(hyperfocus_sessions),
            'high_productivity_days': high_productivity_days,
            'recent_sessions': hyperfocus_sessions[-5:],  # Últimas 5 sesiones
            'average_intensity': statistics.mean([s.get('intensity', 50) for s in hyperfocus_sessions]) if hyperfocus_sessions else 50,
            'hyperfocus_capable': len(hyperfocus_sessions) > 2
        }
    
    def _identify_overwhelm_patterns(self, entries: List[dict]) -> dict:
        """Identifica patrones de overwhelm y días difíciles"""
        
        # Buscar días con muchas tareas creadas pero pocas completadas
        daily_stats = {}
        
        for entry in entries:
            created_dt = datetime.fromisoformat(entry['created_at'])
            date_key = created_dt.date()
            
            if date_key not in daily_stats:
                daily_stats[date_key] = {'created': 0, 'completed': 0}
            
            daily_stats[date_key]['created'] += 1
            
            if entry.get('status') == 'completed':
                daily_stats[date_key]['completed'] += 1
        
        overwhelm_days = []
        low_productivity_days = 0
        
        for date, stats in daily_stats.items():
            created = stats['created']
            completed = stats['completed']
            completion_rate = completed / created if created > 0 else 0
            
            # Detectar posible overwhelm: muchas tareas creadas, pocas completadas
            if created >= 5 and completion_rate < 0.3:
                overwhelm_days.append({
                    'date': date.isoformat(),
                    'tasks_created': created,
                    'tasks_completed': completed,
                    'completion_rate': round(completion_rate, 2),
                    'overwhelm_severity': (created - completed) / created
                })
            
            # Detectar días de baja productividad
            if completion_rate < 0.2 and created > 0:
                low_productivity_days += 1
        
        return {
            'overwhelm_episodes': len(overwhelm_days),
            'low_productivity_days': low_productivity_days,
            'recent_overwhelm': overwhelm_days[-3:],  # Últimos 3 episodios
            'overwhelm_risk': len(overwhelm_days) / len(daily_stats) if daily_stats else 0,
            'resilience_pattern': 'good' if len(overwhelm_days) < 3 else 'needs_support'
        }
    
    def _track_mood_boosting_tasks(self, entries: List[dict]) -> dict:
        """Identifica actividades que típicamente mejoran el estado de ánimo"""
        
        # Palabras clave que típicamente generan dopamina
        dopamine_keywords = {
            'exercise': ['ejercicio', 'caminar', 'correr', 'gym', 'yoga', 'deportes'],
            'creative': ['crear', 'dibujar', 'escribir', 'música', 'arte', 'diseño'],
            'social': ['amigos', 'familia', 'llamar', 'reunión', 'socializar'],
            'learning': ['aprender', 'leer', 'curso', 'estudiar', 'investigar'],
            'organizing': ['organizar', 'limpiar', 'ordenar', 'planificar'],
            'nature': ['parque', 'naturaleza', 'aire libre', 'jardín', 'playa'],
            'achievement': ['completar', 'terminar', 'lograr', 'ganar', 'éxito']
        }
        
        category_completions = {category: [] for category in dopamine_keywords}
        
        for entry in entries:
            description = entry.get('description', '').lower()
            
            for category, keywords in dopamine_keywords.items():
                if any(keyword in description for keyword in keywords):
                    category_completions[category].append({
                        'completed': entry.get('status') == 'completed',
                        'description': entry.get('description', '')
                    })
        
        # Calcular tasa de éxito por categoría
        category_success = {}
        for category, tasks in category_completions.items():
            if tasks:
                success_rate = sum(1 for task in tasks if task['completed']) / len(tasks)
                category_success[category] = {
                    'success_rate': round(success_rate, 2),
                    'total_tasks': len(tasks),
                    'recommended': success_rate > 0.7
                }
        
        return {
            'dopamine_activities': category_success,
            'top_categories': sorted(category_success.items(), 
                                   key=lambda x: x[1]['success_rate'], 
                                   reverse=True)[:3],
            'recommended_activities': [cat for cat, data in category_success.items() 
                                     if data.get('recommended', False)]
        }
    
    def _assess_executive_function(self, entries: List[dict]) -> dict:
        """Evalúa el nivel de función ejecutiva basado en patrones"""
        
        # Métricas de función ejecutiva
        planning_tasks = 0
        completion_consistency = []
        task_switching_frequency = 0
        
        # Analizar patrones de completación por semana
        weekly_completions = {}
        
        for entry in entries:
            description = entry.get('description', '').lower()
            
            # Detectar tareas de planificación
            planning_keywords = ['planificar', 'organizar', 'revisar', 'preparar', 'agenda']
            if any(keyword in description for keyword in planning_keywords):
                planning_tasks += 1
            
            # Agrupar por semana para analizar consistencia
            if entry.get('completed_at'):
                completed_dt = datetime.fromisoformat(entry['completed_at'])
                week_key = completed_dt.isocalendar()[:2]  # (año, semana)
                
                if week_key not in weekly_completions:
                    weekly_completions[week_key] = 0
                weekly_completions[week_key] += 1
        
        # Calcular consistencia semanal
        if weekly_completions:
            completion_counts = list(weekly_completions.values())
            avg_weekly = statistics.mean(completion_counts)
            consistency_score = 1 - (statistics.stdev(completion_counts) / avg_weekly) if avg_weekly > 0 else 0
        else:
            consistency_score = 0.5
        
        # Evaluar nivel de función ejecutiva
        exec_function_score = (
            min(1.0, planning_tasks / 10) * 0.3 +  # Capacidad de planificación
            max(0, min(1.0, consistency_score)) * 0.4 +  # Consistencia
            min(1.0, len(entries) / 50) * 0.3  # Productividad general
        )
        
        return {
            'executive_function_score': round(exec_function_score, 2),
            'planning_task_count': planning_tasks,
            'consistency_score': round(max(0, min(1, consistency_score)), 2),
            'weekly_average': round(statistics.mean(list(weekly_completions.values())), 1) if weekly_completions else 0,
            'function_level': (
                'high' if exec_function_score > 0.7 else
                'medium' if exec_function_score > 0.4 else
                'needs_support'
            )
        }
    
    def _generate_adhd_recommendations(self, analysis: dict) -> dict:
        """Genera recomendaciones personalizadas basadas en el análisis"""
        
        attention = analysis.get('attention_patterns', {})
        energy = analysis.get('energy_cycles', {})
        completion = analysis.get('completion_patterns', {})
        hyperfocus = analysis.get('hyperfocus_indicators', {})
        
        recommendations = {}
        
        # Recomendaciones de duración de tarea
        avg_focus = attention.get('average_focus_duration', 25)
        if avg_focus < 15:
            recommendations['optimal_task_duration'] = 10
            recommendations['session_type'] = 'micro_sessions'
        elif avg_focus < 30:
            recommendations['optimal_task_duration'] = 20
            recommendations['session_type'] = 'short_sessions'
        else:
            recommendations['optimal_task_duration'] = 30
            recommendations['session_type'] = 'standard_sessions'
        
        # Recomendaciones de horarios
        peak_hours = attention.get('peak_attention_hours', [9, 10, 11])
        recommendations['optimal_work_hours'] = peak_hours[:3]
        
        # Recomendaciones de estructura
        micro_success = completion.get('micro_task_success', 0.7)
        if micro_success > 0.8:
            recommendations['task_structure'] = 'micro_task_focused'
            recommendations['break_frequency'] = 'every_task'
        else:
            recommendations['task_structure'] = 'mixed_size'
            recommendations['break_frequency'] = 'every_3_tasks'
        
        # Recomendaciones de apoyo
        overwhelm_risk = analysis.get('overwhelm_triggers', {}).get('overwhelm_risk', 0)
        if overwhelm_risk > 0.3:
            recommendations['crisis_support_level'] = 'high'
            recommendations['daily_task_limit'] = 5
        elif overwhelm_risk > 0.1:
            recommendations['crisis_support_level'] = 'medium'
            recommendations['daily_task_limit'] = 8
        else:
            recommendations['crisis_support_level'] = 'low'
            recommendations['daily_task_limit'] = 12
        
        # Recomendaciones de hiperfoco
        if hyperfocus.get('hyperfocus_capable', False):
            recommendations['hyperfocus_management'] = 'active_monitoring'
            recommendations['max_session_length'] = 90
        else:
            recommendations['hyperfocus_management'] = 'standard'
            recommendations['max_session_length'] = 45
        
        return recommendations