-- Migración para sistema de planes premium y funciones ADHD
-- Ejecutar en Supabase SQL Editor

-- 1. Agregar campos de premium a la tabla users
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS plan_type VARCHAR(20) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS premium_active BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS premium_expires_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS payment_customer_id VARCHAR(255) NULL,
ADD COLUMN IF NOT EXISTS adhd_language_preference VARCHAR(10) DEFAULT 'natural',
ADD COLUMN IF NOT EXISTS trial_used BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS trial_expires_at TIMESTAMPTZ NULL;

-- 2. Crear tabla de planes premium
CREATE TABLE IF NOT EXISTS premium_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL UNIQUE,
    plan_type VARCHAR(20) NOT NULL, -- 'monthly', 'yearly', 'lifetime'
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    features JSONB NOT NULL, -- Lista de features incluidas
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Crear tabla de transacciones/pagos
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES premium_plans(id),
    transaction_id VARCHAR(255) NOT NULL, -- ID del proveedor de pago
    payment_provider VARCHAR(50) NOT NULL, -- 'stripe', 'paypal', etc.
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'pending', 'completed', 'failed', 'refunded'
    payment_method JSONB, -- Información del método de pago
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(transaction_id, payment_provider)
);

-- 4. Crear tabla de historial de planes
CREATE TABLE IF NOT EXISTS user_plan_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES premium_plans(id),
    transaction_id UUID REFERENCES payment_transactions(id),
    plan_type VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ NULL,
    reason VARCHAR(100) NULL, -- 'upgrade', 'downgrade', 'cancellation', 'expiry'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Crear tabla de sesiones de planes ADHD
CREATE TABLE IF NOT EXISTS adhd_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL, -- 'morning_routine', 'attention', 'dopamine', 'crisis'
    plan_name VARCHAR(200) NOT NULL,
    language_style VARCHAR(10) NOT NULL, -- 'neural', 'natural'
    plan_data JSONB NOT NULL, -- Datos completos del plan
    total_tasks INTEGER NOT NULL,
    completed_tasks INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'paused', 'cancelled'
    crisis_mode BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL
);

-- 6. Conectar entries con adhd_plans
ALTER TABLE entries 
ADD COLUMN IF NOT EXISTS adhd_plan_id UUID REFERENCES adhd_plans(id),
ADD COLUMN IF NOT EXISTS adhd_specific BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS language_style VARCHAR(10) NULL,
ADD COLUMN IF NOT EXISTS crisis_mode BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS duration_minutes INTEGER NULL;

-- 7. Insertar planes premium por defecto
INSERT INTO premium_plans (plan_name, plan_type, price, features, description) VALUES 
('adhd_monthly', 'monthly', 9.99, 
 '["adhd_support", "neural_hacking", "crisis_management", "personalized_analysis", "priority_support"]',
 'Soporte ADHD completo con ambos estilos de lenguaje'),
 
('adhd_yearly', 'yearly', 99.99, 
 '["adhd_support", "neural_hacking", "crisis_management", "personalized_analysis", "priority_support", "advanced_analytics"]',
 'Plan anual con descuento - Soporte ADHD premium'),

('free_trial', 'trial', 0.00,
 '["adhd_support_limited", "neural_hacking_preview"]',
 'Prueba gratuita de 7 días para funciones ADHD')
ON CONFLICT (plan_name) DO NOTHING;

-- 8. Función para verificar acceso premium
CREATE OR REPLACE FUNCTION check_premium_access(user_uuid UUID, feature_name VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    user_premium BOOLEAN;
    user_expires TIMESTAMPTZ;
    trial_expires TIMESTAMPTZ;
    trial_used BOOLEAN;
BEGIN
    -- Obtener información del usuario
    SELECT premium_active, premium_expires_at, trial_expires_at, trial_used
    INTO user_premium, user_expires, trial_expires, trial_used
    FROM users 
    WHERE id = user_uuid;
    
    -- Si no existe el usuario
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Si tiene premium activo y no ha expirado
    IF user_premium AND (user_expires IS NULL OR user_expires > NOW()) THEN
        RETURN TRUE;
    END IF;
    
    -- Si está en trial y no ha expirado
    IF NOT trial_used AND trial_expires IS NOT NULL AND trial_expires > NOW() THEN
        RETURN TRUE;
    END IF;
    
    -- Features gratuitas (básicas)
    IF feature_name IN ('basic_tasks', 'basic_stats', 'integrations') THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- 9. Función para activar trial gratuito
CREATE OR REPLACE FUNCTION activate_adhd_trial(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    trial_days INTEGER := 7;
BEGIN
    -- Verificar si ya usó el trial
    IF EXISTS (SELECT 1 FROM users WHERE id = user_uuid AND trial_used = true) THEN
        RETURN FALSE;
    END IF;
    
    -- Activar trial
    UPDATE users 
    SET 
        trial_used = true,
        trial_expires_at = NOW() + INTERVAL '7 days',
        updated_at = NOW()
    WHERE id = user_uuid;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 10. Función para activar premium
CREATE OR REPLACE FUNCTION activate_premium(
    user_uuid UUID, 
    plan_name VARCHAR, 
    transaction_uuid UUID,
    duration_months INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    plan_record premium_plans%ROWTYPE;
BEGIN
    -- Obtener información del plan
    SELECT * INTO plan_record
    FROM premium_plans 
    WHERE premium_plans.plan_name = activate_premium.plan_name 
    AND active = true;
    
    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;
    
    -- Activar premium
    UPDATE users 
    SET 
        premium_active = true,
        plan_type = plan_record.plan_type,
        premium_expires_at = CASE 
            WHEN plan_record.plan_type = 'lifetime' THEN NULL
            ELSE NOW() + (duration_months || ' months')::INTERVAL
        END,
        updated_at = NOW()
    WHERE id = user_uuid;
    
    -- Registrar en historial
    INSERT INTO user_plan_history (user_id, plan_id, transaction_id, plan_type, started_at, expires_at)
    VALUES (
        user_uuid, 
        plan_record.id, 
        transaction_uuid,
        plan_record.plan_type,
        NOW(),
        CASE 
            WHEN plan_record.plan_type = 'lifetime' THEN NULL
            ELSE NOW() + (duration_months || ' months')::INTERVAL
        END
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 11. Índices para performance
CREATE INDEX IF NOT EXISTS idx_users_premium_status 
ON users(premium_active, premium_expires_at);

CREATE INDEX IF NOT EXISTS idx_users_trial_status 
ON users(trial_used, trial_expires_at);

CREATE INDEX IF NOT EXISTS idx_payment_transactions_user 
ON payment_transactions(user_id, status);

CREATE INDEX IF NOT EXISTS idx_adhd_plans_user_status 
ON adhd_plans(user_id, status);

CREATE INDEX IF NOT EXISTS idx_entries_adhd_plan 
ON entries(adhd_plan_id);

-- 12. RLS Policies
ALTER TABLE premium_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_plan_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE adhd_plans ENABLE ROW LEVEL SECURITY;

-- Políticas de acceso
CREATE POLICY premium_plans_public_read ON premium_plans
    FOR SELECT USING (active = true);

CREATE POLICY payment_transactions_user_policy ON payment_transactions
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY user_plan_history_user_policy ON user_plan_history
    FOR ALL USING (auth.uid()::text = user_id::text);

CREATE POLICY adhd_plans_user_policy ON adhd_plans
    FOR ALL USING (auth.uid()::text = user_id::text);

-- 13. Triggers para updated_at
CREATE TRIGGER update_premium_plans_updated_at 
    BEFORE UPDATE ON premium_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payment_transactions_updated_at 
    BEFORE UPDATE ON payment_transactions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adhd_plans_updated_at 
    BEFORE UPDATE ON adhd_plans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 14. Vista para dashboard de admin
CREATE OR REPLACE VIEW premium_analytics AS
SELECT 
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE premium_active = true) as premium_users,
    COUNT(*) FILTER (WHERE trial_used = true AND premium_active = false) as trial_users,
    COUNT(*) FILTER (WHERE plan_type = 'free') as free_users,
    COUNT(*) FILTER (WHERE adhd_language_preference = 'neural') as neural_users,
    COUNT(*) FILTER (WHERE adhd_language_preference = 'natural') as natural_users,
    AVG(CASE WHEN premium_active THEN 
        EXTRACT(EPOCH FROM (premium_expires_at - NOW()))/86400 
        ELSE NULL END) as avg_days_remaining
FROM users;

-- 15. Comentarios de documentación
COMMENT ON TABLE premium_plans IS 'Planes premium disponibles para usuarios';
COMMENT ON TABLE payment_transactions IS 'Historial de transacciones de pago';
COMMENT ON TABLE user_plan_history IS 'Historial de cambios de plan por usuario';
COMMENT ON TABLE adhd_plans IS 'Planes ADHD específicos creados por usuarios premium';

COMMENT ON COLUMN users.plan_type IS 'Tipo de plan actual: free, monthly, yearly, lifetime';
COMMENT ON COLUMN users.premium_active IS 'Si el usuario tiene premium activo';
COMMENT ON COLUMN users.adhd_language_preference IS 'Preferencia de lenguaje: neural o natural';
COMMENT ON COLUMN users.trial_used IS 'Si el usuario ya usó su trial gratuito';

COMMENT ON FUNCTION check_premium_access IS 'Verifica si un usuario tiene acceso a una funcionalidad premium';
COMMENT ON FUNCTION activate_adhd_trial IS 'Activa trial gratuito de 7 días para ADHD';
COMMENT ON FUNCTION activate_premium IS 'Activa plan premium para un usuario';