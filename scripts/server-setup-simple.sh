#!/bin/bash
# Setup simple para servidor DigitalOcean 138.197.41.6
# Ejecutar como root

set -e

echo "🚀 Configurando servidor para Korei Assistant..."

# 1. Actualizar sistema
apt update && apt upgrade -y

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# 3. Crear usuario para deploy
useradd -m -s /bin/bash deploy
usermod -aG docker deploy
echo "deploy ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 4. Crear directorio para la app
mkdir -p /opt/korei
chown -R deploy:deploy /opt/korei

# 5. Configurar SSH para deploy user
mkdir -p /home/deploy/.ssh
chown deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh

# 6. Instalar herramientas básicas
apt install -y curl wget git htop nano ufw

# 7. Configurar firewall básico
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 8. Habilitar swap para mejor rendimiento
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab

echo "✅ Servidor configurado!"
echo ""
echo "📋 SIGUIENTE PASOS:"
echo "1. Generar SSH key para GitHub Actions:"
echo "   Su-usuario deploy:"
echo "   su - deploy"
echo "   ssh-keygen -t rsa -b 4096 -C 'github-actions'"
echo ""
echo "2. Copiar la clave pública al repositorio:"
echo "   cat ~/.ssh/id_rsa.pub"
echo ""
echo "3. Configurar GitHub Secrets con la clave privada:"
echo "   cat ~/.ssh/id_rsa"
echo ""
echo "4. Agregar variables de entorno en GitHub Secrets"