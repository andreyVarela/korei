#!/bin/bash
# ==========================================
# KOREI ASSISTANT - SIMPLE DEPLOY 
# Deploy using existing Docker installation
# ==========================================

set -e

SERVER_IP="138.197.41.6"
ROOT_USER="root"
APP_DIR="/opt/korei"

echo "🚀 Desplegando Korei Assistant (Docker existente)..."
echo "📍 Servidor: $SERVER_IP"
echo "🌐 Webhook: https://$SERVER_IP/webhook/cloud"
echo ""

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

# Transfer to server
echo "📤 Transferiendo archivos..."
scp /tmp/korei-deploy.tar.gz $ROOT_USER@$SERVER_IP:/tmp/

# Deploy on server
ssh $ROOT_USER@$SERVER_IP << 'SERVEREOF'
set -e

echo "📦 Instalando solo nginx (sin conflictos Docker)..."
apt update
apt install -y nginx openssl curl

echo "🔒 Generando certificado SSL autofirmado..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/korei.key \
    -out /etc/nginx/ssl/korei.crt \
    -subj "/C=CR/ST=SanJose/L=SanJose/O=Korei/OU=IT/CN=138.197.41.6"

echo "🌐 Configurando nginx..."
tee /etc/nginx/sites-available/korei > /dev/null << 'NGINXCONF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name _;

    # SSL configuration
    ssl_certificate /etc/nginx/ssl/korei.crt;
    ssl_certificate_key /etc/nginx/ssl/korei.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI app
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
NGINXCONF

# Enable site
ln -sf /etc/nginx/sites-available/korei /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

echo "🔥 Configurando firewall..."
ufw allow 22
ufw allow 80  
ufw allow 443
ufw --force enable

echo "📁 Preparando aplicación..."
mkdir -p $APP_DIR
cd $APP_DIR

# Backup existing
if [ -d "current" ]; then
    echo "💾 Respaldando despliegue anterior..."
    mv current backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
fi

# Extract new deployment
echo "📦 Extrayendo nueva versión..."
mkdir -p current
cd current
tar -xzf /tmp/korei-deploy.tar.gz
rm /tmp/korei-deploy.tar.gz

# Setup production environment
echo "⚙️ Configurando entorno..."
cp .env.production .env
mkdir -p logs temp

echo "🐳 Desplegando con Docker existente..."
# Stop existing containers
docker-compose down 2>/dev/null || true

# Remove nginx from docker-compose (we use system nginx)
sed -i '/# Optional: Nginx reverse proxy/,$d' docker-compose.yml

# Build and start
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Esperando aplicación..."
sleep 30

# Check if app is running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: La aplicación no se inició"
    echo "Logs:"
    docker-compose logs --tail=30
    exit 1
fi

# Test health
echo "🏥 Verificando salud..."
for i in {1..15}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Aplicación funcionando en puerto 8000"
        break
    fi
    echo "⏳ Intento $i/15 - Esperando..."
    sleep 3
    
    if [ $i -eq 15 ]; then
        echo "❌ Aplicación no responde después de 45s"
        docker-compose logs --tail=20
        exit 1
    fi
done

# Start nginx
echo "🌐 Iniciando nginx..."
systemctl restart nginx
systemctl enable nginx

# Final verification
echo "🔍 Verificación final..."
sleep 5

# Test through nginx
if curl -f -k -s https://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy funcionando"
else
    echo "⚠️ Verificando nginx..."
    tail -n 5 /var/log/nginx/error.log || echo "Sin errores en nginx"
fi

echo ""
echo "🎉 ¡DESPLIEGUE COMPLETADO!"
echo ""
echo "📊 Estado de servicios:"
docker-compose ps
systemctl status nginx --no-pager -l

echo ""
echo "📋 INFORMACIÓN:"
echo "🌐 URL: https://138.197.41.6"
echo "🏥 Health: https://138.197.41.6/health"
echo "📨 Webhook: https://138.197.41.6/webhook/cloud"
echo "🔍 App Logs: cd $APP_DIR/current && docker-compose logs -f"
echo ""
SERVEREOF

# Cleanup
rm -f /tmp/korei-deploy.tar.gz

echo ""
echo "✅ ¡DESPLIEGUE TERMINADO!"
echo ""
echo "🧪 Probando conectividad..."
if curl -f -k -s https://138.197.41.6/health > /dev/null 2>&1; then
    echo "✅ Servidor respondiendo correctamente"
else
    echo "⚠️ Servidor puede necesitar unos minutos más"
fi

echo ""
echo "📋 SIGUIENTE PASO:"
echo "Actualizar webhook en Meta Developer Console:"
echo "URL: https://138.197.41.6/webhook/cloud"
echo "Token: korei_webhook_secret_2024"
echo ""