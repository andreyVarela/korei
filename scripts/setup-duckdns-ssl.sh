#!/bin/bash
# ==========================================
# KOREI ASSISTANT - DUCKDNS + LET'S ENCRYPT
# Setup valid SSL certificate with DuckDNS
# ==========================================

set -e

SERVER_IP="138.197.41.6"
ROOT_USER="root"
DOMAIN="${1}"
DUCKDNS_TOKEN="${2}"

if [ -z "$DOMAIN" ] || [ -z "$DUCKDNS_TOKEN" ]; then
    echo "❌ Error: Faltan parámetros"
    echo "Usage: $0 <tu-dominio.duckdns.org> <tu-duckdns-token>"
    echo "Example: $0 korei-api.duckdns.org abc123def456"
    exit 1
fi

echo "🦆 Configurando DuckDNS + Let's Encrypt..."
echo "📍 Servidor: $SERVER_IP"
echo "🌐 Dominio: $DOMAIN"
echo "🔒 SSL: Let's Encrypt"
echo ""

# Setup DuckDNS and Let's Encrypt on server
ssh $ROOT_USER@$SERVER_IP << SERVEREOF
set -e

echo "📦 Instalando certbot..."
apt update
apt install -y certbot

echo "🦆 Configurando DuckDNS..."
# Create DuckDNS update script
mkdir -p /etc/duckdns
cat > /etc/duckdns/duck.sh << 'DUCKSCRIPT'
#!/bin/bash
echo "Updating DuckDNS IP..."
curl -s "https://www.duckdns.org/update?domains=DOMAIN_PLACEHOLDER&token=TOKEN_PLACEHOLDER&ip=" || echo "DuckDNS update failed"
DUCKSCRIPT

# Replace placeholders
sed -i "s/DOMAIN_PLACEHOLDER/${DOMAIN%.duckdns.org}/" /etc/duckdns/duck.sh
sed -i "s/TOKEN_PLACEHOLDER/$DUCKDNS_TOKEN/" /etc/duckdns/duck.sh

chmod +x /etc/duckdns/duck.sh

# Update DuckDNS now
/etc/duckdns/duck.sh

echo "🔍 Verificando resolución DNS..."
sleep 10
if nslookup $DOMAIN | grep -q "138.197.41.6"; then
    echo "✅ DNS resolviendo correctamente"
else
    echo "⚠️ DNS aún no resuelve. Esperando..."
    sleep 30
fi

echo "🔒 Configurando Let's Encrypt..."
# Stop nginx temporarily for standalone mode
cd /opt/korei/korei-app
docker compose stop nginx

# Get Let's Encrypt certificate
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@$DOMAIN \
    -d $DOMAIN

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ Error: No se pudo obtener certificado SSL"
    docker compose start nginx
    exit 1
fi

echo "✅ Certificado SSL obtenido"

echo "🔧 Configurando nginx con certificado válido..."
# Update nginx configuration with real SSL
cat > nginx.conf << 'NGINXEOF'
events {
    worker_connections 1024;
}

http {
    upstream korei_app {
        server korei-api:8000;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=webhook:10m rate=100r/s;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name DOMAIN_PLACEHOLDER;
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server with Let's Encrypt
    server {
        listen 443 ssl http2;
        server_name DOMAIN_PLACEHOLDER;
        
        # Let's Encrypt SSL configuration
        ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

        location /health {
            proxy_pass http://korei_app/health;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /webhook/ {
            limit_req zone=webhook burst=20 nodelay;
            proxy_pass http://korei_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location / {
            limit_req zone=api burst=5 nodelay;
            proxy_pass http://korei_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
NGINXEOF

# Replace domain placeholder
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" nginx.conf

echo "🐳 Actualizando docker-compose para Let's Encrypt..."
# Update docker-compose to mount Let's Encrypt certificates
cat >> docker-compose.yml << 'COMPOSEEOF'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
COMPOSEEOF

# Remove old SSL volume and add new one
sed -i '/- \.\/ssl:\/etc\/nginx\/ssl:ro/d' docker-compose.yml

echo "🚀 Reiniciando servicios..."
docker compose up -d

echo "⏳ Esperando que los servicios inicien..."
sleep 15

echo "🏥 Verificando salud de la aplicación..."
if curl -f https://$DOMAIN/health > /dev/null 2>&1; then
    echo "✅ ¡HTTPS funcionando con certificado válido!"
else
    echo "⚠️ Verificando estado..."
    docker compose ps
    docker compose logs nginx --tail=5
fi

echo "🔄 Configurando renovación automática..."
# Add cron job for certificate renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && cd /opt/korei/korei-app && docker compose restart nginx") | crontab -

echo ""
echo "🎉 ¡CONFIGURACIÓN COMPLETADA!"
echo ""
echo "📋 INFORMACIÓN:"
echo "🌐 URL: https://$DOMAIN"
echo "🏥 Health: https://$DOMAIN/health"
echo "📨 Webhook: https://$DOMAIN/webhook/cloud"
echo "🔒 SSL: Certificado válido de Let's Encrypt"
echo "🔄 Renovación: Automática cada día a las 12:00"
echo ""
SERVEREOF

echo ""
echo "✅ ¡SETUP DE DUCKDNS + SSL COMPLETADO!"
echo ""
echo "📨 ACTUALIZAR EN WHATSAPP:"
echo "URL: https://$DOMAIN/webhook/cloud"
echo "Token: korei_webhook_secret_2024"
echo ""
echo "🧪 PROBAR WEBHOOK:"
echo "curl https://$DOMAIN/webhook/cloud?hub.mode=subscribe&hub.challenge=test&hub.verify_token=korei_webhook_secret_2024"
echo ""