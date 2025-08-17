# 📅 Configuración de Google Calendar OAuth

## 🎯 **Resumen**
Esta guía te ayudará a configurar la autenticación OAuth2 con Google Calendar para que los usuarios puedan conectar sus calendarios desde WhatsApp.

---

## 📋 **Paso 1: Crear Proyecto en Google Cloud Console**

### 1.1 Acceder a Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Crea un nuevo proyecto o selecciona uno existente

### 1.2 Crear Nuevo Proyecto
```
Nombre: Korei Calendar Integration
ID del proyecto: korei-calendar-integration (o el que prefieras)
```

---

## 🔧 **Paso 2: Habilitar Google Calendar API**

### 2.1 Navegar a APIs y Servicios
1. En el menú lateral: **APIs y servicios > Biblioteca**
2. Busca: `Google Calendar API`
3. Haz clic en **Google Calendar API**
4. Clic en **HABILITAR**

---

## 🔑 **Paso 3: Configurar OAuth2**

### 3.1 Pantalla de Consentimiento OAuth
1. Ve a **APIs y servicios > Pantalla de consentimiento de OAuth**
2. Selecciona **Externo** (para usuarios de cualquier cuenta Google)
3. Completa la información:

```
Nombre de la aplicación: Korei Assistant
Correo de asistencia técnica: tu-email@dominio.com
Logotipo (opcional): Sube una imagen si tienes
Dominios autorizados: tu-dominio.com
```

### 3.2 Scopes (Alcances)
Agrega los siguientes scopes:
```
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/calendar.events
```

### 3.3 Usuarios de Prueba
Agrega emails que puedan probar la integración:
```
tu-email@gmail.com
email-de-prueba@gmail.com
```

---

## 🔐 **Paso 4: Crear Credenciales OAuth**

### 4.1 Crear OAuth 2.0 Client ID
1. Ve a **APIs y servicios > Credenciales**
2. Clic en **+ CREAR CREDENCIALES**
3. Selecciona **ID de cliente de OAuth 2.0**

### 4.2 Configurar Aplicación Web
```
Tipo de aplicación: Aplicación web
Nombre: Korei Calendar Integration

URIs de origen autorizados:
https://tu-dominio.com
http://localhost:8000 (para desarrollo)

URIs de redirección autorizados:
https://tu-dominio.com/api/integrations/oauth/google_calendar/callback
http://localhost:8000/api/integrations/oauth/google_calendar/callback
```

### 4.3 Obtener Credenciales
Después de crear, obtendrás:
```
Client ID: 123456789-abcdef.apps.googleusercontent.com
Client Secret: GOCSPX-abcdef123456_example
```

---

## ⚙️ **Paso 5: Configurar Variables de Entorno**

### 5.1 Actualizar .env
Agrega a tu archivo `.env`:

```bash
# Google Calendar OAuth
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456_example
BASE_URL=https://tu-dominio.com/
```

### 5.2 Para Desarrollo Local
```bash
# Para pruebas locales
BASE_URL=http://localhost:8000/
```

---

## 🧪 **Paso 6: Probar la Integración**

### 6.1 Ejecutar el Servidor
```bash
cd korei
python main.py
```

### 6.2 Probar OAuth Flow
1. Ve a: `http://localhost:8000/api/integrations/oauth/google_calendar/start?user_id=test_user_123`
2. Deberías ser redirigido a Google
3. Autoriza los permisos
4. Deberías ser redirigido de vuelta con éxito

### 6.3 Endpoints de Prueba
```bash
# Listar integraciones disponibles
GET http://localhost:8000/api/integrations/available

# Iniciar OAuth
GET http://localhost:8000/api/integrations/oauth/google_calendar/start?user_id=123

# Ver integraciones del usuario
GET http://localhost:8000/api/integrations/user/123

# Probar conexión
POST http://localhost:8000/api/integrations/test/123/google_calendar
```

---

## 📱 **Paso 7: Usar desde WhatsApp**

### 7.1 Comandos para Usuarios
```
/conectar google-calendar
→ Recibe link de OAuth

/integraciones  
→ Ve integraciones conectadas

"Reunión con cliente mañana 3pm"
→ Se crea automáticamente en Google Calendar
```

---

## 🔒 **Seguridad y Producción**

### 8.1 Configuración de Producción
- Usa HTTPS obligatorio
- Configura dominios específicos (no wildcards)
- Implementa rate limiting
- Monitorea logs de OAuth

### 8.2 Rotación de Credenciales
```bash
# Configurar auto-rotación cada 90 días
# Usar Google Cloud Secret Manager
# Implementar logs de auditoría
```

---

## 🐛 **Resolución de Problemas**

### Error: "redirect_uri_mismatch"
```
Solución: Verificar que la URI de redirección en Google Cloud 
coincida exactamente con la configurada en BASE_URL
```

### Error: "invalid_client"
```
Solución: Verificar GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET
```

### Error: "access_denied"
```
Solución: Usuario canceló autorización o app no aprobada
```

### Tokens Expirados
```
Solución: Los refresh tokens se manejan automáticamente
```

---

## 📊 **Monitoreo**

### 9.1 Métricas Importantes
- Flujos OAuth completados vs iniciados
- Tokens refrescados exitosamente
- Eventos creados en Google Calendar
- Errores de API

### 9.2 Logs de Auditoría
Los siguientes eventos se registran:
- Inicio de flujo OAuth
- Autorización completada/fallida
- Acceso a credenciales
- Operaciones en Calendar API

---

## 🚀 **Próximos Pasos**

Una vez configurado Google Calendar:

1. **Probar con usuarios reales**
2. **Configurar Microsoft To-Do** (opcional)
3. **Implementar webhooks** para sincronización en tiempo real
4. **Agregar más funciones** (invitados, recordatorios, etc.)

---

## 📞 **Soporte**

### Documentación Oficial
- [Google Calendar API](https://developers.google.com/calendar/api)
- [OAuth 2.0 para Aplicaciones Web](https://developers.google.com/identity/protocols/oauth2/web-server)

### Contacto
- GitHub Issues para problemas técnicos
- Documentación en `/docs/integrations`