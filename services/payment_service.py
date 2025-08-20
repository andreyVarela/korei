"""
Payment Service - Integración con procesadores de pago (Stripe, PayPal)
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from core.supabase import supabase


class PaymentService:
    """Servicio para manejar pagos y upgrades premium"""
    
    def __init__(self):
        # Configurar según tu procesador de pago preferido
        self.stripe_enabled = os.getenv('STRIPE_SECRET_KEY') is not None
        self.paypal_enabled = os.getenv('PAYPAL_CLIENT_ID') is not None
        
        if self.stripe_enabled:
            self._init_stripe()
    
    def _init_stripe(self):
        """Inicializar Stripe si está configurado"""
        try:
            import stripe
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            self.stripe = stripe
            logger.info("Stripe inicializado correctamente")
        except ImportError:
            logger.warning("Stripe no está instalado. Instalar con: pip install stripe")
            self.stripe_enabled = False
    
    async def create_checkout_session(self, user_id: str, plan_name: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Crea sesión de checkout para upgrade premium
        
        Args:
            user_id: ID del usuario
            plan_name: 'adhd_monthly' o 'adhd_yearly'
            success_url: URL de éxito (ej: https://tu-app.com/success)
            cancel_url: URL de cancelación
            
        Returns:
            Dict con URL de checkout y session_id
        """
        try:
            # Obtener información del plan
            plan = await self._get_plan_info(plan_name)
            if not plan:
                return {'error': 'Plan no encontrado'}
            
            if self.stripe_enabled:
                return await self._create_stripe_session(user_id, plan, success_url, cancel_url)
            elif self.paypal_enabled:
                return await self._create_paypal_session(user_id, plan, success_url, cancel_url)
            else:
                return await self._create_manual_payment(user_id, plan)
                
        except Exception as e:
            logger.error(f"Error creando checkout session: {e}")
            return {'error': 'Error procesando pago'}
    
    async def _create_stripe_session(self, user_id: str, plan: Dict, success_url: str, cancel_url: str) -> Dict[str, Any]:
        """Crear sesión de Stripe"""
        try:
            # Configurar recurrencia
            interval = 'month' if plan['plan_type'] == 'monthly' else 'year'
            
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan['currency'].lower(),
                        'product_data': {
                            'name': f"ADHD Premium - {plan['plan_type'].title()}",
                            'description': plan['description']
                        },
                        'unit_amount': int(plan['price'] * 100),  # Stripe usa centavos
                        'recurring': {
                            'interval': interval
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                client_reference_id=user_id,
                metadata={
                    'user_id': user_id,
                    'plan_name': plan['plan_name'],
                    'plan_type': plan['plan_type']
                }
            )
            
            # Guardar sesión pendiente en BD
            await self._save_pending_transaction(
                user_id=user_id,
                plan_id=plan['id'],
                transaction_id=session.id,
                payment_provider='stripe',
                amount=plan['price'],
                currency=plan['currency'],
                status='pending'
            )
            
            return {
                'checkout_url': session.url,
                'session_id': session.id,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error creando sesión Stripe: {e}")
            return {'error': 'Error con Stripe'}
    
    async def _create_manual_payment(self, user_id: str, plan: Dict) -> Dict[str, Any]:
        """Crear proceso de pago manual (transferencia, etc)"""
        try:
            # Generar ID único para el pago manual
            import uuid
            manual_id = f"manual_{uuid.uuid4().hex[:8]}"
            
            # Guardar transacción manual pendiente
            await self._save_pending_transaction(
                user_id=user_id,
                plan_id=plan['id'],
                transaction_id=manual_id,
                payment_provider='manual',
                amount=plan['price'],
                currency=plan['currency'],
                status='pending'
            )
            
            payment_info = {
                'plan_name': plan['plan_name'],
                'amount': plan['price'],
                'currency': plan['currency'],
                'reference_id': manual_id,
                'instructions': f"""
Para completar tu upgrade a ADHD Premium:

💰 **Monto**: ${plan['price']} {plan['currency']}
🔢 **Referencia**: {manual_id}
📧 **Notificar a**: support@tu-app.com

📱 **Métodos de pago disponibles**:
• Transferencia bancaria
• PayPal: tu-paypal@email.com
• Otro método acordado

✅ **Activación**: Manual (24-48 horas después del pago)
""",
                'success': True
            }
            
            return payment_info
            
        except Exception as e:
            logger.error(f"Error creando pago manual: {e}")
            return {'error': 'Error procesando pago manual'}
    
    async def handle_payment_success(self, transaction_id: str, payment_provider: str) -> Dict[str, Any]:
        """
        Maneja el éxito de un pago (webhook desde Stripe/PayPal)
        
        Args:
            transaction_id: ID de la transacción exitosa
            payment_provider: 'stripe', 'paypal', 'manual'
            
        Returns:
            Dict con resultado de activación
        """
        try:
            # Obtener transacción pendiente
            transaction = await self._get_transaction(transaction_id, payment_provider)
            
            if not transaction:
                return {'error': 'Transacción no encontrada'}
            
            if transaction['status'] == 'completed':
                return {'success': True, 'message': 'Ya activado previamente'}
            
            # Activar premium para el usuario
            activation_result = await self._activate_user_premium(
                user_id=transaction['user_id'],
                plan_id=transaction['plan_id'],
                transaction_id=transaction['id']
            )
            
            if activation_result['success']:
                # Marcar transacción como completada
                await self._update_transaction_status(transaction['id'], 'completed')
                
                logger.info(f"Premium activado exitosamente para usuario {transaction['user_id']}")
                
                return {
                    'success': True,
                    'user_id': transaction['user_id'],
                    'plan_activated': activation_result['plan_type'],
                    'expires_at': activation_result.get('expires_at')
                }
            else:
                return {'error': 'Error activando premium'}
                
        except Exception as e:
            logger.error(f"Error manejando pago exitoso: {e}")
            return {'error': 'Error procesando activación'}
    
    async def _get_plan_info(self, plan_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del plan desde la BD"""
        try:
            result = supabase._get_client().table("premium_plans").select("*").eq(
                "plan_name", plan_name
            ).eq("active", True).single().execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo plan {plan_name}: {e}")
            return None
    
    async def _save_pending_transaction(self, user_id: str, plan_id: str, transaction_id: str, 
                                      payment_provider: str, amount: float, currency: str, status: str):
        """Guarda transacción pendiente en BD"""
        try:
            transaction_data = {
                'user_id': user_id,
                'plan_id': plan_id,
                'transaction_id': transaction_id,
                'payment_provider': payment_provider,
                'amount': amount,
                'currency': currency,
                'status': status,
                'created_at': datetime.now().isoformat()
            }
            
            result = supabase._get_client().table("payment_transactions").insert(
                transaction_data
            ).execute()
            
            logger.info(f"Transacción guardada: {transaction_id}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error guardando transacción: {e}")
            return None
    
    async def _get_transaction(self, transaction_id: str, payment_provider: str) -> Optional[Dict]:
        """Obtiene transacción por ID y proveedor"""
        try:
            result = supabase._get_client().table("payment_transactions").select("*").eq(
                "transaction_id", transaction_id
            ).eq("payment_provider", payment_provider).single().execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo transacción {transaction_id}: {e}")
            return None
    
    async def _activate_user_premium(self, user_id: str, plan_id: str, transaction_id: str) -> Dict[str, Any]:
        """Activa plan para un usuario (básico o ADHD) usando función de BD"""
        try:
            # Obtener información del plan
            plan = await self._get_plan_info_by_id(plan_id)
            if not plan:
                return {'success': False, 'error': 'Plan no encontrado'}
            
            # Usar función de BD para upgrade de plan
            result = supabase._get_client().rpc('upgrade_user_plan', {
                'user_uuid': user_id,
                'new_plan_name': plan['plan_name'],
                'transaction_uuid': transaction_id
            }).execute()
            
            if result.data and result.data.get('success'):
                duration_months = 12 if plan['plan_type'] == 'yearly' else 1
                expires_at = None
                
                if plan['plan_type'] != 'lifetime':
                    expires_at = (datetime.now() + timedelta(days=duration_months * 30)).isoformat()
                
                return {
                    'success': True,
                    'plan_type': plan['plan_type'],
                    'plan_name': plan['plan_name'],
                    'is_premium': result.data.get('is_premium', False),
                    'expires_at': expires_at
                }
            else:
                error_msg = result.data.get('error', 'Error en función de BD') if result.data else 'Sin respuesta de BD'
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Error activando plan: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_plan_info_by_id(self, plan_id: str) -> Optional[Dict]:
        """Obtiene plan por ID"""
        try:
            result = supabase._get_client().table("premium_plans").select("*").eq(
                "id", plan_id
            ).single().execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo plan por ID {plan_id}: {e}")
            return None
    
    async def _update_transaction_status(self, transaction_id: str, status: str):
        """Actualiza estado de transacción"""
        try:
            supabase._get_client().table("payment_transactions").update({
                'status': status,
                'updated_at': datetime.now().isoformat()
            }).eq('id', transaction_id).execute()
            
        except Exception as e:
            logger.error(f"Error actualizando transacción {transaction_id}: {e}")

# Instancia singleton
payment_service = PaymentService()