"""
Tutorial Service - Tutorial interactivo para el sistema ADHD
"""
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger


class ADHDTutorialService:
    """Servicio para tutorial interactivo del sistema ADHD"""
    
    def __init__(self):
        self.tutorial_steps = {
            'neural': self._get_neural_tutorial_steps(),
            'natural': self._get_natural_tutorial_steps()
        }
    
    async def start_tutorial(self, user_context: Dict[str, Any], language_style: str = 'natural') -> Dict[str, Any]:
        """Inicia el tutorial interactivo"""
        try:
            # Verificar acceso premium
            from services.premium_service import premium_service
            access = await premium_service.check_user_access(user_context['id'], 'adhd_support_full')
            
            if not access['has_access']:
                # Ofrecer trial si está disponible
                if access.get('trial_available'):
                    return await self._offer_trial_tutorial(user_context, language_style)
                else:
                    return await self._offer_upgrade_tutorial(user_context, language_style)
            
            # Usuario tiene acceso - mostrar tutorial completo
            return await self._show_welcome_tutorial(user_context, language_style)
            
        except Exception as e:
            logger.error(f"Error iniciando tutorial ADHD: {e}")
            return {"error": "Error iniciando tutorial"}
    
    async def _offer_trial_tutorial(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Ofrece activar trial gratuito"""
        
        if language_style == 'neural':
            message = """🧠 NEURAL_HACKING_SYSTEM detected
            
════════════════════════════════════════════
⚡ ADHD OPTIMIZATION MODULE - Trial Available

🔬 SYSTEM_ANALYSIS:
├─ ADHD support protocols: LOCKED 🔒
├─ Neural enhancement tools: PREMIUM_REQUIRED
├─ Crisis management systems: LIMITED_ACCESS
└─ Advanced analytics: PREMIUM_FEATURE

🎁 FREE_TRIAL_AVAILABLE:
├─ Duration: 7 days FULL_ACCESS
├─ Features: ALL_PROTOCOLS unlocked
├─ Limitation: None during trial period
└─ Auto-expires: No charges

⚙️ ACTIVATION_COMMANDS:
• /neural-trial - Activate 7-day trial
• /neural-upgrade - View premium plans
• /neural - Continue with limited access

💡 RECOMMENDATION: Activate trial to experience full neural optimization"""
        else:
            message = """🌟 ¡Bienvenido al soporte ADHD especializado!

Tu cerebro ADHD es único y merece herramientas diseñadas específicamente para ti.

🎁 **Tienes disponible una prueba gratuita de 7 días:**

✨ **¿Qué incluye tu trial?**
• Rutinas matutinas personalizadas para ADHD
• Planes de atención y concentración
• Boost de dopamina cuando lo necesites  
• Apoyo para días difíciles y crisis
• Ambos estilos: Natural y Neural Hacking

🚀 **¿Cómo activarlo?**
• `/adhd-trial` - Activar prueba gratis
• `/adhd-upgrade` - Ver planes premium
• `/adhd` - Continuar con versión limitada

💝 **¿Por qué premium?** Porque tu bienestar mental vale la inversión, y estos son herramientas especializadas desarrolladas específicamente para cerebros ADHD"""
        
        return {
            'type': 'adhd_trial_offer',
            'message': message,
            'language_style': language_style,
            'trial_available': True
        }
    
    async def _offer_upgrade_tutorial(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Ofrece upgrade a premium (trial ya usado)"""
        
        if language_style == 'neural':
            message = """🧠 NEURAL_SYSTEM_STATUS: TRIAL_EXPIRED
            
════════════════════════════════════════════
⚠️ ADHD_OPTIMIZATION_MODULE: PREMIUM_REQUIRED

📊 TRIAL_ANALYSIS_COMPLETE:
├─ Trial period: USED
├─ System access: BASIC_MODE_ONLY
├─ Advanced features: LOCKED 🔒
└─ Unlock status: PREMIUM_KEY_REQUIRED

💎 PREMIUM_NEURAL_PROTOCOLS:
├─ Unlimited ADHD plan generation
├─ Crisis management systems  
├─ Advanced cognitive analytics
├─ Priority neural support
└─ Full system optimization

⚡ UPGRADE_OPTIONS:
• /neural-plans - View pricing matrix
• /neural-upgrade - Activate premium
• Basic mode continues with limited features

🚀 RECOMMENDATION: Upgrade for full neural enhancement"""
        else:
            message = """🌈 Gracias por probar nuestro soporte ADHD

Espero que hayas sentido la diferencia que hacen herramientas diseñadas específicamente para tu cerebro ADHD.

💝 **Tu trial ha expirado, pero tu progreso continúa:**

🎯 **Versión gratuita incluye:**
• Funciones básicas de tareas
• Integración con tus apps
• Soporte general

✨ **Premium te da acceso completo a:**
• Rutinas ADHD ilimitadas
• Gestión de crisis especializada  
• Análisis personalizado de patrones
• Ambos estilos de lenguaje
• Soporte prioritario

🚀 **Siguiente paso:**
• `/adhd-planes` - Ver opciones de precio
• `/adhd-upgrade` - Actualizar a premium
• Puedes seguir usando las funciones básicas

🧠 Recuerda: Invertir en herramientas para tu ADHD es invertir en tu bienestar y productividad"""
        
        return {
            'type': 'adhd_upgrade_offer', 
            'message': message,
            'language_style': language_style,
            'trial_used': True
        }
    
    async def _show_welcome_tutorial(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Muestra tutorial de bienvenida para usuarios premium"""
        
        # Obtener preferencia guardada del usuario
        from services.premium_service import premium_service
        status = await premium_service.get_premium_status(user_context['id'])
        
        # Usar preferencia guardada o la seleccionada
        user_preference = status.get('adhd_language_preference', language_style)
        
        if user_preference == 'neural':
            message = """🧠 NEURAL_HACKING_SYSTEM v2.1 - WELCOME_PROTOCOL
            
════════════════════════════════════════════
✅ PREMIUM_ACCESS confirmed | User authenticated

🎯 AVAILABLE_NEURAL_PROTOCOLS:

🔧 MORNING_OPTIMIZATION:
• /neural-protocol basica - Basic boot sequence
• /neural-protocol completa - Full system startup

⚡ ATTENTION_MANAGEMENT:
• /neural-focus corta - 15min concentration bursts  
• /neural-focus media - 25min optimal sessions
• /neural-focus larga - 45min deep work protocols

🧬 DOPAMINE_REGULATION:
• /neural-boost quick - Instant motivation injection
• /neural-boost sustained - Long-term optimization

🆘 CRISIS_PROTOCOLS:
• /neural-recovery overwhelm - System overflow management
• /neural-recovery executive - Function restoration
• /neural-recovery general - Universal support protocol

📊 SYSTEM_MONITORING:
• /neural-status - Full cognitive analytics
• /neural-config - Adjust preferences

💡 GETTING_STARTED:
1. Run /neural-status for baseline analysis
2. Create your first protocol with /neural-protocol basica
3. Customize based on system recommendations

⚙️ All protocols auto-adapt to your cognitive patterns"""
        else:
            message = """🌟 ¡Bienvenido a tu sistema de soporte ADHD personalizado!

Tu cerebro ADHD es increíble, y ahora tienes herramientas que realmente lo entienden.

💝 **¿Por dónde empezar?**

🌅 **Rutinas matutinas que funcionan:**
• `/adhd-rutina basica` - Para empezar suave
• `/adhd-rutina completa` - Cuando te sientas listo

🎯 **Gestión de atención personalizada:**
• `/adhd-atencion corta` - Sesiones de 15 min
• `/adhd-atencion media` - Bloques de 25 min  
• `/adhd-atencion larga` - Trabajo profundo de 45 min

✨ **Boost de motivación cuando lo necesites:**
• `/adhd-dopamina quick` - Energía rápida (5 min)
• `/adhd-dopamina sustained` - Plan de bienestar completo

🤗 **Apoyo para días difíciles:**
• `/adhd-crisis overwhelm` - Cuando todo se siente demasiado
• `/adhd-crisis executive` - Cuando no puedes empezar
• `/adhd-crisis general` - Plan básico de día difícil

🚀 **Tu primer paso:**
1. Prueba `/adhd-rutina basica` para crear tu primera rutina
2. Todo se adapta automáticamente a tus patrones
3. Cada plan se integra con tus apps favoritas

💡 **Tip:** Puedes alternar entre este estilo natural y el modo "Neural Hacking" técnico cuando quieras usando `/neural`"""
        
        return {
            'type': 'adhd_welcome_tutorial',
            'message': message,
            'language_style': user_preference,
            'premium_active': True,
            'next_steps': self._get_suggested_next_steps(user_preference)
        }
    
    def _get_suggested_next_steps(self, language_style: str) -> List[str]:
        """Obtiene sugerencias de próximos pasos"""
        
        if language_style == 'neural':
            return [
                "/neural-status - Baseline cognitive analysis",
                "/neural-protocol basica - First optimization routine", 
                "/neural-focus media - Attention calibration session"
            ]
        else:
            return [
                "/adhd-rutina basica - Tu primera rutina matutina",
                "/adhd-atencion media - Sesión de concentración",
                "/adhd-dopamina quick - Boost rápido de energía"
            ]
    
    def _get_neural_tutorial_steps(self) -> List[Dict[str, Any]]:
        """Pasos del tutorial estilo neural"""
        return [
            {
                'step': 1,
                'title': 'SYSTEM_INITIALIZATION',
                'content': 'Neural optimization protocols loading...',
                'action': '/neural-status'
            },
            {
                'step': 2, 
                'title': 'ROUTINE_DEPLOYMENT',
                'content': 'Deploying morning optimization sequence',
                'action': '/neural-protocol basica'
            },
            {
                'step': 3,
                'title': 'ATTENTION_CALIBRATION', 
                'content': 'Calibrating focus enhancement systems',
                'action': '/neural-focus media'
            }
        ]
    
    def _get_natural_tutorial_steps(self) -> List[Dict[str, Any]]:
        """Pasos del tutorial estilo natural"""
        return [
            {
                'step': 1,
                'title': 'Conoce tu rutina matutina',
                'content': 'Vamos a crear una rutina que funcione con tu cerebro ADHD',
                'action': '/adhd-rutina basica'
            },
            {
                'step': 2,
                'title': 'Gestiona tu atención',
                'content': 'Prueba sesiones de concentración diseñadas para ti',
                'action': '/adhd-atencion media'
            },
            {
                'step': 3,
                'title': 'Boost de energía',
                'content': 'Cuando necesites motivación rápida',
                'action': '/adhd-dopamina quick'
            }
        ]
    
    async def handle_trial_activation(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Maneja la activación del trial desde el tutorial"""
        try:
            from services.premium_service import premium_service
            
            # Activar trial
            trial_result = await premium_service.activate_trial(user_context['id'])
            
            if trial_result['success']:
                # Trial activado, mostrar bienvenida
                if language_style == 'neural':
                    message = f"""🧠 TRIAL_ACTIVATION_SUCCESSFUL
                    
════════════════════════════════════════════
✅ NEURAL_HACKING_SYSTEM: FULL_ACCESS_GRANTED

📅 Trial expires: {trial_result['expires_at'][:10]}
⏰ Time remaining: {trial_result['days_remaining']} days
🔓 All protocols: UNLOCKED

🚀 IMMEDIATE_NEXT_STEPS:
1. /neural-status - Run system analysis
2. /neural-protocol basica - Deploy first routine
3. /neural-focus media - Test attention systems

⚡ FULL_NEURAL_ENHANCEMENT activated for 7 days"""
                else:
                    message = f"""🎉 ¡Trial activado exitosamente!

Tu prueba gratuita de 7 días está activa.

✨ **Lo que puedes hacer ahora:**
• Crear todas las rutinas ADHD que necesites
• Probar ambos estilos de lenguaje
• Acceso completo a gestión de crisis
• Análisis personalizado de tus patrones

📅 **Tu trial expira:** {trial_result['expires_at'][:10]}
⏰ **Días restantes:** {trial_result['days_remaining']}

🚀 **Empezar ahora:**
1. `/adhd-rutina basica` - Tu primera rutina
2. `/adhd-atencion media` - Prueba la gestión de atención  
3. `/neural` - Cambia al modo técnico cuando quieras

💡 Recuerda: Durante el trial tienes acceso completo. ¡Aprovéchalo!"""
                
                return {
                    'type': 'trial_activated',
                    'message': message,
                    'trial_active': True,
                    'expires_at': trial_result['expires_at'],
                    'language_style': language_style
                }
            else:
                return {
                    'type': 'trial_failed',
                    'message': trial_result['message'],
                    'reason': trial_result['reason']
                }
                
        except Exception as e:
            logger.error(f"Error activando trial desde tutorial: {e}")
            return {"error": "Error activando trial"}

# Instancia singleton
tutorial_service = ADHDTutorialService()