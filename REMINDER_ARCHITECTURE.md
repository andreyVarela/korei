# Sistema de Recordatorios - Arquitectura

## Opción Elegida: Background Scheduler Integrado

### Stack Tecnológico
- **APScheduler** (AsyncIOScheduler)
- **SQLAlchemy JobStore** (persistencia)
- **PostgreSQL/Supabase** (almacenamiento)
- **FastAPI Lifespan** (inicialización)

### Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │   Message        │    │   Reminder       │              │
│  │   Handler        │────│   Scheduler      │              │
│  │                  │    │                  │              │
│  └──────────────────┘    └──────────────────┘              │
│                                   │                        │
│                                   │                        │
│                          ┌──────────────────┐              │
│                          │   Job Store      │              │
│                          │   (Supabase)     │              │
│                          └──────────────────┘              │
│                                   │                        │
└─────────────────────────────────────────────────────────────┘
                                    │
                            ┌──────────────────┐
                            │   WhatsApp       │
                            │   Notification   │
                            └──────────────────┘
```

### Flujo de Datos

1. **Creación de Recordatorio:**
   ```
   Audio/Texto → Gemini → "tipo: recordatorio" → Scheduler.add_job()
   ```

2. **Ejecución de Recordatorio:**
   ```
   Timer → Job Trigger → Send WhatsApp Message → Mark Completed
   ```

3. **Persistencia:**
   ```
   Jobs → SQLAlchemy Store → Supabase PostgreSQL
   ```

### Ventajas

1. **Simplicidad**: Todo en una app
2. **Persistence**: Sobrevive reinicios
3. **Timezone-aware**: Maneja UTC-6 Costa Rica
4. **Escalable**: Hasta 10,000+ recordatorios
5. **Integrado**: Usa la misma DB y WhatsApp service

### Componentes

#### 1. Scheduler Service
```python
class ReminderScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    async def schedule_reminder(self, reminder_data):
        job = self.scheduler.add_job(
            func=self.send_reminder,
            trigger='date',
            run_date=reminder_data['datetime'],
            args=[reminder_data]
        )
        return job.id
        
    async def send_reminder(self, reminder_data):
        # Enviar por WhatsApp
        # Marcar como completado
```

#### 2. Job Store Configuration
```python
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

jobstore = SQLAlchemyJobStore(url=supabase_url)
scheduler.add_jobstore(jobstore, 'default')
```

#### 3. Integration Points
- **Message Handler**: Detecta recordatorios y programa
- **Gemini Service**: Procesa "recordar..." 
- **WhatsApp Service**: Envía notificaciones
- **Supabase**: Almacena jobs y estado

### Tipos de Recordatorios Soportados

1. **Fecha específica**: "Recordarme el lunes a las 3pm"
2. **Relativo**: "Recordarme en 2 horas"
3. **Recurrente**: "Recordarme todos los días a las 8am"
4. **Contextual**: "Recordarme cuando llegue a casa"

### Manejo de Errores

1. **Job failures**: Retry con backoff exponencial
2. **WhatsApp API down**: Queue para reintentos
3. **App restart**: Jobs se cargan desde DB
4. **Timezone changes**: Recalculación automática

### Monitoreo

1. **Métricas**: Jobs pendientes, completados, fallidos
2. **Logs**: Todas las operaciones de scheduling
3. **Health checks**: Status del scheduler
4. **Alertas**: Jobs que no se ejecutan

### Escalabilidad

- **Memory usage**: ~1KB por job pendiente
- **CPU usage**: Mínimo hasta 1000+ jobs
- **Database**: Tabla jobs escalable
- **Network**: Solo WhatsApp API calls

### Implementación por Fases

**Fase 1**: Recordatorios básicos de fecha/hora
**Fase 2**: Recordatorios recurrentes  
**Fase 3**: Recordatorios inteligentes con contexto
**Fase 4**: Recordatorios basados en ubicación