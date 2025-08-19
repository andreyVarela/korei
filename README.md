# 🤖 Korei Assistant

**Tu asistente personal inteligente en WhatsApp con IA**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Korei Assistant es un asistente de WhatsApp con inteligencia artificial que procesa mensajes de texto, audio e imágenes usando Google Gemini. Está construido con FastAPI, Supabase y WAHA para crear un sistema robusto y escalable.

### ✨ Características Principales

- 🧠 **IA Multimodal**: Procesa texto, audio e imágenes con Google Gemini
- 💰 **Gestión Financiera**: Tracking automático de gastos e ingresos
- 📅 **Organización Personal**: Tareas, eventos y recordatorios inteligentes
- 🔗 **Integraciones**: Todoist, Google Calendar, y más
- 🔒 **Seguridad**: Encriptación AES-256-GCM para datos sensibles
- 📱 **WhatsApp Nativo**: Soporte para WhatsApp Cloud API y WAHA

## 🚀 Instalación Rápida

### Prerequisitos

- Python 3.11+
- PostgreSQL (o Supabase)
- WhatsApp Business Account
- Google Gemini API Key

### 1. Clonar Repositorio

```bash
git clone https://github.com/tu-usuario/korei-assistant.git
cd korei-assistant
```

### 2. Configurar Entorno

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

```bash
# Copiar archivo de configuración
cp config/.env.example .env

# Editar variables de entorno
nano .env
```

**Variables requeridas:**
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id

# Gemini AI
GEMINI_API_KEY=your_gemini_key

# Encriptación
ENCRYPTION_MASTER_KEY=your_master_key
```

### 4. Base de Datos

```bash
# Ejecutar migraciones en Supabase SQL Editor
psql -f scripts/database_migrations.sql
```

### 5. Ejecutar

```bash
# Desarrollo
python main.py

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker

```bash
# Build imagen
docker build -t korei-assistant .

# Ejecutar con Docker Compose
docker-compose up -d
```

## 📁 Estructura del Proyecto

```
korei-assistant/
├── 🔧 api/                  # Endpoints HTTP
├── ⚙️ app/                  # Configuración de la aplicación
├── 💾 core/                 # Modelos y acceso a datos
├── 🎯 handlers/             # Lógica de negocio
├── 🔌 services/             # Integraciones externas
├── 🧪 tests/               # Suite de pruebas
├── 📁 docs/                # Documentación
├── 🛠️ scripts/             # Scripts utilitarios
├── ⚙️ config/              # Archivos de configuración
└── 📊 logs/               # Archivos de log
```

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
coverage run -m pytest
coverage report
coverage html  # Reporte HTML en htmlcov/

# Tests específicos
pytest tests/unit/          # Tests unitarios
pytest tests/integration/   # Tests de integración
pytest tests/e2e/          # Tests end-to-end
```

## 📖 Documentación

- **[Arquitectura Técnica](docs/TECH_LEAD_ANALYSIS.md)** - Análisis completo de arquitectura
- **[Configuración de Integraciones](docs/INTEGRATION_SETUP.md)** - Setup de APIs externas
- **[Google OAuth Setup](docs/GOOGLE_OAUTH_SETUP.md)** - Configuración OAuth
- **[Arquitectura de Recordatorios](docs/REMINDER_ARCHITECTURE.md)** - Sistema de recordatorios
- **[Reporte de Limpieza](docs/CODE_CLEANUP_REPORT.md)** - Limpieza de código

## 🔧 Comandos de Desarrollo

```bash
# Linting y formateo
black .
flake8 .
isort .

# Análisis de seguridad
bandit -r .

# Actualizar dependencias
pip-tools compile requirements.in
```

## 🌟 Uso

### Comandos Básicos

- `/help` - Ver ayuda completa
- `/tareas` - Ver tareas de hoy
- `/gastos` - Ver gastos del día
- `/stats` - Estadísticas del mes

### Uso Natural

- "Gasté $50 en supermercado"
- "Reunión con cliente mañana 3pm"
- "Recordarme llamar al doctor"
- Envía fotos de recibos para procesamiento automático

### Integraciones

- `/conectar todoist [token]` - Conectar Todoist
- `/conectar google-calendar` - Conectar Google Calendar
- `/proyectos` - Ver proyectos de Todoist

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 License

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🆘 Soporte

- 📧 Email: support@korei-assistant.com
- 💬 Discord: [Korei Community](https://discord.gg/korei)
- 📚 Wiki: [GitHub Wiki](https://github.com/tu-usuario/korei-assistant/wiki)

## 🏆 Reconocimientos

- [Google Gemini](https://ai.google.dev/) - IA Multimodal
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Supabase](https://supabase.com/) - Backend como servicio
- [WAHA](https://waha.devlike.pro/) - WhatsApp HTTP API

---

⭐ **¡Danos una estrella si te gusta el proyecto!**# Deployment Test
