# 📋 Guía de Gestión de Tareas - Korei Assistant

## 🎯 Funcionalidad Implementada

Korei Assistant ahora incluye un **sistema completo de gestión de tareas interactivo** que permite visualizar, organizar y completar tareas directamente desde WhatsApp con integración a Todoist.

---

## 🚀 Comandos Principales

### **📅 `/today` o `/hoy` - Resumen del Día**

Muestra un resumen completo de tu día actual incluyendo:
- ✅ Tareas pendientes y completadas
- 📅 Eventos programados  
- 💰 Gastos e ingresos del día
- 🎯 Botones interactivos para completar tareas

**Ejemplo de uso:**
```
Usuario: /today
```

**Respuesta típica:**
```
📅 Resumen de Hoy - 17 de Agosto

📋 TAREAS (3):
⏳ Pendientes (2):
• 🔴 Llamar al doctor (14:00)
• 🟡 Comprar leche
• 🟢 Revisar emails (16:30)

✅ Completadas (1):
• ✓ Reunión con equipo

📅 EVENTOS (1):
• ⏰ Cita médica a las 15:00

💰 FINANZAS:
• 💸 Gastos: ₡15.000
• 💚 Balance: ₡35.000

🎯 Acciones rápidas:
• Botón: Completar 'Llamar al doctor'
• Botón: Completar 'Comprar leche'
• Usa /completar [tarea] para completar otras

🚀 Comandos útiles:
• /tomorrow - Ver mañana
• /agenda - Agenda de la semana
• /gastos - Detalles de gastos
• /completar [tarea] - Marcar tarea como completada
```

---

### **🌅 `/tomorrow` o `/mañana` - Vista de Mañana**

Muestra todas las tareas y eventos programados para el día siguiente.

**Ejemplo:**
```
Usuario: /tomorrow
```

**Respuesta:**
```
📅 Mañana - 18 de Agosto, Sábado

📋 TAREAS (2):
• 🟡 Ir al supermercado (10:00)
• 🟢 Lavar el carro

📅 EVENTOS (1):
• 📆 Almuerzo familiar a las 13:00

💡 Tips:
• Usa /today para ver el día actual
• Agrega más tareas diciendo 'Recordarme [algo] mañana'
```

---

### **✅ `/completar [tarea]` - Completar Tareas**

Marca tareas como completadas tanto en la base de datos local como en Todoist (si está conectado).

**Características:**
- 🔍 **Búsqueda inteligente** - Solo necesitas escribir parte del nombre
- 🎯 **Coincidencias múltiples** - Te muestra opciones si encuentra varias
- 🔄 **Sincronización automática** con Todoist
- ✅ **Confirmación visual** con detalles

**Ejemplos de uso:**
```
Usuario: /completar doctor
```

**Respuesta exitosa:**
```
✅ Tarea completada!

📋 Llamar al doctor
📅 Programada: 17/08 14:00
⏰ Completada: 17/08 14:15
✅ También completada en Todoist

🎉 ¡Buen trabajo! Usa /today para ver tu progreso del día.
```

**Si hay múltiples coincidencias:**
```
🔍 Encontré 2 tareas similares:

1. Llamar al doctor (17/08 14:00)
2. Cita con doctor especialista (18/08 10:00)

💡 Sé más específico o usa /completar [nombre exacto]
```

---

### **📅 `/agenda` - Vista Semanal**

Muestra tu agenda completa de la semana con estadísticas de progreso.

**Ejemplo:**
```
Usuario: /agenda
```

**Respuesta:**
```
📅 Agenda Semanal
17/08 - 23/08

📍 Lunes 17/08 (HOY)
  ✅ 09:00 - Reunión con equipo 🔴
  ⏳ 14:00 - Llamar al doctor 🔴
  📆 15:00 - Cita médica

📅 Martes 18/08 (MAÑANA)
  ⏳ 10:00 - Ir al supermercado 🟡
  📆 13:00 - Almuerzo familiar

📅 Miércoles 19/08
  Sin actividades

📊 Resumen semanal:
• Tareas: 15 (8 completadas)
• Eventos: 5
• Progreso: 53%

💡 Usa /today para ver detalles del día actual
```

---

## 🔄 Integración con Todoist

### **Configuración**
```
Usuario: /conectar todoist YOUR_API_TOKEN
```

**Respuesta:**
```
✅ Todoist conectado exitosamente!

🎉 Ya puedes:
• Crear tareas desde WhatsApp
• Sincronizar automáticamente  
• Ver tareas con /tareas

📝 Ejemplos:
• "Comprar leche mañana" → Se crea en Todoist
• "Llamar doctor viernes 2pm prioridad alta"

🔄 Usa /sincronizar para importar tareas existentes.
```

### **Asignación Automática de Proyectos**

Korei asigna automáticamente tareas a proyectos basándose en:
- 🏠 **Contexto:** "limpiar casa" → Proyecto "Casa"
- 💼 **Trabajo:** "reunión equipo" → Proyecto "Trabajo"  
- 🛒 **Compras:** "comprar leche" → Proyecto "Compras"
- 💰 **Finanzas:** "pagar factura" → Proyecto "Finanzas"

**Ver proyectos:**
```
Usuario: /proyectos
```

**Probar asignación:**
```
Usuario: /test-proyectos comprar ingredientes para la cena
```

---

## 🎯 Botones Interactivos

### **Completar Tareas con Un Clic**

Cuando usas `/today` y tienes tareas pendientes, Korei te muestra botones interactivos:

```
🎯 Acciones rápidas:
• Botón: Completar 'Llamar al doctor'
• Botón: Completar 'Comprar leche'  
• Botón: Completar 'Revisar emails'
```

**Solo haz clic en el botón y la tarea se marca como completada automáticamente!**

---

## 📱 Flujo de Trabajo Completo

### **1. Revisión Matutina**
```
Usuario: /hola
```
- Saludo personalizado con resumen del día
- Tareas pendientes de hoy
- Eventos programados

### **2. Gestión Durante el Día**
```
Usuario: /today
```
- Ver todas las actividades
- Completar tareas con botones
- Revisar progreso financiero

### **3. Planificación**
```
Usuario: /tomorrow
Usuario: /agenda
```
- Preparar el día siguiente
- Vista general de la semana

### **4. Completar Tareas**
```
Usuario: /completar doctor
Usuario: [Clic en botón de tarea]
```
- Múltiples formas de completar
- Sincronización automática

---

## 🔧 Características Técnicas

### **Búsqueda Inteligente**
- Coincidencia parcial de texto
- Búsqueda por palabras clave
- Manejo de múltiples resultados

### **Integración Todoist**
- Asignación automática de proyectos
- Sincronización bidireccional
- Manejo de errores y fallbacks

### **Botones Interactivos**
- WhatsApp Cloud API compatible
- Fallback a comandos de texto
- Máximo 3 botones por mensaje

### **Base de Datos**
- Timestamp de completado
- Historial de cambios de estado
- Integración con external_id para Todoist

---

## 🎉 Ejemplos de Uso Real

### **Caso 1: Desarrollador Freelance**
```
9:00 AM: /hola
"Buenos días! 📋 Tienes 5 tareas pendientes para hoy"

10:30 AM: "Terminé la implementación de login"
10:31 AM: /completar login

12:00 PM: /today
"📋 TAREAS: 4 pendientes, 1 completada"
[Clic en botón "Completar reunión cliente"]

6:00 PM: /agenda
"📅 Mañana: Presentación proyecto 10am, Call con team 3pm"
```

### **Caso 2: Gestión Personal**
```
7:00 AM: /today
"📋 Comprar leche, 📅 Cita médica 2pm, 💸 Budget: ₡45,000"

8:30 AM: "Compré leche ₡2500"
[Automáticamente se marca como completada y se registra el gasto]

2:15 PM: /completar medica
"✅ Cita médica completada! También completada en Todoist"

8:00 PM: /tomorrow  
"📅 Mañana: Reunión padres, Gym, Preparar presentación"
```

---

## 🚀 Próximas Mejoras

- ⏰ **Recordatorios proactivos** antes de eventos
- 📊 **Analytics de productividad** semanal
- 🔄 **Sincronización con Google Calendar**
- 🎯 **Sugerencias automáticas** de tareas
- 📱 **Templates de tareas** recurrentes

---

*Esta funcionalidad está lista para producción y completamente integrada con el sistema existente de Korei Assistant.*