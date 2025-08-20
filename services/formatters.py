"""
Formatters para mensajes de WhatsApp
"""
from typing import Dict, Any, Optional
from datetime import datetime
import pytz
from app.config import settings

class MessageFormatter:
    """Formatear mensajes para WhatsApp con estilo consistente"""
    
    def __init__(self):
        self.tz = pytz.timezone(settings.timezone)
    
    def format_currency(self, amount: float) -> str:
        """
        Formatear moneda con separadores de miles
        
        Args:
            amount: Monto a formatear
            
        Returns:
            String formateado como "₡10.000" o "$10.000"
        """
        if amount is None:
            return ""
        
        # Formatear con separador de miles
        formatted = f"{amount:,.0f}".replace(",", ".")
        
        # Agregar símbolo de moneda (asumiendo colones de Costa Rica)
        return f"₡{formatted}"
    
    def format_date(self, date_str: str) -> str:
        """
        Formatear fecha de ISO a formato legible
        
        Args:
            date_str: Fecha en formato ISO
            
        Returns:
            Fecha formateada como "16 Ago 2025, 7:17 AM"
        """
        try:
            # Parsear fecha ISO
            if isinstance(date_str, str):
                # Manejar diferentes formatos de fecha
                for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        if dt.tzinfo is None:
                            dt = self.tz.localize(dt)
                        break
                    except ValueError:
                        continue
                else:
                    # Si no puede parsear, usar fecha actual
                    dt = datetime.now(self.tz)
            else:
                dt = datetime.now(self.tz)
            
            # Convertir a timezone local
            dt = dt.astimezone(self.tz)
            
            # Formatear como "16 Ago 2025, 7:17 AM"
            months = {
                1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
            }
            
            day = dt.day
            month = months[dt.month]
            year = dt.year
            hour = dt.strftime('%I').lstrip('0')  # Quitar 0 inicial
            minute = dt.strftime('%M')
            period = dt.strftime('%p')
            
            return f"{day} {month} {year}, {hour}:{minute} {period}"
            
        except Exception:
            # Fallback en caso de error
            return datetime.now(self.tz).strftime("%d %b %Y, %I:%M %p")
    
    def format_priority(self, priority: str) -> str:
        """
        Formatear prioridad con emoji
        
        Args:
            priority: Prioridad (alta, media, baja)
            
        Returns:
            Prioridad con emoji
        """
        priority_map = {
            'alta': '🔴 Alta',
            'media': '🟡 Media', 
            'baja': '🟢 Baja'
        }
        
        return priority_map.get(priority.lower() if priority else 'media', '🟡 Media')
    
    def format_entry_response(self, result: Dict[str, Any]) -> str:
        """
        Formatear respuesta completa para una entrada
        
        Args:
            result: Diccionario con datos de la entrada
            
        Returns:
            Mensaje formateado para WhatsApp
        """
        # Descripción principal
        description = result.get('description', 'Procesado')
        entry_type = result.get('type', '').lower()
        
        # Emoji por tipo
        type_emojis = {
            'gasto': '💸',
            'ingreso': '💰', 
            'tarea': '📋',
            'evento': '📅',
            'recordatorio': '🔔'
        }
        
        emoji = type_emojis.get(entry_type, '✅')
        response = f"{emoji} {description}\n\n"
        
        # Agregar monto si existe
        amount = result.get('amount')
        if amount and amount > 0:
            if entry_type == 'gasto':
                response += f"💸 Gasto: {self.format_currency(amount)}\n"
            elif entry_type == 'ingreso':
                response += f"💰 Ingreso: {self.format_currency(amount)}\n"
            else:
                response += f"💵 Monto: {self.format_currency(amount)}\n"
        
        # Agregar fecha si existe
        date_field = result.get('datetime')
        if date_field:
            formatted_date = self.format_date(date_field)
            response += f"📅 Fecha: {formatted_date}\n"
        
        # Agregar prioridad si existe y no es 'none'
        priority = result.get('priority')
        if priority and priority != 'none':
            response += f"⚡ Prioridad: {self.format_priority(priority)}\n"
        
        # Agregar categoría si existe
        category = result.get('task_category')
        if category:
            response += f"📂 Categoría: {category}\n"
        
        return response.strip()
    
    def format_error_message(self, error: str) -> str:
        """
        Formatear mensaje de error
        
        Args:
            error: Descripción del error
            
        Returns:
            Mensaje de error formateado
        """
        friendly_errors = [
            "🤖 ¡Ups! Algo no salió como esperaba.",
            "😅 Perdón, no pude procesar eso correctamente.",
            "🔧 Hmm, parece que tuve un pequeño problema.",
            "🤔 No logré entender eso completamente."
        ]
        
        import random
        error_intro = random.choice(friendly_errors)
        
        return f"{error_intro}\n\n💡 Puedes intentar de nuevo o escribir `/help` si necesitas una mano. ¡Estoy aquí para ayudarte!"
    
    def format_help_message(self) -> str:
        """
        Formatear mensaje de ayuda
        
        Returns:
            Mensaje de ayuda formateado
        """
        return """✨ **¡Hola! Soy Korei, tu asistente personal**

Estoy aquí para ayudarte a organizar tu vida de forma súper fácil. Solo háblame de forma natural y yo me encargo del resto 😊

🗣️ **Háblame como le hablarías a un amigo:**
• "Gasté ₡5,000 en almuerzo hoy"
• "Me pagaron ₡50,000 por el proyecto"
• "Tengo reunión con María mañana a las 3pm"
• "Recuérdame llamar al doctor el viernes"
• Envíame fotos de recibos y los proceso automáticamente 📸

📱 **Comandos rápidos que te van a encantar:**
• `/hoy` - ¿Qué tengo planeado para hoy?
• `/mañana` - ¿Qué viene mañana?
• `/agenda` - Mi semana completa
• `/tareas-botones` - ✨ Mis tareas con botones interactivos
• `/stats` - ¿Cómo van mis finanzas?

⚡ **Gestión súper fácil:**
• `/completar llamar doctor` - Marcar tareas como hechas
• `/eliminar` + descripción - Eliminar cosas que no necesito
• Solo haz click en los botones de las tareas 👆

📊 **Tu analista personal:**
• `/resumen-mes` - Cómo va mi mes
• `/analisis-gastos` - ¿En qué gasto más?
• `/tips-finanzas` - Consejos personalizados para ti

👤 **Conóceme mejor:**
• `/registro` - Cuéntame sobre ti para ayudarte mejor
• `/perfil` - Ver mi información

🔗 **Conecta tus apps favoritas:**
• `/conectar google-calendar` - Sincronizar calendario
• `/conectar todoist` - Conectar Todoist
• `/integraciones` - Ver qué tienes conectado

🧠 **Soporte ADHD especializado:**
• `/adhd-tutorial` - Tutorial completo del sistema ADHD
• `/adhd` - Herramientas diseñadas para tu cerebro ADHD
• `/neural` - Modo "Neural Hacking" con terminología técnica 
• `/adhd-trial` - Prueba gratuita de 7 días (funciones premium)
• Rutinas, atención, dopamina y apoyo para días difíciles

💡 **Pro tip:** Mientras más me uses, mejor te entiendo y más útil soy para ti. ¡Hablemos!"""
    
    def format_stats_message(self, stats: Dict[str, Any]) -> str:
        """
        Formatear mensaje de estadísticas
        
        Args:
            stats: Diccionario con estadísticas
            
        Returns:
            Mensaje de estadísticas formateado
        """
        total_gastos = stats.get('gastos', 0)
        total_ingresos = stats.get('ingresos', 0)
        balance = total_ingresos - total_gastos
        total_entries = stats.get('total_entries', 0)
        pending_tasks = stats.get('pending_tasks', 0)
        
        # Mensaje personalizado según el balance
        if balance > 0:
            intro = "🎉 **¡Vas súper bien este mes!**"
            balance_msg = f"📈 Tienes un balance positivo de {self.format_currency(balance)}"
        elif balance == 0:
            intro = "⚖️ **Perfecto equilibrio este mes**"
            balance_msg = f"📊 Tus ingresos y gastos están parejos"
        else:
            intro = "💡 **Tu resumen del mes**"
            balance_msg = f"📉 Déficit de {self.format_currency(abs(balance))} - ¡pero no te preocupes, siempre hay tiempo para ajustar!"
        
        response = f"{intro}\n\n"
        response += f"📊 Has registrado {total_entries} movimientos\n"
        response += f"💰 Ingresos: {self.format_currency(total_ingresos)}\n"
        response += f"💸 Gastos: {self.format_currency(total_gastos)}\n"
        response += f"{balance_msg}\n"
        
        if pending_tasks > 0:
            response += f"\n📋 Tienes {pending_tasks} tareas pendientes"
            if pending_tasks == 1:
                response += " - ¡casi terminando todo!"
            elif pending_tasks <= 3:
                response += " - ¡ya casi!"
            else:
                response += " - vamos paso a paso 💪"
        else:
            response += f"\n✅ ¡Increíble! No tienes tareas pendientes"
        
        response += f"\n\n💡 ¿Quieres ver más detalles? Usa `/analisis-gastos` o `/tips-finanzas`"
        
        return response.strip()

# Instancia singleton
message_formatter = MessageFormatter()