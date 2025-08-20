# 🚀 Estrategia de Implementación: Generación Automática de Tareas

## 🎯 Estrategia de Desarrollo

### **Enfoque MVP (Minimum Viable Product)**

**Objetivo**: Implementar funcionalidad básica pero impactante en **1 semana** que demuestre el valor del sistema.

### **Priorización Smart**
1. **Alto Impacto + Baja Complejidad** → Implementar PRIMERO
2. **Alto Impacto + Alta Complejidad** → Versión simplificada
3. **Bajo Impacto** → Fase futura

## 📋 Plan de Implementación - Fase 1 (7 días)

### **Día 1-2: Comandos Base**
```python
# Estructura de comandos simple pero extensible
/plan ejercicio [nivel] [frecuencia]
/plan lectura <libro> [tiempo_diario]  
/plan productividad [tipo_trabajo]

# Ejemplos funcionales:
"/plan ejercicio principiante"          → 12 tareas (4 semanas, 3x/semana)
"/plan lectura atomic habits 20min"     → 15 sesiones de lectura
"/plan productividad trabajo_remoto"    → Rutina diaria de productividad
```

### **Día 3-4: Templates Inteligentes**
```python
# 3 templates esenciales completamente desarrollados
class ExercisePlan:
    def generate_beginner_plan(self, user_context):
        """4 semanas progresivas, 3x por semana"""
        
class ReadingPlan:
    def generate_book_plan(self, book_info, daily_time):
        """División inteligente por capítulos/páginas"""
        
class ProductivityPlan:
    def generate_work_routine(self, work_type):
        """Bloques de tiempo optimizados"""
```

### **Día 5-6: Integración y Optimización**
- Integración con sistema de tareas existente
- Creación automática en Todoist con proyectos correctos
- Optimización de horarios basada en contexto de usuario
- Sistema básico de progreso

### **Día 7: Testing y Refinamiento**
- Tests end-to-end con usuarios reales
- Ajustes basados en feedback
- Documentación de usuario

## 🔧 Implementación Técnica Detallada

### **1. Command Handler Enhancement**

```python
# handlers/command_handler.py - Nuevos métodos

async def handle_plan_command(self, command: str, message: str, user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maneja comandos /plan con parseo inteligente
    
    Ejemplos:
    "/plan ejercicio principiante" → ExercisePlan(level='principiante')
    "/plan lectura atomic habits 30min" → ReadingPlan(book='atomic habits', time='30min')
    "/plan productividad remoto" → ProductivityPlan(type='remoto')
    """
    try:
        parts = message.split()
        plan_type = parts[1] if len(parts) > 1 else None
        
        if plan_type == 'ejercicio':
            return await self._handle_exercise_plan(parts[2:], user)
        elif plan_type == 'lectura':
            return await self._handle_reading_plan(parts[2:], user)
        elif plan_type == 'productividad':
            return await self._handle_productivity_plan(parts[2:], user)
        else:
            return await self._show_plan_help()
            
    except Exception as e:
        logger.error(f"Error in plan command: {e}")
        return {"error": "No pude crear el plan. Usa /help para ver ejemplos."}

async def _handle_exercise_plan(self, params: List[str], user: Dict[str, Any]) -> Dict[str, Any]:
    """Crea plan de ejercicio personalizado"""
    level = params[0] if params else 'principiante'
    frequency = params[1] if len(params) > 1 else '3x'
    
    # Analizar contexto del usuario
    user_context = await self._analyze_user_context(user)
    
    # Generar plan
    plan_generator = ExercisePlanGenerator()
    plan = await plan_generator.create_plan(level, frequency, user_context)
    
    # Crear todas las tareas
    tasks_created = await self._create_plan_tasks(plan, user)
    
    return {
        "type": "plan_created",
        "message": f"🏋️ Plan de ejercicio creado: {plan['name']}\n\n"
                  f"📅 Duración: {plan['duration_weeks']} semanas\n"
                  f"📋 {len(tasks_created)} tareas programadas\n"
                  f"⏰ Horario: {plan['schedule']}\n\n"
                  f"🎯 Usa /planes para ver tu progreso",
        "plan_id": plan['id'],
        "tasks_count": len(tasks_created)
    }
```

### **2. Plan Generators (Foco en Simplicidad)**

```python
# services/plan_generators.py

class ExercisePlanGenerator:
    """Generador de planes de ejercicio con templates probados"""
    
    BEGINNER_TEMPLATE = {
        'duration_weeks': 4,
        'frequency': 3,  # 3x por semana
        'progression': {
            'week_1': {'intensity': 'low', 'duration': 20},
            'week_2': {'intensity': 'low', 'duration': 25}, 
            'week_3': {'intensity': 'medium', 'duration': 30},
            'week_4': {'intensity': 'medium', 'duration': 35}
        }
    }
    
    async def create_plan(self, level: str, frequency: str, user_context: dict) -> dict:
        """Crea plan de ejercicio específico"""
        
        template = self.BEGINNER_TEMPLATE  # MVP: solo principiante
        
        # Optimizar horarios basado en contexto
        optimal_time = self._find_optimal_exercise_time(user_context)
        optimal_days = self._find_optimal_days(frequency, user_context)
        
        plan = {
            'id': str(uuid.uuid4()),
            'name': f'Plan de Ejercicio - {level.title()}',
            'type': 'ejercicio', 
            'duration_weeks': template['duration_weeks'],
            'schedule': f"{optimal_days} a las {optimal_time}",
            'tasks': []
        }
        
        # Generar tareas específicas
        start_date = datetime.now()
        for week in range(1, template['duration_weeks'] + 1):
            week_config = template['progression'][f'week_{week}']
            
            for day_offset in optimal_days:  # [0, 2, 4] = Lu, Mi, Vi
                task_date = start_date + timedelta(weeks=week-1, days=day_offset)
                
                task = {
                    'title': f'Ejercicio - Semana {week}',
                    'description': self._generate_workout_description(week_config),
                    'datetime': f"{task_date.strftime('%Y-%m-%d')}T{optimal_time}:00",
                    'priority': 'media',
                    'category': 'Ejercicio',
                    'week': week,
                    'duration_minutes': week_config['duration']
                }
                plan['tasks'].append(task)
        
        return plan
    
    def _find_optimal_exercise_time(self, user_context: dict) -> str:
        """Encuentra la mejor hora para ejercicio basado en patrones de usuario"""
        
        # Análisis simple pero efectivo
        recent_tasks = user_context.get('recent_task_times', [])
        
        # Si usuario es más activo en la mañana (antes de 10 AM)
        morning_tasks = [t for t in recent_tasks if t.hour < 10]
        if len(morning_tasks) > len(recent_tasks) * 0.6:
            return "07:00"  # Madrugador
        
        # Si es más activo en la tarde
        evening_tasks = [t for t in recent_tasks if 17 <= t.hour <= 19]  
        if len(evening_tasks) > len(recent_tasks) * 0.4:
            return "18:00"  # Después del trabajo
            
        return "07:00"  # Default seguro
```

### **3. User Context Analyzer (Versión Simple)**

```python
# services/user_context_analyzer.py

class UserContextAnalyzer:
    """Análisis de contexto enfocado en datos existentes"""
    
    async def analyze_user_context(self, user_id: str) -> dict:
        """Analiza patrones existentes del usuario"""
        
        # Obtener últimas 30 tareas completadas
        recent_entries = await supabase.get_user_entries(
            user_id, 
            days=30, 
            status='completed'
        )
        
        return {
            'task_completion_times': self._analyze_completion_times(recent_entries),
            'most_active_days': self._analyze_active_days(recent_entries),
            'typical_task_duration': self._analyze_task_durations(recent_entries),
            'completion_rate': self._calculate_completion_rate(user_id),
            'preferred_categories': self._analyze_categories(recent_entries)
        }
    
    def _analyze_completion_times(self, entries: List[dict]) -> List[int]:
        """Extrae horas del día cuando más completa tareas"""
        hours = []
        for entry in entries:
            if entry.get('completed_at'):
                dt = datetime.fromisoformat(entry['completed_at'])
                hours.append(dt.hour)
        return hours
    
    def _calculate_completion_rate(self, user_id: str) -> float:
        """Calcula tasa de completación general"""
        total = len(await supabase.get_user_entries(user_id, days=30))
        completed = len(await supabase.get_user_entries(user_id, days=30, status='completed'))
        
        return (completed / total * 100) if total > 0 else 80  # Default optimista
```

### **4. Plan Task Creator**

```python
# En command_handler.py

async def _create_plan_tasks(self, plan: dict, user: Dict[str, Any]) -> List[dict]:
    """Crea todas las tareas del plan en BD y Todoist"""
    
    tasks_created = []
    
    # Guardar plan en BD primero
    plan_id = await self._save_plan_to_db(plan, user['id'])
    
    for task in plan['tasks']:
        # Crear tarea en formato estándar
        task_data = {
            'type': 'tarea',
            'description': task['title'], 
            'datetime': task['datetime'],
            'priority': task['priority'],
            'task_category': task['category'],
            'user_id': user['id'],
            'plan_id': plan_id,  # Vincular al plan
            'status': 'pending'
        }
        
        # Usar el flujo existente de creación (incluye Todoist)
        try:
            # Crear en Todoist si hay integración
            from services.integrations.integration_manager import integration_manager
            todoist_integration = await integration_manager.get_user_integration(user['id'], 'todoist')
            
            if todoist_integration:
                todoist_id = await todoist_integration.create_task(task_data)
                if todoist_id:
                    task_data['external_id'] = todoist_id
                    task_data['external_service'] = 'todoist'
            
            # Crear en BD local
            entry = await supabase.create_entry(task_data)
            tasks_created.append(entry)
            
        except Exception as e:
            logger.error(f"Error creating plan task: {e}")
            # Continuar con las demás tareas
    
    return tasks_created

async def _save_plan_to_db(self, plan: dict, user_id: str) -> str:
    """Guarda el plan en la tabla smart_plans"""
    
    plan_data = {
        'user_id': user_id,
        'plan_type': plan['type'],
        'name': plan['name'],
        'total_tasks': len(plan['tasks']),
        'status': 'active',
        'target_end_date': self._calculate_end_date(plan),
        'context_snapshot': plan.get('user_context', {})
    }
    
    result = supabase._get_client().table("smart_plans").insert(plan_data).execute()
    return result.data[0]['id']
```

## 📊 Base de Datos - Implementación MVP

```sql
-- Tabla simple para MVP
CREATE TABLE IF NOT EXISTS smart_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plan_type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    total_tasks INTEGER NOT NULL,
    completed_tasks INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    target_end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vincular tareas existentes a planes
ALTER TABLE entries ADD COLUMN IF NOT EXISTS plan_id UUID REFERENCES smart_plans(id);
```

## 🎯 Testing Strategy

### **Tests Automatizados**
```python
# tests/test_plan_generation.py

async def test_exercise_plan_creation():
    """Test completo de generación de plan de ejercicio"""
    
    user = {'id': 'test-user', 'whatsapp_number': '50612345678'}
    command = '/plan ejercicio principiante'
    
    result = await command_handler.handle_command('/plan', command, user)
    
    assert result['type'] == 'plan_created'
    assert 'plan_id' in result
    assert result['tasks_count'] == 12  # 4 semanas * 3 días
    
    # Verificar que las tareas se crearon
    plan_tasks = await supabase.get_entries_by_plan_id(result['plan_id'])
    assert len(plan_tasks) == 12
    
    # Verificar fechas progresivas
    dates = [task['datetime'] for task in plan_tasks]
    assert dates == sorted(dates)  # Fechas en orden
```

### **Tests de Usuario Real**
1. **Test con usuario existente con Todoist**
2. **Test con usuario sin integraciones**  
3. **Test de diferentes tipos de planes**
4. **Test de parámetros inválidos**

## 🚀 Roadmap de Expansión

### **Versión 1.1 (Semana 2)**
- Templates adicionales: intermedio, avanzado
- Planes de lectura inteligentes (OCR para obtener info de libros)
- Análisis más sofisticado de contexto

### **Versión 1.2 (Semana 3)** 
- Adaptación automática basada en progreso
- Generación con Gemini para casos complejos
- Dashboard de progreso

### **Versión 2.0 (Mes 2)**
- Gamificación y logros
- Sharing de planes exitosos
- ML para optimización continua

## 💡 Consideraciones de UX

### **Mensajes Optimizados**
```
❌ ANTES: "He creado un plan de ejercicio personalizado con 12 tareas distribuidas en 4 semanas..."

✅ AHORA: "🏋️ Plan de ejercicio creado
📅 4 semanas | ⏰ Lu-Mi-Vi 7:00 AM
📋 12 tareas programadas
🎯 /planes para ver progreso"
```

### **Fallbacks Inteligentes**
- Si no hay Todoist → crear solo en BD local
- Si parámetros incorrectos → sugerir opciones válidas
- Si falla análisis → usar defaults seguros

## 🎯 Métricas de Éxito MVP

**Semana 1:**
- [ ] 3 tipos de planes funcionando
- [ ] Integración con Todoist working
- [ ] Al menos 5 usuarios reales testean
- [ ] 0 errores críticos en producción

**Criterio de Éxito:**
- 80% de usuarios que prueban un plan lo completan al menos 50%
- Tiempo de generación < 5 segundos
- 95% de tareas se crean correctamente en Todoist

Esta estrategia **equilibra ambición con realismo**, entregando valor inmediato mientras construye la base para funcionalidades más avanzadas.