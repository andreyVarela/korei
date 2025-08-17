# 🔗 Guía de Configuración de Integraciones

## 📋 **Resumen**

Korei ahora soporta integraciones con aplicaciones externas para sincronizar automáticamente tareas, eventos y datos entre WhatsApp y tus apps favoritas.

### **Integraciones Disponibles:**
- ✅ **Google Calendar** - Sincroniza eventos automáticamente
- ✅ **Todoist** - Sincroniza tareas y proyectos
- 🔄 **Microsoft To-Do** - Próximamente
- 🔄 **Notion** - Próximamente

---

## 🔧 **Configuración Inicial**

### 1. **Instalar Dependencias**
```bash
pip install -r requirements_integrations.txt
```

### 2. **Ejecutar Migraciones de Base de Datos**
```sql
-- En Supabase SQL Editor, ejecutar:
-- C:\Users\avsol\OneDrive\Documents\App\korei\database_migrations.sql
```

### 3. **Variables de Entorno**
Agregar a tu archivo `.env`:

```env
# Google Calendar (OAuth2)
GOOGLE_CLIENT_ID=tu_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_google_client_secret
BASE_URL=https://tu-dominio.com/

# Opcional: Para Microsoft Graph
# MICROSOFT_CLIENT_ID=tu_microsoft_client_id
# MICROSOFT_CLIENT_SECRET=tu_microsoft_client_secret
```

---

## 📅 **Configurar Google Calendar**

### **Paso 1: Crear Proyecto en Google Cloud**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Calendar API**

### **Paso 2: Configurar OAuth2**
1. Ve a **APIs & Services > Credentials**
2. Crea **OAuth 2.0 Client ID**
3. Configura **Authorized redirect URIs**:
   ```
   https://tu-dominio.com/integrations/oauth/google_calendar/callback
   ```

### **Paso 3: Configurar Scopes**
Los scopes requeridos:
- `https://www.googleapis.com/auth/calendar`

---

## ✅ **Configurar Todoist**

### **Paso 1: Obtener API Token**
1. Ve a [Todoist Settings](https://todoist.com/prefs/integrations)
2. Copia tu **API Token**
3. Los usuarios conectarán con: `/conectar todoist [token]`

### **Paso 2: Configurar Webhooks (Opcional)**
Para sincronización en tiempo real:
1. Crea webhook en Todoist
2. URL: `https://tu-dominio.com/webhooks/todoist`

---

## 🚀 **Activar Integraciones en API**

### **Registrar Rutas**
En `main.py`:

```python
from api.routes import integrations

app.include_router(integrations.router, prefix="/api")
```

### **Comandos de WhatsApp Disponibles**

| Comando | Descripción |
|---------|-------------|
| `/conectar` | Lista integraciones disponibles |
| `/conectar google-calendar` | Conecta Google Calendar |
| `/conectar todoist [token]` | Conecta Todoist |
| `/integraciones` | Ver integraciones conectadas |
| `/sincronizar` | Sincronizar datos manualmente |

---

## 🔄 **Sincronización Automática**

### **Cómo Funciona:**
1. **Usuario crea tarea/evento en WhatsApp** → Se crea automáticamente en app externa
2. **Usuario crea en app externa** → Se importa a Korei en próxima sincronización
3. **Sincronización bidireccional** → Mantiene todo sincronizado

### **Triggers de Sincronización:**
- Al crear nuevas tareas/eventos desde WhatsApp
- Comando manual `/sincronizar`
- Webhook de servicio externo (si configurado)

---

## 💡 **Ejemplos de Uso**

### **Google Calendar:**
```
Usuario: "Reunión con cliente mañana a las 3pm"
Korei: ✅ Tarea creada y agregada a tu Google Calendar
```

### **Todoist:**
```
Usuario: "Comprar leche prioridad alta"
Korei: ✅ Tarea creada en Todoist con prioridad alta
```

### **Importación:**
```
Usuario: /sincronizar
Korei: 📥 Importados: 5 tareas de Todoist, 2 eventos de Google Calendar
```

---

## 🔒 **Seguridad**

### **Encriptación de Credenciales:**
- Todas las credenciales se almacenan encriptadas
- Tokens de OAuth se refrescan automáticamente
- RLS (Row Level Security) en Supabase

### **Permisos Mínimos:**
- Google Calendar: Solo lectura/escritura de eventos
- Todoist: Solo acceso a tareas del usuario
- Sin acceso a datos sensibles

---

## 🐛 **Resolución de Problemas**

### **Error de Autenticación Google:**
```bash
# Verificar credenciales
curl -X GET "https://tu-dominio.com/api/integrations/test/{user_id}/google_calendar"
```

### **Token Todoist Inválido:**
```
❌ Error: Token de API inválido
💡 Solución: Obtén nuevo token en https://todoist.com/prefs/integrations
```

### **Sincronización Fallida:**
- Verificar conexión a internet
- Comprobar que APIs externas estén disponibles
- Revisar logs: `tail -f logs/korei.log`

---

## 📊 **Monitoreo**

### **Logs de Integración:**
```python
# En production, configura logging
import logging

logging.getLogger("integrations").setLevel(logging.INFO)
```

### **Métricas Recomendadas:**
- Número de integraciones activas
- Éxito/fallo de sincronizaciones
- Tiempo de respuesta de APIs externas

---

## 🔮 **Futuras Integraciones**

### **En Desarrollo:**
- 📱 **Microsoft To-Do** - Para usuarios de Office 365
- 📝 **Notion** - Para bases de datos avanzadas
- 📧 **Gmail** - Para crear tareas desde emails
- 💬 **Slack** - Para notificaciones y comandos

### **Solicitudes de Usuarios:**
¿Qué integración te gustaría ver? Comenta en GitHub Issues.

---

## 📞 **Soporte**

### **Documentación de APIs:**
- [Google Calendar API](https://developers.google.com/calendar)
- [Todoist API](https://developer.todoist.com/guides/)

### **Contacto:**
- GitHub Issues para bugs
- Documentación en `/docs/integrations`