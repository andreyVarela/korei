#!/bin/bash

# Script de validación para el deploy de Korei
set -e

echo "🔍 VALIDANDO CONFIGURACIÓN DE DEPLOY..."

# 1. Verificar que existen las variables necesarias
echo "📋 Verificando variables de entorno..."

required_vars=(
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY" 
    "WHATSAPP_ACCESS_TOKEN"
    "WHATSAPP_PHONE_NUMBER_ID"
    "WHATSAPP_VERIFY_TOKEN"
    "GEMINI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Falta variable: $var"
        exit 1
    else
        echo "✅ $var configurada"
    fi
done

# 2. Verificar conexión con Supabase
echo "🗄️  Probando conexión con Supabase..."
curl -s -H "apikey: $SUPABASE_SERVICE_KEY" \
     -H "Authorization: Bearer $SUPABASE_SERVICE_KEY" \
     "$SUPABASE_URL/rest/v1/" > /dev/null || {
    echo "❌ Error conectando con Supabase"
    exit 1
}
echo "✅ Supabase conectado"

# 3. Verificar token de Gemini
echo "🤖 Probando API de Gemini..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"test"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=$GEMINI_API_KEY" \
  | grep -q "candidates" || {
    echo "❌ Error con API de Gemini"
    exit 1
}
echo "✅ Gemini API funcionando"

# 4. Verificar token de WhatsApp
echo "📱 Verificando token de WhatsApp..."
curl -s -H "Authorization: Bearer $WHATSAPP_ACCESS_TOKEN" \
     "https://graph.facebook.com/v18.0/$WHATSAPP_PHONE_NUMBER_ID" \
     | grep -q "verified_name" || {
    echo "❌ Error con WhatsApp Cloud API"
    exit 1
}
echo "✅ WhatsApp API funcionando"

# 5. Construir imagen Docker localmente
echo "🐳 Construyendo imagen Docker..."
docker build -t korei-test . --no-cache || {
    echo "❌ Error construyendo imagen Docker"
    exit 1
}
echo "✅ Imagen Docker construida"

# 6. Probar contenedor localmente
echo "🚀 Probando contenedor..."
docker run -d --name korei-test -p 8001:8000 \
    -e SUPABASE_URL="$SUPABASE_URL" \
    -e SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY" \
    -e WHATSAPP_ACCESS_TOKEN="$WHATSAPP_ACCESS_TOKEN" \
    -e WHATSAPP_PHONE_NUMBER_ID="$WHATSAPP_PHONE_NUMBER_ID" \
    -e WHATSAPP_VERIFY_TOKEN="$WHATSAPP_VERIFY_TOKEN" \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e ENVIRONMENT=production \
    korei-test || {
    echo "❌ Error ejecutando contenedor"
    exit 1
}

# Esperar que el contenedor arranque
echo "⏳ Esperando que el servicio arranque..."
sleep 10

# Probar health endpoint
curl -f http://localhost:8001/health || {
    echo "❌ Health check falló"
    docker logs korei-test
    docker rm -f korei-test
    exit 1
}
echo "✅ Health check exitoso"

# Probar webhook endpoint
curl -s "http://localhost:8001/webhook/cloud?hub.mode=subscribe&hub.challenge=TEST123&hub.verify_token=$WHATSAPP_VERIFY_TOKEN" \
    | grep -q "TEST123" || {
    echo "❌ Webhook verification falló"
    docker logs korei-test
    docker rm -f korei-test
    exit 1
}
echo "✅ Webhook verification exitoso"

# Limpiar
docker rm -f korei-test
docker rmi korei-test

echo ""
echo "🎉 TODAS LAS VALIDACIONES PASARON"
echo "✅ El deploy debería funcionar correctamente"
echo ""
echo "📝 Para hacer deploy:"
echo "   git add ."
echo "   git commit -m 'fix: Deploy configuration corrections'"
echo "   git push origin main"