#!/bin/bash

# Script para verificar el estado del deploy en producción
# Ejecutar en el servidor DigitalOcean

echo "🔍 VERIFICANDO ESTADO DE PRODUCCIÓN..."

# 1. Verificar contenedores
echo "🐳 Estado de contenedores:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 2. Verificar logs de la aplicación
echo ""
echo "📋 Últimos logs de la aplicación:"
docker logs korei-assistant --tail=20

# 3. Verificar health endpoint
echo ""
echo "🏥 Probando health endpoint:"
if curl -f http://localhost/health; then
    echo "✅ Health check exitoso"
else
    echo "❌ Health check falló"
fi

# 4. Verificar webhook endpoint
echo ""
echo "🔗 Probando webhook verification:"
if curl -s "http://localhost/webhook/cloud?hub.mode=subscribe&hub.challenge=TEST123&hub.verify_token=korei_webhook_token_2024" | grep -q "TEST123"; then
    echo "✅ Webhook verification exitoso"
else
    echo "❌ Webhook verification falló"
fi

# 5. Verificar uso de recursos
echo ""
echo "📊 Uso de recursos:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 6. Verificar imágenes
echo ""
echo "🏗️ Imágenes disponibles:"
docker images | grep korei

# 7. Verificar red
echo ""
echo "🌐 Configuración de red:"
docker network ls | grep korei

# 8. Verificar variables de entorno (enmascaradas)
echo ""
echo "🔐 Variables de entorno (verificación):"
cd /opt/korei/korei-app
if [ -f .env ]; then
    echo "✅ Archivo .env existe"
    echo "Variables configuradas:"
    grep -v "^#" .env | cut -d'=' -f1 | while read var; do
        echo "  ✓ $var"
    done
else
    echo "❌ Archivo .env no encontrado"
fi

# 9. Test de conectividad externa
echo ""
echo "🌍 Conectividad externa:"
if curl -s --max-time 5 https://api.supabase.com > /dev/null; then
    echo "✅ Supabase accesible"
else
    echo "❌ Supabase no accesible"
fi

if curl -s --max-time 5 https://generativelanguage.googleapis.com > /dev/null; then
    echo "✅ Gemini API accesible"
else
    echo "❌ Gemini API no accesible"  
fi

if curl -s --max-time 5 https://graph.facebook.com > /dev/null; then
    echo "✅ WhatsApp API accesible"
else
    echo "❌ WhatsApp API no accesible"
fi

echo ""
echo "🎯 COMANDOS ÚTILES:"
echo "   Ver logs en tiempo real: docker logs korei-assistant -f"
echo "   Reiniciar aplicación:   docker compose restart korei-api"
echo "   Reconstruir:            docker compose up -d --build --force-recreate"
echo "   Limpiar imágenes:       docker image prune -af"