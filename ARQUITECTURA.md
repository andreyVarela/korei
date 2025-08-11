# 🏗️ ARQUITECTURA - Korei Assistant

## 📋 RESUMEN EJECUTIVO

**Korei Assistant** es un asistente de WhatsApp con IA que procesa mensajes de texto, audio e imágenes usando Google Gemini. Construido con FastAPI, Supabase y WAHA para crear un sistema robusto y escalable.

## 🎯 OBJETIVO DEL SISTEMA

- **Recibir mensajes** de WhatsApp via WAHA webhooks
- **Procesar con IA** usando Google Gemini (texto, audio, imágenes)
- **Almacenar datos** en Supabase (usuarios, conversaciones, entries)
- **Responder inteligentemente** basado en el contexto del usuario

---

## 🏛️ ARQUITECTURA DE ALTO NIVEL

```
WhatsApp User → WAHA → Webhook → FastAPI → [Gemini AI] → Supabase → Response
```

### **Flujo de Datos:**
1. **Usuario envía mensaje** en WhatsApp
2. **WAHA recibe** y envía webhook a nuestro servidor
3. **FastAPI procesa** el webhook en background
4. **Gemini AI analiza** el contenido (texto/audio/imagen)
5. **Supabase almacena** la información estructurada
6. **WhatsApp responde** al usuario con resultado procesado

---

## 📁 ESTRUCTURA DE CARPETAS DETALLADA

### **🔧 `/api/` - Capa de API**
```
api/
├── middleware.py          # Logging y manejo de errores
└── routes/               # Endpoints organizados por funcionalidad
    ├── health.py         # Health checks y monitoreo
    ├── stats.py          # Estadísticas y métricas
    └── webhook.py        # Recepción de webhooks WAHA
```

**📘 Propósito:** Define los puntos de entrada HTTP del sistema. Separa responsabilidades por tipo de endpoint.

**🏗️ Patrón:** Router Pattern - Cada archivo maneja un dominio específico.

### **⚙️ `/app/` - Configuración de la aplicación**
```
app/
├── config.py            # Configuración con Pydantic Settings
├── dependencies.py      # Dependency injection para FastAPI
├── lifespan.py         # Eventos de startup/shutdown
└── supabase_client.py  # Cliente base de Supabase
```

**📘 Propósito:** Configuración centralizada y bootstrapping de la aplicación.

**🏗️ Patrón:** Settings Pattern - Configuración externa via environment variables.

### **💾 `/core/` - Modelos y esquemas centrales**
```
core/
├── models.py           # Modelos de datos (Pydantic/SQLAlchemy)
├── schemas.py          # Esquemas de validación
└── supabase.py        # Service layer para base de datos
```

**📘 Propósito:** Define la estructura de datos y operaciones de base de datos.

**🏗️ Patrón:** Repository Pattern - Abstrae la lógica de acceso a datos.

### **🎯 `/handlers/` - Procesadores de lógica de negocio**
```
handlers/
├── command_handler.py  # Comandos específicos (/help, /stats)
├── media_handler.py    # Procesamiento de multimedia
└── message_handler.py  # Orquestador principal de mensajes
```

**📘 Propósito:** Contiene la lógica de negocio específica del dominio.

**🏗️ Patrón:** Handler Pattern - Cada tipo de mensaje tiene su manejador.

### **🔌 `/services/` - Integraciones externas**
```
services/
├── audio.py           # Procesamiento de audio
├── gemini.py         # Integración con Google Gemini AI
├── image.py          # Procesamiento de imágenes
├── scheduler.py      # Programación de tareas
└── whatsapp.py       # Integración con WAHA API
```

**📘 Propósito:** Abstrae las integraciones con servicios externos.

**🏗️ Patrón:** Service Layer Pattern - Encapsula lógica de integración.

### **🛠️ `/utils/` - Utilidades comunes**
```
utils/
├── formatters.py     # Formateo de mensajes y datos
├── helpers.py        # Funciones auxiliares
└── validators.py     # Validaciones personalizadas
```

**📘 Propósito:** Funciones reutilizables en todo el sistema.

**🏗️ Patrón:** Utility Pattern - Funciones puras sin estado.

### **🧪 `/tests/` - Suite de pruebas**
```
tests/
├── api/              # Tests de endpoints
├── services/         # Tests de servicios
├── conftest.py       # Configuración de pytest
└── test_handlers.py  # Tests de handlers
```

**📘 Propósito:** Garantiza calidad y comportamiento correcto.

**🏗️ Patrón:** Test Pyramid - Unitarias, integración y end-to-end.

---

## 🏗️ PATRONES DE ARQUITECTURA IMPLEMENTADOS

### **1. 🎯 Layered Architecture (Arquitectura por Capas)**
```
Presentation Layer    → /api/ (FastAPI routes)
Business Logic Layer → /handlers/ (Domain logic)
Service Layer        → /services/ (External integrations)  
Data Access Layer    → /core/ (Database operations)
```

### **2. 🔄 Dependency Injection**
- **FastAPI Dependencies** para autenticación y validación
- **Singleton Services** para conexiones (Supabase, Gemini)
- **Configuration Injection** via Pydantic Settings

### **3. 📨 Asynchronous Message Processing**
- **Background Tasks** para procesamiento no bloqueante
- **Async/Await** para I/O operations
- **Event-driven processing** via webhooks

### **4. 🛡️ Error Handling & Middleware**
- **Custom Middleware** para logging y errores
- **Structured Logging** con Loguru
- **Graceful Error Recovery** con fallbacks

---

## 🔧 TECNOLOGÍAS Y JUSTIFICACIÓN

### **🚀 FastAPI** - Framework Web
**¿Por qué?** 
- **Performance:** Uno de los frameworks Python más rápidos
- **Type Safety:** Validación automática con Pydantic
- **Async Native:** Ideal para I/O intensivo (webhooks, APIs)
- **Auto Documentation:** Swagger UI automático

### **🧠 Google Gemini** - Inteligencia Artificial  
**¿Por qué?**
- **Multimodal:** Texto, imagen, audio en un solo modelo
- **Context Awareness:** Entiende conversaciones largas
- **JSON Mode:** Respuestas estructuradas para programación
- **Costo-efectivo:** Más barato que GPT-4 para casos de uso similares

### **🗄️ Supabase** - Base de Datos y Backend
**¿Por qué?**
- **PostgreSQL:** Base de datos robusta y escalable
- **Real-time:** Subscripciones en tiempo real
- **Storage:** Manejo de archivos multimedia
- **Auth Ready:** Sistema de autenticación integrado

### **📱 WAHA** - WhatsApp API
**¿Por qué?**
- **Self-hosted:** Control completo sobre la infraestructura
- **Multi-session:** Múltiples números de WhatsApp
- **Media Support:** Audio, imagen, documento, video
- **Webhook Based:** Procesamiento asíncrono

---

## 📊 FLUJO DE DATOS DETALLADO

### **1. 📱 Recepción de Mensaje**
```json
// Webhook WAHA
{
  "event": "message",
  "session": "default", 
  "payload": {
    "id": "msg_12345",
    "from": "5557890123@c.us",
    "body": "Gasté $50 en supermercado",
    "type": "text",
    "timestamp": 1691234567
  }
}
```

### **2. 🔄 Procesamiento en Background**
1. **Extracción:** Obtener datos del payload WAHA
2. **Usuario:** Obtener o crear usuario en Supabase
3. **IA:** Procesar contenido con Gemini
4. **Almacenamiento:** Guardar resultado en base de datos
5. **Respuesta:** Enviar confirmación vía WhatsApp

### **3. 🧠 Procesamiento con IA**
```python
# Gemini procesa el texto y retorna JSON estructurado
{
  "type": "gasto",
  "description": "Compra en supermercado", 
  "amount": 50.00,
  "datetime": "2024-08-11T10:30:00",
  "category": "alimentación"
}
```

### **4. 💾 Almacenamiento**
```sql
-- Tabla entries en Supabase
INSERT INTO entries (
  user_id, type, description, amount, 
  datetime, category, created_at
) VALUES (...);
```

---

## 🎨 PRINCIPIOS DE CÓDIGO LIMPIO IMPLEMENTADOS

### **1. 📁 Single Responsibility Principle**
- Cada clase/función tiene **una sola responsabilidad**
- **Separación de concerns** por capas
- **Modular design** con imports específicos

### **2. 🔗 Dependency Inversion**
- **Abstracciones** en lugar de implementaciones concretas
- **Interface segregation** con protocolos/ABC
- **Dependency injection** via FastAPI

### **3. 📝 Clear Naming & Documentation**
- **Nombres descriptivos** en español para el dominio
- **Docstrings** explicando propósito y parámetros
- **Type hints** en todas las funciones

### **4. 🛡️ Error Handling**
- **Try-catch específico** para cada tipo de error
- **Logging estructurado** para debugging
- **Graceful degradation** cuando fallan servicios externos

### **5. 🧪 Testability**
- **Async testing** con pytest-asyncio
- **Mock services** para external APIs
- **Test fixtures** para datos de prueba

---

## 🚀 ESCALABILIDAD Y FUTURO

### **📈 Optimizaciones Actuales**
- **Async processing** para no bloquear webhooks
- **Connection pooling** en Supabase
- **Lazy loading** de servicios pesados
- **Background tasks** para procesamiento lento

### **🔮 Mejoras Futuras**
- **Message Queue** (Redis/RabbitMQ) para alta carga
- **Microservices** separar AI processing
- **Caching** para respuestas frecuentes
- **Load balancing** para múltiples instancias

---

## 🏁 ESTADO ACTUAL

### ✅ **COMPLETADO:**
- **FastAPI base** con health checks
- **Webhook WAHA** configurado y funcionando  
- **Estructura de carpetas** organizada
- **Logging middleware** implementado
- **Configuration management** con Pydantic
- **Supabase integration** preparada

### 🚧 **EN DESARROLLO:**
- **Gemini AI integration** completa
- **Message handlers** para diferentes tipos
- **Database models** finalizados
- **Response system** vía WhatsApp

### 📋 **TODO:**
- **Authentication/Authorization**
- **Rate limiting**
- **Monitoring & Alerting** 
- **Production deployment**

---

## 💡 PROMPT PARA APRENDIZAJE

Usa este prompt con ChatGPT para aprender más sobre el código:

"Soy principiante en Python y desarrollo de APIs. Tengo este proyecto de un asistente de WhatsApp con IA que usa FastAPI, Google Gemini, Supabase y WAHA. 

ARQUITECTURA: [Pega aquí la arquitectura completa]
CÓDIGO ACTUAL: [Pega archivos específicos]

Explícame paso a paso:
1. ¿Cómo funciona la arquitectura por capas?
2. ¿Qué ventajas tiene separar handlers/services/core?  
3. ¿Cómo funciona el procesamiento asíncrono?
4. ¿Qué patrones de diseño estoy usando?
5. ¿Cómo mejorar el código siguiendo principios SOLID?

Recomiéndame recursos específicos para aprender cada tecnología utilizada."