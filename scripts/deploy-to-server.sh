#!/bin/bash
# ==========================================
# KOREI ASSISTANT - DEPLOYMENT SCRIPT
# Deploy to production server with SSL
# ==========================================

set -e  # Exit on any error

# Configuration
SERVER_IP="138.197.41.6"
DEPLOY_USER="deploy"
APP_DIR="/home/deploy/korei"
DOMAIN="${1:-korei.example.com}"  # Pass domain as first argument

echo "🚀 Desplegando Korei Assistant..."
echo "📍 Servidor: $SERVER_IP"
echo "🌐 Dominio: $DOMAIN"
echo "📁 Directorio: $APP_DIR"
echo ""

# Check if domain was provided
if [ "$DOMAIN" = "korei.example.com" ]; then
    echo "❌ Error: Debes proporcionar un dominio válido"
    echo "Usage: $0 tu-dominio.com"
    echo "Example: $0 api.korei.app"
    exit 1
fi

# Check if we can SSH to the server
echo "🔐 Verificando conexión SSH..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $DEPLOY_USER@$SERVER_IP exit 2>/dev/null; then
    echo "❌ Error: No se puede conectar al servidor"
    echo "Asegúrate de que:"
    echo "1. El servidor esté corriendo"
    echo "2. Las llaves SSH estén configuradas"
    echo "3. El usuario 'deploy' exista"
    exit 1
fi

echo "✅ Conexión SSH exitosa"

# Create deployment package
echo "📦 Creando paquete de despliegue..."
tar -czf /tmp/korei-deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='logs' \
    --exclude='temp' \
    --exclude='.env' \
    .

echo "✅ Paquete creado: $(du -h /tmp/korei-deploy.tar.gz | cut -f1)"

# Transfer files to server
echo "📤 Transferiendo archivos al servidor..."
scp /tmp/korei-deploy.tar.gz $DEPLOY_USER@$SERVER_IP:/tmp/

# Deploy on server
echo "🔧 Desplegando en el servidor..."
ssh $DEPLOY_USER@$SERVER_IP << EOF
set -e

echo "📁 Preparando directorio de aplicación..."
mkdir -p $APP_DIR
cd $APP_DIR

# Backup current deployment if exists
if [ -d "current" ]; then
    echo "💾 Respaldando despliegue actual..."
    mv current backup-\$(date +%Y%m%d-%H%M%S) || true
fi

# Extract new deployment
echo "📦 Extrayendo nueva versión..."
mkdir -p current
cd current
tar -xzf /tmp/korei-deploy.tar.gz
rm /tmp/korei-deploy.tar.gz

# Setup production environment
echo "⚙️ Configurando entorno de producción..."
cp .env.production .env
sed -i "s/YOUR_DOMAIN.com/$DOMAIN/g" .env

# Update nginx configuration
echo "🌐 Configurando nginx..."
sudo sed "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/korei > /tmp/korei-nginx-final.conf
sudo mv /tmp/korei-nginx-final.conf /etc/nginx/sites-available/korei

# Enable site
sudo ln -sf /etc/nginx/sites-available/korei /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Get SSL certificate
echo "🔒 Configurando certificado SSL..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || echo "⚠️ SSL setup may need manual intervention"

# Build and start application
echo "🐳 Construyendo y iniciando aplicación..."
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

# Wait for application to start
echo "⏳ Esperando que la aplicación inicie..."
sleep 15

# Check health
echo "🏥 Verificando salud de la aplicación..."
if curl -f http://localhost:8000/health; then
    echo "✅ Aplicación iniciada correctamente"
else
    echo "❌ Error: La aplicación no responde"
    echo "Logs de la aplicación:"
    docker-compose logs --tail=20 korei-api
    exit 1
fi

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo ""
echo "📋 INFORMACIÓN DEL DESPLIEGUE:"
echo "🌐 URL: https://$DOMAIN"
echo "🏥 Health: https://$DOMAIN/health"
echo "📨 Webhook: https://$DOMAIN/webhook/cloud"
echo "📁 Logs: docker-compose logs -f"
echo "🔄 Restart: docker-compose restart"
echo ""
EOF

# Cleanup
rm -f /tmp/korei-deploy.tar.gz

echo "✅ ¡Despliegue completado!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Verificar que el sitio funcione: https://$DOMAIN/health"
echo "2. Actualizar webhook URL en WhatsApp Business API"
echo "3. Probar envío de mensajes"
echo ""
echo "🔗 URLs importantes:"
echo "   - Aplicación: https://$DOMAIN"
echo "   - Health: https://$DOMAIN/health"  
echo "   - Webhook: https://$DOMAIN/webhook/cloud"
echo ""