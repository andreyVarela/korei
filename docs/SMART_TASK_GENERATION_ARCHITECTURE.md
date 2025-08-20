# 🎯 Arquitectura: Generación Automática de Tareas y Hábitos Inteligentes

## 📋 Visión General

Sistema para crear automáticamente listas de tareas recurrentes, planes personalizados y hábitos basados en el contexto del usuario, utilizando IA para generar horarios inteligentes y rutinas optimizadas.

## 🎯 Casos de Uso

### 1. **Generación de Hábitos**
```
Usuario: "/plan ejercicio"
Sistema: Crea 30 tareas para un plan de ejercicio de 4 semanas
- Análisis: nivel fitness, horarios disponibles, preferencias
- Resultado: Rutina progresiva personalizada
```

### 2. **Planes de Lectura**
```
Usuario: "/leer Clean Code"
Sistema: Divide el libro en 20 sesiones de lectura
- Análisis: páginas del libro, velocidad de lectura estimada
- Resultado: Cronograma de lectura con objetivos diarios
```

### 3. **Rutinas de Productividad**
```
Usuario: "/productividad trabajo"
Sistema: Crea rutina diaria de trabajo optimizada
- Análisis: horarios laborales, tipo de trabajo, pausas
- Resultado: Bloques de tiempo con tareas específicas
```

### 4. **Hábitos de Bienestar**
```
Usuario: "/salud mejorar"
Sistema: Plan integral de bienestar
- Análisis: estilo de vida actual, metas de salud
- Resultado: Ejercicio + alimentación + sueño + hidratación
```

## 🏗️ Arquitectura del Sistema

### Componente 1: **Smart Plan Generator**
```
services/smart_plans/
├── plan_generator.py          # Generador principal
├── habit_templates.py         # Templates predefinidos
├── schedule_optimizer.py      # Optimización de horarios
└── context_analyzer.py        # Análisis de contexto de usuario
```

### Componente 2: **Plan Execution Engine**
```
services/plan_execution/
├── task_scheduler.py          # Programación de tareas
├── progress_tracker.py        # Seguimiento de progreso
├── adaptation_engine.py       # Adaptación basada en comportamiento
└── reminder_system.py         # Sistema de recordatorios
```

### Componente 3: **Command Handlers**
```
handlers/plan_commands/
├── plan_command_handler.py    # Comandos principales (/plan, /habito)
├── plan_types.py             # Definición de tipos de planes
└── plan_validators.py        # Validación de parámetros
```

## 🎯 Comandos Propuestos

### Comandos Principales

```bash
# Generación de planes generales
/plan <tipo> [parámetros]
/habito <categoría> [duración]
/rutina <área> [frecuencia]

# Planes específicos
/leer <libro> [tiempo_disponible]
/ejercicio [nivel] [objetivos]
/productividad [área_enfoque]
/aprender <skill> [tiempo_semanal]

# Gestión de planes
/planes                        # Ver planes activos
/plan-progreso <id>           # Ver progreso específico
/plan-modificar <id>          # Modificar plan existente
/plan-pausar <id>             # Pausar temporalmente
```

### Ejemplos de Uso

```bash
# Ejemplo 1: Plan de lectura
Usuario: "/leer The Pragmatic Programmer 30min diarios"
Respuesta: 
📚 Plan de Lectura Creado
• Libro: The Pragmatic Programmer (352 páginas)
• Duración: 24 días (30 min/día)
• Horario: 8:00 PM todos los días
• 24 tareas creadas en Todoist

# Ejemplo 2: Hábito de ejercicio
Usuario: "/ejercicio principiante 3veces"
Respuesta:
💪 Plan de Ejercicio - Principiante
• Duración: 6 semanas progresivas
• Frecuencia: 3x por semana (Lu-Mi-Vi)
• Horario: 7:00 AM (basado en tu rutina)
• 18 sesiones programadas

# Ejemplo 3: Productividad
Usuario: "/productividad trabajo remoto"
Respuesta:
🎯 Rutina de Productividad
• Bloques de enfoque: 2h cada mañana
• Revisión diaria: 15 min al final del día
• Planificación semanal: Domingos 6 PM
• 35 tareas recurrentes creadas
```

## 🧠 Sistema de IA Inteligente

### Análisis de Contexto
```python
class UserContextAnalyzer:
    def analyze_user_context(self, user_id: str) -> dict:
        """Analiza contexto completo del usuario"""
        return {
            'schedule_patterns': self._analyze_schedule(user_id),
            'energy_levels': self._analyze_energy_patterns(user_id),
            'completion_rates': self._analyze_task_completion(user_id),
            'preferences': self._extract_preferences(user_id),
            'availability': self._calculate_availability(user_id)
        }
```

### Generación con Gemini
```python
async def generate_smart_plan(self, plan_type: str, user_context: dict, parameters: dict):
    """Genera plan usando Gemini con contexto rico"""
    
    prompt = f"""
    SISTEMA: Eres un experto en productividad y hábitos.
    
    CONTEXTO DEL USUARIO:
    - Horarios típicos: {user_context['schedule_patterns']}
    - Nivel de energía: {user_context['energy_levels']}
    - Tasa de completación: {user_context['completion_rates']}%
    - Preferencias: {user_context['preferences']}
    
    SOLICITUD: Crear plan de {plan_type}
    PARÁMETROS: {parameters}
    
    FORMATO DE RESPUESTA:
    {{
        "plan_name": "Nombre descriptivo",
        "duration_weeks": 4,
        "tasks": [
            {{
                "title": "Título de la tarea",
                "description": "Descripción detallada",
                "day_of_week": "lunes", 
                "time": "07:00",
                "duration_minutes": 30,
                "week": 1,
                "priority": "alta",
                "category": "ejercicio"
            }}
        ],
        "success_tips": ["tip1", "tip2"],
        "adaptation_rules": ["regla1", "regla2"]
    }}
    """
```

## 📊 Base de Datos

### Nuevas Tablas
```sql
-- Planes generados
CREATE TABLE smart_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    total_tasks INTEGER,
    completed_tasks INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, cancelled
    start_date TIMESTAMPTZ DEFAULT NOW(),
    target_end_date TIMESTAMPTZ,
    actual_end_date TIMESTAMPTZ,
    context_snapshot JSONB, -- Contexto del usuario cuando se creó
    adaptation_rules JSONB, -- Reglas para adaptar el plan
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seguimiento de progreso
CREATE TABLE plan_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES smart_plans(id),
    date DATE NOT NULL,
    tasks_completed INTEGER DEFAULT 0,
    tasks_total INTEGER NOT NULL,
    completion_rate DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plantillas de planes
CREATE TABLE plan_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    template_data JSONB NOT NULL, -- Estructura del plan
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔄 Flujo de Ejecución

### 1. **Comando Recibido**
```python
# Usuario: "/plan ejercicio principiante"
async def handle_plan_command(self, command: str, user: dict):
    # Parsear comando y parámetros
    plan_type, params = self.parse_plan_command(command)
    
    # Analizar contexto del usuario
    context = await self.context_analyzer.analyze_user_context(user['id'])
    
    # Generar plan con IA
    plan = await self.plan_generator.generate_plan(plan_type, context, params)
    
    # Crear tareas en Todoist y DB
    await self.create_plan_tasks(plan, user)
    
    # Responder al usuario
    return self.format_plan_response(plan)
```

### 2. **Generación de Tareas**
```python
async def create_plan_tasks(self, plan: dict, user: dict):
    """Crea todas las tareas del plan"""
    
    for task in plan['tasks']:
        # Calcular fecha específica basada en semana y día
        task_date = self.calculate_task_date(
            plan['start_date'], 
            task['week'], 
            task['day_of_week']
        )
        
        # Crear tarea en formato Korei
        task_data = {
            'type': 'tarea',
            'description': task['title'],
            'datetime': f"{task_date}T{task['time']}:00",
            'priority': task['priority'],
            'recurrence': 'none',  # Individual para cada instancia
            'plan_id': plan['id'],
            'category': task['category']
        }
        
        # Crear en BD y Todoist
        await self.create_entry_with_external_sync(task_data, user)
```

### 3. **Seguimiento y Adaptación**
```python
async def track_plan_progress(self, plan_id: str):
    """Sigue el progreso y adapta si es necesario"""
    
    progress = await self.get_plan_progress(plan_id)
    
    if progress['completion_rate'] < 0.6:  # Menos del 60%
        # Sugerir adaptaciones
        suggestions = await self.generate_adaptations(plan_id, progress)
        await self.notify_user_adaptations(suggestions)
```

## 🎨 Templates Predefinidos

### Categorías de Templates
```python
PLAN_TEMPLATES = {
    'ejercicio': {
        'principiante': ExerciseBeginner(),
        'intermedio': ExerciseIntermediate(),
        'avanzado': ExerciseAdvanced(),
        'rehabilitacion': ExerciseRehab()
    },
    'lectura': {
        'tecnico': TechnicalBookPlan(),
        'ficcion': FictionBookPlan(),
        'desarrollo_personal': SelfHelpPlan(),
        'educativo': EducationalPlan()
    },
    'productividad': {
        'trabajo_remoto': RemoteWorkPlan(),
        'estudiante': StudentPlan(),
        'emprendedor': EntrepreneurPlan(),
        'freelancer': FreelancerPlan()
    },
    'bienestar': {
        'salud_mental': MentalHealthPlan(),
        'nutricion': NutritionPlan(),
        'sueño': SleepHygienePlan(),
        'mindfulness': MindfulnessPlan()
    }
}
```

## 🚀 Implementación por Fases

### **Fase 1: Core System (Semana 1)**
- [ ] Estructura básica de comandos `/plan`
- [ ] Generador simple con templates
- [ ] Integración con Todoist
- [ ] 3 tipos básicos: ejercicio, lectura, productividad

### **Fase 2: AI Integration (Semana 2)**
- [ ] Análisis de contexto de usuario
- [ ] Generación con Gemini
- [ ] Optimización de horarios
- [ ] Sistema de progreso

### **Fase 3: Advanced Features (Semana 3)**
- [ ] Adaptación automática
- [ ] Templates avanzados
- [ ] Métricas de éxito
- [ ] Recomendaciones personalizadas

### **Fase 4: Enhancement (Semana 4)**
- [ ] Análisis de patrones
- [ ] Gamificación
- [ ] Compartir planes exitosos
- [ ] Dashboard de progreso

## 💡 Beneficios Esperados

### Para el Usuario:
- **Automatización completa** de planificación de hábitos
- **Personalización inteligente** basada en comportamiento real
- **Seguimiento automático** de progreso sin esfuerzo manual
- **Adaptación dinámica** cuando algo no funciona

### Para el Sistema:
- **Retención aumentada** por valor agregado significativo
- **Datos ricos** de comportamiento de usuarios
- **Diferenciación clara** de otros asistentes
- **Casos de uso expandidos** más allá de tareas simples

## 🎯 Métricas de Éxito

- **Tasa de adopción**: % usuarios que crean al menos 1 plan
- **Completion rate**: % tareas completadas vs generadas
- **Retention**: Usuarios activos después de crear planes
- **Adaptation success**: % planes que mejoran tras adaptación
- **User satisfaction**: Rating promedio de planes generados

---

Esta arquitectura convierte a Korei en un **verdadero coach personal inteligente** que no solo responde a solicitudes, sino que **proactivamente ayuda a construir mejores hábitos** de manera sistemática y personalizada.