#!/bin/bash
# ==========================================
# KOREI ASSISTANT - DEPLOY WITH IP + SSL
# Deploy directly to IP with self-signed SSL
# ==========================================

set -e

SERVER_IP="138.197.41.6"
DEPLOY_USER="deploy"
APP_DIR="/home/deploy/korei"

echo "🚀 Desplegando Korei Assistant con IP directa..."
echo "📍 Servidor: $SERVER_IP" 
echo "🔒 SSL: Certificado autofirmado"
echo "🌐 Webhook: https://$SERVER_IP/webhook/cloud"
echo ""

# Check SSH connection
echo "🔐 Verificando conexión SSH..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $DEPLOY_USER@$SERVER_IP exit 2>/dev/null; then
    echo "❌ Error: No se puede conectar al servidor"
    echo ""
    echo "🔧 Para configurar SSH:"
    echo "1. ssh root@$SERVER_IP"
    echo "2. adduser deploy"
    echo "3. usermod -aG sudo deploy" 
    echo "4. mkdir -p /home/deploy/.ssh"
    echo "5. cat >> /home/deploy/.ssh/authorized_keys"
    echo "   (pegar tu clave pública)"
    echo "6. chown -R deploy:deploy /home/deploy/.ssh"
    echo "7. chmod 700 /home/deploy/.ssh"
    echo "8. chmod 600 /home/deploy/.ssh/authorized_keys"
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
scp /tmp/korei-deploy.tar.gz $DEPLOY_USER@$SERVER_IP:/tmp/

# Setup and deploy on server
echo "🔧 Configurando servidor y desplegando..."
ssh $DEPLOY_USER@$SERVER_IP << 'SERVEREOF'
set -e

echo "📦 Actualizando sistema..."
sudo apt update
sudo apt install -y nginx openssl curl git docker.io docker-compose

echo "👤 Configurando permisos Docker..."
sudo usermod -aG docker deploy
sudo systemctl start docker
sudo systemctl enable docker

echo "🔒 Generando certificado SSL autofirmado..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/korei.key \
    -out /etc/nginx/ssl/korei.crt \
    -subj "/C=CR/ST=SanJose/L=SanJose/O=Korei/OU=IT/CN=138.197.41.6"

echo "🌐 Configurando nginx..."
sudo tee /etc/nginx/nginx.conf > /dev/null << 'NGINXCONF'
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
sudo nginx -t

echo "🔥 Configurando firewall..."
sudo ufw allow 22
sudo ufw allow 80  
sudo ufw allow 443
sudo ufw --force enable

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
sleep 20

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
    if curl -f -k http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Aplicación respondiendo en puerto 8000"
        break
    fi
    echo "⏳ Intento $i/12 - Esperando..."
    sleep 5
done

# Start nginx
echo "🌐 Iniciando nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Final health check through nginx
echo "🏥 Verificación final a través de nginx..."
sleep 5
if curl -f -k https://localhost/health > /dev/null 2>&1; then
    echo "✅ Nginx proxy funcionando correctamente"
else
    echo "⚠️ Advertencia: Nginx proxy puede necesitar ajustes"
    echo "Verificando logs de nginx:"
    sudo tail -n 10 /var/log/nginx/error.log
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