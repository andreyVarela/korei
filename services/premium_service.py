"""
Premium Service - Gestión de planes premium y acceso a funciones ADHD
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from loguru import logger
from core.supabase import supabase


class PremiumService:
    """Servicio para gestionar acceso premium y funciones ADHD"""
    
    # Features del Plan FREE (muy limitado)
    FREE_FEATURES = {
        'basic_help',             # Comando /help
        'basic_register',         # Comando /register  
        'limited_tasks'           # Máximo 5 tareas/mes
    }
    
    # Features del Plan BASIC (servicio completo sin ADHD)
    BASIC_FEATURES = {
        'unlimited_tasks',        # Tareas ilimitadas
        'integrations',          # Todoist, Calendar, etc.
        'stats',                 # Estadísticas completas
        'reminders',             # Recordatorios
        'expenses',              # Gestión de gastos
        'events',                # Gestión de eventos
        'email_support'          # Soporte por email
    }
    
    # Features del Plan ADHD PREMIUM (todo incluido)
    ADHD_FEATURES = {
        'adhd_support',          # Soporte ADHD completo
        'neural_hacking',        # Estilo Neural Hacking
        'crisis_management',     # Gestión de crisis
        'pattern_analysis',      # Análisis de patrones
        'priority_support',      # Soporte prioritario
        'advanced_analytics'     # Analytics avanzados
    }
    
    # Todos los features disponibles
    ALL_FEATURES = FREE_FEATURES | BASIC_FEATURES | ADHD_FEATURES
    
    async def check_user_access(self, user_id: str, feature: str) -> Dict[str, Any]:
        """
        Verifica si el usuario tiene acceso a una funcionalidad según plan escalonado
        
        Args:
            user_id: ID del usuario
            feature: Nombre de la funcionalidad
            
        Returns:
            Dict con información de acceso
        """
        try:
            # Usar función de BD para verificación completa
            result = supabase._get_client().rpc('check_feature_access', {
                'user_uuid': user_id,
                'feature_name': feature
            }).execute()
            
            if result.data:
                access_info = result.data
                
                # Convertir respuesta de BD a formato Python
                return {
                    'has_access': access_info.get('has_access', False),
                    'reason': access_info.get('reason'),
                    'plan_type': access_info.get('plan_type'),
                    'current_plan': access_info.get('current_plan'),
                    'expires_at': access_info.get('expires_at'),
                    'remaining_tasks': access_info.get('remaining_tasks'),
                    'upgrade_required': access_info.get('upgrade_required', False),
                    'basic_trial_available': access_info.get('basic_trial_available', False),
                    'adhd_trial_available': access_info.get('adhd_trial_available', False)
                }
            else:
                return {
                    'has_access': False,
                    'reason': 'db_error',
                    'upgrade_required': True
                }
            
        except Exception as e:
            logger.error(f"Error verificando acceso: {e}")
            return {
                'has_access': False,
                'reason': 'error',
                'error': str(e)
            }
    
    async def activate_basic_trial(self, user_id: str) -> Dict[str, Any]:
        """Activa trial gratuito de 3 días para plan básico"""
        try:
            # Activar trial usando función de base de datos
            result = supabase._get_client().rpc('activate_basic_trial', {
                'user_uuid': user_id
            }).execute()
            
            if result.data:
                trial_expires = datetime.now() + timedelta(days=3)
                return {
                    'success': True,
                    'trial_type': 'basic',
                    'expires_at': trial_expires.isoformat(),
                    'days_remaining': 3,
                    'message': '🎉 ¡Trial básico activado! Tienes 3 días para probar todas las funciones principales'
                }
            else:
                return {
                    'success': False,
                    'reason': 'trial_already_used',
                    'message': 'Ya has usado tu trial gratuito del plan básico'
                }
                
        except Exception as e:
            logger.error(f"Error activando trial básico: {e}")
            return {
                'success': False,
                'reason': 'error',
                'error': str(e)
            }
    
    async def activate_adhd_trial(self, user_id: str) -> Dict[str, Any]:
        """Activa trial gratuito de 7 días para ADHD"""
        try:
            # Verificar si ya usó el trial
            user_data = await self._get_user_premium_info(user_id)
            
            if user_data and user_data['trial_used']:
                return {
                    'success': False,
                    'reason': 'trial_already_used',
                    'message': 'Ya has usado tu trial gratuito de 7 días para ADHD'
                }
            
            # Activar trial usando función de base de datos
            result = supabase._get_client().rpc('activate_adhd_trial', {
                'user_uuid': user_id
            }).execute()
            
            if result.data:
                trial_expires = datetime.now() + timedelta(days=7)
                return {
                    'success': True,
                    'trial_type': 'adhd',
                    'expires_at': trial_expires.isoformat(),
                    'days_remaining': 7,
                    'message': '🎉 ¡Trial ADHD activado! Tienes 7 días para probar todas las funciones premium'
                }
            else:
                return {
                    'success': False,
                    'reason': 'activation_failed',
                    'message': 'Error activando trial ADHD'
                }
                
        except Exception as e:
            logger.error(f"Error activando trial ADHD: {e}")
            return {
                'success': False,
                'reason': 'error',
                'error': str(e)
            }
    
    async def get_premium_status(self, user_id: str) -> Dict[str, Any]:
        """Obtiene el estado premium completo del usuario"""
        try:
            user_data = await self._get_user_premium_info(user_id)
            
            if not user_data:
                return {
                    'plan_type': 'free',
                    'premium_active': False,
                    'trial_available': True
                }
            
            # Calcular días restantes
            days_remaining = None
            if user_data['premium_expires_at']:
                expires = datetime.fromisoformat(user_data['premium_expires_at'].replace('Z', '+00:00'))
                now = datetime.now(expires.tzinfo) if expires.tzinfo else datetime.now()
                if expires > now:
                    days_remaining = (expires - now).days
            
            trial_days_remaining = None
            if user_data['trial_expires_at'] and not user_data['premium_active']:
                trial_expires = datetime.fromisoformat(user_data['trial_expires_at'].replace('Z', '+00:00'))
                now = datetime.now(trial_expires.tzinfo) if trial_expires.tzinfo else datetime.now()
                if trial_expires > now:
                    trial_days_remaining = (trial_expires - now).days
            
            # Obtener estadísticas de uso ADHD
            adhd_stats = await self._get_adhd_usage_stats(user_id)
            
            return {
                'plan_type': user_data['plan_type'],
                'premium_active': user_data['premium_active'],
                'premium_expires_at': user_data['premium_expires_at'],
                'days_remaining': days_remaining,
                'trial_used': user_data['trial_used'],
                'trial_expires_at': user_data['trial_expires_at'],
                'trial_days_remaining': trial_days_remaining,
                'trial_available': not user_data['trial_used'],
                'adhd_language_preference': user_data.get('adhd_language_preference', 'natural'),
                'adhd_stats': adhd_stats
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado premium: {e}")
            return {'error': str(e)}
    
    async def get_available_plans(self) -> List[Dict[str, Any]]:
        """Obtiene los planes premium disponibles"""
        try:
            result = supabase._get_client().table("premium_plans").select("*").eq(
                "active", True
            ).execute()
            
            plans = []
            for plan in result.data:
                plans.append({
                    'id': plan['id'],
                    'name': plan['plan_name'],
                    'type': plan['plan_type'],
                    'price': float(plan['price']),
                    'currency': plan['currency'],
                    'features': plan['features'],
                    'description': plan['description']
                })
            
            return plans
            
        except Exception as e:
            logger.error(f"Error obteniendo planes: {e}")
            return []
    
    async def count_adhd_plans_used(self, user_id: str) -> int:
        """Cuenta cuántos planes ADHD ha creado el usuario"""
        try:
            result = supabase._get_client().table("adhd_plans").select(
                "id", count="exact"
            ).eq("user_id", user_id).execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Error contando planes ADHD: {e}")
            return 0
    
    async def can_create_adhd_plan(self, user_id: str, plan_type: str) -> Dict[str, Any]:
        """Verifica si el usuario puede crear un plan ADHD específico"""
        try:
            # Verificar acceso general a ADHD
            access = await self.check_user_access(user_id, 'adhd_support_full')
            
            if access['has_access']:
                return {
                    'can_create': True,
                    'reason': 'premium_access'
                }
            
            # Verificar trial
            trial_access = await self.check_user_access(user_id, 'adhd_support_limited')
            
            if trial_access['has_access']:
                # En trial, verificar límites
                plans_used = await self.count_adhd_plans_used(user_id)
                
                if plans_used < 3:  # Límite de trial
                    return {
                        'can_create': True,
                        'reason': 'trial_access',
                        'remaining': 3 - plans_used
                    }
                else:
                    return {
                        'can_create': False,
                        'reason': 'trial_limit_reached',
                        'upgrade_required': True
                    }
            
            # Verificar si puede activar trial
            if trial_access.get('trial_available'):
                return {
                    'can_create': False,
                    'reason': 'trial_available',
                    'can_start_trial': True
                }
            
            return {
                'can_create': False,
                'reason': 'premium_required',
                'upgrade_required': True
            }
            
        except Exception as e:
            logger.error(f"Error verificando creación de plan ADHD: {e}")
            return {
                'can_create': False,
                'reason': 'error',
                'error': str(e)
            }
    
    async def _get_user_premium_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene información premium del usuario"""
        try:
            result = supabase._get_client().table("users").select(
                "plan_type, premium_active, premium_expires_at, trial_used, trial_expires_at, adhd_language_preference"
            ).eq("id", user_id).single().execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo info premium: {e}")
            return None
    
    async def _deactivate_expired_premium(self, user_id: str):
        """Desactiva premium expirado"""
        try:
            await supabase._get_client().table("users").update({
                "premium_active": False
            }).eq("id", user_id).execute()
            
            logger.info(f"Premium expirado desactivado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"Error desactivando premium expirado: {e}")
    
    async def _get_adhd_usage_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de funciones ADHD"""
        try:
            # Contar planes ADHD
            plans_result = supabase._get_client().table("adhd_plans").select(
                "status", count="exact"
            ).eq("user_id", user_id).execute()
            
            # Contar tareas ADHD
            tasks_result = supabase._get_client().table("entries").select(
                "status", count="exact"
            ).eq("user_id", user_id).eq("adhd_specific", True).execute()
            
            return {
                'total_adhd_plans': plans_result.count or 0,
                'total_adhd_tasks': tasks_result.count or 0,
                'last_plan_created': None  # TODO: Implementar
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats ADHD: {e}")
            return {
                'total_adhd_plans': 0,
                'total_adhd_tasks': 0
            }

# Instancia singleton
premium_service = PremiumService()