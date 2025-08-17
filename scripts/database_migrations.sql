-- Migraciones para soportar integraciones externas
-- Ejecutar en Supabase SQL Editor

-- 1. Tabla para almacenar integraciones de usuarios
CREATE TABLE IF NOT EXISTS user_integrations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service VARCHAR(50) NOT NULL, -- 'google_calendar', 'todoist', etc.
    credentials TEXT NOT NULL, -- Credenciales encriptadas con AES-256-GCM (Base64)
    config JSONB DEFAULT '{}', -- Configuración específica
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'inactive', 'deleted'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_sync TIMESTAMPTZ NULL,
    
    -- Campos para auditoría de seguridad
    encryption_version VARCHAR(10) DEFAULT 'v1', -- Para futuras migraciones de encriptación
    last_access TIMESTAMPTZ NULL,
    access_count INTEGER DEFAULT 0,
    
    -- Índices únicos para prevenir duplicados
    UNIQUE(user_id, service)
);

-- 2. Tabla para almacenar insights de IA
CREATE TABLE IF NOT EXISTS ai_insights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL, -- 'financial_tip', 'spending_pattern', etc.
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    relevance_score DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NULL -- Para insights temporales
);

-- 3. Agregar campos para IDs externos en entries
ALTER TABLE entries 
ADD COLUMN IF NOT EXISTS external_id VARCHAR(255) NULL,
ADD COLUMN IF NOT EXISTS external_service VARCHAR(50) NULL,
ADD COLUMN IF NOT EXISTS external_url TEXT NULL;

-- 3.1. Agregar campos para proyectos de Todoist
ALTER TABLE entries 
ADD COLUMN IF NOT EXISTS project_id VARCHAR(255) NULL,
ADD COLUMN IF NOT EXISTS project_name VARCHAR(255) NULL;

-- 3.2. Agregar campos para timestamps de completado y actualización
ALTER TABLE entries 
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMPTZ NULL,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 4. Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_user_integrations_user_service 
ON user_integrations(user_id, service);

CREATE INDEX IF NOT EXISTS idx_user_integrations_status 
ON user_integrations(status);

CREATE INDEX IF NOT EXISTS idx_ai_insights_user_type 
ON ai_insights(user_id, insight_type);

CREATE INDEX IF NOT EXISTS idx_ai_insights_created 
ON ai_insights(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_entries_external 
ON entries(external_id, external_service);

CREATE INDEX IF NOT EXISTS idx_entries_project 
ON entries(project_id);

-- 5. Función para limpiar insights antiguos (opcional)
CREATE OR REPLACE FUNCTION cleanup_old_insights()
RETURNS void AS $$
BEGIN
    DELETE FROM ai_insights 
    WHERE expires_at IS NOT NULL 
    AND expires_at < NOW();
    
    -- Mantener solo los 20 insights más recientes por usuario/tipo
    DELETE FROM ai_insights 
    WHERE id NOT IN (
        SELECT id FROM (
            SELECT id,
                   ROW_NUMBER() OVER (PARTITION BY user_id, insight_type ORDER BY created_at DESC) as rn
            FROM ai_insights
        ) ranked
        WHERE rn <= 20
    );
END;
$$ LANGUAGE plpgsql;

-- 6. RLS (Row Level Security) policies
ALTER TABLE user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_insights ENABLE ROW LEVEL SECURITY;

-- Política para user_integrations: usuarios solo ven sus propias integraciones
CREATE POLICY user_integrations_user_policy ON user_integrations
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Política para ai_insights: usuarios solo ven sus propios insights
CREATE POLICY ai_insights_user_policy ON ai_insights
    FOR ALL USING (auth.uid()::text = user_id::text);

-- 7. Triggers para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_integrations_updated_at 
    BEFORE UPDATE ON user_integrations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger para updated_at en entries
CREATE TRIGGER update_entries_updated_at 
    BEFORE UPDATE ON entries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8. Trigger para auditoría de acceso a integraciones
CREATE OR REPLACE FUNCTION log_integration_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Solo actualizar en SELECT (cuando se accede a las credenciales)
    IF TG_OP = 'SELECT' THEN
        UPDATE user_integrations 
        SET 
            last_access = NOW(),
            access_count = access_count + 1
        WHERE id = NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Nota: Los triggers SELECT no están soportados directamente en PostgreSQL
-- Este trigger se aplicará en updates para fines de demostración
CREATE TRIGGER integration_access_log
    AFTER UPDATE ON user_integrations
    FOR EACH ROW 
    WHEN (OLD.last_access IS DISTINCT FROM NEW.last_access)
    EXECUTE FUNCTION log_integration_access();

-- 9. Función para rotar claves de encriptación (preparación futura)
CREATE OR REPLACE FUNCTION schedule_key_rotation()
RETURNS TABLE(
    user_id UUID,
    service VARCHAR(50),
    needs_rotation BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ui.user_id,
        ui.service,
        (ui.created_at < NOW() - INTERVAL '90 days') as needs_rotation
    FROM user_integrations ui
    WHERE ui.status = 'active'
    AND ui.encryption_version = 'v1'; -- Versiones antiguas
END;
$$ LANGUAGE plpgsql;

-- 10. Vista para monitoreo de seguridad (sin exponer credenciales)
CREATE OR REPLACE VIEW integration_security_audit AS
SELECT 
    ui.user_id,
    ui.service,
    ui.status,
    ui.created_at,
    ui.last_access,
    ui.access_count,
    ui.encryption_version,
    CASE 
        WHEN ui.last_access < NOW() - INTERVAL '30 days' THEN 'inactive'
        WHEN ui.access_count > 1000 THEN 'high_usage'
        ELSE 'normal'
    END as security_status,
    u.whatsapp_number
FROM user_integrations ui
JOIN users u ON ui.user_id = u.id
WHERE ui.status = 'active';

-- 11. Comentarios para documentación de seguridad
COMMENT ON TABLE user_integrations IS 'Almacena integraciones externas de usuarios con credenciales encriptadas AES-256-GCM';
COMMENT ON COLUMN user_integrations.credentials IS 'Credenciales encriptadas con AES-256-GCM, codificadas en Base64';
COMMENT ON COLUMN user_integrations.encryption_version IS 'Versión de encriptación para futuras migraciones de seguridad';
COMMENT ON COLUMN user_integrations.access_count IS 'Contador de accesos para auditoría de seguridad';
COMMENT ON VIEW integration_security_audit IS 'Vista de auditoría sin exponer credenciales sensibles';

COMMENT ON TABLE ai_insights IS 'Almacena insights generados por IA para evitar repetición y mejorar contexto';
COMMENT ON COLUMN entries.external_id IS 'ID del objeto en el servicio externo';
COMMENT ON COLUMN entries.external_service IS 'Nombre del servicio externo (google_calendar, todoist, etc.)';
COMMENT ON COLUMN entries.external_url IS 'URL para abrir el objeto en el servicio externo';
COMMENT ON COLUMN entries.project_id IS 'ID del proyecto de Todoist asignado automáticamente';
COMMENT ON COLUMN entries.project_name IS 'Nombre del proyecto de Todoist para referencia';

-- 12. Políticas adicionales de seguridad
-- Prevenir acceso a credenciales desde vistas no autorizadas
REVOKE ALL ON user_integrations FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_integrations TO authenticated;

-- Solo permitir acceso a la vista de auditoría
GRANT SELECT ON integration_security_audit TO authenticated;