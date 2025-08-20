#!/bin/bash
# ==========================================
# KOREI ASSISTANT - DEPLOY AS ROOT
# Deploy using root user directly
# ==========================================

set -e

SERVER_IP="138.197.41.6"
ROOT_USER="root"
APP_DIR="/opt/korei"

echo "🚀 Desplegando Korei Assistant como root..."
echo "📍 Servidor: $SERVER_IP"
echo "👤 Usuario: $ROOT_USER" 
echo "🔒 SSL: Certificado autofirmado"
echo "🌐 Webhook: https://$SERVER_IP/webhook/cloud"
echo ""

# Check SSH connection
echo "🔐 Verificando conexión SSH como root..."
if ! ssh -o ConnectTimeout=10 $ROOT_USER@$SERVER_IP exit 2>/dev/null; then
    echo "❌ Error: No se puede conectar al servidor como root"
    echo ""
    echo "🔧 Opciones:"
    echo "1. Usar consola web de DigitalOcean"
    echo "2. Configurar clave SSH en el panel de DigitalOcean" 
    echo "3. Usar password authentication: ssh root@$SERVER_IP"
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

# Transfer to server
echo "📤 Transferiendo archivos..."
scp /tmp/korei-deploy.tar.gz $ROOT_USER@$SERVER_IP:/tmp/

# Setup and deploy on server
echo "🔧 Configurando servidor y desplegando..."
ssh $ROOT_USER@$SERVER_IP << 'SERVEREOF'
set -e

echo "📦 Actualizando sistema..."
apt update
apt install -y nginx openssl curl git docker.io docker-compose

echo "🐳 Configurando Docker..."
systemctl start docker
systemctl enable docker

echo "🔒 Generando certificado SSL autofirmado..."
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/korei.key \
    -out /etc/nginx/ssl/korei.crt \
    -subj "/C=CR/ST=SanJose/L=SanJose/O=Korei/OU=IT/CN=138.197.41.6"

echo "🌐 Configurando nginx..."
tee /etc/nginx/nginx.conf > /dev/null << 'NGINXCONF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

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
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

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
            
            # Timeouts for long requests
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # Special handling for webhook
        location /webhook {
            proxy_pass http://127.0.0.1:8000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Webhook specific settings
            proxy_buffering off;
            proxy_request_buffering off;
        }
    }
}
NGINXCONF

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

# Backup existing deployment
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
echo "⚙️ Configurando entorno de producción..."
cp .env.production .env

# Create logs and temp directories
mkdir -p logs temp

echo "🐳 Construyendo y desplegando aplicación..."
# Stop existing containers
docker-compose down 2>/dev/null || true

# Remove nginx service from docker-compose for our setup
sed -i '/nginx:/,$d' docker-compose.yml

# Build and start
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Esperando que la aplicación inicie..."
sleep 30

# Check if app is running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Error: La aplicación no se inició correctamente"
    echo "Logs:"
    docker-compose logs
    exit 1
fi

# Test application health
echo "🏥 Verificando salud de la aplicación..."
for i in {1..12}; do
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Aplicación respondiendo en puerto 8000"
        break
    fi
    echo "⏳ Intento $i/12 - Esperando..."
    sleep 5
    
    if [ $i -eq 12 ]; then
        echo "❌ La aplicación no responde después de 60 segundos"
        echo "Logs de la aplicación:"
        docker-compose logs --tail=20
        exit 1
    fi
done

# Start nginx
echo "🌐 Iniciando nginx..."
systemctl restart nginx
systemctl enable nginx

# Final health check through nginx
echo "🏥 Verificación final a través de nginx..."
sleep 5
if curl -f -k -s https://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy funcionando correctamente"
else
    echo "⚠️ Advertencia: Nginx proxy puede necesitar ajustes"
    echo "Verificando logs de nginx:"
    tail -n 10 /var/log/nginx/error.log
fi

echo ""
echo "🎉 ¡DESPLIEGUE COMPLETADO!"
echo ""
echo "📋 INFORMACIÓN DEL DESPLIEGUE:"
echo "🌐 URL Principal: https://138.197.41.6"
echo "🏥 Health Check: https://138.197.41.6/health" 
echo "📨 Webhook URL: https://138.197.41.6/webhook/cloud"
echo "🔍 Logs: cd $APP_DIR/current && docker-compose logs -f"
echo "🔄 Restart: cd $APP_DIR/current && docker-compose restart"
echo ""
echo "⚠️ NOTA: Usas certificado autofirmado."
echo "   WhatsApp funcionará, pero navegadores mostrarán advertencia."
echo ""
SERVEREOF

# Cleanup local files
rm -f /tmp/korei-deploy.tar.gz

echo ""
echo "✅ ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Verificar aplicación: https://138.197.41.6/health"
echo "2. Actualizar webhook en Meta Developer Console:"
echo "   - URL: https://138.197.41.6/webhook/cloud"
echo "   - Token: korei_webhook_secret_2024"
echo "3. Probar enviando mensaje de WhatsApp"
echo ""
echo "🔗 URLs importantes:"
echo "   - App: https://138.197.41.6"
echo "   - Health: https://138.197.41.6/health"
echo "   - Webhook: https://138.197.41.6/webhook/cloud"
echo ""