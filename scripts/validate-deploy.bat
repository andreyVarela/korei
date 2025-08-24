@echo off
setlocal EnableDelayedExpansion

echo 🔍 VALIDANDO CONFIGURACIÓN DE DEPLOY...

REM Cargar variables del .env
if exist .env (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        set "%%a=%%b"
    )
) else (
    echo ❌ Archivo .env no encontrado
    exit /b 1
)

echo 📋 Verificando variables de entorno...

REM Verificar variables necesarias
if "%SUPABASE_URL%"=="" (
    echo ❌ Falta variable: SUPABASE_URL
    exit /b 1
) else (
    echo ✅ SUPABASE_URL configurada
)

if "%SUPABASE_SERVICE_KEY%"=="" (
    echo ❌ Falta variable: SUPABASE_SERVICE_KEY  
    exit /b 1
) else (
    echo ✅ SUPABASE_SERVICE_KEY configurada
)

if "%WHATSAPP_ACCESS_TOKEN%"=="" (
    echo ❌ Falta variable: WHATSAPP_ACCESS_TOKEN
    exit /b 1
) else (
    echo ✅ WHATSAPP_ACCESS_TOKEN configurada
)

if "%WHATSAPP_PHONE_NUMBER_ID%"=="" (
    echo ❌ Falta variable: WHATSAPP_PHONE_NUMBER_ID
    exit /b 1
) else (
    echo ✅ WHATSAPP_PHONE_NUMBER_ID configurada
)

if "%WHATSAPP_VERIFY_TOKEN%"=="" (
    echo ❌ Falta variable: WHATSAPP_VERIFY_TOKEN
    exit /b 1
) else (
    echo ✅ WHATSAPP_VERIFY_TOKEN configurada
)

if "%GEMINI_API_KEY%"=="" (
    echo ❌ Falta variable: GEMINI_API_KEY
    exit /b 1
) else (
    echo ✅ GEMINI_API_KEY configurada
)

echo.
echo 🐳 Construyendo imagen Docker...
docker build -t korei-test . --no-cache
if errorlevel 1 (
    echo ❌ Error construyendo imagen Docker
    exit /b 1
)
echo ✅ Imagen Docker construida

echo.
echo 🚀 Probando contenedor...
docker run -d --name korei-test -p 8001:8000 ^
    -e SUPABASE_URL=%SUPABASE_URL% ^
    -e SUPABASE_SERVICE_KEY=%SUPABASE_SERVICE_KEY% ^
    -e WHATSAPP_ACCESS_TOKEN=%WHATSAPP_ACCESS_TOKEN% ^
    -e WHATSAPP_PHONE_NUMBER_ID=%WHATSAPP_PHONE_NUMBER_ID% ^
    -e WHATSAPP_VERIFY_TOKEN=%WHATSAPP_VERIFY_TOKEN% ^
    -e GEMINI_API_KEY=%GEMINI_API_KEY% ^
    -e ENVIRONMENT=production ^
    korei-test

if errorlevel 1 (
    echo ❌ Error ejecutando contenedor
    exit /b 1
)

echo ⏳ Esperando que el servicio arranque...
timeout /t 15 /nobreak >nul

echo.
echo 🏥 Probando health endpoint...
curl -f http://localhost:8001/health
if errorlevel 1 (
    echo ❌ Health check falló
    docker logs korei-test
    docker rm -f korei-test
    exit /b 1
)
echo ✅ Health check exitoso

echo.
echo 🔗 Probando webhook endpoint...
curl -s "http://localhost:8001/webhook/cloud?hub.mode=subscribe&hub.challenge=TEST123&hub.verify_token=%WHATSAPP_VERIFY_TOKEN%" | findstr "TEST123" >nul
if errorlevel 1 (
    echo ❌ Webhook verification falló
    docker logs korei-test
    docker rm -f korei-test
    exit /b 1
)
echo ✅ Webhook verification exitoso

echo.
echo 🧹 Limpiando...
docker rm -f korei-test
docker rmi korei-test

echo.
echo 🎉 TODAS LAS VALIDACIONES PASARON
echo ✅ El deploy debería funcionar correctamente
echo.
echo 📝 Para hacer deploy:
echo    git add .
echo    git commit -m "fix: Deploy configuration corrections"
echo    git push origin main