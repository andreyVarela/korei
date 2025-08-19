"""
Payment Webhook Route - Maneja confirmaciones de pago desde Stripe/PayPal
"""
import os
import json
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Header
from loguru import logger
from services.payment_service import payment_service


router = APIRouter()


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Webhook para confirmaciones de pago de Stripe
    
    Este endpoint recibe confirmaciones automáticas cuando:
    - Un pago es exitoso
    - Una suscripción se renueva
    - Un pago falla
    """
    try:
        payload = await request.body()
        
        # Verificar signature de Stripe (opcional pero recomendado)
        if stripe_signature and os.getenv('STRIPE_WEBHOOK_SECRET'):
            try:
                import stripe
                event = stripe.Webhook.construct_event(
                    payload, 
                    stripe_signature, 
                    os.getenv('STRIPE_WEBHOOK_SECRET')
                )
            except ValueError:
                logger.error("Payload inválido en webhook Stripe")
                raise HTTPException(status_code=400, detail="Invalid payload")
            except stripe.error.SignatureVerificationError:
                logger.error("Signature inválida en webhook Stripe")
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Sin verificación de signature (para testing)
            event = json.loads(payload)
        
        # Manejar diferentes tipos de eventos
        if event['type'] == 'checkout.session.completed':
            # Pago exitoso
            session = event['data']['object']
            
            result = await payment_service.handle_payment_success(
                transaction_id=session['id'],
                payment_provider='stripe'
            )
            
            if result.get('success'):
                logger.info(f"Premium activado via Stripe para usuario {result['user_id']}")
                
                # Opcional: Enviar notificación al usuario via WhatsApp
                await _notify_user_premium_activated(result['user_id'], result)
            else:
                logger.error(f"Error activando premium desde Stripe: {result}")
        
        elif event['type'] == 'invoice.payment_succeeded':
            # Renovación de suscripción exitosa
            invoice = event['data']['object']
            logger.info(f"Suscripción renovada: {invoice['subscription']}")
            
        elif event['type'] == 'invoice.payment_failed':
            # Pago fallido
            invoice = event['data']['object']
            logger.warning(f"Pago fallido para suscripción: {invoice['subscription']}")
            
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error en webhook Stripe: {e}")
        raise HTTPException(status_code=500, detail="Webhook error")


@router.post("/paypal-webhook")
async def paypal_webhook(request: Request):
    """
    Webhook para confirmaciones de pago de PayPal
    """
    try:
        payload = await request.body()
        event = json.loads(payload)
        
        # Verificar que es un evento de pago exitoso de PayPal
        if event.get('event_type') == 'PAYMENT.CAPTURE.COMPLETED':
            capture = event['resource']
            
            # El ID de transacción debería estar en custom_id o reference_id
            transaction_id = capture.get('custom_id') or capture.get('reference_id')
            
            if transaction_id:
                result = await payment_service.handle_payment_success(
                    transaction_id=transaction_id,
                    payment_provider='paypal'
                )
                
                if result.get('success'):
                    logger.info(f"Premium activado via PayPal para usuario {result['user_id']}")
                    await _notify_user_premium_activated(result['user_id'], result)
                else:
                    logger.error(f"Error activando premium desde PayPal: {result}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error en webhook PayPal: {e}")
        raise HTTPException(status_code=500, detail="Webhook error")


@router.post("/manual-payment-confirm")
async def manual_payment_confirm(request: Request):
    """
    Endpoint para confirmar pagos manuales (solo para admins)
    
    Body esperado:
    {
        "transaction_id": "manual_12345678",
        "admin_key": "tu_admin_key_secreto"
    }
    """
    try:
        data = await request.json()
        
        # Verificar admin key (simple auth para confirmar pagos manuales)
        admin_key = data.get('admin_key')
        expected_key = os.getenv('ADMIN_PAYMENT_KEY', 'default_key_change_this')
        
        if admin_key != expected_key:
            raise HTTPException(status_code=401, detail="Admin key inválido")
        
        transaction_id = data.get('transaction_id')
        if not transaction_id:
            raise HTTPException(status_code=400, detail="transaction_id requerido")
        
        # Confirmar pago manual
        result = await payment_service.handle_payment_success(
            transaction_id=transaction_id,
            payment_provider='manual'
        )
        
        if result.get('success'):
            logger.info(f"Pago manual confirmado para usuario {result['user_id']}")
            await _notify_user_premium_activated(result['user_id'], result)
            
            return {
                "success": True,
                "user_id": result['user_id'],
                "plan_activated": result['plan_activated']
            }
        else:
            return {"success": False, "error": result.get('error')}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirmando pago manual: {e}")
        raise HTTPException(status_code=500, detail="Error confirmando pago")


async def _notify_user_premium_activated(user_id: str, activation_result: Dict):
    """
    Notifica al usuario que su premium fue activado
    """
    try:
        # Obtener info del usuario para enviar mensaje
        from core.supabase import supabase
        
        user_result = supabase._get_client().table("users").select(
            "whatsapp_number, name, adhd_language_preference"
        ).eq("id", user_id).single().execute()
        
        if not user_result.data:
            logger.warning(f"Usuario {user_id} no encontrado para notificación")
            return
        
        user = user_result.data
        language_style = user.get('adhd_language_preference', 'natural')
        
        # Formatear mensaje de activación
        if language_style == 'neural':
            message = f"""🧠 PREMIUM_ACTIVATION_COMPLETE
            
════════════════════════════════════════════
✅ NEURAL_SYSTEM: FULLY_UNLOCKED

🎯 Plan activated: {activation_result['plan_activated'].upper()}
📅 Valid until: {activation_result.get('expires_at', 'LIFETIME')[:10]}
⚡ All ADHD protocols: AVAILABLE

🚀 READY_COMMANDS:
• /neural-status - Full system analysis
• /neural-protocol - Deploy routines
• /neural-focus - Attention optimization

💡 Your neural enhancement journey begins now!"""
        else:
            message = f"""🎉 ¡Premium activado exitosamente!

Tu upgrade a ADHD Premium está completo.

✨ **Plan activado:** {activation_result['plan_activated'].title()}
📅 **Válido hasta:** {activation_result.get('expires_at', 'Para siempre')[:10]}
🧠 **Acceso:** Todas las herramientas ADHD desbloqueadas

🚀 **Empezar ahora:**
• `/adhd-tutorial` - Tutorial completo
• `/adhd-rutina basica` - Tu primera rutina
• `/adhd-status` - Ver tu estado premium

💝 ¡Gracias por invertir en tu bienestar mental!"""
        
        # Enviar mensaje via WhatsApp
        from services.whatsapp_cloud import whatsapp_service
        
        await whatsapp_service.send_message(
            phone_number=user['whatsapp_number'],
            message=message
        )
        
        logger.info(f"Notificación de activación enviada a usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error enviando notificación de activación: {e}")


# Rutas de información (para debugging)
@router.get("/payment-status/{transaction_id}")
async def get_payment_status(transaction_id: str):
    """
    Endpoint para verificar estado de un pago (para debugging)
    """
    try:
        from core.supabase import supabase
        
        result = supabase._get_client().table("payment_transactions").select("*").eq(
            "transaction_id", transaction_id
        ).execute()
        
        if result.data:
            return {
                "found": True,
                "status": result.data[0]['status'],
                "amount": result.data[0]['amount'],
                "created_at": result.data[0]['created_at']
            }
        else:
            return {"found": False}
            
    except Exception as e:
        logger.error(f"Error verificando estado de pago: {e}")
        raise HTTPException(status_code=500, detail="Error verificando pago")