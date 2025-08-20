-- Migración para sistema de planes escalonados (FREE → BASIC → ADHD)
-- Ejecutar después de premium_features_migration.sql

-- 1. Actualizar planes existentes
DELETE FROM premium_plans; -- Limpiar planes anteriores

-- 2. Insertar nueva estructura de planes
INSERT INTO premium_plans (plan_name, plan_type, price, features, description) VALUES 

-- Plan FREE (muy limitado)
('free_plan', 'free', 0.00, 
 '["basic_help", "basic_register", "limited_tasks"]',
 'Plan gratuito con funcionalidad muy limitada - máximo 5 tareas/mes'),

-- Plan 1: BASIC (servicio completo sin ADHD)
('basic_monthly', 'monthly', 4.99, 
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events", "email_support"]',
 'Plan básico completo - Todas las funciones actuales sin ADHD'),

('basic_yearly', 'yearly', 49.99, 
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events", "email_support", "priority_features"]',
 'Plan básico anual con descuento (2 meses gratis)'),

-- Plan 2: ADHD PREMIUM (todo incluido)
('adhd_monthly', 'monthly', 9.99, 
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events", "adhd_support", "neural_hacking", "crisis_management", "pattern_analysis", "priority_support"]',
 'Plan premium completo con soporte ADHD especializado'),

('adhd_yearly', 'yearly', 99.99, 
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events", "adhd_support", "neural_hacking", "crisis_management", "pattern_analysis", "priority_support", "advanced_analytics"]',
 'Plan premium anual con todas las funciones ADHD'),

-- Trial para probar BASIC (3 días)
('basic_trial', 'trial', 0.00,
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events"]',
 'Prueba gratuita de 3 días del plan básico'),

-- Trial para probar ADHD (7 días)
('adhd_trial', 'trial', 0.00,
 '["unlimited_tasks", "integrations", "stats", "reminders", "expenses", "events", "adhd_support", "neural_hacking", "crisis_management"]',
 'Prueba gratuita de 7 días del plan ADHD premium');

-- 3. Agregar campos adicionales para el nuevo sistema
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS basic_trial_used BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS basic_trial_expires_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS monthly_task_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_task_reset_date DATE DEFAULT CURRENT_DATE;

-- 4. Función para verificar límites del plan FREE
CREATE OR REPLACE FUNCTION check_free_plan_limits(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    user_plan VARCHAR(20);
    task_count INTEGER;
    reset_date DATE;
BEGIN
    -- Obtener plan del usuario
    SELECT plan_type, monthly_task_count, last_task_reset_date
    INTO user_plan, task_count, reset_date
    FROM users 
    WHERE id = user_uuid;
    
    -- Si no es plan free, no hay límites
    IF user_plan != 'free' THEN
        RETURN TRUE;
    END IF;
    
    -- Reset contador si cambió el mes
    IF reset_date < DATE_TRUNC('month', CURRENT_DATE)::DATE THEN
        UPDATE users 
        SET 
            monthly_task_count = 0,
            last_task_reset_date = CURRENT_DATE
        WHERE id = user_uuid;
        task_count := 0;
    END IF;
    
    -- Verificar límite de 5 tareas para FREE
    RETURN task_count < 5;
END;
$$ LANGUAGE plpgsql;

-- 5. Función para incrementar contador de tareas
CREATE OR REPLACE FUNCTION increment_task_count(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET 
        monthly_task_count = monthly_task_count + 1,
        last_task_reset_date = CURRENT_DATE
    WHERE id = user_uuid;
END;
$$ LANGUAGE plpgsql;

-- 6. Función para activar trial básico
CREATE OR REPLACE FUNCTION activate_basic_trial(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Verificar si ya usó el trial básico
    IF EXISTS (SELECT 1 FROM users WHERE id = user_uuid AND basic_trial_used = true) THEN
        RETURN FALSE;
    END IF;
    
    -- Activar trial básico de 3 días
    UPDATE users 
    SET 
        basic_trial_used = true,
        basic_trial_expires_at = NOW() + INTERVAL '3 days',
        plan_type = 'basic_trial',
        updated_at = NOW()
    WHERE id = user_uuid;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 7. Función mejorada para verificar acceso (reemplaza la anterior)
CREATE OR REPLACE FUNCTION check_feature_access(user_uuid UUID, feature_name VARCHAR)
RETURNS JSONB AS $$
DECLARE
    user_record RECORD;
    result JSONB;
BEGIN
    -- Obtener información completa del usuario
    SELECT 
        plan_type, 
        premium_active, 
        premium_expires_at,
        trial_used,
        trial_expires_at,
        basic_trial_used,
        basic_trial_expires_at,
        monthly_task_count,
        last_task_reset_date
    INTO user_record
    FROM users 
    WHERE id = user_uuid;
    
    -- Si no existe el usuario
    IF NOT FOUND THEN
        RETURN '{"has_access": false, "reason": "user_not_found"}'::JSONB;
    END IF;
    
    -- Features siempre gratuitas
    IF feature_name IN ('basic_help', 'basic_register') THEN
        RETURN '{"has_access": true, "reason": "always_free"}'::JSONB;
    END IF;
    
    -- Premium activo (Plan ADHD)
    IF user_record.premium_active AND 
       (user_record.premium_expires_at IS NULL OR user_record.premium_expires_at > NOW()) THEN
        RETURN jsonb_build_object(
            'has_access', true,
            'reason', 'adhd_premium_active',
            'plan_type', user_record.plan_type,
            'expires_at', user_record.premium_expires_at
        );
    END IF;
    
    -- Trial ADHD activo
    IF user_record.trial_expires_at IS NOT NULL AND user_record.trial_expires_at > NOW() THEN
        IF feature_name IN ('adhd_support', 'neural_hacking', 'crisis_management') THEN
            RETURN jsonb_build_object(
                'has_access', true,
                'reason', 'adhd_trial_active',
                'expires_at', user_record.trial_expires_at
            );
        END IF;
        -- Trial ADHD incluye todas las funciones básicas también
        IF feature_name IN ('unlimited_tasks', 'integrations', 'stats', 'reminders', 'expenses', 'events') THEN
            RETURN jsonb_build_object(
                'has_access', true,
                'reason', 'adhd_trial_includes_basic',
                'expires_at', user_record.trial_expires_at
            );
        END IF;
    END IF;
    
    -- Plan básico pagado o trial básico activo
    IF user_record.plan_type IN ('basic_monthly', 'basic_yearly') OR
       (user_record.basic_trial_expires_at IS NOT NULL AND user_record.basic_trial_expires_at > NOW()) THEN
        IF feature_name IN ('unlimited_tasks', 'integrations', 'stats', 'reminders', 'expenses', 'events') THEN
            RETURN jsonb_build_object(
                'has_access', true,
                'reason', 'basic_plan_active',
                'plan_type', user_record.plan_type
            );
        END IF;
        -- Plan básico NO incluye funciones ADHD
        IF feature_name IN ('adhd_support', 'neural_hacking', 'crisis_management') THEN
            RETURN jsonb_build_object(
                'has_access', false,
                'reason', 'adhd_upgrade_required',
                'current_plan', 'basic'
            );
        END IF;
    END IF;
    
    -- Plan FREE - verificar límites
    IF user_record.plan_type = 'free' OR user_record.plan_type IS NULL THEN
        -- Reset contador si cambió el mes
        IF user_record.last_task_reset_date < DATE_TRUNC('month', CURRENT_DATE)::DATE THEN
            UPDATE users 
            SET 
                monthly_task_count = 0,
                last_task_reset_date = CURRENT_DATE
            WHERE id = user_uuid;
            user_record.monthly_task_count := 0;
        END IF;
        
        -- Features limitadas para FREE
        IF feature_name = 'limited_tasks' THEN
            IF user_record.monthly_task_count < 5 THEN
                RETURN jsonb_build_object(
                    'has_access', true,
                    'reason', 'free_plan_within_limits',
                    'remaining_tasks', 5 - user_record.monthly_task_count
                );
            ELSE
                RETURN jsonb_build_object(
                    'has_access', false,
                    'reason', 'free_plan_limit_reached',
                    'upgrade_required', true
                );
            END IF;
        END IF;
        
        -- Otras features requieren upgrade
        RETURN jsonb_build_object(
            'has_access', false,
            'reason', 'basic_plan_required',
            'current_plan', 'free',
            'basic_trial_available', NOT user_record.basic_trial_used,
            'adhd_trial_available', NOT user_record.trial_used
        );
    END IF;
    
    -- Default: sin acceso
    RETURN '{"has_access": false, "reason": "unknown_state"}'::JSONB;
END;
$$ LANGUAGE plpgsql;

-- 8. Vista para analytics de planes escalonados
CREATE OR REPLACE VIEW tiered_plan_analytics AS
SELECT 
    COUNT(*) as total_users,
    COUNT(*) FILTER (WHERE plan_type = 'free' OR plan_type IS NULL) as free_users,
    COUNT(*) FILTER (WHERE plan_type LIKE 'basic_%') as basic_users,
    COUNT(*) FILTER (WHERE plan_type LIKE 'adhd_%' AND premium_active = true) as adhd_users,
    COUNT(*) FILTER (WHERE basic_trial_used = true AND plan_type = 'free') as basic_trial_users,
    COUNT(*) FILTER (WHERE trial_used = true AND NOT premium_active) as adhd_trial_users,
    
    -- Ingresos mensuales estimados
    COUNT(*) FILTER (WHERE plan_type = 'basic_monthly') * 4.99 as basic_monthly_revenue,
    COUNT(*) FILTER (WHERE plan_type = 'basic_yearly') * 49.99 as basic_yearly_revenue,
    COUNT(*) FILTER (WHERE plan_type = 'adhd_monthly') * 9.99 as adhd_monthly_revenue,
    COUNT(*) FILTER (WHERE plan_type = 'adhd_yearly') * 99.99 as adhd_yearly_revenue
FROM users;

-- 9. Función para upgrade entre planes
CREATE OR REPLACE FUNCTION upgrade_user_plan(
    user_uuid UUID,
    new_plan_name VARCHAR,
    transaction_uuid UUID DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    plan_record premium_plans%ROWTYPE;
    result JSONB;
BEGIN
    -- Obtener información del nuevo plan
    SELECT * INTO plan_record
    FROM premium_plans 
    WHERE plan_name = new_plan_name AND active = true;
    
    IF NOT FOUND THEN
        RETURN '{"success": false, "error": "Plan not found"}'::JSONB;
    END IF;
    
    -- Actualizar usuario según el tipo de plan
    IF plan_record.plan_name LIKE 'basic_%' THEN
        -- Upgrade a plan básico
        UPDATE users 
        SET 
            plan_type = plan_record.plan_type,
            premium_active = false,  -- Plan básico no es premium
            premium_expires_at = CASE 
                WHEN plan_record.plan_type = 'yearly' THEN NOW() + INTERVAL '1 year'
                WHEN plan_record.plan_type = 'monthly' THEN NOW() + INTERVAL '1 month'
                ELSE NULL
            END,
            updated_at = NOW()
        WHERE id = user_uuid;
        
    ELSIF plan_record.plan_name LIKE 'adhd_%' THEN
        -- Upgrade a plan ADHD premium
        UPDATE users 
        SET 
            plan_type = plan_record.plan_type,
            premium_active = true,
            premium_expires_at = CASE 
                WHEN plan_record.plan_type = 'yearly' THEN NOW() + INTERVAL '1 year'
                WHEN plan_record.plan_type = 'monthly' THEN NOW() + INTERVAL '1 month'
                ELSE NULL
            END,
            updated_at = NOW()
        WHERE id = user_uuid;
    END IF;
    
    -- Registrar en historial
    INSERT INTO user_plan_history (user_id, plan_id, transaction_id, plan_type, started_at, expires_at)
    VALUES (
        user_uuid,
        plan_record.id,
        transaction_uuid,
        plan_record.plan_type,
        NOW(),
        CASE 
            WHEN plan_record.plan_type = 'yearly' THEN NOW() + INTERVAL '1 year'
            WHEN plan_record.plan_type = 'monthly' THEN NOW() + INTERVAL '1 month'
            ELSE NULL
        END
    );
    
    RETURN jsonb_build_object(
        'success', true,
        'plan_name', plan_record.plan_name,
        'plan_type', plan_record.plan_type,
        'is_premium', plan_record.plan_name LIKE 'adhd_%'
    );
END;
$$ LANGUAGE plpgsql;

-- 10. Triggers para mantener contadores actualizados
CREATE OR REPLACE FUNCTION update_task_counter()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo contar si es una tarea nueva (no actualización)
    IF TG_OP = 'INSERT' AND NEW.type = 'tarea' THEN
        PERFORM increment_task_count(NEW.user_id);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear trigger si no existe
DROP TRIGGER IF EXISTS task_counter_trigger ON entries;
CREATE TRIGGER task_counter_trigger
    AFTER INSERT ON entries
    FOR EACH ROW
    EXECUTE FUNCTION update_task_counter();

-- 11. Comentarios de documentación
COMMENT ON FUNCTION check_feature_access IS 'Verifica acceso a funcionalidades según el plan del usuario (FREE → BASIC → ADHD)';
COMMENT ON FUNCTION check_free_plan_limits IS 'Verifica límites del plan gratuito (5 tareas/mes)';
COMMENT ON FUNCTION activate_basic_trial IS 'Activa trial de 3 días para plan básico';
COMMENT ON FUNCTION upgrade_user_plan IS 'Actualiza plan de usuario (FREE → BASIC → ADHD)';
COMMENT ON VIEW tiered_plan_analytics IS 'Analytics de usuarios por nivel de plan y ingresos estimados';