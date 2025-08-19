"""
Middleware para verificar acceso según plan del usuario
"""
from typing import Dict, Any
from loguru import logger
from services.premium_service import premium_service


async def verify_feature_access(user_context: Dict[str, Any], feature: str) -> Dict[str, Any]:
    """
    Verifica si el usuario tiene acceso a una funcionalidad
    
    Args:
        user_context: Contexto del usuario
        feature: Feature a verificar
        
    Returns:
        Dict con resultado de verificación
    """
    try:
        return await premium_service.check_user_access(user_context["id"], feature)
    except Exception as e:
        logger.error(f"Error verificando acceso a {feature}: {e}")
        return {
            'has_access': False,
            'reason': 'verification_error',
            'error': str(e)
        }


def get_upgrade_message(access_result: Dict[str, Any], feature_name: str, language_style: str = "natural") -> str:
    """
    Genera mensaje de upgrade apropiado según el resultado de acceso
    """
    reason = access_result.get('reason')
    current_plan = access_result.get('current_plan', 'free')
    
    if reason == 'free_plan_limit_reached':
        if language_style == "neural":
            return f"""🔒 FREE_PLAN_QUOTA_EXCEEDED
            
════════════════════════════════════════════
⚠️ Monthly task limit reached: 5/5 tasks used

🆙 UPGRADE_OPTIONS:
├─ BASIC_PLAN: $4.99/month → Unlimited tasks + integrations
├─ ADHD_PREMIUM: $9.99/month → BASIC + Neural optimization
└─ FREE_RESET: Next month (tasks reset automatically)

⚡ UPGRADE_COMMANDS:
• /basic-trial - 3 days free trial
• /basic-upgrade - View BASIC plan options
• /adhd-trial - 7 days ADHD trial"""
        else:
            remaining = access_result.get('remaining_tasks', 0)
            return f"""📊 Límite mensual alcanzado

Has usado tus 5 tareas gratuitas de este mes.

💝 **Opciones para continuar:**

🚀 **Plan Básico - $4.99/mes:**
• Tareas ilimitadas
• Todas las integraciones (Todoist, Calendar)
• Estadísticas completas
• Sin funciones ADHD

🧠 **Plan ADHD - $9.99/mes:**
• Todo del plan básico
• + Herramientas ADHD especializadas
• + Ambos estilos de lenguaje

🎁 **Pruebas gratuitas:**
• `/basic-trial` - 3 días de plan básico
• `/adhd-trial` - 7 días de plan premium

⏰ **O espera:** Tus tareas se resetean el próximo mes"""
    
    elif reason == 'basic_plan_required':
        if language_style == "neural":
            return f"""🔒 BASIC_TIER_REQUIRED - {feature_name.upper()}
            
════════════════════════════════════════════
⚠️ Current access level: FREE_TIER
📊 Required access level: BASIC_TIER or higher

💎 BASIC_PLAN_FEATURES:
├─ Unlimited tasks and events
├─ All integrations (Todoist, Calendar)
├─ Complete statistics and analytics  
├─ Reminder system
└─ Email support

⚡ ACTIVATION_PROTOCOLS:
• /basic-trial - 3 days free trial
• /basic-upgrade - View subscription options
• /adhd-trial - 7 days premium trial (includes BASIC)"""
        else:
            basic_trial_available = access_result.get('basic_trial_available', False)
            adhd_trial_available = access_result.get('adhd_trial_available', False)
            
            trial_options = []
            if basic_trial_available:
                trial_options.append("• `/basic-trial` - 3 días de plan básico gratis")
            if adhd_trial_available:
                trial_options.append("• `/adhd-trial` - 7 días de plan premium gratis")
            
            trial_text = "\n".join(trial_options) if trial_options else "• Ya has usado tus trials gratuitos"
            
            return f"""🔒 Funcionalidad del Plan Básico

Esta función requiere el Plan Básico ($4.99/mes) o superior.

💼 **Plan Básico incluye:**
• Tareas y eventos ilimitados
• Todas las integraciones
• Estadísticas completas
• Sistema de recordatorios
• Soporte por email

🎁 **Pruebas disponibles:**
{trial_text}

🚀 **Para upgradar:**
• `/basic-upgrade` - Ver opciones de plan básico"""
    
    elif reason == 'adhd_upgrade_required':
        if language_style == "neural":
            return f"""🧠 ADHD_PREMIUM_REQUIRED - {feature_name.upper()}
            
════════════════════════════════════════════
⚠️ Current tier: BASIC_PLAN
📊 Required tier: ADHD_PREMIUM

🧬 ADHD_PREMIUM_FEATURES:
├─ All BASIC features included
├─ Neural optimization protocols  
├─ Crisis management systems
├─ Cognitive pattern analysis
├─ Dual language interface (Neural/Natural)
└─ Priority support queue

⚡ UPGRADE_PROTOCOL:
• /adhd-upgrade - Activate ADHD premium
• /neural-trial - 7 days free trial (if available)"""
        else:
            return f"""🧠 Funcionalidad ADHD Premium

Tienes el plan básico, pero esta función específica requiere el Plan ADHD Premium ($9.99/mes).

✨ **ADHD Premium incluye:**
• Todo tu plan básico actual
• + Rutinas matutinas personalizadas
• + Gestión de atención y concentración  
• + Boost de dopamina
• + Apoyo para días difíciles
• + Ambos estilos de lenguaje
• + Análisis de patrones cognitivos

🚀 **Para upgradar:**
• `/adhd-upgrade` - Ver opciones de upgrade
• `/adhd-trial` - 7 días gratis (si disponible)"""
    
    else:
        # Mensaje genérico
        if language_style == "neural":
            return f"""🔒 ACCESS_RESTRICTED - {feature_name.upper()}
            
════════════════════════════════════════════
⚠️ Feature requires subscription tier upgrade

⚡ Available upgrade protocols:
• /basic-upgrade - BASIC tier options
• /adhd-upgrade - Premium ADHD tier
• /help - View all available commands"""
        else:
            return f"""🔒 Funcionalidad Restringida

Esta función requiere un plan de pago.

🚀 **Opciones:**
• `/basic-upgrade` - Plan básico ($4.99/mes)
• `/adhd-upgrade` - Plan premium ADHD ($9.99/mes)
• `/help` - Ver comandos disponibles"""


async def check_task_creation_limit(user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifica específicamente si el usuario puede crear más tareas
    """
    access_result = await verify_feature_access(user_context, 'unlimited_tasks')
    
    if access_result['has_access']:
        return {'can_create': True}
    
    # Si no tiene acceso ilimitado, verificar límites del plan FREE
    free_access = await verify_feature_access(user_context, 'limited_tasks')
    
    if free_access['has_access']:
        remaining = free_access.get('remaining_tasks', 0)
        return {
            'can_create': True,
            'plan': 'free',
            'remaining_tasks': remaining,
            'warning_message': f"Plan gratuito: Te quedan {remaining} tareas este mes"
        }
    else:
        return {
            'can_create': False,
            'reason': free_access['reason'],
            'upgrade_message': get_upgrade_message(free_access, 'tareas')
        }