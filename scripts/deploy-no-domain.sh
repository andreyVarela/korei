#!/bin/bash
# ==========================================
# KOREI ASSISTANT - DEPLOY WITHOUT DOMAIN
# Deploy with self-signed SSL certificate
# ==========================================

set -e

SERVER_IP="138.197.41.6"
DEPLOY_USER="deploy" 

echo "🚀 Desplegando Korei Assistant SIN dominio..."
echo "📍 Servidor: $SERVER_IP"
echo "🔒 SSL: Certificado autofirmado"
echo ""

# Deploy to server
ssh $DEPLOY_USER@$SERVER_IP << 'EOF'
set -e

echo "📦 Actualizando sistema..."
sudo apt update
sudo apt install -y nginx openssl curl git docker.io docker-compose

echo "👤 Configurando usuario deploy..."
sudo usermod -aG docker deploy

echo "🔒 Generando certificado SSL autofirmado..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/korei.key \
    -out /etc/nginx/ssl/korei.crt \
    -subj "/C=CR/ST=SanJose/L=SanJose/O=Korei/OU=IT/CN=138.197.41.6"

echo "🌐 Configurando nginx..."
cat > /tmp/nginx-config << 'NGINXEOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

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

        # Proxy to FastAPI
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
}
NGINXEOF

sudo mv /tmp/nginx-config /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "🔥 Configurando firewall..."
sudo ufw allow 22
sudo ufw allow 80  
sudo ufw allow 443
sudo ufw --force enable

echo "📁 Preparando directorio de aplicación..."
mkdir -p /home/deploy/korei
cd /home/deploy/korei

echo "✅ Servidor configurado. Listo para recibir código."
EOF

echo ""
echo "✅ ¡Servidor configurado!"
echo ""
echo "📋 URLs para WhatsApp:"
echo "🔗 Webhook URL: https://138.197.41.6/webhook/cloud"
echo "🏥 Health Check: https://138.197.41.6/health"
echo ""
echo "⚠️ NOTA: Usarás certificado autofirmado"
echo "WhatsApp puede mostrar advertencia pero funcionará"
echo ""