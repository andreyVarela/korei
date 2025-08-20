"""
Dual Language Formatter for ADHD Support
Formats responses in Neural Hacking or Natural language styles
"""
import random
from typing import Dict, Any, List
from datetime import datetime

class ADHDLanguageFormatter:
    """Formateador de lenguaje dual para soporte ADHD"""
    
    def __init__(self, language_style: str = "natural"):
        """
        Initialize formatter with language style
        
        Args:
            language_style: "neural" or "natural"
        """
        self.style = language_style
        
    def format_plan_created(self, plan_data: Dict[str, Any]) -> str:
        """Formatea mensaje de plan creado"""
        
        if self.style == "neural":
            return self._format_neural_plan_created(plan_data)
        else:
            return self._format_natural_plan_created(plan_data)
    
    def _format_neural_plan_created(self, plan_data: Dict[str, Any]) -> str:
        """Estilo Neural Hacking"""
        plan_name = plan_data.get('name', 'PROTOCOL_UNKNOWN')
        tasks_count = plan_data.get('tasks_count', 0)
        duration = plan_data.get('duration_weeks', 0)
        
        return f"""🧠 NEURAL_PROTOCOL ejecutado exitosamente

├─ Module: {plan_name.upper().replace(' ', '_')}_v2.1
├─ Tasks injected: {tasks_count} optimization_cycles
├─ Duration: {duration} semanas de neural_training
├─ Expected boost: +25% cognitive_efficiency
├─ Monitoring: ACTIVE | Auto-adjust: ENABLED
└─ Next scan: 24:00:00 hrs

⚡ Protocol ready for deployment
💡 Use /neural-status para monitoreo en tiempo real"""
    
    def _format_natural_plan_created(self, plan_data: Dict[str, Any]) -> str:
        """Estilo Natural y empático"""
        plan_name = plan_data.get('name', 'Tu nuevo plan')
        tasks_count = plan_data.get('tasks_count', 0)
        duration = plan_data.get('duration_weeks', 0)
        
        return f"""🌟 {plan_name} creado con éxito

Tu cerebro ADHD merece herramientas que funcionen contigo, no contra ti.

📋 {tasks_count} pasos diseñados específicamente para tu forma de pensar
⏰ {duration} semanas de crecimiento gradual y sostenible
🎯 Cada tarea está pensada para darte esa satisfacción inmediata que necesitas

💪 Recuerda: No eres perezoso, tu cerebro simplemente funciona diferente
✨ Cada pequeño paso es una victoria que merece celebrarse"""
    
    def format_crisis_activated(self, crisis_type: str, tasks_count: int) -> str:
        """Formatea mensaje de crisis activado"""
        
        if self.style == "neural":
            return f"""🆘 RECOVERY_PROTOCOL activado

├─ Crisis Level: {crisis_type.upper()}_DETECTED
├─ Priority: SURVIVAL_MODE
├─ Non-essential tasks: SUSPENDED
├─ Emergency routines: {tasks_count} tasks LOADED
└─ Support systems: ONLINE

💊 Ejecutando MINIMAL_VIABLE_DAY.sh...
🔄 Auto-recovery iniciado | ETA: Variable"""
        else:
            return f"""🤗 Plan de apoyo activado

Detecté que hoy es uno de esos días difíciles. Está bien, todos los tenemos.

💝 He preparado {tasks_count} cosas súper simples para ayudarte
🕯️ Solo lo absolutamente esencial, sin presión
💚 Recuerda: Cuidarte a ti mismo no es opcional, es necesario

🌈 Los días difíciles también pasan. Esto es temporal."""
    
    def format_attention_session(self, session_data: Dict[str, Any]) -> str:
        """Formatea inicio de sesión de atención"""
        
        duration = session_data.get('duration', 25)
        task = session_data.get('task', 'trabajo enfocado')
        
        if self.style == "neural":
            return f"""🎯 ATTENTION_LOCK activado

├─ Target: {task.upper().replace(' ', '_')}
├─ Duration: {duration}:00 [OPTIMIZED_TIMEBLOCK]
├─ Distractions: FILTERED
├─ Dopamine rewards: SCHEDULED
└─ Background monitoring: ACTIVE

⏱️ Timer iniciado | 🔇 DND mode | 🎵 Focus_soundscape loaded"""
        else:
            return f"""🎯 Sesión de enfoque iniciada

Perfecto, vamos a concentrarnos en: {task}

⏰ {duration} minutos de atención pura - tu cerebro puede hacerlo
🌟 Recordatorios suaves programados para mantenerte en el camino
🎵 Ambiente optimizado para tu concentración

💪 Tu cerebro ADHD tiene súper poderes cuando se enfoca. ¡Vamos!"""
    
    def format_dopamine_boost(self, boost_data: Dict[str, Any]) -> str:
        """Formatea mensaje de boost de dopamina"""
        
        activities = boost_data.get('activities_count', 3)
        duration = boost_data.get('duration', 5)
        
        if self.style == "neural":
            return f"""⚡ DOPAMINE_SYNC iniciado

├─ Protocol: QUICK_BURST_v2.3
├─ Activities: {activities} dopamine_triggers
├─ Duration: {duration} minutes
├─ Expected boost: +15 neural_points
└─ Monitoring: REAL_TIME

🧬 Activating neurotransmitter optimization..."""
        else:
            return f"""✨ Boost de energía activado

Tu cerebro necesita esa chispa de motivación, y está perfecto.

🎁 {activities} actividades rápidas para despertar tu dopamina
⏱️ Solo {duration} minutos para sentirte mejor
🌈 Cada una está diseñada para darte esa satisfacción instantánea

💝 Cuidar tu bienestar mental es inteligente, no débil"""
    
    def format_hyperfocus_warning(self, session_time: int) -> str:
        """Formatea advertencia de hiperfoco prolongado"""
        
        if self.style == "neural":
            return f"""⚠️ HYPERFOCUS_OVERFLOW detectado

├─ Session time: {session_time} minutes
├─ Burnout risk: ELEVATED
├─ Recommendation: GRACEFUL_SHUTDOWN
└─ Next optimal session: +2 hours

🔧 Ejecutando protective_break_protocol..."""
        else:
            return f"""🤗 Gentil recordatorio de autocuidado

Llevas {session_time} minutos súper concentrado, ¡qué increíble!

Pero tu cerebro necesita un descanso para seguir brillando:
🌸 Toma 10 minutos para moverte o hidratarte
🌿 Tu creatividad se recarga con las pausas
✨ Vas súper bien, solo cuida tu energía

💚 El mejor trabajo viene de un cerebro descansado"""
    
    def format_achievement_unlocked(self, achievement: Dict[str, Any]) -> str:
        """Formatea logro desbloqueado"""
        
        name = achievement.get('name', 'Achievement')
        description = achievement.get('description', '')
        
        if self.style == "neural":
            return f"""🏆 ACHIEVEMENT_UNLOCKED

├─ Badge: {achievement.get('badge', '🎯')} {name.upper()}
├─ XP Gained: +{achievement.get('xp', 100)} neural_points
├─ Description: {description}
└─ Progression: LEVEL_UP_CANDIDATE

⚡ Neural optimization protocol enhanced"""
        else:
            return f"""🎉 ¡Logro desbloqueado!

{achievement.get('badge', '🎯')} {name}

{description}

🌟 Esto demuestra que tu constancia está dando frutos
💪 Cada logro es evidencia de tu crecimiento
✨ ¡Sigue así, vas increíble!"""
    
    def format_daily_summary(self, summary_data: Dict[str, Any]) -> str:
        """Formatea resumen diario"""
        
        completed = summary_data.get('completed_tasks', 0)
        total = summary_data.get('total_tasks', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        if self.style == "neural":
            return f"""📊 DAILY_NEURAL_REPORT - Day {summary_data.get('day_number', 1)}

════════════════════════════════════
⚡ Task completion: {completed}/{total} ({completion_rate:.0f}%)
🧠 Cognitive performance: {summary_data.get('cognitive_score', 85)}%
🎯 Attention coherence: {summary_data.get('attention_score', 75)}%
💊 Dopamine regulation: {summary_data.get('dopamine_level', 'STABLE')}

📈 System optimization: +{summary_data.get('improvement', 5)}% vs baseline
🔄 Next protocol scan: 06:00:00 hrs"""
        else:
            return f"""🌟 Resumen de tu día increíble

Completaste {completed} de {total} tareas ({completion_rate:.0f}%)

🎯 Lo que más me gusta de hoy:
• Cada tarea completada es una victoria
• Tu cerebro ADHD demostró su poder
• Construiste momentum positivo

💝 Para mañana:
• Descansa bien, te lo mereces
• Confía en tu proceso único
• Cada día es una nueva oportunidad

🌈 Estás creciendo, aunque no siempre lo veas"""
    
    def get_random_encouragement(self) -> str:
        """Retorna mensaje aleatorio de ánimo"""
        
        if self.style == "neural":
            neural_encouragements = [
                "🧠 Neural efficiency: OPTIMIZING...",
                "⚡ Cognitive boost protocol: ACTIVE",
                "🎯 Focus algorithms: CALIBRATED",
                "🔋 Mental energy: RECHARGING...",
                "🚀 Performance enhancement: LOADING..."
            ]
            return random.choice(neural_encouragements)
        else:
            natural_encouragements = [
                "🌟 Tu cerebro ADHD es único y poderoso",
                "💪 Cada pequeño paso cuenta muchísimo",
                "🌈 Los días difíciles también pasan",
                "✨ Eres más fuerte de lo que crees",
                "💝 Cuidarte es un acto de amor propio",
                "🎯 Tu forma de pensar es tu súper poder"
            ]
            return random.choice(natural_encouragements)
    
    def format_error_message(self, error_type: str, context: str = "") -> str:
        """Formatea mensajes de error"""
        
        if self.style == "neural":
            return f"""🔴 PROTOCOL_ERROR

├─ Error type: {error_type.upper()}
├─ Context: {context}
├─ Suggestion: Run /neural-scan for recalibration
└─ Fallback: BASIC_ROUTINE loaded

💡 Neural systems require optimization data"""
        else:
            return f"""😅 Algo no salió como esperaba

{context}

💡 Pero no te preocupes, estos pequeños obstáculos son normales:
• Tu cerebro ADHD a veces necesita información extra
• Podemos intentarlo de nuevo cuando quieras
• Siempre hay un plan B (y C, y D...)

🌟 ¿Probamos algo diferente?"""