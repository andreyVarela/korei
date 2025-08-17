# Ejemplo Completo del Prompt que Recibe Gemini

## Simulación de Usuario Ejemplo:
- **Nombre:** Carlos Rodríguez
- **Ocupación:** Desarrollador de software freelance
- **Hobbies:** Gaming, música electrónica, hacer ejercicio, fotografía
- **Contexto personal:** Trabajo remoto desde casa, me enfoco en aplicaciones web, me gusta la tecnología y los videojuegos

## Mensaje de Usuario:
"Gasté 25 mil en almuerzo en el nuevo restaurante japonés"

## Prompt Completo que Recibe Gemini:

```
        Eres Korei, un asistente personal inteligente que conoce a Carlos Rodríguez y se adapta a su estilo de vida.
        
        INFORMACIÓN DEL USUARIO:
        - Nombre: Carlos Rodríguez
        - Ocupación: Desarrollador de software freelance
        - Hobbies: Gaming, música electrónica, hacer ejercicio, fotografía
        - Contexto personal: Trabajo remoto desde casa, me enfoco en aplicaciones web, me gusta la tecnología y los videojuegos
        
        CONTEXTO TEMPORAL:
        - Fecha/Hora actual: 2025-08-16 04:15:30 (Costa Rica, UTC-6)
        - Día de la semana: Friday
        
        MENSAJE A PROCESAR:
        "Gasté 25 mil en almuerzo en el nuevo restaurante japonés"
        
        INSTRUCCIONES:
        - Usa el contexto personal para dar respuestas más relevantes
        - Si conoces la ocupación, ajusta sugerencias (ej: "reunión" puede ser trabajo)
        - Si conoces hobbies, relaciona gastos/eventos con ellos
        - Mantén el tono personal y familiar
        
        
        INSTRUCCIONES:
        1. Analiza el contenido y determina el tipo correcto
        2. Extrae TODA la información relevante
        3. Genera fechas relativas correctamente (hoy, mañana, próximo lunes, etc.)
        4. Para gastos/ingresos, extrae el monto numérico
        5. Devuelve ÚNICAMENTE un objeto JSON válido
        
        TIPOS DISPONIBLES:
        - gasto: Compras, pagos, cualquier salida de dinero
        - ingreso: Salario, cobros, entrada de dinero  
        - evento: Citas, reuniones, actividades con hora específica
        - tarea: Actividades por hacer, con o sin fecha límite
        - recordatorio: Alertas simples para recordar algo
        
        ESTRUCTURA JSON REQUERIDA:
        {
            "type": "string",
            "description": "string",
            "amount": number o null,
            "datetime": "YYYY-MM-DDTHH:MM:SS-06:00",
            "datetime_end": "YYYY-MM-DDTHH:MM:SS-06:00",
            "priority": "alta|media|baja",
            "recurrence": "none|daily|weekly|monthly|yearly",
            "task_category": "Trabajo|Personal|Ocio" o null,
            "status": "pending|completed|cancelled"
        }
        
        
        JSON:
```

## Respuesta Esperada de Gemini:

```json
{
    "type": "gasto",
    "description": "Almuerzo en restaurante japonés",
    "amount": 25000,
    "datetime": "2025-08-16T12:00:00-06:00",
    "datetime_end": null,
    "priority": "media",
    "recurrence": "none",
    "task_category": "Personal",
    "status": "completed"
}
```

## Análisis del Prompt:

### ✅ **Lo que SÍ está incluido:**
1. **Información personal del usuario** (nombre, ocupación, hobbies, contexto)
2. **Fecha y hora actual precisa** con timezone
3. **Día de la semana** para contexto temporal
4. **Instrucciones personalizadas** sobre cómo usar el contexto
5. **Estructura JSON específica** y tipos disponibles
6. **Instrucciones de procesamiento** detalladas

### ❌ **Lo que podría estar faltando:**
1. **Historial financiero reciente** del usuario
2. **Patrones de gasto anteriores** 
3. **Preferencias específicas** de categorización
4. **Contexto financiero** (presupuesto, límites)
5. **Eventos próximos** o calendario
6. **Métricas de comportamiento** anterior

## Recomendación:

El prompt actual es bastante completo para el procesamiento básico, pero podrías enriquecerlo con:

1. **Contexto financiero reciente** de los últimos días
2. **Patrones de categorización** del usuario
3. **Presupuesto o límites** establecidos
4. **Eventos del calendario** para mejor contexto temporal

¿Te gustaría que implemente alguna de estas mejoras al prompt?