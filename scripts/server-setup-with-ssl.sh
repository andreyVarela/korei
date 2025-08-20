#!/bin/bash
# ==========================================
# KOREI ASSISTANT - SERVER SETUP WITH SSL
# Setup for DigitalOcean Ubuntu Droplet
# ==========================================

set -e  # Exit on any error

echo "🚀 Iniciando configuración del servidor con SSL..."

# Update system
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "🔧 Instalando dependencias..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    nginx \
    certbot \
    python3-certbot-nginx

# Install Docker
echo "🐳 Instalando Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "Docker ya está instalado"
fi

# Install Docker Compose
echo "📋 Instalando Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose ya está instalado"
fi

# Create deploy user
echo "👤 Configurando usuario deploy..."
if ! id -u deploy > /dev/null 2>&1; then
    sudo adduser --disabled-password --gecos "" deploy
    sudo usermod -aG docker deploy
    sudo usermod -aG sudo deploy
    
    # Setup SSH directory
    sudo mkdir -p /home/deploy/.ssh
    sudo chown deploy:deploy /home/deploy/.ssh
    sudo chmod 700 /home/deploy/.ssh
    
    echo "✅ Usuario deploy creado"
else
    echo "Usuario deploy ya existe"
fi

# Create application directory
echo "📁 Creando directorio de aplicación..."
sudo mkdir -p /home/deploy/korei
sudo chown -R deploy:deploy /home/deploy/korei

# Configure firewall
echo "🔒 Configurando firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Configure nginx
echo "🌐 Configurando nginx..."
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Create nginx config template (will be updated with actual domain)
cat > /tmp/korei-nginx.conf << 'EOF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name DOMAIN_PLACEHOLDER;

    # SSL configuration (will be handled by certbot)
    ssl_certificate /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/DOMAIN_PLACEHOLDER/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

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

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo mv /tmp/korei-nginx.conf /etc/nginx/sites-available/korei
sudo chown root:root /etc/nginx/sites-available/korei

# Create swap if needed
echo "💽 Configurando swap..."
if ! swapon --show | grep -q "/swapfile"; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ Swap de 2GB creado"
else
    echo "Swap ya existe"
fi

# Create deployment script
echo "📋 Creando script de despliegue..."
cat > /tmp/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Desplegando Korei Assistant..."

cd /home/deploy/korei

# Pull latest code
git pull origin main

# Build and start containers
docker-compose down || true
docker-compose build --no-cache
docker-compose up -d

echo "✅ Despliegue completado"

# Show status
docker-compose ps
EOF

sudo mv /tmp/deploy.sh /home/deploy/korei/deploy.sh
sudo chown deploy:deploy /home/deploy/korei/deploy.sh
sudo chmod +x /home/deploy/korei/deploy.sh

# Install GitHub CLI for easier repository management
echo "📱 Instalando GitHub CLI..."
if ! command -v gh &> /dev/null; then
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
else
    echo "GitHub CLI ya está instalado"
fi

echo ""
echo "🎉 ¡SERVIDOR CONFIGURADO EXITOSAMENTE!"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. Configurar dominio DNS apuntando a esta IP"
echo "2. Ejecutar certificado SSL: sudo certbot --nginx -d tu-dominio.com"
echo "3. Clonar repositorio en /home/deploy/korei"
echo "4. Configurar variables de entorno"
echo "5. Ejecutar primer despliegue"
echo ""
echo "🔗 IP del servidor: $(curl -s ifconfig.me)"
echo "📁 Directorio de aplicación: /home/deploy/korei"
echo "👤 Usuario: deploy"
echo ""