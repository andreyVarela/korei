# 💎 Sistema de Upgrade Premium - Guía Completa

## 🔄 **Cómo Funciona el Sistema de Upgrade**

### **1. Flujo de Usuario Completo**

```
Usuario → /adhd-upgrade → Ve opciones → /adhd-checkout monthly → Pago → Activación automática
```

### **2. Dónde se Guarda Todo**

#### **Información del Usuario (tabla `users`):**
```sql
-- Estado premium del usuario
plan_type: 'free' → 'monthly' → 'yearly'
premium_active: false → true
premium_expires_at: NULL → '2024-09-17T00:00:00Z'
payment_customer_id: NULL → 'cus_stripe_123456'
adhd_language_preference: 'natural' / 'neural'
```

#### **Historial de Transacciones (tabla `payment_transactions`):**
```sql
-- Cada pago genera un registro
transaction_id: 'cs_stripe_abc123' (ID de Stripe)
payment_provider: 'stripe' / 'paypal' / 'manual'
amount: 9.99
currency: 'USD'
status: 'pending' → 'completed' → 'failed'
```

#### **Historial de Planes (tabla `user_plan_history`):**
```sql
-- Cada cambio de plan genera un registro
plan_type: 'monthly'
started_at: '2024-08-17T00:00:00Z'
expires_at: '2024-09-17T00:00:00Z'
reason: 'upgrade' / 'downgrade' / 'renewal'
```

## 🚀 **Comandos de Upgrade Implementados**

### **Para Usuarios que Necesitan Upgrade:**
```bash
# Ver opciones de upgrade
/adhd-upgrade          # Estilo natural  
/neural-upgrade        # Estilo técnico

# Crear checkout para pago
/adhd-checkout monthly     # Plan mensual ($9.99)
/adhd-checkout yearly      # Plan anual ($99.99)
/neural-checkout monthly   # Versión técnica
/neural-checkout yearly    # Versión técnica
```

### **Mensajes que Ve el Usuario:**

#### **Upgrade Natural Style:**
```
🌟 ¡Upgrade a Premium ADHD!

💝 **Opciones de upgrade:**

🌅 **Plan Mensual - $9.99/mes**
• Perfecto para probar a largo plazo
• Cancela cuando quieras  
• Todas las funciones ADHD desbloqueadas

⚡ **Plan Anual - $99.99/año** (¡Recomendado!)
• Ahorra $19.89 al año (17% descuento)
• 2 meses gratis incluidos

🚀 **Para upgradar:**
• `/adhd-checkout monthly` - Suscripción mensual
• `/adhd-checkout yearly` - Suscripción anual
```

#### **Upgrade Neural Style:**
```
🧠 PREMIUM_UPGRADE_PROTOCOL

⚡ NEURAL_MONTHLY_v2.1:
├─ Price: $9.99/month
├─ Features: ALL_ADHD_PROTOCOLS unlocked
└─ Activation: Immediate

🚀 NEURAL_YEARLY_v2.1 [OPTIMIZED]:
├─ Price: $99.99/year (17% savings)
└─ Recommended: MAXIMUM_VALUE

⚙️ UPGRADE_PROTOCOLS:
• /neural-checkout monthly - Start subscription
• /neural-checkout yearly - Start subscription
```

## 💳 **Métodos de Pago Implementados**

### **1. Stripe (Automático - Recomendado)**
```bash
# Configurar variables de entorno:
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
APP_BASE_URL=https://tu-app.com

# El usuario recibe:
🔗 Enlace de pago: https://checkout.stripe.com/pay/cs_abc123
✅ Activación automática después del pago
```

### **2. PayPal (Automático)**
```bash
# Configurar variables:
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# Flujo similar a Stripe
```

### **3. Pago Manual (Para casos especiales)**
```bash
# El usuario recibe:
💰 Monto: $9.99 USD
🔢 Referencia: manual_abc12345
📧 Notificar a: support@tu-app.com

💳 Métodos disponibles:
• Transferencia bancaria
• PayPal: tu-email@paypal.com
```

## 🔧 **Configuración Requerida**

### **Variables de Entorno:**
```env
# Stripe (Recomendado)
STRIPE_SECRET_KEY=sk_test_o_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal (Opcional)  
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...

# App URLs (para redirects)
APP_BASE_URL=https://tu-app.com

# Admin key para confirmar pagos manuales
ADMIN_PAYMENT_KEY=tu_admin_key_super_secreto
```

### **Instalar Dependencias:**
```bash
# Para Stripe
pip install stripe

# Para PayPal  
pip install paypalrestsdk
```

## 🔗 **Webhooks - Activación Automática**

### **URLs de Webhook Configuradas:**

```
# Stripe webhook
POST /webhook/payment/stripe-webhook

# PayPal webhook  
POST /webhook/payment/paypal-webhook

# Confirmación manual (solo admins)
POST /webhook/payment/manual-payment-confirm
```

### **Flujo de Activación Automática:**
```
1. Usuario paga en Stripe/PayPal
2. Proveedor envía webhook a tu servidor
3. Sistema verifica el pago
4. Activa premium automáticamente  
5. Envía notificación via WhatsApp al usuario
6. Usuario puede usar funciones premium inmediatamente
```

## 📊 **Verificación de Acceso Premium**

### **Cómo Verifica el Sistema:**
```python
# En cada comando ADHD, el sistema verifica:
1. ¿Usuario tiene premium_active = true?
2. ¿premium_expires_at > now() o es NULL (lifetime)?
3. ¿Trial disponible o activo?

# Si no tiene acceso → Muestra mensaje de upgrade
# Si tiene acceso → Ejecuta comando normalmente
```

### **Estados Posibles del Usuario:**
```
🆓 FREE: plan_type='free', premium_active=false
🎁 TRIAL: trial_expires_at > now(), premium_active=false  
💎 PREMIUM: premium_active=true, premium_expires_at > now()
⏰ EXPIRED: premium_active=false, premium_expires_at < now()
```

## 🧪 **Testing del Sistema**

### **1. Test Local (Sin Pagos Reales):**
```bash
# Activar trial para test
/adhd-trial

# Crear plan sin pago  
/adhd-rutina basica

# Verificar límites de trial
# (3 planes máximo en trial)
```

### **2. Test con Stripe Test Mode:**
```bash
# Usar tarjetas de prueba de Stripe:
# 4242424242424242 - Visa exitosa
# 4000000000000002 - Tarjeta declinada

# Configurar:
STRIPE_SECRET_KEY=sk_test_...
```

### **3. Test de Pago Manual:**
```bash
# Crear pago manual
curl -X POST /webhook/payment/manual-payment-confirm \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "manual_test123",
    "admin_key": "tu_admin_key"
  }'
```

## 📈 **Métricas y Monitoreo**

### **Queries Útiles para Analytics:**
```sql
-- Conversión trial → premium
SELECT 
  COUNT(*) FILTER (WHERE trial_used = true) as trial_users,
  COUNT(*) FILTER (WHERE premium_active = true) as premium_users,
  ROUND(
    COUNT(*) FILTER (WHERE premium_active = true) * 100.0 / 
    COUNT(*) FILTER (WHERE trial_used = true), 2
  ) as conversion_rate
FROM users;

-- Ingresos mensuales
SELECT 
  DATE_TRUNC('month', created_at) as month,
  SUM(amount) as revenue,
  COUNT(*) as transactions
FROM payment_transactions 
WHERE status = 'completed'
GROUP BY month
ORDER BY month;

-- Planes más populares
SELECT plan_type, COUNT(*) 
FROM users 
WHERE premium_active = true 
GROUP BY plan_type;
```

## ⚠️ **Consideraciones Importantes**

### **Seguridad:**
1. **Verificar signatures** de webhooks en producción
2. **Usar HTTPS** para todos los endpoints de pago
3. **Admin key** debe ser complejo y secreto
4. **No guardar** datos de tarjetas (Stripe se encarga)

### **UX:**
1. **Mensajes claros** sobre qué incluye premium
2. **Trial gratuito** reduce fricción de compra
3. **Dual language** amplía mercado potencial
4. **Activación inmediata** mejora satisfacción

### **Mantenimiento:**
1. **Monitorear webhooks** (logs de errores)
2. **Revisar suscripciones** que fallan al renovar
3. **Actualizar precios** en tabla premium_plans
4. **Backup** de datos de transacciones

---

## ✅ **Checklist de Implementación de Pagos**

- [x] ✅ Código de upgrade implementado
- [x] ✅ Payment service creado
- [x] ✅ Webhooks implementados  
- [x] ✅ Base de datos preparada
- [x] ✅ Comandos de checkout listos
- [ ] 🔲 Stripe/PayPal configurado en producción
- [ ] 🔲 Variables de entorno configuradas
- [ ] 🔲 Webhooks registrados con proveedores
- [ ] 🔲 Testing end-to-end completado
- [ ] 🔲 Monitoring de transacciones activo

**El sistema de upgrade está completamente implementado y listo para recibir pagos reales.** Solo necesitas configurar las credenciales de Stripe/PayPal y registrar los webhooks.