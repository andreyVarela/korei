"""
Servicio de programación de recordatorios y tareas automáticas
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
import pytz
from loguru import logger

from services.whatsapp_cloud import whatsapp_cloud_service
from core.supabase import supabase


class ReminderScheduler:
    def __init__(self):
        """Inicializa el scheduler con configuración optimizada"""
        self.scheduler = AsyncIOScheduler()
        self.tz = pytz.timezone('America/Costa_Rica')
        self.is_running = False
        
        # Configurar job store en memoria (más rápido que DB para recordatorios)
        jobstore = MemoryJobStore()
        self.scheduler.add_jobstore(jobstore, 'default')
        
        logger.info("ReminderScheduler inicializado")
    
    async def start(self):
        """Inicia el scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ ReminderScheduler iniciado")
            
            # Programar mensaje de buenos días para todos los usuarios activos
            await self.schedule_daily_good_morning()
            
    async def stop(self):
        """Detiene el scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("⏹️ ReminderScheduler detenido")
    
    async def schedule_reminder(self, reminder_data: Dict[str, Any], user: Dict[str, Any]) -> Optional[str]:
        """
        Programa un recordatorio individual o recurrente
        
        Args:
            reminder_data: Datos del recordatorio (datetime, description, recurrence, etc.)
            user: Datos del usuario
            
        Returns:
            job_id si se programó exitosamente, None si falló
        """
        try:
            # Extraer datetime del recordatorio
            reminder_time = reminder_data.get('datetime')
            if not reminder_time:
                logger.warning("Recordatorio sin datetime válido")
                return None
            
            # Convertir string a datetime si es necesario
            if isinstance(reminder_time, str):
                reminder_time = datetime.fromisoformat(reminder_time.replace('Z', '+00:00'))
            
            # Asegurar que está en timezone de Costa Rica
            if reminder_time.tzinfo is None:
                reminder_time = self.tz.localize(reminder_time)
            else:
                reminder_time = reminder_time.astimezone(self.tz)
            
            # Verificar recurrencia
            recurrence = reminder_data.get('recurrence', 'none')
            
            # Para recordatorios recurrentes, permitir fechas en el pasado para la primera ocurrencia
            if recurrence == 'none':
                now = datetime.now(self.tz)
                if reminder_time <= now:
                    logger.warning(f"Recordatorio en el pasado: {reminder_time} <= {now}")
                    return None
                # Crear trigger de fecha única
                trigger = DateTrigger(run_date=reminder_time, timezone=self.tz)
                job_id = f"reminder_{user['id']}_{int(reminder_time.timestamp())}"
            else:
                # Manejar recordatorio recurrente
                trigger = self._create_recurring_trigger(reminder_time, recurrence)
                if not trigger:
                    logger.error(f"No se pudo crear trigger recurrente para: {recurrence}")
                    return None
                job_id = f"recurring_reminder_{user['id']}_{recurrence}_{int(reminder_time.timestamp())}"
            
            # Programar el job
            job = self.scheduler.add_job(
                func=self.send_recurring_reminder if recurrence != 'none' else self.send_reminder,
                trigger=trigger,
                args=[reminder_data, user],
                id=job_id,
                max_instances=1,
                replace_existing=True
            )
            
            logger.info(f"📅 Recordatorio programado: {job_id} para {reminder_time}")
            return job_id
            
        except Exception as e:
            logger.error(f"Error programando recordatorio: {e}")
            return None
    
    def _create_recurring_trigger(self, reminder_time: datetime, recurrence: str):
        """
        Crea un trigger recurrente basado en el tipo de recurrencia
        
        Args:
            reminder_time: Tiempo inicial del recordatorio
            recurrence: Tipo de recurrencia (daily, weekly, monthly, yearly)
            
        Returns:
            CronTrigger configurado o None si el tipo no es válido
        """
        try:
            hour = reminder_time.hour
            minute = reminder_time.minute
            
            if recurrence == 'daily':
                # Todos los días a la misma hora
                return CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=self.tz
                )
            elif recurrence == 'weekly':
                # Mismo día de la semana cada semana
                day_of_week = reminder_time.weekday()  # 0=Monday, 6=Sunday
                return CronTrigger(
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    timezone=self.tz
                )
            elif recurrence == 'monthly':
                # Mismo día del mes cada mes
                day = reminder_time.day
                return CronTrigger(
                    day=day,
                    hour=hour,
                    minute=minute,
                    timezone=self.tz
                )
            elif recurrence == 'yearly':
                # Mismo día y mes cada año
                month = reminder_time.month
                day = reminder_time.day
                return CronTrigger(
                    month=month,
                    day=day,
                    hour=hour,
                    minute=minute,
                    timezone=self.tz
                )
            else:
                logger.error(f"Tipo de recurrencia no válido: {recurrence}")
                return None
                
        except Exception as e:
            logger.error(f"Error creando trigger recurrente: {e}")
            return None
    
    async def send_reminder(self, reminder_data: Dict[str, Any], user: Dict[str, Any]):
        """
        Envía un recordatorio por WhatsApp
        
        Args:
            reminder_data: Datos del recordatorio
            user: Datos del usuario
        """
        try:
            # Construir mensaje del recordatorio
            description = reminder_data.get('description', 'Recordatorio')
            priority = reminder_data.get('priority', 'media')
            
            # Emojis según prioridad
            priority_emoji = {
                'alta': '🔴',
                'media': '🟡', 
                'baja': '🟢'
            }
            
            emoji = priority_emoji.get(priority, '🔔')
            
            message = f"{emoji} **RECORDATORIO**\n\n"
            message += f"📝 {description}\n\n"
            message += f"⏰ Programado para ahora\n"
            message += f"⚡ Prioridad: {priority.title()}\n\n"
            message += "✅ ¡No olvides completar esta tarea!"
            
            # Enviar mensaje
            success = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=message
            )
            
            if success:
                logger.info(f"✅ Recordatorio enviado a {user['whatsapp_number']}: {description}")
                
                # Marcar recordatorio como completado en la base de datos
                await self.mark_reminder_completed(reminder_data, user)
            else:
                logger.error(f"❌ Falló envío de recordatorio a {user['whatsapp_number']}")
                
        except Exception as e:
            logger.error(f"Error enviando recordatorio: {e}")
    
    async def send_recurring_reminder(self, reminder_data: Dict[str, Any], user: Dict[str, Any]):
        """
        Envía un recordatorio recurrente por WhatsApp
        """
        try:
            # Construir mensaje del recordatorio recurrente
            description = reminder_data.get('description', 'Recordatorio')
            priority = reminder_data.get('priority', 'media')
            recurrence = reminder_data.get('recurrence', 'none')
            
            # Emojis según prioridad
            priority_emoji = {
                'alta': '🔴',
                'media': '🟡', 
                'baja': '🟢'
            }
            
            # Emojis según recurrencia
            recurrence_emoji = {
                'daily': '📅',
                'weekly': '📆',
                'monthly': '🗓️',
                'yearly': '🎂'
            }
            
            emoji = priority_emoji.get(priority, '🔔')
            recurrence_icon = recurrence_emoji.get(recurrence, '🔁')
            
            # Crear mensaje con información de recurrencia
            message = f"{emoji} **RECORDATORIO RECURRENTE** {recurrence_icon}\n\n"
            message += f"📝 {description}\n\n"
            message += f"⏰ Recordatorio {recurrence.replace('daily', 'diario').replace('weekly', 'semanal').replace('monthly', 'mensual').replace('yearly', 'anual')}\n"
            message += f"⚡ Prioridad: {priority.title()}\n\n"
            message += "✅ ¡No olvides completar esta tarea!"
            
            # Enviar mensaje
            success = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=message
            )
            
            if success:
                logger.info(f"✅ Recordatorio recurrente enviado a {user['whatsapp_number']}: {description} ({recurrence})")
                
                # No marcar como completado ya que es recurrente
                # Solo registrar la ejecución si es necesario
                await self.log_recurring_reminder_execution(reminder_data, user)
            else:
                logger.error(f"❌ Falló envío de recordatorio recurrente a {user['whatsapp_number']}")
                
        except Exception as e:
            logger.error(f"Error enviando recordatorio recurrente: {e}")
    
    async def log_recurring_reminder_execution(self, reminder_data: Dict[str, Any], user: Dict[str, Any]):
        """Registra la ejecución de un recordatorio recurrente (opcional)"""
        try:
            # Aquí se podría registrar en la base de datos cada ejecución si es necesario
            # Por ahora solo logeamos
            logger.info(f"Recordatorio recurrente ejecutado: {reminder_data.get('description')} para {user.get('name', 'Usuario')}")
        except Exception as e:
            logger.error(f"Error registrando ejecución de recordatorio recurrente: {e}")
    
    async def mark_reminder_completed(self, reminder_data: Dict[str, Any], user: Dict[str, Any]):
        """Marca un recordatorio como completado en la base de datos"""
        try:
            # Si el recordatorio viene de la DB, actualizarlo
            if 'id' in reminder_data:
                await supabase.update_entry(reminder_data['id'], {
                    'status': 'completed',
                    'completed_at': datetime.now(self.tz).isoformat()
                })
                logger.info(f"Recordatorio {reminder_data['id']} marcado como completado")
        except Exception as e:
            logger.error(f"Error marcando recordatorio como completado: {e}")
    
    async def schedule_daily_good_morning(self):
        """
        Programa mensajes de buenos días para todos los usuarios activos
        Analiza patrones de actividad para determinar hora óptima
        """
        try:
            logger.info("🌅 Programando mensajes de buenos días...")
            
            # Obtener todos los usuarios activos
            users = await self.get_active_users()
            
            for user in users:
                await self.schedule_user_good_morning(user)
                
            logger.info(f"✅ Mensajes de buenos días programados para {len(users)} usuarios")
            
        except Exception as e:
            logger.error(f"Error programando mensajes de buenos días: {e}")
    
    async def get_active_users(self) -> list:
        """Obtiene lista de usuarios activos (que han enviado mensajes recientemente)"""
        try:
            # Obtener usuarios que han sido activos en los últimos 7 días
            seven_days_ago = datetime.now(self.tz) - timedelta(days=7)
            
            result = supabase._get_client().table("entries").select(
                "user_id"
            ).gte(
                "created_at", seven_days_ago.isoformat()
            ).execute()
            
            # Obtener IDs únicos de usuarios
            active_user_ids = list(set(entry['user_id'] for entry in result.data))
            
            # Obtener datos completos de usuarios
            if not active_user_ids:
                return []
            
            users_result = supabase._get_client().table("users").select("*").in_(
                "id", active_user_ids
            ).execute()
            
            return users_result.data
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios activos: {e}")
            return []
    
    async def schedule_user_good_morning(self, user: Dict[str, Any]):
        """
        Programa mensaje de buenos días para un usuario específico
        basado en sus patrones de actividad
        """
        try:
            # Analizar patrones de actividad del usuario
            optimal_time = await self.calculate_optimal_morning_time(user)
            
            # Crear trigger diario
            trigger = CronTrigger(
                hour=optimal_time.hour,
                minute=optimal_time.minute,
                timezone=self.tz
            )
            
            job_id = f"good_morning_{user['id']}"
            
            # Programar mensaje diario
            job = self.scheduler.add_job(
                func=self.send_good_morning_message,
                trigger=trigger,
                args=[user],
                id=job_id,
                max_instances=1,
                replace_existing=True
            )
            
            logger.info(f"🌅 Buenos días programado para {user.get('name', 'Usuario')} a las {optimal_time.strftime('%H:%M')}")
            
        except Exception as e:
            logger.error(f"Error programando buenos días para usuario {user.get('id')}: {e}")
    
    async def calculate_optimal_morning_time(self, user: Dict[str, Any]) -> datetime:
        """
        Calcula la hora óptima para enviar mensaje de buenos días
        basado en patrones de actividad del usuario
        """
        try:
            # Obtener actividad reciente del usuario
            thirty_days_ago = datetime.now(self.tz) - timedelta(days=30)
            
            result = supabase._get_client().table("entries").select(
                "created_at"
            ).eq(
                "user_id", user['id']
            ).gte(
                "created_at", thirty_days_ago.isoformat()
            ).execute()
            
            if not result.data:
                # Sin datos, usar hora por defecto (8:30 AM)
                return datetime.now(self.tz).replace(hour=8, minute=30, second=0, microsecond=0)
            
            # Analizar horas de actividad
            activity_hours = []
            for entry in result.data:
                created_at = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00'))
                created_at = created_at.astimezone(self.tz)
                activity_hours.append(created_at.hour + created_at.minute / 60.0)
            
            # Filtrar actividad matutina (6 AM - 12 PM)
            morning_activity = [h for h in activity_hours if 6 <= h <= 12]
            
            if morning_activity:
                # Calcular hora promedio de actividad matutina menos 2 horas
                avg_morning_hour = sum(morning_activity) / len(morning_activity)
                optimal_hour = max(6.0, avg_morning_hour - 2.0)  # Mínimo 6 AM
            else:
                # Sin actividad matutina, usar promedio general menos 3 horas
                avg_hour = sum(activity_hours) / len(activity_hours)
                optimal_hour = max(6.0, min(10.0, avg_hour - 3.0))  # Entre 6-10 AM
            
            # Convertir a hora y minutos
            hour = int(optimal_hour)
            minute = int((optimal_hour - hour) * 60)
            
            # Redondear a intervalos de 15 minutos
            minute = round(minute / 15) * 15
            if minute >= 60:
                hour += 1
                minute = 0
            
            optimal_time = datetime.now(self.tz).replace(
                hour=hour, 
                minute=minute, 
                second=0, 
                microsecond=0
            )
            
            logger.info(f"📊 Hora óptima calculada para {user.get('name', 'Usuario')}: {optimal_time.strftime('%H:%M')} (basado en {len(activity_hours)} actividades)")
            
            return optimal_time
            
        except Exception as e:
            logger.error(f"Error calculando hora óptima para {user.get('id')}: {e}")
            # Fallback: 8:30 AM
            return datetime.now(self.tz).replace(hour=8, minute=30, second=0, microsecond=0)
    
    async def send_good_morning_message(self, user: Dict[str, Any]):
        """
        Envía mensaje de buenos días personalizado
        """
        try:
            # Generar resumen del día
            today_summary = await self.generate_today_summary(user)
            
            # Crear mensaje personalizado
            name = user.get('name', 'Usuario')
            
            message = f"🌅 **¡Buenos días, {name}!**\n\n"
            message += f"☀️ **Resumen de hoy:**\n"
            message += today_summary
            message += f"\n\n🚀 **¡Que tengas un excelente día!**\n"
            message += f"💬 Estoy aquí para ayudarte con lo que necesites."
            
            # Enviar mensaje
            success = await whatsapp_cloud_service.send_text_message(
                to=user['whatsapp_number'],
                message=message
            )
            
            if success:
                logger.info(f"🌅 Buenos días enviado a {name} ({user['whatsapp_number']})")
            else:
                logger.error(f"❌ Falló envío de buenos días a {user['whatsapp_number']}")
                
        except Exception as e:
            logger.error(f"Error enviando buenos días: {e}")
    
    async def generate_today_summary(self, user: Dict[str, Any]) -> str:
        """
        Genera resumen personalizado del día para el usuario
        """
        try:
            today = datetime.now(self.tz).date()
            tomorrow = today + timedelta(days=1)
            
            # Obtener eventos/tareas de hoy
            today_entries = supabase._get_client().table("entries").select(
                "type, description, datetime, priority"
            ).eq(
                "user_id", user['id']
            ).gte(
                "datetime", today.isoformat()
            ).lt(
                "datetime", tomorrow.isoformat()
            ).eq(
                "status", "pending"
            ).execute()
            
            if not today_entries.data:
                return "📅 No tienes eventos programados para hoy\n🆓 ¡Día libre para nuevas oportunidades!"
            
            # Categorizar por tipo
            eventos = [e for e in today_entries.data if e['type'] == 'evento']
            tareas = [e for e in today_entries.data if e['type'] == 'tarea']
            recordatorios = [e for e in today_entries.data if e['type'] == 'recordatorio']
            
            summary = ""
            
            if eventos:
                summary += f"📅 **{len(eventos)} evento(s):**\n"
                for evento in eventos[:3]:  # Máximo 3
                    time_str = ""
                    if evento.get('datetime'):
                        dt = datetime.fromisoformat(evento['datetime'].replace('Z', '+00:00'))
                        time_str = f" a las {dt.strftime('%H:%M')}"
                    summary += f"• {evento['description']}{time_str}\n"
                if len(eventos) > 3:
                    summary += f"• ... y {len(eventos) - 3} más\n"
                summary += "\n"
            
            if tareas:
                summary += f"✅ **{len(tareas)} tarea(s) pendiente(s):**\n"
                for tarea in tareas[:3]:  # Máximo 3
                    priority_emoji = {'alta': '🔴', 'media': '🟡', 'baja': '🟢'}.get(tarea.get('priority', 'media'), '📝')
                    summary += f"{priority_emoji} {tarea['description']}\n"
                if len(tareas) > 3:
                    summary += f"• ... y {len(tareas) - 3} más\n"
                summary += "\n"
            
            if recordatorios:
                summary += f"🔔 **{len(recordatorios)} recordatorio(s)**\n"
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generando resumen del día: {e}")
            return "📅 Revisa tu agenda para ver qué tienes programado hoy"


# Singleton
reminder_scheduler = ReminderScheduler()