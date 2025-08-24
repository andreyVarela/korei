# 🚀 GUÍA DE DEPLOY - KOREI ASSISTANT

## ⚡ DEPLOY CORREGIDO - EJECUTAR INMEDIATAMENTE

### 🔧 Configuración de GitHub Secrets

Asegúrate de tener configurados estos secrets en tu repositorio:

```
SUPABASE_URL              - URL de tu proyecto Supabase
SUPABASE_KEY              - Service role key de Supabase  
WHATSAPP_CLOUD_TOKEN      - Token de WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID  - ID del número de teléfono
WHATSAPP_BUSINESS_ACCOUNT_ID - ID de la cuenta business
VERIFY_TOKEN              - Token de verificación del webhook
GEMINI_API_KEY            - API key de Google Gemini
SECRET_KEY                - Clave secreta para JWT
SSH_PRIVATE_KEY           - Clave privada SSH para acceso al droplet
```

### 🧪 Validar antes del Deploy

**En Windows:**
```cmd
scripts\validate-deploy.bat
```

**En Linux/macOS:**
```bash
chmod +x scripts/validate-deploy.sh
./scripts/validate-deploy.sh
```

### 🚀 Hacer Deploy

1. **Commit y push:**
```bash
git add .
git commit -m "fix: Deploy configuration corrections - containerized build"
git push origin main
```

2. **El workflow automáticamente:**
   - ✅ Construye imagen Docker con `--no-cache`
   - ✅ Sube imagen a GHCR con tag SHA específico
   - ✅ Hace deploy al droplet usando imagen específica
   - ✅ Verifica que el servicio esté funcionando

### 🔍 Verificar Deploy

**SSH al servidor:**
```bash
ssh deploy@138.197.41.6
cd /opt/korei/korei-app
./scripts/check-production.sh
```

**Endpoints importantes:**
- Health: `http://138.197.41.6/health`
- Webhook: `http://138.197.41.6/webhook/cloud`

### 🆘 Si algo falla

**Ver logs:**
```bash
# En el servidor
docker logs korei-assistant -f --tail=50
```

**Reconstruir completamente:**
```bash
# En el servidor  
cd /opt/korei/korei-app
docker compose down
docker system prune -af
export KOREI_IMAGE="ghcr.io/tu-usuario/korei:main-$(git rev-parse HEAD)"
docker compose up -d --force-recreate
```

**Reset completo:**
```bash
# En el servidor
cd /opt/korei
rm -rf korei-app
# Luego re-ejecutar el workflow
```

## 🔧 Cambios Realizados

### 1. **GitHub Actions** (`deploy.yml`)
- ✅ Construye imagen Docker con `--no-cache`
- ✅ Sube a GitHub Container Registry
- ✅ Usa tags SHA específicos (no `latest`)
- ✅ Verifica health check post-deploy

### 2. **Dockerfile** 
- ✅ Puerto dinámico con `$PORT`
- ✅ Health check con puerto dinámico
- ✅ Comando ajustado para Gunicorn

### 3. **docker-compose.yml**
- ✅ Usa imagen pre-construida de GHCR
- ✅ Puerto dinámico configurado
- ✅ Variables de entorno mejoradas

### 4. **main.py**
- ✅ Respeta `process.env.PORT` 
- ✅ Compatible con DigitalOcean App Platform

### 5. **nginx.conf**
- ✅ Rate limiting relajado para webhooks
- ✅ Configuración de proxy mejorada

## 📱 Configurar WhatsApp Webhook

Después del deploy exitoso, configura el webhook en Meta:

```
URL: https://tu-dominio.com/webhook/cloud
Verify Token: tu-verify-token-configurado
```

## 🎯 El deploy debería funcionar ahora

Los errores principales corregidos:
- ❌ **Build sin caché** → ✅ Usa `--no-cache`
- ❌ **Sin versionado** → ✅ Tags SHA específicos  
- ❌ **Puerto hardcodeado** → ✅ Puerto dinámico
- ❌ **Variables inconsistentes** → ✅ Mapping correcto
- ❌ **Sin validación** → ✅ Health check automático

**🚀 ¡LISTO PARA DEPLOY!**