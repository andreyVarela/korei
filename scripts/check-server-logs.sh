#!/bin/bash

# Script para revisar logs del servidor DigitalOcean
echo "🔍 REVISANDO LOGS DEL SERVIDOR KOREI..."

# SSH al servidor y obtener logs
ssh deploy@138.197.41.6 << 'EOF'
echo "=== LOGS DEL CONTENEDOR KOREI ==="
cd /opt/korei/korei-app
docker logs korei-assistant --tail=100 --since="10m"

echo ""
echo "=== ESTADO DE CONTENEDORES ==="
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== ÚLTIMOS LOGS DE NGINX ==="
docker logs korei-nginx --tail=20 --since="10m" || echo "No nginx logs"

echo ""
echo "=== ARCHIVOS DE LOG EN EL CONTENEDOR ==="
docker exec korei-assistant ls -la /app/logs/ || echo "No log files"

echo ""
echo "=== ÚLTIMOS LOGS DE LA APLICACIÓN ==="
docker exec korei-assistant tail -50 /app/logs/app.log || echo "No app.log file"

EOF