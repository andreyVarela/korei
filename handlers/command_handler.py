"""
Handler para comandos especiales como /register, /help, /stats y nuevos comandos
"""
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime, timedelta
import pytz
import os
from core.supabase import supabase
from services.gemini import gemini_service
from app.config import settings

class CommandHandler:
    def __init__(self):
        pass
    
    async def handle_command(self, command: str, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa comandos especiales"""
        try:
            if command == "/register" or command == "/registro":
                return await self.handle_register(message, user_context)
            elif command == "/profile" or command == "/perfil":
                return await self.handle_profile(user_context)
            elif command == "/help" or command == "/ayuda":
                return await self.handle_help()
            elif command == "/stats" or command == "/estadisticas":
                return await self.handle_stats(user_context)
            elif command == "/tareas" or command == "/tasks":
                return await self.handle_daily_tasks(user_context, "today")
            elif command == "/tareas-hoy" or command == "/tasks-today":
                return await self.handle_daily_tasks(user_context, "today")
            elif command == "/tareas-mañana" or command == "/tasks-tomorrow":
                return await self.handle_daily_tasks(user_context, "tomorrow")
            elif command == "/eventos" or command == "/events":
                return await self.handle_daily_events(user_context, "today")
            elif command == "/eventos-hoy" or command == "/events-today":
                return await self.handle_daily_events(user_context, "today")
            elif command == "/eventos-mañana" or command == "/events-tomorrow":
                return await self.handle_daily_events(user_context, "tomorrow")
            elif command == "/gastos" or command == "/expenses":
                return await self.handle_daily_expenses(user_context, "today")
            elif command == "/gastos-hoy" or command == "/expenses-today":
                return await self.handle_daily_expenses(user_context, "today")
            elif command == "/ingresos" or command == "/income":
                return await self.handle_daily_income(user_context, "today")
            elif command == "/ingresos-hoy" or command == "/income-today":
                return await self.handle_daily_income(user_context, "today")
            elif command == "/resumen-mes" or command == "/monthly-summary":
                return await self.handle_monthly_summary(user_context)
            elif command == "/tips-finanzas" or command == "/financial-tips":
                return await self.handle_financial_tips(user_context)
            elif command == "/analisis-gastos" or command == "/spending-analysis":
                return await self.handle_spending_analysis(user_context)
            elif command == "/hola" or command == "/hello" or command == "/inicio":
                return await self.handle_greeting(user_context)
            elif command == "/recordatorio" or command == "/reminder":
                return await self.handle_reminder_help()
            elif command == "/proyectos" or command == "/projects":
                return await self.handle_projects_list(user_context)
            elif command == "/test-proyectos" or command == "/test-projects":
                return await self.handle_test_project_selection(user_context, message)
            elif command == "/conectar" or command == "/connect":
                return await self.handle_connect_integration(message, user_context)
            elif command == "/integraciones" or command == "/integrations":
                return await self.handle_list_integrations(user_context)
            elif command == "/sincronizar" or command == "/sync":
                return await self.handle_sync_integrations(user_context)
            # NUEVOS COMANDOS INTELIGENTES
            elif command == "/today" or command == "/hoy":
                return await self.handle_today_summary(user_context)
            elif command == "/tomorrow" or command == "/mañana":
                return await self.handle_tomorrow_summary(user_context)
            elif command == "/completar" or command == "/complete":
                return await self.handle_complete_task(message, user_context)
            elif command == "/agenda" or command == "/schedule":
                return await self.handle_agenda_view(user_context)
            elif command == "/tareas-botones" or command == "/tasks-buttons":
                return await self.handle_tasks_with_buttons(user_context, message)
            elif command == "/hola" or command == "/hello" or command == "/hi":
                return await self.handle_greeting(user_context)
            # ADHD SUPPORT COMMANDS - Natural language style
            elif command == "/adhd":
                return await self.handle_adhd_command(message, user_context, "natural")
            elif command == "/adhd-rutina" or command == "/adhd-routine":
                return await self.handle_adhd_routine(message, user_context, "natural")
            elif command == "/adhd-atencion" or command == "/adhd-attention":
                return await self.handle_adhd_attention(message, user_context, "natural")
            elif command == "/adhd-dopamina" or command == "/adhd-dopamine":
                return await self.handle_adhd_dopamine(message, user_context, "natural")
            elif command == "/adhd-crisis" or command == "/adhd-emergency":
                return await self.handle_adhd_crisis(message, user_context, "natural")
            # NEURAL HACKING COMMANDS - Technical/gaming style
            elif command == "/neural":
                return await self.handle_adhd_command(message, user_context, "neural")
            elif command == "/neural-protocol" or command == "/neural-routine":
                return await self.handle_adhd_routine(message, user_context, "neural")
            elif command == "/neural-focus" or command == "/neural-attention":
                return await self.handle_adhd_attention(message, user_context, "neural")
            elif command == "/neural-boost" or command == "/neural-dopamine":
                return await self.handle_adhd_dopamine(message, user_context, "neural")
            elif command == "/neural-recovery" or command == "/neural-crisis":
                return await self.handle_adhd_crisis(message, user_context, "neural")
            elif command == "/neural-status" or command == "/neural-scan":
                return await self.handle_neural_status(user_context)
            # TUTORIAL AND PREMIUM COMMANDS
            elif command == "/adhd-tutorial" or command == "/adhd-help":
                return await self.handle_adhd_tutorial(user_context, "natural")
            elif command == "/neural-tutorial" or command == "/neural-help":
                return await self.handle_adhd_tutorial(user_context, "neural")
            elif command == "/adhd-trial" or command == "/neural-trial":
                return await self.handle_adhd_trial_activation(user_context, "natural" if "adhd" in command else "neural")
            elif command == "/adhd-planes" or command == "/adhd-plans":
                return await self.handle_adhd_plans(user_context, "natural")
            elif command == "/neural-plans" or command == "/neural-upgrade":
                return await self.handle_adhd_plans(user_context, "neural")
            elif command == "/adhd-status" or command == "/premium-status":
                return await self.handle_premium_status(user_context)
            elif command == "/adhd-upgrade" or command == "/neural-upgrade":
                return await self.handle_upgrade_premium(user_context, "natural" if "adhd" in command else "neural")
            elif command == "/adhd-checkout" or command == "/neural-checkout":
                return await self.handle_create_checkout(message, user_context, "natural" if "adhd" in command else "neural")
            # BASIC PLAN COMMANDS
            elif command == "/basic-trial":
                return await self.handle_basic_trial_activation(user_context)
            elif command == "/basic-upgrade" or command == "/basic-plans":
                return await self.handle_basic_upgrade(user_context)
            elif command == "/basic-checkout":
                return await self.handle_create_basic_checkout(message, user_context)
            # PLAN STATUS
            elif command == "/plan-status" or command == "/mi-plan":
                return await self.handle_plan_status(user_context)
            else:
                return {"error": f"Comando no reconocido: {command}"}
                
        except Exception as e:
            logger.error(f"Error procesando comando {command}: {e}")
            return {"error": "Error procesando comando"}
    
    async def handle_register(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa comando de registro con verificación de perfil completo
        Ejemplos:
        - "/register Soy desarrollador, me gusta la música y el gaming"
        - "/registro Trabajo como diseñador, hobbies: fotografía, cocinar"
        """
        try:
            # 1. Verificar si es un usuario existente con perfil completo
            existing_profile = user_context.get("profile", {})
            has_complete_profile = (
                existing_profile.get("occupation") and 
                existing_profile.get("context_summary") and
                len(existing_profile.get("hobbies", [])) > 0
            )
            
            # Si ya tiene perfil completo, preguntar si quiere actualizar
            if has_complete_profile:
                content_to_process = message.replace("/register", "").replace("/registro", "").strip()
                if not content_to_process:
                    return {
                        "type": "profile_exists",
                        "message": f"✅ Ya tienes un perfil registrado.\n\n**Perfil actual:**\n- Trabajo: {existing_profile.get('occupation')}\n- Hobbies: {', '.join(existing_profile.get('hobbies', []))}\n\n✏️ Para actualizar, usa `/register` seguido de nueva información.\n👤 Para ver completo usa `/profile`"
                    }
            
            # 2. Extraer contenido del mensaje
            content_to_process = message.replace("/register", "").replace("/registro", "").strip()
            
            # Si no hay contenido, solicitar información
            if not content_to_process:
                return {
                    "type": "registration_request",
                    "message": "📝 Para registrarte, cuéntame sobre ti:\n\n💼 **Trabajo:** ¿A qué te dedicas?\n🎯 **Hobbies:** ¿Qué te gusta hacer?\n🔍 **Otros:** Cualquier detalle que me ayude a conocerte\n\n📌 **Ejemplo:**\n`/register Soy desarrollador de software, me gusta la música electrónica, los videojuegos y hacer ejercicio. Trabajo remoto y me enfoco en aplicaciones web.`"
                }
            
            # 3. Usar Gemini para procesar y estructurar la información
            registration_prompt = f"""
            El usuario quiere registrar/actualizar su perfil personal. 
            Procesa y estructura la información del mensaje en un formato claro y útil.
            
            INFORMACIÓN DEL USUARIO: "{content_to_process}"
            
            PERFIL ACTUAL: {existing_profile if existing_profile else "Nuevo usuario"}
            
            Extrae y devuelve JSON con esta estructura EXACTA:
            {{
                "occupation": "trabajo/profesión del usuario (string o null)",
                "hobbies": ["array", "de", "hobbies", "individuales"],
                "context_summary": "resumen completo y detallado de quién es la persona, su trabajo, gustos y personalidad",
                "preferences": {{
                    "work_style": "remoto/oficina/híbrido o null",
                    "interests": ["intereses", "principales"]
                }},
                "extracted": true,
                "confidence": "high/medium/low"
            }}
            
            REGLAS:
            - Si no hay información suficiente, usa "extracted": false
            - Los hobbies deben ser individuales, no agrupados
            - El context_summary debe ser detallado y personal
            - Si es actualización, mejora la información existente
            """
            
            # Llamar a Gemini para extraer información
            extracted_info = gemini_service.model.generate_content(registration_prompt)
            
            # Parsear respuesta de Gemini
            import json
            try:
                # Limpiar la respuesta por si viene con formato markdown
                response_text = extracted_info.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                
                info = json.loads(response_text)
            except Exception as parse_error:
                logger.warning(f"Error parseando respuesta de Gemini: {parse_error}")
                # Fallback manual básico
                info = {
                    "occupation": None,
                    "hobbies": [],
                    "context_summary": content_to_process,
                    "preferences": {},
                    "extracted": False,
                    "confidence": "low"
                }
            
            # 4. Validar que se extrajo información útil
            if not info.get("extracted", False) or info.get("confidence") == "low":
                return {
                    "type": "registration_incomplete",
                    "message": "❌ Necesito más información para crear tu perfil.\n\n📝 **Por favor incluye:**\n- Tu trabajo o profesión\n- Tus hobbies o actividades favoritas\n- Un poco sobre tu personalidad\n\n📌 **Ejemplo:**\n`/register Soy diseñador gráfico freelance, me gusta la fotografía, cocinar y ver documentales. Soy creativo y organizado.`"
                }
            
            # 5. Preparar datos del perfil
            profile_data = {
                "occupation": info.get("occupation"),
                "hobbies": info.get("hobbies", []),
                "context_summary": info.get("context_summary"),
                "preferences": info.get("preferences", {})
            }
            
            # 6. Guardar en base de datos
            await supabase.create_user_profile(user_context["id"], profile_data)
            
            # 7. Mensaje de éxito personalizado
            action = "actualizado" if has_complete_profile else "creado"
            hobbies_text = ', '.join(info.get('hobbies', []))[:100] + ('...' if len(', '.join(info.get('hobbies', []))) > 100 else '')
            
            return {
                "type": "registration_success",
                "message": f"✅ ¡Perfil {action} exitosamente!\n\n👤 **Tu perfil:**\n💼 **Trabajo:** {info.get('occupation', 'No especificado')}\n🎯 **Hobbies:** {hobbies_text or 'No especificados'}\n\n🚀 Ahora puedo darte sugerencias personalizadas y entender mejor tus mensajes.\n\n👤 Usa `/profile` para ver tu perfil completo.",
                "profile": profile_data
            }
            
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            return {
                "type": "error", 
                "message": "❌ Error procesando tu registro. Por favor intenta de nuevo."
            }
    
    async def handle_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra el perfil actual del usuario"""
        try:
            profile = user_context.get("profile", {})
            
            if not profile or not profile.get("occupation"):
                return {
                    "type": "profile_empty",
                    "message": "❌ No tienes un perfil registrado.\n\nUsa `/register` seguido de información sobre ti para comenzar.\n\nEjemplo: `/register Soy diseñador, me gusta el café y leer`"
                }
            
            occupation = profile.get("occupation", "No especificado")
            hobbies = profile.get("hobbies", [])
            context = profile.get("context_summary", "")
            
            profile_text = f"👤 **Tu perfil:**\n\n"
            profile_text += f"💼 **Ocupación:** {occupation}\n"
            
            if hobbies:
                profile_text += f"🎯 **Hobbies:** {', '.join(hobbies)}\n"
            
            if context:
                profile_text += f"📝 **Contexto:** {context}\n"
            
            profile_text += f"\n✏️ Para actualizar usa `/register` con nueva información"
            
            return {
                "type": "profile_display",
                "message": profile_text,
                "profile": profile
            }
            
        except Exception as e:
            logger.error(f"Error mostrando perfil: {e}")
            return {"type": "error", "message": "❌ Error obteniendo perfil"}
    
    async def handle_help(self) -> Dict[str, Any]:
        """Muestra ayuda de comandos"""
        from services.formatters import message_formatter
        help_text = message_formatter.format_help_message()

        return {
            "type": "help",
            "message": help_text
        }
    
    async def handle_stats(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra estadísticas del usuario"""
        try:
            user_id = user_context["id"]
            stats = await supabase.get_user_stats(user_id)
            
            if not stats:
                return {
                    "type": "stats_empty",
                    "message": "📊 No tienes estadísticas aún.\n\nComienza enviando gastos, tareas o eventos para ver tu resumen."
                }
            
            from services.formatters import message_formatter
            
            stats_text = f"""📊 **Tus estadísticas este mes:**

💰 **Finanzas:**
• Gastos: {message_formatter.format_currency(stats.get('gastos', 0))}
• Ingresos: {message_formatter.format_currency(stats.get('ingresos', 0))}
• Balance: {message_formatter.format_currency(stats.get('balance', 0))}

📈 **Actividad:**
• Total entradas: {stats.get('total_entries', 0)}
• Tareas pendientes: {stats.get('pending_tasks', 0)}

📂 **Por tipo:**"""

            by_type = stats.get('by_type', {})
            for entry_type, count in by_type.items():
                stats_text += f"\n• {entry_type.title()}: {count}"
            
            return {
                "type": "stats",
                "message": stats_text,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {"type": "error", "message": "❌ Error obteniendo estadísticas"}
    
    async def handle_daily_tasks(self, user_context: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Muestra tareas del día especificado"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "hoy"
            elif period == "tomorrow":
                tomorrow = now + timedelta(days=1)
                start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "mañana"
            
            # Obtener tareas del período
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "tarea"
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            tasks = result.data
            
            if not tasks:
                return {
                    "type": "daily_tasks_empty",
                    "message": f"📝 No tienes tareas programadas para {period_text}.\n\n💡 Puedes agregar tareas diciendo algo como:\n'Reunión con equipo mañana a las 3pm'"
                }
            
            # Agrupar por estado
            pending_tasks = [t for t in tasks if t['status'] == 'pending']
            completed_tasks = [t for t in tasks if t['status'] == 'completed']
            
            message = f"📋 **Tareas para {period_text}:**\n\n"
            
            if pending_tasks:
                message += "⏳ **Pendientes:**\n"
                for task in pending_tasks:
                    time_str = ""
                    if task.get('datetime'):
                        task_time = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                        time_str = f" ({task_time.strftime('%H:%M')})"
                    priority_icon = "🔴" if task.get('priority') == 'alta' else "🟡" if task.get('priority') == 'media' else "🟢"
                    message += f"• {priority_icon} {task['description']}{time_str}\n"
                message += "\n"
            
            if completed_tasks:
                message += "✅ **Completadas:**\n"
                for task in completed_tasks:
                    message += f"• ✓ {task['description']}\n"
                message += "\n"
            
            message += f"📊 Total: {len(tasks)} tareas ({len(pending_tasks)} pendientes, {len(completed_tasks)} completadas)"
            
            # Preparar botones para tareas pendientes (máximo 3)
            buttons = []
            if pending_tasks:
                for i, task in enumerate(pending_tasks[:3]):
                    task_short_desc = task['description'][:15] + "..." if len(task['description']) > 15 else task['description']
                    buttons.append({
                        "id": f"complete_task_{task['id']}",
                        "title": f"✓ {task_short_desc}"
                    })
            
            return {
                "type": "daily_tasks",
                "message": message,
                "tasks": tasks,
                "period": period,
                "buttons": buttons,
                "has_pending": len(pending_tasks) > 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo tareas diarias: {e}")
            return {"type": "error", "message": "❌ Error obteniendo tareas"}
    
    async def handle_daily_expenses(self, user_context: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Muestra gastos del día especificado"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener gastos del día
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "gasto"
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime", desc=True).execute()
            
            expenses = result.data
            
            if not expenses:
                return {
                    "type": "daily_expenses_empty",
                    "message": "💰 No has registrado gastos hoy.\n\n💡 Puedes agregar gastos diciendo:\n'Gasté 25 mil en almuerzo'"
                }
            
            total = sum(float(exp.get('amount', 0)) for exp in expenses)
            
            message = f"💸 **Gastos de hoy:**\n\n"
            
            # Agrupar por categoría si existe
            by_category = {}
            for exp in expenses:
                category = exp.get('category', 'Sin categoría')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(exp)
            
            for category, items in by_category.items():
                from services.formatters import message_formatter
                category_total = sum(float(item.get('amount', 0)) for item in items)
                message += f"📂 **{category}** ({message_formatter.format_currency(category_total)}):\n"
                for item in items:
                    time_str = ""
                    if item.get('datetime'):
                        exp_time = datetime.fromisoformat(item['datetime'].replace('Z', '+00:00'))
                        time_str = f" ({exp_time.strftime('%H:%M')})"
                    amount_formatted = message_formatter.format_currency(float(item.get('amount', 0)))
                    message += f"• {amount_formatted} - {item['description']}{time_str}\n"
                message += "\n"
            
            message += f"💰 **Total del día: {message_formatter.format_currency(total)}**"
            
            return {
                "type": "daily_expenses",
                "message": message,
                "expenses": expenses,
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo gastos diarios: {e}")
            return {"type": "error", "message": "❌ Error obteniendo gastos"}
    
    async def handle_daily_income(self, user_context: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Muestra ingresos del día especificado"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener ingresos del día
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "ingreso"
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime", desc=True).execute()
            
            income = result.data
            
            if not income:
                return {
                    "type": "daily_income_empty",
                    "message": "💚 No has registrado ingresos hoy.\n\n💡 Puedes agregar ingresos diciendo:\n'Recibí 50 mil por freelance'"
                }
            
            total = sum(float(inc.get('amount', 0)) for inc in income)
            
            message = f"💚 **Ingresos de hoy:**\n\n"
            
            from services.formatters import message_formatter
            for item in income:
                time_str = ""
                if item.get('datetime'):
                    inc_time = datetime.fromisoformat(item['datetime'].replace('Z', '+00:00'))
                    time_str = f" ({inc_time.strftime('%H:%M')})"
                amount_formatted = message_formatter.format_currency(float(item.get('amount', 0)))
                message += f"• {amount_formatted} - {item['description']}{time_str}\n"
            
            message += f"\n💰 **Total del día: {message_formatter.format_currency(total)}**"
            
            return {
                "type": "daily_income",
                "message": message,
                "income": income,
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo ingresos diarios: {e}")
            return {"type": "error", "message": "❌ Error obteniendo ingresos"}
    
    async def handle_monthly_summary(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera resumen mensual detallado con análisis"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            month_start = now.replace(day=1, hour=0, minute=0, second=0)
            
            # Obtener todas las entries del mes
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", month_start.isoformat()
            ).order("datetime", desc=True).execute()
            
            entries = result.data
            
            if not entries:
                return {
                    "type": "monthly_summary_empty",
                    "message": "📊 No tienes actividad registrada este mes.\n\n💡 Comienza registrando gastos, tareas o eventos para ver tu resumen mensual."
                }
            
            # Analizar datos
            gastos = [e for e in entries if e['type'] == 'gasto']
            ingresos = [e for e in entries if e['type'] == 'ingreso']
            tareas = [e for e in entries if e['type'] == 'tarea']
            
            total_gastos = sum(float(g.get('amount', 0)) for g in gastos)
            total_ingresos = sum(float(i.get('amount', 0)) for i in ingresos)
            balance = total_ingresos - total_gastos
            
            # Categorías de gastos
            gastos_por_categoria = {}
            for gasto in gastos:
                cat = gasto.get('category', 'Sin categoría')
                gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0) + float(gasto.get('amount', 0))
            
            # Encontrar mayor gasto
            mayor_gasto = max(gastos, key=lambda x: float(x.get('amount', 0))) if gastos else None
            
            from services.formatters import message_formatter
            message = f"📊 **Resumen de {now.strftime('%B %Y')}:**\n\n"
            message += f"💰 **Finanzas:**\n"
            message += f"• Ingresos: {message_formatter.format_currency(total_ingresos)}\n"
            message += f"• Gastos: {message_formatter.format_currency(total_gastos)}\n"
            balance_icon = "💚" if balance >= 0 else "🔴"
            message += f"• Balance: {balance_icon} {message_formatter.format_currency(balance)}\n\n"
            
            if gastos_por_categoria:
                message += f"📂 **Gastos por categoría:**\n"
                sorted_categories = sorted(gastos_por_categoria.items(), key=lambda x: x[1], reverse=True)
                for cat, amount in sorted_categories[:5]:  # Top 5
                    percentage = (amount / total_gastos) * 100 if total_gastos > 0 else 0
                    message += f"• {cat}: {message_formatter.format_currency(amount)} ({percentage:.1f}%)\n"
                message += "\n"
            
            if mayor_gasto:
                message += f"🎯 **Mayor gasto:** {message_formatter.format_currency(float(mayor_gasto.get('amount', 0)))} - {mayor_gasto['description']}\n\n"
            
            message += f"📈 **Actividad:**\n"
            message += f"• Total registros: {len(entries)}\n"
            message += f"• Tareas completadas: {len([t for t in tareas if t['status'] == 'completed'])}\n"
            message += f"• Tareas pendientes: {len([t for t in tareas if t['status'] == 'pending'])}\n"
            
            return {
                "type": "monthly_summary",
                "message": message,
                "data": {
                    "total_gastos": total_gastos,
                    "total_ingresos": total_ingresos,
                    "balance": balance,
                    "gastos_por_categoria": gastos_por_categoria,
                    "mayor_gasto": mayor_gasto
                }
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen mensual: {e}")
            return {"type": "error", "message": "❌ Error generando resumen"}
    
    async def handle_financial_tips(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Genera tips financieros personalizados usando contexto del usuario"""
        try:
            user_id = user_context["id"]
            profile = user_context.get("profile", {})
            
            # Obtener contexto financiero avanzado
            financial_context = await supabase.get_financial_context_summary(user_id)
            spending_patterns = await supabase.get_spending_patterns(user_id, 30)
            recent_insights = await supabase.get_recent_ai_insights(user_id, "financial_tip", 3)
            
            # Preparar prompt mejorado para Gemini con contexto avanzado
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            # Obtener insights previos para evitar repetir
            previous_tips = [insight['content'] for insight in recent_insights]
            
            enhanced_prompt = f"""
            Genera 3-4 tips financieros personalizados, específicos y accionables para este usuario.
            
            PERFIL DEL USUARIO:
            - Ocupación: {profile.get('occupation', 'No especificada')}
            - Hobbies: {', '.join(profile.get('hobbies', [])) or 'No especificados'}
            - Contexto personal: {profile.get('context_summary', 'No disponible')}
            
            ANÁLISIS FINANCIERO DETALLADO:
            - Balance mensual: ₡{financial_context.get('monthly_summary', {}).get('total_ingresos', 0) - financial_context.get('monthly_summary', {}).get('total_gastos', 0):,.0f}
            - Promedio gasto diario: ₡{spending_patterns.get('average_per_day', 0):,.0f}
            - Tendencia de gasto: {"Aumentando" if financial_context.get('spending_trends', {}).get('is_increasing') else "Estable/Decreciendo"} ({financial_context.get('spending_trends', {}).get('trend_percentage', 0):.1f}%)
            
            PATRONES DE COMPORTAMIENTO:
            - Categorías principales: {list(spending_patterns.get('by_category', {}).keys())[:3]}
            - Días de mayor gasto: {list(spending_patterns.get('by_day_of_week', {}).keys())[:2]}
            - Gastos más grandes recientes: {[f"₡{float(e.get('amount', 0)):,.0f} - {e.get('description', '')}" for e in spending_patterns.get('largest_expenses', [])[:3]]}
            
            TIPS PREVIOS (evita repetir):
            {previous_tips[:2] if previous_tips else "Ninguno"}
            
            INSTRUCCIONES:
            1. Genera tips específicos basados en sus patrones reales
            2. Incluye montos específicos cuando sea relevante  
            3. Considera su ocupación y estilo de vida
            4. Sugiere acciones concretas y medibles
            5. No repitas consejos ya dados
            6. Enfócate en las categorías donde más gasta
            
            Formato: Consejos directos con emojis, números específicos y acciones claras.
            """
            
            # Llamar a Gemini
            response = gemini_service.model.generate_content(enhanced_prompt)
            tips_content = response.text.strip()
            
            # Almacenar el insight para referencia futura
            await supabase.store_ai_insight(
                user_id, 
                "financial_tip", 
                tips_content,
                {
                    "month": now.strftime('%B %Y'),
                    "balance": financial_context.get('monthly_summary', {}).get('total_ingresos', 0) - financial_context.get('monthly_summary', {}).get('total_gastos', 0),
                    "spending_trend": financial_context.get('spending_trends', {}).get('trend_percentage', 0),
                    "top_categories": list(spending_patterns.get('by_category', {}).keys())[:3]
                }
            )
            
            message = f"💡 **Tips financieros personalizados:**\n\n{tips_content}\n\n"
            message += f"📊 *Análisis basado en {len(spending_patterns.get('largest_expenses', []))} transacciones de {now.strftime('%B')}*\n"
            
            balance = financial_context.get('monthly_summary', {}).get('total_ingresos', 0) - financial_context.get('monthly_summary', {}).get('total_gastos', 0)
            balance_icon = "💚" if balance >= 0 else "🔴"
            message += f"💰 Balance actual: {balance_icon} ₡{balance:,.0f}"
            
            if financial_context.get('spending_trends', {}).get('is_increasing'):
                message += f"\n⚠️ Tendencia: Gastos aumentando {financial_context.get('spending_trends', {}).get('trend_percentage', 0):.1f}%"
            
            return {
                "type": "financial_tips",
                "message": message,
                "tips": tips_content,
                "context": financial_context,
                "patterns": spending_patterns
            }
            
        except Exception as e:
            logger.error(f"Error generando tips financieros: {e}")
            return {
                "type": "financial_tips_fallback",
                "message": "💡 **Tips financieros generales:**\n\n• 📊 Revisa tus gastos semanalmente\n• 🎯 Define un presupuesto mensual\n• 💳 Evita gastos impulsivos grandes\n• 💰 Separa un % para ahorro\n• 📱 Usa /gastos para monitorear tu día"
            }
    
    async def handle_spending_analysis(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis detallado de patrones de gasto"""
        try:
            user_id = user_context["id"]
            
            # Obtener análisis de patrones de gasto
            patterns = await supabase.get_spending_patterns(user_id, 30)
            financial_context = await supabase.get_financial_context_summary(user_id)
            
            if patterns.get('total_amount', 0) == 0:
                return {
                    "type": "spending_analysis_empty",
                    "message": "📊 No tienes suficiente actividad de gastos para generar un análisis.\n\n💡 Registra gastos durante unos días para ver patrones detallados."
                }
            
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            from services.formatters import message_formatter
            message = f"📈 **Análisis de gastos - Últimos 30 días:**\n\n"
            
            # Resumen general
            message += f"💰 **Resumen:**\n"
            message += f"• Total gastado: {message_formatter.format_currency(patterns['total_amount'])}\n"
            message += f"• Promedio diario: {message_formatter.format_currency(patterns['average_per_day'])}\n"
            message += f"• Número de transacciones: {len(patterns.get('largest_expenses', []))}\n"
            
            # Tendencia
            trend = financial_context.get('spending_trends', {})
            if trend.get('trend_percentage', 0) != 0:
                trend_icon = "📈" if trend.get('is_increasing') else "📉"
                message += f"• Tendencia: {trend_icon} {abs(trend.get('trend_percentage', 0)):.1f}% {'más' if trend.get('is_increasing') else 'menos'} que antes\n"
            
            message += "\n"
            
            # Análisis por categoría (top 5)
            if patterns.get('by_category'):
                message += f"📂 **Por categoría:**\n"
                sorted_cats = sorted(patterns['by_category'].items(), key=lambda x: x[1], reverse=True)
                for i, (cat, amount) in enumerate(sorted_cats[:5], 1):
                    percentage = (amount / patterns['total_amount']) * 100
                    message += f"{i}. {cat}: {message_formatter.format_currency(amount)} ({percentage:.1f}%)\n"
                message += "\n"
            
            # Análisis temporal
            if patterns.get('by_day_of_week'):
                message += f"📅 **Días con más gastos:**\n"
                day_counts = sorted(patterns['by_day_of_week'].items(), key=lambda x: x[1], reverse=True)
                for day, count in day_counts[:3]:
                    day_spanish = {
                        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
                    }.get(day, day)
                    message += f"• {day_spanish}: {count} transacciones\n"
                message += "\n"
            
            # Gastos más grandes
            if patterns.get('largest_expenses'):
                message += f"💸 **Gastos más grandes:**\n"
                for i, expense in enumerate(patterns['largest_expenses'][:3], 1):
                    date_obj = datetime.fromisoformat(expense['datetime'].replace('Z', '+00:00'))
                    amount_formatted = message_formatter.format_currency(float(expense.get('amount', 0)))
                    message += f"{i}. {amount_formatted} - {expense['description']} ({date_obj.strftime('%d/%m')})\n"
                message += "\n"
            
            # Insights automáticos
            message += f"💡 **Insights:**\n"
            
            # Categoría dominante
            if patterns.get('by_category'):
                top_cat, top_amount = max(patterns['by_category'].items(), key=lambda x: x[1])
                top_percentage = (top_amount / patterns['total_amount']) * 100
                if top_percentage > 40:
                    message += f"• ⚠️ {top_percentage:.0f}% de tus gastos son en '{top_cat}'\n"
                else:
                    message += f"• ✅ Gastos bien distribuidos entre categorías\n"
            
            # Patrón de días
            if patterns.get('by_day_of_week'):
                weekend_count = patterns['by_day_of_week'].get('Saturday', 0) + patterns['by_day_of_week'].get('Sunday', 0)
                weekday_count = sum(patterns['by_day_of_week'].values()) - weekend_count
                if weekend_count > weekday_count * 0.4:  # Weekend spending is high
                    message += f"• 🎉 Gastas más los fines de semana\n"
                else:
                    message += f"• 💼 Mayoría de gastos son días laborales\n"
            
            # Consejo rápido
            message += f"• 🎯 Usa /tips-finanzas para consejos personalizados"
            
            return {
                "type": "spending_analysis",
                "message": message,
                "patterns": patterns,
                "financial_context": financial_context
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de gastos: {e}")
            return {"type": "error", "message": "❌ Error generando análisis"}
    
    async def handle_greeting(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Saludo personalizado con resumen del usuario"""
        try:
            user_id = user_context["id"]
            name = user_context.get("name", "Usuario")
            profile = user_context.get("profile", {})
            
            # Obtener resumen rápido del día
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", today_start.isoformat()
            ).execute()
            
            today_entries = result.data
            
            # Calcular datos del día
            gastos_hoy = [e for e in today_entries if e['type'] == 'gasto']
            tareas_hoy = [e for e in today_entries if e['type'] == 'tarea']
            total_gastos_hoy = sum(float(g.get('amount', 0)) for g in gastos_hoy)
            tareas_pendientes = len([t for t in tareas_hoy if t['status'] == 'pending'])
            
            # Mensaje personalizado
            greeting_time = "Buenos días" if now.hour < 12 else "Buenas tardes" if now.hour < 18 else "Buenas noches"
            
            message = f"{greeting_time}, {name}! 👋\n\n"
            
            # Contexto personal si existe
            if profile.get('occupation'):
                message += f"💼 {profile['occupation']}\n"
            
            # Resumen del día
            from services.formatters import message_formatter
            message += f"📅 **Resumen de hoy:**\n"
            if total_gastos_hoy > 0:
                message += f"• 💸 Gastos: {message_formatter.format_currency(total_gastos_hoy)}\n"
            if tareas_pendientes > 0:
                message += f"• ⏳ Tareas pendientes: {tareas_pendientes}\n"
            if total_gastos_hoy == 0 and tareas_pendientes == 0:
                message += f"• ✨ Día tranquilo hasta ahora\n"
            
            message += f"\n🚀 **Comandos útiles:**\n"
            message += f"• `/tareas` - Ver tareas de hoy\n"
            message += f"• `/eventos` - Ver eventos de hoy\n"
            message += f"• `/gastos` - Ver gastos de hoy\n"
            message += f"• `/resumen-mes` - Resumen mensual\n"
            message += f"• `/help` - Ver todos los comandos\n"
            
            message += f"\n💬 O simplemente dime qué gastaste, qué tienes que hacer, o envía una foto de un recibo!"
            
            return {
                "type": "greeting",
                "message": message,
                "today_summary": {
                    "gastos": total_gastos_hoy,
                    "tareas_pendientes": tareas_pendientes
                }
            }
            
        except Exception as e:
            logger.error(f"Error en saludo: {e}")
            return {
                "type": "greeting_simple",
                "message": f"¡Hola! 👋\n\n💬 Dime qué gastaste, qué tienes que hacer, o usa `/help` para ver comandos disponibles."
            }
    
    async def handle_reminder_help(self) -> Dict[str, Any]:
        """Ayuda sobre recordatorios"""
        message = """🔔 **Recordatorios en Korei:**

📝 **Crear recordatorios:**
• "Recordarme llamar al médico mañana a las 2pm"
• "Reunión con cliente el viernes 10am"
• "Pagar factura de luz el 15 de enero"

⏰ **Formatos de tiempo:**
• Hoy/mañana + hora: "mañana 3pm"
• Fecha específica: "15 enero 2pm"
• Días de semana: "viernes 9am"

🔔 **Tipos de recordatorios:**
• 📋 Tareas con fecha límite
• 📅 Eventos programados
• ⏰ Recordatorios simples

💡 **Tip:** Entre más específico seas con el tiempo, mejor funcionará el recordatorio!"""

        return {
            "type": "reminder_help",
            "message": message
        }
    
    async def handle_connect_integration(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Conecta integraciones externas"""
        try:
            from services.integrations.integration_manager import integration_manager
            from app.config import settings
            
            user_id = user_context["id"]
            content = message.replace("/conectar", "").replace("/connect", "").strip().lower()
            
            if not content:
                return {
                    "type": "connect_help",
                    "message": """🔗 **Conectar integraciones:**

📅 **Google Calendar:**
• `/conectar google-calendar` - Conectar calendario

✅ **Todoist:**
• `/conectar todoist [tu-api-token]` - Conectar tareas
• Obtén tu token en: https://todoist.com/prefs/integrations

📱 **Microsoft To-Do:** (Próximamente)
• `/conectar microsoft-todo`

💡 **Ejemplo:**
`/conectar todoist 1234567890abcdef`

🔍 Usa `/integraciones` para ver las conectadas."""
                }
            
            # Conectar Google Calendar
            if "google" in content or "calendar" in content:
                # Generar URL de OAuth
                base_url = getattr(settings, 'base_url', 'https://tu-dominio.com/')
                oauth_url = f"{base_url}/api/oauth/google_calendar/start?user_id={user_id}"
                
                return {
                    "type": "oauth_required",
                    "message": f"""📅 **Conectar Google Calendar:**

🔗 Haz clic en este enlace para conectar:
{oauth_url}

⚠️ **Importante:**
• Solo funciona en navegador web
• Te pedirá permisos de Google
• Una vez conectado, podrás crear eventos desde WhatsApp

📱 Después podrás usar comandos como:
• "Reunión con cliente mañana 3pm" → Se crea automáticamente en tu calendario"""
                }
            
            # Conectar Todoist
            elif "todoist" in content:
                parts = content.split()
                if len(parts) < 2:
                    return {
                        "type": "todoist_token_required",
                        "message": """✅ **Conectar Todoist:**

🔑 Necesito tu token de API:
`/conectar todoist TU_TOKEN_AQUI`

📋 **Cómo obtener tu token:**
1. Ve a https://todoist.com/prefs/integrations
2. Copia tu "Token de API"
3. Úsalo con el comando

📝 **Ejemplo:**
`/conectar todoist 1234567890abcdef1234567890abcdef12345678`

🔒 Tu token se almacena de forma segura."""
                    }
                
                api_token = parts[1]
                
                # Intentar conectar
                success = await integration_manager.register_user_integration(
                    user_id=user_id,
                    service="todoist",
                    credentials={"api_token": api_token},
                    config={"auto_sync": True}
                )
                
                if success:
                    return {
                        "type": "integration_connected",
                        "message": """✅ **Todoist conectado exitosamente!**

🎉 Ya puedes:
• Crear tareas desde WhatsApp
• Sincronizar automáticamente  
• Ver tareas con `/tareas`

📝 **Ejemplos:**
• "Comprar leche mañana" → Se crea en Todoist
• "Llamar doctor viernes 2pm prioridad alta"

🔄 Usa `/sincronizar` para importar tareas existentes."""
                    }
                else:
                    return {
                        "type": "integration_failed",
                        "message": """❌ **Error conectando Todoist**

🔍 **Posibles causas:**
• Token de API inválido
• Sin conexión a internet
• Token expirado

💡 **Solución:**
1. Verifica tu token en https://todoist.com/prefs/integrations
2. Intenta de nuevo con `/conectar todoist TU_TOKEN`"""
                    }
            
            else:
                return {
                    "type": "integration_not_found",
                    "message": f"❌ Integración '{content}' no disponible.\n\nUsa `/conectar` para ver opciones disponibles."
                }
                
        except Exception as e:
            logger.error(f"Error connecting integration: {e}")
            return {
                "type": "error",
                "message": "❌ Error conectando integración. Intenta de nuevo."
            }
    
    async def handle_list_integrations(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Lista integraciones conectadas del usuario"""
        try:
            from services.integrations.integration_manager import integration_manager
            
            user_id = user_context["id"]
            integrations = await integration_manager.get_user_integrations(user_id)
            
            if not integrations:
                return {
                    "type": "no_integrations",
                    "message": """📱 **No tienes integraciones conectadas**

🔗 **Disponibles:**
• Google Calendar - `/conectar google-calendar`
• Todoist - `/conectar todoist [token]`

💡 Las integraciones te permiten:
• 📅 Crear eventos en tu calendario
• ✅ Sincronizar tareas automáticamente
• 📊 Importar datos existentes

🚀 ¡Conecta una para comenzar!"""
                }
            
            message = "🔗 **Tus integraciones conectadas:**\n\n"
            
            for integration in integrations:
                status = integration.get_integration_status()
                service_name = status['service'].replace('_', ' ').title()
                
                # Iconos por servicio
                icon = {
                    'Google Calendar': '📅',
                    'Todoist': '✅',
                    'Microsoft Todo': '📝'
                }.get(service_name, '🔧')
                
                connection_status = "✅ Conectado" if status['is_connected'] else "❌ Desconectado"
                last_sync = status['last_sync']
                
                message += f"{icon} **{service_name}**\n"
                message += f"• Estado: {connection_status}\n"
                if last_sync:
                    sync_date = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    message += f"• Última sincronización: {sync_date.strftime('%d/%m %H:%M')}\n"
                message += "\n"
            
            message += "🔄 **Comandos útiles:**\n"
            message += "• `/sincronizar` - Sincronizar datos\n"
            message += "• `/conectar` - Conectar más integraciones"
            
            return {
                "type": "integrations_list",
                "message": message,
                "integrations": [i.get_integration_status() for i in integrations]
            }
            
        except Exception as e:
            logger.error(f"Error listing integrations: {e}")
            return {
                "type": "error",
                "message": "❌ Error obteniendo integraciones"
            }
    
    async def handle_sync_integrations(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Sincroniza datos con integraciones"""
        try:
            from services.integrations.integration_manager import integration_manager
            
            user_id = user_context["id"]
            
            # Verificar que tiene integraciones
            integrations = await integration_manager.get_user_integrations(user_id)
            if not integrations:
                return {
                    "type": "no_integrations_to_sync",
                    "message": "❌ No tienes integraciones conectadas para sincronizar.\n\nUsa `/conectar` para agregar integraciones."
                }
            
            # Realizar sincronización
            results = await integration_manager.sync_user_data(user_id, direction="both")
            
            success_count = len(results['success'])
            failed_count = len(results['failed'])
            imported_count = len(results['imported_items'])
            exported_count = len(results['exported_items'])
            
            message = "🔄 **Sincronización completada:**\n\n"
            
            if success_count > 0:
                message += f"✅ **Servicios sincronizados:** {success_count}\n"
                for service in results['success']:
                    service_name = service.replace('Integration', '').replace('_', ' ')
                    message += f"• {service_name}\n"
                message += "\n"
            
            if imported_count > 0:
                message += f"📥 **Importados:** {imported_count} elementos\n"
                for item in results['imported_items'][:3]:  # Mostrar solo primeros 3
                    service = item['service'].replace('Integration', '')
                    message += f"• {service}: {item['item'][:50]}...\n"
                if imported_count > 3:
                    message += f"• ... y {imported_count - 3} más\n"
                message += "\n"
            
            if exported_count > 0:
                message += f"📤 **Exportados:** {exported_count} elementos\n"
                for item in results['exported_items'][:3]:
                    service = item['service'].replace('Integration', '')
                    message += f"• {service}: {item['entry'][:50]}...\n"
                if exported_count > 3:
                    message += f"• ... y {exported_count - 3} más\n"
                message += "\n"
            
            if failed_count > 0:
                message += f"❌ **Errores:** {failed_count} servicios\n"
                for failure in results['failed']:
                    message += f"• {failure['service']}: {failure['error'][:50]}...\n"
                message += "\n"
            
            if imported_count == 0 and exported_count == 0:
                message += "ℹ️ No hay datos nuevos para sincronizar.\n\n"
            
            message += "💡 La sincronización automática ocurre cada vez que creas tareas o eventos."
            
            return {
                "type": "sync_completed",
                "message": message,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error syncing integrations: {e}")
            return {
                "type": "error", 
                "message": "❌ Error sincronizando. Intenta de nuevo en unos minutos."
            }
    
    async def handle_daily_events(self, user_context: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Muestra eventos del día especificado"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "hoy"
            elif period == "tomorrow":
                tomorrow = now + timedelta(days=1)
                start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "mañana"
            
            # Obtener eventos del período
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "evento"
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            events = result.data
            
            if not events:
                return {
                    "type": "daily_events_empty",
                    "message": f"📅 No tienes eventos programados para {period_text}.\n\n💡 Puedes agregar eventos diciendo algo como:\n'Cita médica mañana a las 2pm'"
                }
            
            # Agrupar por estado si es necesario
            pending_events = [e for e in events if e['status'] == 'pending']
            completed_events = [e for e in events if e['status'] == 'completed']
            
            message = f"📅 **Eventos para {period_text}:**\n\n"
            
            if pending_events:
                message += "⏳ **Próximos:**\n"
                for event in pending_events:
                    time_str = ""
                    if event.get('datetime'):
                        event_time = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                        time_str = f" a las {event_time.strftime('%H:%M')}"
                    
                    duration_str = ""
                    if event.get('datetime_end'):
                        end_time = datetime.fromisoformat(event['datetime_end'].replace('Z', '+00:00'))
                        event_start = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                        duration = end_time - event_start
                        if duration.total_seconds() > 0:
                            hours = int(duration.total_seconds() // 3600)
                            minutes = int((duration.total_seconds() % 3600) // 60)
                            if hours > 0:
                                duration_str = f" ({hours}h"
                                if minutes > 0:
                                    duration_str += f" {minutes}m"
                                duration_str += ")"
                            elif minutes > 0:
                                duration_str = f" ({minutes}m)"
                    
                    message += f"• {event['description']}{time_str}{duration_str}\n"
                message += "\n"
            
            if completed_events:
                message += "✅ **Completados:**\n"
                for event in completed_events:
                    time_str = ""
                    if event.get('datetime'):
                        event_time = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                        time_str = f" ({event_time.strftime('%H:%M')})"
                    message += f"• {event['description']}{time_str}\n"
                message += "\n"
            
            message += f"💡 Total: {len(events)} evento(s)"
            
            return {
                "type": "daily_events",
                "message": message.strip(),
                "events": events
            }
            
        except Exception as e:
            logger.error(f"Error manejando eventos diarios: {e}")
            return {
                "type": "error",
                "message": "❌ Error obteniendo eventos. Intenta de nuevo."
            }
    
    async def handle_projects_list(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra la lista de proyectos disponibles en Todoist"""
        try:
            user_id = user_context["id"]
            
            # Obtener integración de Todoist
            from services.integrations.integration_manager import integration_manager
            todoist_integration = await integration_manager.get_user_integration(user_id, 'todoist')
            
            if not todoist_integration:
                return {
                    "type": "projects_not_connected",
                    "message": "📂 **Proyectos de Todoist**\n\n❌ No tienes Todoist conectado.\n\n🔗 Usa `/conectar todoist` para conectar tu cuenta."
                }
            
            # Obtener proyectos
            projects = await todoist_integration.get_projects()
            
            if not projects:
                return {
                    "type": "projects_empty",
                    "message": "📂 **Proyectos de Todoist**\n\n📭 No se encontraron proyectos.\n\n💡 Crea proyectos en Todoist primero."
                }
            
            # Formatear lista de proyectos
            message = "📂 **Tus Proyectos en Todoist:**\n\n"
            
            for i, project in enumerate(projects, 1):
                name = project.get('name', 'Sin nombre')
                project_id = project.get('id', '')
                color = project.get('color', '')
                
                # Agregar emoji basado en el nombre del proyecto
                emoji = self._get_project_emoji(name)
                
                message += f"{emoji} **{name}**\n"
                message += f"   ID: `{project_id}`\n"
                if color:
                    message += f"   Color: {color}\n"
                message += "\n"
            
            message += f"📊 **Total:** {len(projects)} proyectos\n\n"
            message += "💡 **¿Cómo funciona?**\n"
            message += "• Al crear tareas, Korei las asigna automáticamente al proyecto más relevante\n"
            message += "• Usa `/test-proyectos [tu tarea]` para probar la asignación"
            
            return {
                "type": "projects_list",
                "message": message,
                "projects": projects
            }
            
        except Exception as e:
            logger.error(f"Error listando proyectos: {e}")
            return {
                "type": "error",
                "message": "❌ Error obteniendo proyectos. Intenta de nuevo."
            }
    
    async def handle_test_project_selection(self, user_context: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Prueba la selección automática de proyecto para una tarea"""
        try:
            user_id = user_context["id"]
            
            # Extraer la tarea del mensaje
            parts = message.split(maxsplit=1)
            if len(parts) < 2:
                return {
                    "type": "test_projects_help",
                    "message": "🧪 **Test de Asignación de Proyectos**\n\n📝 **Uso:**\n`/test-proyectos [tu tarea]`\n\n**Ejemplo:**\n`/test-proyectos comprar leche mañana`\n`/test-proyectos reunión con el equipo`"
                }
            
            task_text = parts[1]
            
            # Obtener integración de Todoist
            from services.integrations.integration_manager import integration_manager
            todoist_integration = await integration_manager.get_user_integration(user_id, 'todoist')
            
            if not todoist_integration:
                return {
                    "type": "test_projects_not_connected",
                    "message": "❌ No tienes Todoist conectado.\n\n🔗 Usa `/conectar todoist` para conectar tu cuenta."
                }
            
            # Obtener proyectos y seleccionar el óptimo
            projects = await todoist_integration.get_projects()
            
            if not projects:
                return {
                    "type": "test_projects_empty",
                    "message": "📭 No tienes proyectos en Todoist."
                }
            
            # Usar la función de selección inteligente
            from services.integrations.todoist_integration import select_optimal_project
            optimal_project = select_optimal_project(projects, user_context, task_text)
            
            # Formatear respuesta
            message_response = f"🧪 **Test de Asignación de Proyecto**\n\n"
            message_response += f"📝 **Tarea:** {task_text}\n\n"
            
            if optimal_project:
                project_name = optimal_project.get('name', 'Sin nombre')
                project_emoji = self._get_project_emoji(project_name)
                
                message_response += f"🎯 **Proyecto Seleccionado:**\n"
                message_response += f"{project_emoji} **{project_name}**\n"
                message_response += f"🆔 ID: `{optimal_project.get('id', '')}`\n\n"
                
                # Mostrar alternativas
                message_response += "📋 **Otros proyectos disponibles:**\n"
                for project in projects[:5]:  # Máximo 5 proyectos
                    if project.get('id') != optimal_project.get('id'):
                        name = project.get('name', 'Sin nombre')
                        emoji = self._get_project_emoji(name)
                        message_response += f"• {emoji} {name}\n"
                
                if len(projects) > 5:
                    message_response += f"• ... y {len(projects) - 5} más\n"
                
            else:
                message_response += "❌ No se pudo seleccionar un proyecto óptimo."
            
            message_response += f"\n💡 Usa `/proyectos` para ver todos tus proyectos."
            
            return {
                "type": "test_projects_result",
                "message": message_response,
                "selected_project": optimal_project,
                "task_text": task_text
            }
            
        except Exception as e:
            logger.error(f"Error en test de proyectos: {e}")
            return {
                "type": "error",
                "message": "❌ Error en test de proyectos. Intenta de nuevo."
            }
    
    def _get_project_emoji(self, project_name: str) -> str:
        """Obtiene un emoji apropiado para el proyecto basado en su nombre"""
        name_lower = project_name.lower()
        
        # Mapeo de palabras clave a emojis
        emoji_map = {
            'trabajo': '💼', 'work': '💼', 'oficina': '🏢', 'office': '🏢',
            'personal': '👤', 'privado': '🔒', 'private': '🔒',
            'casa': '🏠', 'home': '🏠', 'hogar': '🏡',
            'compras': '🛒', 'shopping': '🛒', 'mercado': '🛒',
            'finanzas': '💰', 'finance': '💰', 'dinero': '💸', 'money': '💸',
            'salud': '⚕️', 'health': '⚕️', 'medico': '🩺', 'doctor': '🩺',
            'estudio': '📚', 'study': '📚', 'educacion': '🎓', 'education': '🎓',
            'proyecto': '📋', 'project': '📋', 'desarrollo': '⚙️', 'dev': '⚙️',
            'viaje': '✈️', 'travel': '✈️', 'vacaciones': '🏖️', 'vacation': '🏖️',
            'gym': '💪', 'ejercicio': '🏃', 'fitness': '🏋️',
            'cocina': '👨‍🍳', 'cooking': '👨‍🍳', 'recetas': '📝',
            'arte': '🎨', 'art': '🎨', 'musica': '🎵', 'music': '🎵'
        }
        
        # Buscar coincidencias
        for keyword, emoji in emoji_map.items():
            if keyword in name_lower:
                return emoji
        
        # Emojis por defecto según patrones comunes
        if any(word in name_lower for word in ['inbox', 'general', 'misc', 'varios']):
            return '📥'
        elif 'urgente' in name_lower or 'importante' in name_lower:
            return '🚨'
        else:
            return '📂'  # Emoji por defecto

    async def handle_today_summary(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Resumen completo del día actual - tareas, eventos, gastos"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener todas las entries del día
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            entries = result.data
            
            if not entries:
                return {
                    "type": "today_empty",
                    "message": f"📅 **Hoy {now.strftime('%d de %B')}** - Sin actividad registrada\n\n💡 **Comandos útiles:**\n• Dime qué gastaste: 'Gasté 5000 en almuerzo'\n• Crea tareas: 'Llamar al doctor a las 3pm'\n• Ver ayuda completa: `/help`",
                    "buttons": []
                }
            
            # Separar por tipos
            tareas = [e for e in entries if e['type'] == 'tarea']
            eventos = [e for e in entries if e['type'] == 'evento']
            gastos = [e for e in entries if e['type'] == 'gasto']
            ingresos = [e for e in entries if e['type'] == 'ingreso']
            
            # Construir mensaje
            from services.formatters import message_formatter
            message = f"📅 **Resumen de Hoy - {now.strftime('%d de %B')}**\n\n"
            
            # TAREAS - Solo mostrar pendientes prominentemente
            tareas_pendientes = [t for t in tareas if t['status'] == 'pending']
            tareas_completadas = [t for t in tareas if t['status'] == 'completed']
            
            if tareas_pendientes:
                message += f"📋 **TAREAS PENDIENTES ({len(tareas_pendientes)}):**\n"
                for tarea in tareas_pendientes:  # Mostrar todas las pendientes
                    time_str = ""
                    if tarea.get('datetime'):
                        task_time = datetime.fromisoformat(tarea['datetime'].replace('Z', '+00:00'))
                        time_str = f" ({task_time.strftime('%H:%M')})"
                    priority_icon = "🔴" if tarea.get('priority') == 'alta' else "🟡" if tarea.get('priority') == 'media' else "🟢"
                    message += f"• {priority_icon} {tarea['description']}{time_str}\n"
                message += "\n"
            elif tareas_completadas:
                message += f"✅ **¡Todas las tareas del día completadas!** ({len(tareas_completadas)})\n"
                # Mostrar solo las primeras 3 completadas como resumen
                for tarea in tareas_completadas[:3]:
                    message += f"• ✓ {tarea['description']}\n"
                if len(tareas_completadas) > 3:
                    message += f"• ... y {len(tareas_completadas) - 3} más\n"
                message += "\n"
            
            # EVENTOS
            if eventos:
                message += f"📅 **EVENTOS ({len(eventos)}):**\n"
                for evento in eventos[:5]:  # Máximo 5
                    time_str = ""
                    if evento.get('datetime'):
                        event_time = datetime.fromisoformat(evento['datetime'].replace('Z', '+00:00'))
                        time_str = f" a las {event_time.strftime('%H:%M')}"
                    status_icon = "✅" if evento['status'] == 'completed' else "⏰"
                    message += f"• {status_icon} {evento['description']}{time_str}\n"
                
                if len(eventos) > 5:
                    message += f"• ... y {len(eventos) - 5} más\n"
                message += "\n"
            
            # FINANZAS
            if gastos or ingresos:
                total_gastos = sum(float(g.get('amount', 0)) for g in gastos)
                total_ingresos = sum(float(i.get('amount', 0)) for i in ingresos)
                balance = total_ingresos - total_gastos
                
                message += f"💰 **FINANZAS:**\n"
                if total_gastos > 0:
                    message += f"• 💸 Gastos: {message_formatter.format_currency(total_gastos)}\n"
                if total_ingresos > 0:
                    message += f"• 💚 Ingresos: {message_formatter.format_currency(total_ingresos)}\n"
                
                balance_icon = "💚" if balance >= 0 else "🔴"
                message += f"• {balance_icon} Balance: {message_formatter.format_currency(balance)}\n\n"
            
            # BOTONES INTERACTIVOS para tareas pendientes
            # BOTONES DE ACCIÓN RÁPIDA INTELIGENTES
            buttons = []
            
            # Si hay tareas pendientes, agregar botones útiles
            if tareas_pendientes:
                message += "⚡ **Acciones disponibles:**\n"
                message += "• Gestiona todas tus tareas con botones\n"
                message += "• Ve tu agenda completa\n"
                message += "• Analiza tus finanzas del día\n"
                buttons.extend([
                    {"id": "action_tasks_buttons", "title": "📋 Tareas con Botones"},
                    {"id": "action_show_agenda", "title": "📅 Ver Agenda"},
                    {"id": "action_analyze_expenses", "title": "💸 Analizar Gastos"}
                ])
            else:
                # Si no hay tareas pendientes, ofrecer planificación
                message += "🎯 **¿Qué hacemos hoy?**\n"
                message += "• Planifica tu semana\n"
                message += "• Revisa tu progreso\n"
                message += "• Agrega nuevas metas\n"
                buttons.extend([
                    {"id": "action_show_agenda", "title": "📅 Planificar Semana"},
                    {"id": "action_show_stats", "title": "📊 Ver Mi Progreso"},
                    {"id": "action_quick_add", "title": "➕ Agregar Tarea"}
                ])
            
            message += "\n💡 **Comandos rápidos:** `/mañana` `/agenda` `/stats` `/tareas-botones`"
            
            return {
                "type": "today_summary",
                "message": message,
                "data": {
                    "tareas": len(tareas),
                    "tareas_pendientes": len([t for t in tareas if t['status'] == 'pending']),
                    "eventos": len(eventos),
                    "gastos": total_gastos if gastos else 0,
                    "balance": total_ingresos - total_gastos if gastos or ingresos else 0
                },
                "buttons": buttons,
                "has_pending_tasks": len(tareas_pendientes) > 0
            }
            
        except Exception as e:
            logger.error(f"Error en today summary: {e}")
            return {"type": "error", "message": "❌ Error obteniendo resumen del día"}

    async def handle_tomorrow_summary(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Resumen de tareas y eventos para mañana"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            tomorrow = now + timedelta(days=1)
            
            start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener entries de mañana
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            entries = result.data
            
            if not entries:
                return {
                    "type": "tomorrow_empty",
                    "message": f"📅 **Mañana {tomorrow.strftime('%d de %B')}** - Sin actividad programada\n\n💡 **Puedes agregar:**\n• 'Reunión con cliente mañana 3pm'\n• 'Recordarme llamar al doctor mañana'\n• 'Ir al gym mañana por la mañana'",
                    "buttons": []
                }
            
            # Separar por tipos
            tareas = [e for e in entries if e['type'] == 'tarea']
            eventos = [e for e in entries if e['type'] == 'evento']
            
            message = f"📅 **Mañana - {tomorrow.strftime('%d de %B, %A')}**\n\n"
            
            # TAREAS PARA MAÑANA
            if tareas:
                message += f"📋 **TAREAS ({len(tareas)}):**\n"
                for tarea in tareas:
                    time_str = ""
                    if tarea.get('datetime'):
                        task_time = datetime.fromisoformat(tarea['datetime'].replace('Z', '+00:00'))
                        time_str = f" ({task_time.strftime('%H:%M')})"
                    priority_icon = "🔴" if tarea.get('priority') == 'alta' else "🟡" if tarea.get('priority') == 'media' else "🟢"
                    message += f"• {priority_icon} {tarea['description']}{time_str}\n"
                message += "\n"
            
            # EVENTOS PARA MAÑANA
            if eventos:
                message += f"📅 **EVENTOS ({len(eventos)}):**\n"
                for evento in eventos:
                    time_str = ""
                    if evento.get('datetime'):
                        event_time = datetime.fromisoformat(evento['datetime'].replace('Z', '+00:00'))
                        time_str = f" a las {event_time.strftime('%H:%M')}"
                    message += f"• 📆 {evento['description']}{time_str}\n"
                message += "\n"
            
            message += "💡 **Tips:**\n"
            message += "• Usa `/today` para ver el día actual\n"
            message += "• Agrega más tareas diciendo 'Recordarme [algo] mañana'"
            
            return {
                "type": "tomorrow_summary",
                "message": message,
                "data": {
                    "tareas": len(tareas),
                    "eventos": len(eventos)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en tomorrow summary: {e}")
            return {"type": "error", "message": "❌ Error obteniendo resumen de mañana"}

    async def handle_complete_task(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Marca una tarea como completada en BD y Todoist"""
        try:
            user_id = user_context["id"]
            
            # Extraer descripción de la tarea del comando
            task_description = message.replace("/completar", "").replace("/complete", "").strip()
            
            if not task_description:
                return {
                    "type": "complete_task_help",
                    "message": "✅ **Completar Tarea:**\n\n📝 **Uso:**\n`/completar [descripción o parte de la tarea]`\n\n**Ejemplos:**\n• `/completar llamar doctor`\n• `/completar reunión equipo`\n• `/completar comprar`\n\n💡 Solo necesitas escribir parte del nombre de la tarea."
                }
            
            # Buscar tareas pendientes que coincidan
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            # Buscar en tareas de hoy y días anteriores
            past_date = now - timedelta(days=7)  # Últimos 7 días
            
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "tarea"
            ).eq(
                "status", "pending"
            ).gte(
                "datetime", past_date.isoformat()
            ).order("datetime", desc=True).execute()
            
            pending_tasks = result.data
            
            if not pending_tasks:
                return {
                    "type": "no_pending_tasks",
                    "message": "📋 No tienes tareas pendientes para completar.\n\n💡 Usa `/tareas` para ver todas tus tareas o `/today` para un resumen del día."
                }
            
            # Buscar coincidencias por descripción (búsqueda inteligente)
            task_lower = task_description.lower()
            matching_tasks = []
            
            for task in pending_tasks:
                task_desc_lower = task['description'].lower()
                # Coincidencia exacta o contiene la descripción
                if task_lower in task_desc_lower or task_desc_lower in task_lower:
                    matching_tasks.append(task)
                # Coincidencia por palabras clave
                elif any(word in task_desc_lower for word in task_lower.split() if len(word) > 2):
                    matching_tasks.append(task)
            
            if not matching_tasks:
                # Mostrar tareas disponibles
                message = f"❌ No encontré tareas que coincidan con '{task_description}'\n\n"
                message += "📋 **Tareas pendientes disponibles:**\n"
                for i, task in enumerate(pending_tasks[:5], 1):
                    task_date = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                    date_str = task_date.strftime('%d/%m')
                    message += f"{i}. {task['description']} ({date_str})\n"
                
                if len(pending_tasks) > 5:
                    message += f"... y {len(pending_tasks) - 5} más\n"
                
                message += "\n💡 Intenta con parte del nombre exacto de la tarea."
                
                return {
                    "type": "task_not_found",
                    "message": message,
                    "suggestions": pending_tasks[:5]
                }
            
            # Si hay múltiples coincidencias, mostrar opciones
            if len(matching_tasks) > 1:
                message = f"🔍 **Encontré {len(matching_tasks)} tareas similares:**\n\n"
                for i, task in enumerate(matching_tasks[:5], 1):
                    task_date = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                    date_str = task_date.strftime('%d/%m %H:%M')
                    message += f"{i}. {task['description']} ({date_str})\n"
                
                message += "\n💡 Sé más específico o usa `/completar [nombre exacto]`"
                
                return {
                    "type": "multiple_tasks_found",
                    "message": message,
                    "matches": matching_tasks[:5]
                }
            
            # Completar la tarea encontrada
            task_to_complete = matching_tasks[0]
            task_id = task_to_complete['id']
            
            logger.info(f"🎯 Completando tarea: {task_to_complete['description']} (ID: {task_id})")
            
            # Actualizar en base de datos
            updated_task = await supabase.update_entry_status(task_id, "completed")
            logger.info(f"✅ Tarea actualizada en BD: {updated_task}")
            
            # Intentar completar en Todoist si está conectado
            todoist_success = False
            todoist_message = ""
            
            try:
                from services.integrations.integration_manager import integration_manager
                todoist_integration = await integration_manager.get_user_integration(user_id, 'todoist')
                
                if todoist_integration and task_to_complete.get('external_id'):
                    # Completar en Todoist
                    todoist_result = await todoist_integration.complete_task(task_to_complete['external_id'])
                    if todoist_result:
                        todoist_success = True
                        todoist_message = "\n✅ También completada en Todoist"
                    else:
                        todoist_message = "\n⚠️ Completada localmente, pero no se pudo sincronizar con Todoist"
                elif todoist_integration:
                    todoist_message = "\n💡 Tarea no sincronizada con Todoist"
            except Exception as e:
                logger.warning(f"Error completando en Todoist: {e}")
                todoist_message = "\n⚠️ Error sincronizando con Todoist"
            
            # Mensaje de éxito
            task_date = datetime.fromisoformat(task_to_complete['datetime'].replace('Z', '+00:00'))
            completed_message = f"✅ **Tarea completada!**\n\n"
            completed_message += f"📋 **{task_to_complete['description']}**\n"
            completed_message += f"📅 Programada: {task_date.strftime('%d/%m %H:%M')}\n"
            completed_message += f"⏰ Completada: {now.strftime('%d/%m %H:%M')}"
            completed_message += todoist_message
            
            completed_message += f"\n\n🎉 ¡Buen trabajo! Usa `/today` para ver tu progreso del día."
            
            return {
                "type": "task_completed",
                "message": completed_message,
                "completed_task": task_to_complete,
                "todoist_synced": todoist_success
            }
            
        except Exception as e:
            logger.error(f"Error completando tarea: {e}")
            return {"type": "error", "message": "❌ Error completando tarea. Intenta de nuevo."}

    async def handle_agenda_view(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Vista de agenda semanal"""
        try:
            user_id = user_context["id"]
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            # Obtener semana actual (lunes a domingo)
            days_since_monday = now.weekday()
            monday = now - timedelta(days=days_since_monday)
            sunday = monday + timedelta(days=6)
            
            start_date = monday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener todas las entries de la semana
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).in_(
                "type", ["tarea", "evento"]
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            entries = result.data
            
            if not entries:
                return {
                    "type": "agenda_empty",
                    "message": f"📅 **Agenda Semanal** ({monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')})\n\n📭 No tienes actividades programadas esta semana.\n\n💡 Agrega tareas y eventos para organizar tu semana!"
                }
            
            # Organizar por días
            days_data = {}
            for i in range(7):
                day = monday + timedelta(days=i)
                day_key = day.strftime('%Y-%m-%d')
                days_data[day_key] = {
                    'day_name': day.strftime('%A'),
                    'day_date': day.strftime('%d/%m'),
                    'entries': []
                }
            
            # Clasificar entries por día
            for entry in entries:
                entry_date = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00'))
                day_key = entry_date.strftime('%Y-%m-%d')
                if day_key in days_data:
                    days_data[day_key]['entries'].append(entry)
            
            # Construir mensaje de agenda
            message = f"📅 **Agenda Semanal**\n{monday.strftime('%d/%m')} - {sunday.strftime('%d/%m')}\n\n"
            
            # Nombres de días en español
            day_names_spanish = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            
            current_day_key = now.strftime('%Y-%m-%d')
            
            for day_key in sorted(days_data.keys()):
                day_info = days_data[day_key]
                day_spanish = day_names_spanish.get(day_info['day_name'], day_info['day_name'])
                
                # Marcar día actual
                day_indicator = "📍" if day_key == current_day_key else "📅"
                
                message += f"{day_indicator} **{day_spanish} {day_info['day_date']}**"
                
                if day_key == current_day_key:
                    message += " *(HOY)*"
                elif day_key == (now + timedelta(days=1)).strftime('%Y-%m-%d'):
                    message += " *(MAÑANA)*"
                
                message += "\n"
                
                if day_info['entries']:
                    for entry in day_info['entries']:
                        entry_time = datetime.fromisoformat(entry['datetime'].replace('Z', '+00:00'))
                        time_str = entry_time.strftime('%H:%M')
                        
                        if entry['type'] == 'tarea':
                            status_icon = "✅" if entry['status'] == 'completed' else "⏳"
                            priority_icon = "🔴" if entry.get('priority') == 'alta' else "🟡" if entry.get('priority') == 'media' else "🟢"
                            message += f"  {status_icon} {time_str} - {entry['description']} {priority_icon}\n"
                        else:  # evento
                            status_icon = "✅" if entry['status'] == 'completed' else "📆"
                            message += f"  {status_icon} {time_str} - {entry['description']}\n"
                else:
                    message += "  *Sin actividades*\n"
                
                message += "\n"
            
            # Estadísticas de la semana
            tareas = [e for e in entries if e['type'] == 'tarea']
            eventos = [e for e in entries if e['type'] == 'evento']
            tareas_completadas = [t for t in tareas if t['status'] == 'completed']
            
            message += "📊 **Resumen semanal:**\n"
            message += f"• Tareas: {len(tareas)} ({len(tareas_completadas)} completadas)\n"
            message += f"• Eventos: {len(eventos)}\n"
            
            if len(tareas) > 0:
                completion_rate = (len(tareas_completadas) / len(tareas)) * 100
                message += f"• Progreso: {completion_rate:.0f}%\n"
            
            message += f"\n💡 Usa `/today` para ver detalles del día actual"
            
            return {
                "type": "agenda_view",
                "message": message,
                "week_data": days_data,
                "stats": {
                    "total_tasks": len(tareas),
                    "completed_tasks": len(tareas_completadas),
                    "total_events": len(eventos),
                    "completion_rate": (len(tareas_completadas) / len(tareas) * 100) if tareas else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error en agenda view: {e}")
            return {"type": "error", "message": "❌ Error obteniendo agenda semanal"}

    async def handle_tasks_with_buttons(self, user_context: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Envía tareas pendientes con botones de WhatsApp en mensajes separados"""
        try:
            user_id = user_context["id"]
            whatsapp_number = user_context.get("whatsapp_number", "")
            
            # Verificar si específica el período (hoy/mañana/semana)
            period = "today"  # Default
            if "mañana" in message.lower() or "tomorrow" in message.lower():
                period = "tomorrow"
            elif "semana" in message.lower() or "week" in message.lower():
                period = "week"
            
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            if period == "today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "hoy"
            elif period == "tomorrow":
                tomorrow = now + timedelta(days=1)
                start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "mañana"
            else:  # week
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = (now + timedelta(days=7)).replace(hour=23, minute=59, second=59, microsecond=999999)
                period_text = "esta semana"
            
            # Obtener tareas pendientes del período
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).eq(
                "type", "tarea"
            ).eq(
                "status", "pending"
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).order("datetime").execute()
            
            pending_tasks = result.data
            
            # Ordenar tareas por prioridad e importancia
            pending_tasks = self._sort_tasks_by_priority(pending_tasks)
            
            if not pending_tasks:
                if period == "today":
                    empty_message = f"🎉 **¡Increíble!** No tienes tareas pendientes para hoy.\n\n✨ Tienes el día libre o ya terminaste todo. ¡Qué productivo!\n\n💡 **¿Quieres planificar algo?** Solo dime:\n• 'Recordarme llamar al doctor mañana 3pm'\n• 'Comprar ingredientes para la cena'\n• 'Reunión importante el viernes'"
                elif period == "tomorrow":
                    empty_message = f"🌅 **Mañana está despejado!** No tienes tareas programadas.\n\n🎯 Perfecto momento para planificar. Prueba decir:\n• 'Llamada importante mañana a las 10am'\n• 'Ir al gym mañana por la tarde'\n• 'Revisar emails mañana temprano'"
                else:
                    empty_message = f"📅 **Esta semana se ve tranquila** - no hay tareas pendientes.\n\n🚀 ¡Excelente oportunidad para planificar! Dime algo como:\n• 'Reunión con el equipo el miércoles'\n• 'Terminar proyecto para el viernes'\n• 'Cita médica el jueves 2pm'"
                
                return {
                    "type": "tasks_buttons_empty",
                    "message": empty_message
                }
            
            # Usar WhatsApp Cloud Service para enviar tareas con botones
            from services.whatsapp_cloud import whatsapp_cloud_service
            
            logger.info(f"📤 Enviando {len(pending_tasks)} tareas con botones a {whatsapp_number}")
            
            # Enviar tareas individualmente con botones
            send_results = await whatsapp_cloud_service.send_multiple_tasks(
                to=whatsapp_number,
                tasks=pending_tasks,
                send_individually=True
            )
            
            # Contar éxitos y errores
            successful_sends = len([r for r in send_results if r.get('success', False)])
            failed_sends = len(send_results) - successful_sends
            
            # Mensaje de respuesta al comando
            response_message = f"📱 **Tareas enviadas con botones de WhatsApp:**\n\n"
            response_message += f"✅ Enviadas: {successful_sends}/{len(pending_tasks)} tareas para {period_text}\n"
            
            if failed_sends > 0:
                response_message += f"❌ Errores: {failed_sends} tareas\n"
            
            response_message += f"\n🎯 **Cada tarea incluye botones para:**\n"
            response_message += f"• ✅ Completar la tarea\n"
            response_message += f"• 🗑️ Eliminar la tarea\n"
            response_message += f"• ℹ️ Ver más información\n"
            
            response_message += f"\n💡 ¡Haz clic directamente en los botones para gestionar tus tareas!"
            
            return {
                "type": "tasks_buttons_sent",
                "message": response_message,
                "sent_count": successful_sends,
                "failed_count": failed_sends,
                "tasks": pending_tasks,
                "send_results": send_results
            }
            
        except Exception as e:
            logger.error(f"Error enviando tareas con botones: {e}")
            return {
                "type": "error",
                "message": "❌ Error enviando tareas con botones. Intenta de nuevo."
            }

    async def handle_delete_task(self, task_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Elimina una tarea específica"""
        try:
            user_id = user_context["id"]
            
            # Verificar que la tarea existe y pertenece al usuario
            task = await supabase.get_entry_by_id(task_id)
            if not task:
                return {
                    "type": "task_not_found",
                    "message": "❌ Tarea no encontrada."
                }
            
            if task.get('user_id') != user_id:
                return {
                    "type": "task_not_authorized",
                    "message": "❌ No tienes permisos para eliminar esta tarea."
                }
            
            # Eliminar de la base de datos
            delete_result = supabase._get_client().table("entries").delete().eq(
                "id", task_id
            ).execute()
            
            if delete_result.data:
                # Intentar eliminar de Todoist si está conectado
                todoist_message = ""
                try:
                    from services.integrations.integration_manager import integration_manager
                    todoist_integration = await integration_manager.get_user_integration(user_id, 'todoist')
                    
                    if todoist_integration and task.get('external_id'):
                        await todoist_integration.delete_task(task['external_id'])
                        todoist_message = "\n✅ También eliminada de Todoist"
                except Exception as e:
                    logger.warning(f"Error eliminando de Todoist: {e}")
                    todoist_message = "\n⚠️ No se pudo eliminar de Todoist"
                
                return {
                    "type": "task_deleted",
                    "message": f"🗑️ **Tarea eliminada**\n\n📋 {task['description']}\n\n✅ Eliminada de la base de datos{todoist_message}",
                    "deleted_task": task
                }
            else:
                return {
                    "type": "delete_failed",
                    "message": "❌ No se pudo eliminar la tarea. Intenta de nuevo."
                }
                
        except Exception as e:
            logger.error(f"Error eliminando tarea {task_id}: {e}")
            return {
                "type": "error",
                "message": "❌ Error eliminando tarea."
            }

    async def handle_greeting(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Saludo personalizado con resumen rápido del día"""
        try:
            # Obtener nombre del usuario o usar un saludo genérico
            user_name = user_context.get("name", "")
            if user_name:
                greeting_start = f"¡Hola {user_name}! 👋"
            else:
                greeting_start = "¡Hola! 👋 Soy Korei, tu asistente personal"
            
            # Obtener hora actual para saludo contextual
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            hour = now.hour
            
            if 5 <= hour < 12:
                time_greeting = "¡Buenos días! ☀️"
            elif 12 <= hour < 18:
                time_greeting = "¡Buenas tardes! 🌤️"
            else:
                time_greeting = "¡Buenas noches! 🌙"
            
            # Obtener resumen rápido del día
            user_id = user_context["id"]
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Obtener estadísticas del día
            result = supabase._get_client().table("entries").select("*").eq(
                "user_id", user_id
            ).gte(
                "datetime", start_date.isoformat()
            ).lte(
                "datetime", end_date.isoformat()
            ).execute()
            
            entries_today = result.data
            pending_tasks = [e for e in entries_today if e['type'] == 'tarea' and e['status'] == 'pending']
            completed_tasks = [e for e in entries_today if e['type'] == 'tarea' and e['status'] == 'completed']
            
            # Construir mensaje personalizado
            message = f"{greeting_start}\n{time_greeting}\n\n"
            
            # Resumen del día
            if not entries_today:
                message += "📅 **Tu día está empezando** - no hay nada registrado aún.\n\n"
                message += "✨ ¡Perfecto momento para planificar! Dime qué tienes en mente."
            else:
                message += "📋 **Resumen de hoy:**\n"
                
                if pending_tasks:
                    message += f"• {len(pending_tasks)} tarea{'s' if len(pending_tasks) != 1 else ''} pendiente{'s' if len(pending_tasks) != 1 else ''} ⏳\n"
                
                if completed_tasks:
                    message += f"• {len(completed_tasks)} tarea{'s' if len(completed_tasks) != 1 else ''} completada{'s' if len(completed_tasks) != 1 else ''} ✅\n"
                
                # Calcular gastos del día
                expenses_today = [e for e in entries_today if e['type'] == 'gasto']
                if expenses_today:
                    total_expenses = sum(float(e.get('amount', 0)) for e in expenses_today)
                    from services.formatters import message_formatter
                    message += f"• Gastos del día: {message_formatter.format_currency(total_expenses)} 💸\n"
                
                message += "\n"
                
                # Mensaje motivacional basado en el progreso
                if completed_tasks and not pending_tasks:
                    message += "🎉 **¡Excelente!** Has completado todas tus tareas de hoy. ¡Qué productivo!"
                elif completed_tasks and pending_tasks:
                    message += f"💪 **¡Vas súper bien!** Has completado {len(completed_tasks)} tareas. Te quedan {len(pending_tasks)} por hacer."
                elif pending_tasks and not completed_tasks:
                    message += f"🎯 **¡Es hora de la acción!** Tienes {len(pending_tasks)} tarea{'s' if len(pending_tasks) != 1 else ''} esperándote."
            
            # Agregar acciones rápidas
            message += "\n\n🚀 **¿En qué te ayudo?**\n"
            message += "• `/hoy` - Resumen completo\n"
            message += "• `/tareas-botones` - Gestionar tareas\n"
            message += "• `/stats` - Ver tu progreso\n"
            message += "• `/help` - Ver todos los comandos\n"
            message += "\n💬 O simplemente háblame natural sobre lo que necesitas."
            
            return {
                "type": "greeting",
                "message": message,
                "data": {
                    "pending_tasks": len(pending_tasks),
                    "completed_tasks": len(completed_tasks),
                    "total_entries": len(entries_today)
                }
            }
            
        except Exception as e:
            logger.error(f"Error en saludo personalizado: {e}")
            return {
                "type": "greeting",
                "message": "¡Hola! 👋 Soy Korei, tu asistente personal.\n\n¿En qué te puedo ayudar hoy? Usa `/help` para ver todo lo que puedo hacer por ti. 😊"
            }

    def _sort_tasks_by_priority(self, tasks: list) -> list:
        """Ordena tareas por prioridad, tiempo y otros factores de importancia"""
        try:
            from datetime import datetime
            import pytz
            
            tz = pytz.timezone(settings.timezone)
            now = datetime.now(tz)
            
            def task_priority_score(task):
                """Calcula un score de prioridad para ordenar tareas"""
                score = 0
                
                # 1. Prioridad explícita (peso mayor)
                priority = task.get('priority', 'media')
                priority_scores = {'alta': 100, 'media': 50, 'baja': 20}
                score += priority_scores.get(priority, 50)
                
                # 2. Proximidad temporal (tareas más cercanas = mayor prioridad)
                if task.get('datetime'):
                    try:
                        task_time = datetime.fromisoformat(task['datetime'].replace('Z', '+00:00'))
                        task_time_local = task_time.astimezone(tz)
                        
                        # Si es hoy, agregar score basado en qué tan pronto es
                        if task_time_local.date() == now.date():
                            hours_until = (task_time_local - now).total_seconds() / 3600
                            if hours_until <= 2:  # Muy pronto
                                score += 80
                            elif hours_until <= 6:  # Pronto
                                score += 60
                            elif hours_until <= 12:  # Hoy pero más tarde
                                score += 40
                        
                        # Si ya pasó la hora, darle más prioridad (atrasada)
                        if task_time_local < now:
                            score += 90
                            
                    except:
                        pass
                
                # 3. Palabras clave urgentes en descripción
                description = task.get('description', '').lower()
                urgent_keywords = ['urgente', 'importante', 'crítico', 'emergencia', 'asap', 'ya', 'ahora']
                for keyword in urgent_keywords:
                    if keyword in description:
                        score += 30
                        break
                
                # 4. Tareas de trabajo/profesionales (heurística)
                work_keywords = ['reunión', 'meeting', 'call', 'llamada', 'cliente', 'proyecto', 'presentación', 'deadline']
                for keyword in work_keywords:
                    if keyword in description:
                        score += 25
                        break
                
                # 5. Tareas cortas (más fáciles de completar)
                if len(description) < 30:  # Descripción corta = tarea simple
                    score += 15
                
                return score
            
            # Ordenar por score descendente (mayor prioridad primero)
            sorted_tasks = sorted(tasks, key=task_priority_score, reverse=True)
            
            logger.info(f"🎯 Ordenadas {len(sorted_tasks)} tareas por prioridad")
            for i, task in enumerate(sorted_tasks[:3]):  # Log primeras 3
                score = task_priority_score(task)
                priority = task.get('priority', 'media')
                logger.info(f"  {i+1}. Score: {score}, Prioridad: {priority}, Desc: {task['description'][:30]}...")
            
            return sorted_tasks
            
        except Exception as e:
            logger.error(f"Error ordenando tareas por prioridad: {e}")
            # Fallback: retornar las tareas como están
            return tasks

    # =============================================================
    # ADHD SUPPORT METHODS - Dual Language (Neural & Natural)
    # =============================================================
    
    async def handle_adhd_command(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Comando principal ADHD - muestra opciones disponibles"""
        try:
            from services.adhd_support.language_formatter import ADHDLanguageFormatter
            formatter = ADHDLanguageFormatter(language_style)
            
            if language_style == "neural":
                help_message = """🧠 NEURAL_HACKING_SYSTEM v2.1 - ADHD Optimization Module

════════════════════════════════════════════
⚡ AVAILABLE_PROTOCOLS:

🔧 /neural-protocol [type] - Rutinas optimizadas
   • basica | completa
   
🎯 /neural-focus [span] - Gestión de atención  
   • corta | media | larga
   
⚡ /neural-boost [type] - Dopamine regulation
   • quick | sustained
   
🆘 /neural-recovery [crisis] - Emergency protocols
   • overwhelm | executive | general
   
📊 /neural-status - System analysis & metrics

════════════════════════════════════════════
💡 Neural optimization requires personalized data
⚙️ All protocols auto-adapt to your cognitive patterns"""
            else:
                help_message = """🌟 Soporte ADHD - Tu cerebro merece herramientas que funcionen

💝 **Comandos disponibles:**

🌅 `/adhd-rutina [tipo]` - Rutinas matutinas ADHD-friendly
   • basica - Para empezar suave
   • completa - Rutina más estructurada

🎯 `/adhd-atencion [duración]` - Planes de concentración
   • corta - Sesiones de 15 min
   • media - Sesiones de 25 min  
   • larga - Sesiones de 45 min

✨ `/adhd-dopamina [tipo]` - Boost de motivación
   • quick - Actividades rápidas (5 min)
   • sustained - Plan de regulación completo

🤗 `/adhd-crisis [tipo]` - Apoyo para días difíciles
   • overwhelm - Cuando todo se siente demasiado
   • executive - Cuando no puedes empezar
   • general - Plan de día difícil básico

🌈 **Recuerda:** No eres perezoso, tu cerebro simplemente funciona diferente"""
            
            return {
                "type": "adhd_help",
                "message": help_message,
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error en comando ADHD: {e}")
            return {"error": "Error procesando comando ADHD"}
    
    async def handle_adhd_routine(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Crea rutinas matutinas ADHD-optimizadas"""
        try:
            # Verificar acceso premium
            from services.premium_service import premium_service
            access_check = await premium_service.can_create_adhd_plan(user_context["id"], "routine")
            
            if not access_check['can_create']:
                return await self._handle_premium_required(access_check, language_style, "rutina")
            
            from services.adhd_support.adhd_plan_generator import ADHDPlanGenerator
            from services.adhd_support.context_analyzer import ADHDContextAnalyzer
            
            # Parsear parámetros
            parts = message.split()
            complexity = parts[1] if len(parts) > 1 else 'basica'
            
            # Analizar contexto del usuario
            analyzer = ADHDContextAnalyzer()
            user_context_analysis = await analyzer.analyze_adhd_patterns(user_context["id"])
            
            # Generar plan
            generator = ADHDPlanGenerator(language_style)
            plan = await generator.create_morning_routine(complexity, user_context_analysis)
            
            # Crear tareas en el sistema
            tasks_created = await self._create_adhd_plan_tasks(plan, user_context)
            
            # Formatear respuesta
            from services.adhd_support.language_formatter import ADHDLanguageFormatter
            formatter = ADHDLanguageFormatter(language_style)
            
            plan_data = {
                'name': plan['name'],
                'tasks_count': len(tasks_created),
                'duration_weeks': 4  # Rutinas por defecto 4 semanas
            }
            
            response_message = formatter.format_plan_created(plan_data)
            
            # Agregar información de acceso si está en trial
            if access_check['reason'] == 'trial_access':
                remaining = access_check.get('remaining', 0)
                if language_style == 'neural':
                    response_message += f"\n\n⚡ TRIAL_STATUS: {remaining} protocols remaining"
                else:
                    response_message += f"\n\n🎁 Trial: Te quedan {remaining} planes por crear"
            
            return {
                "type": "adhd_routine_created",
                "message": response_message,
                "plan_id": plan['id'],
                "tasks_created": len(tasks_created),
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error creando rutina ADHD: {e}")
            return {"error": "Error creando rutina ADHD"}
    
    async def handle_adhd_attention(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Crea planes de gestión de atención"""
        try:
            from services.adhd_support.adhd_plan_generator import ADHDPlanGenerator
            from services.adhd_support.context_analyzer import ADHDContextAnalyzer
            
            # Parsear parámetros
            parts = message.split()
            attention_span = parts[1] if len(parts) > 1 else 'media'
            
            # Analizar contexto del usuario
            analyzer = ADHDContextAnalyzer()
            user_context_analysis = await analyzer.analyze_adhd_patterns(user_context["id"])
            
            # Generar plan
            generator = ADHDPlanGenerator(language_style)
            plan = await generator.create_attention_management_plan(attention_span, user_context_analysis)
            
            # Crear tareas en el sistema
            tasks_created = await self._create_adhd_plan_tasks(plan, user_context)
            
            # Formatear respuesta
            from services.adhd_support.language_formatter import ADHDLanguageFormatter
            formatter = ADHDLanguageFormatter(language_style)
            
            plan_data = {
                'name': plan['name'],
                'tasks_count': len(tasks_created),
                'duration_weeks': 1  # Planes de atención por 1 semana
            }
            
            response_message = formatter.format_plan_created(plan_data)
            
            return {
                "type": "adhd_attention_created",
                "message": response_message,
                "plan_id": plan['id'],
                "tasks_created": len(tasks_created),
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error creando plan de atención: {e}")
            return {"error": "Error creando plan de atención"}
    
    async def handle_adhd_dopamine(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Crea planes de regulación de dopamina"""
        try:
            from services.adhd_support.adhd_plan_generator import ADHDPlanGenerator
            from services.adhd_support.context_analyzer import ADHDContextAnalyzer
            
            # Parsear parámetros
            parts = message.split()
            plan_type = parts[1] if len(parts) > 1 else 'quick'
            
            # Analizar contexto del usuario
            analyzer = ADHDContextAnalyzer()
            user_context_analysis = await analyzer.analyze_adhd_patterns(user_context["id"])
            
            # Generar plan
            generator = ADHDPlanGenerator(language_style)
            plan = await generator.create_dopamine_regulation_plan(plan_type, user_context_analysis)
            
            # Para boost rápido, crear tareas inmediatas
            if plan_type in ['quick', 'boost']:
                # Crear tareas inmediatas
                tasks_created = await self._create_adhd_plan_tasks(plan, user_context)
                
                # Formatear respuesta de boost
                from services.adhd_support.language_formatter import ADHDLanguageFormatter
                formatter = ADHDLanguageFormatter(language_style)
                
                boost_data = {
                    'activities_count': len(tasks_created),
                    'duration': 15  # 15 min total aprox
                }
                
                response_message = formatter.format_dopamine_boost(boost_data)
            else:
                # Plan de regulación sostenida
                tasks_created = await self._create_adhd_plan_tasks(plan, user_context)
                
                from services.adhd_support.language_formatter import ADHDLanguageFormatter
                formatter = ADHDLanguageFormatter(language_style)
                
                plan_data = {
                    'name': plan['name'],
                    'tasks_count': len(tasks_created),
                    'duration_weeks': 2  # Regulación sostenida
                }
                
                response_message = formatter.format_plan_created(plan_data)
            
            return {
                "type": "adhd_dopamine_created",
                "message": response_message,
                "plan_id": plan['id'],
                "tasks_created": len(tasks_created),
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error creando plan de dopamina: {e}")
            return {"error": "Error creando plan de dopamina"}
    
    async def handle_adhd_crisis(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Activa planes de crisis para días difíciles"""
        try:
            from services.adhd_support.adhd_plan_generator import ADHDPlanGenerator
            from services.adhd_support.context_analyzer import ADHDContextAnalyzer
            
            # Parsear tipo de crisis
            parts = message.split()
            crisis_type = parts[1] if len(parts) > 1 else 'general'
            
            # Analizar contexto del usuario
            analyzer = ADHDContextAnalyzer()
            user_context_analysis = await analyzer.analyze_adhd_patterns(user_context["id"])
            
            # Generar plan de crisis
            generator = ADHDPlanGenerator(language_style)
            plan = await generator.create_crisis_plan(crisis_type, user_context_analysis)
            
            # Crear tareas de emergencia (inmediatas)
            tasks_created = await self._create_adhd_plan_tasks(plan, user_context, is_crisis=True)
            
            # Formatear respuesta de crisis
            from services.adhd_support.language_formatter import ADHDLanguageFormatter
            formatter = ADHDLanguageFormatter(language_style)
            
            response_message = formatter.format_crisis_activated(crisis_type, len(tasks_created))
            
            return {
                "type": "adhd_crisis_activated",
                "message": response_message,
                "plan_id": plan['id'],
                "tasks_created": len(tasks_created),
                "crisis_type": crisis_type,
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error activando plan de crisis: {e}")
            return {"error": "Error activando plan de crisis"}
    
    async def handle_neural_status(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra análisis completo del sistema neural (solo estilo neural)"""
        try:
            from services.adhd_support.context_analyzer import ADHDContextAnalyzer
            from services.adhd_support.language_formatter import ADHDLanguageFormatter
            
            # Analizar patrones completos
            analyzer = ADHDContextAnalyzer()
            analysis = await analyzer.analyze_adhd_patterns(user_context["id"])
            
            # Formatear en estilo neural
            formatter = ADHDLanguageFormatter("neural")
            
            # Crear reporte detallado
            status_message = f"""🧠 NEURAL_SYSTEM_ANALYSIS - User ID: {user_context["id"][:8]}

════════════════════════════════════════════
📊 COGNITIVE_PERFORMANCE_METRICS:

🎯 Attention coherence: {analysis['attention_patterns']['average_focus_duration']:.1f} min avg
⚡ Energy fluctuations: {analysis['energy_cycles']['energy_consistency']*100:.0f}% consistency
🏆 Task completion rate: {analysis['completion_patterns']['overall_completion_rate']*100:.0f}%
🔥 Hyperfocus capability: {'DETECTED' if analysis['hyperfocus_indicators']['hyperfocus_capable'] else 'STANDARD'}

📈 OPTIMIZATION_RECOMMENDATIONS:
├─ Optimal session length: {analysis['recommendations']['optimal_task_duration']} min
├─ Peak performance hours: {', '.join(map(str, analysis['attention_patterns']['peak_attention_hours'][:3]))}:00
├─ Break frequency: {analysis['recommendations']['break_frequency']}
└─ Crisis support level: {analysis['recommendations']['crisis_support_level'].upper()}

🔄 SYSTEM_STATUS: {'OPTIMAL' if analysis['completion_patterns']['overall_completion_rate'] > 0.7 else 'NEEDS_CALIBRATION'}
📡 Data points analyzed: {analysis['data_points']}
⏱️ Last scan: {analysis['analysis_date'][:16]}

💡 Use protocols based on these metrics for maximum efficiency"""
            
            return {
                "type": "neural_status",
                "message": status_message,
                "analysis_data": analysis,
                "language_style": "neural"
            }
            
        except Exception as e:
            logger.error(f"Error en neural status: {e}")
            return {"error": "Error obteniendo estado neural"}
    
    async def _create_adhd_plan_tasks(self, plan: dict, user_context: Dict[str, Any], is_crisis: bool = False) -> List[dict]:
        """Crea tareas específicas para planes ADHD"""
        try:
            tasks_created = []
            
            for task in plan.get('tasks', []):
                # Crear tarea en formato estándar
                task_data = {
                    'type': 'tarea',
                    'description': task['title'],
                    'datetime': task['datetime'],
                    'priority': 'alta' if is_crisis else task.get('priority', 'media'),
                    'task_category': 'ADHD',
                    'user_id': user_context['id'],
                    'adhd_plan_id': plan['id'],
                    'status': 'pending',
                    'duration_minutes': task.get('duration_minutes', 5),
                    'adhd_specific': True,
                    'crisis_mode': is_crisis,
                    'language_style': plan.get('language_style', 'natural')
                }
                
                # Crear en BD usando el sistema existente
                try:
                    # Usar el servicio Gemini para crear con formato estándar
                    from core.supabase import supabase
                    entry = await supabase.create_entry(task_data)
                    
                    # Intentar crear en Todoist si hay integración
                    try:
                        from services.integrations.integration_manager import integration_manager
                        todoist_integration = await integration_manager.get_user_integration(user_context['id'], 'todoist')
                        
                        if todoist_integration:
                            # Convertir a formato Todoist
                            todoist_task_data = {
                                'type': 'tarea',
                                'description': task_data['description'],
                                'datetime': task_data['datetime'],
                                'priority': task_data['priority'],
                                'task_category': task_data['task_category']
                            }
                            
                            todoist_id = await todoist_integration.create_task(todoist_task_data)
                            if todoist_id:
                                # Actualizar entry con ID de Todoist
                                await supabase.update_entry_external_id(entry['id'], todoist_id, 'todoist')
                                
                    except Exception as todoist_error:
                        logger.warning(f"No se pudo crear tarea ADHD en Todoist: {todoist_error}")
                        # Continuar sin Todoist
                    
                    tasks_created.append(entry)
                    
                except Exception as task_error:
                    logger.error(f"Error creando tarea ADHD: {task_error}")
                    continue
            
            logger.info(f"✅ Creadas {len(tasks_created)} tareas ADHD para plan {plan['id']}")
            return tasks_created
            
        except Exception as e:
            logger.error(f"Error creando tareas de plan ADHD: {e}")
            return []
    
    # =============================================================
    # PREMIUM AND TUTORIAL METHODS
    # =============================================================
    
    async def handle_adhd_tutorial(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Maneja el tutorial interactivo ADHD"""
        try:
            from services.adhd_support.tutorial_service import tutorial_service
            return await tutorial_service.start_tutorial(user_context, language_style)
            
        except Exception as e:
            logger.error(f"Error en tutorial ADHD: {e}")
            return {"error": "Error iniciando tutorial"}
    
    async def handle_adhd_trial_activation(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Activa trial gratuito de ADHD"""
        try:
            from services.adhd_support.tutorial_service import tutorial_service
            return await tutorial_service.handle_trial_activation(user_context, language_style)
            
        except Exception as e:
            logger.error(f"Error activando trial ADHD: {e}")
            return {"error": "Error activando trial"}
    
    async def handle_adhd_plans(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Muestra planes premium disponibles"""
        try:
            from services.premium_service import premium_service
            
            plans = await premium_service.get_available_plans()
            status = await premium_service.get_premium_status(user_context["id"])
            
            if language_style == "neural":
                message = """🧠 NEURAL_PREMIUM_MATRIX - Pricing Protocol
                
════════════════════════════════════════════
💎 AVAILABLE_SUBSCRIPTION_TIERS:

🔬 ADHD_MONTHLY_v2.1:
├─ Price: $9.99/month
├─ Features: ALL_NEURAL_PROTOCOLS unlocked
├─ Crisis management: UNLIMITED
├─ Analytics: REAL_TIME monitoring
└─ Support: PRIORITY_QUEUE

⚡ ADHD_YEARLY_v2.1 [OPTIMIZED]:
├─ Price: $99.99/year (2 months FREE)
├─ Features: MONTHLY + advanced_analytics
├─ Bonus: Extended system optimization  
├─ ROI: 17% cost_reduction vs monthly
└─ Recommended: MAXIMUM_VALUE protocol

🎁 FREE_TRIAL_v1.0:
├─ Duration: 7 days FULL_ACCESS
├─ Features: ALL_SYSTEMS unlocked
├─ Limitation: None during trial period
└─ Auto-expires: No payment required

⚙️ UPGRADE_PROTOCOL:
• Contact support for payment processing
• Manual activation required
• System auto-upgrades upon confirmation

📊 CURRENT_STATUS:"""
                
                if status['premium_active']:
                    message += f"""
✅ Premium: ACTIVE
📅 Expires: {status.get('premium_expires_at', 'Never')[:10]}
⏰ Days remaining: {status.get('days_remaining', 'Unlimited')}"""
                elif status['trial_available']:
                    message += """
🎁 Trial: AVAILABLE
⚡ Activate with: /neural-trial"""
                else:
                    message += """
🔒 Status: FREE_TIER
💡 Upgrade available"""
            else:
                message = """🌟 Planes ADHD Premium - Invierte en tu bienestar

Tu cerebro ADHD merece herramientas profesionales.

💝 **Planes disponibles:**

🌅 **Plan Mensual - $9.99/mes**
• Rutinas ADHD ilimitadas  
• Gestión de crisis especializada
• Ambos estilos de lenguaje
• Análisis personalizado de patrones
• Soporte prioritario

⚡ **Plan Anual - $99.99/año (¡2 meses gratis!)**
• Todo del plan mensual
• Análisis avanzado de productividad
• Optimización continua de planes
• 17% de ahorro vs plan mensual
• **Más popular** 🏆

🎁 **Prueba Gratuita - 7 días**
• Acceso completo sin límites
• Todas las funciones desbloqueadas
• Sin compromisos ni cargos automáticos
• Cancela cuando quieras

💡 **¿Por qué premium?**
• Son herramientas especializadas, no genéricas
• Desarrolladas específicamente para ADHD
• Tu bienestar mental vale la inversión
• Mejora medible en productividad y bienestar

📊 **Tu estado actual:**"""
                
                if status['premium_active']:
                    message += f"""
✅ **Premium activo**
📅 Expira: {status.get('premium_expires_at', 'Nunca')[:10]}
⏰ Días restantes: {status.get('days_remaining', 'Ilimitado')}"""
                elif status['trial_available']:
                    message += """
🎁 **Trial disponible**
⚡ Activa con: `/adhd-trial`"""
                else:
                    message += """
🔒 **Plan gratuito**
💡 Upgrade disponible

**Para actualizar:** Contacta soporte o visita nuestra página de planes"""
            
            return {
                "type": "adhd_plans",
                "message": message,
                "plans": plans,
                "current_status": status,
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error mostrando planes ADHD: {e}")
            return {"error": "Error obteniendo planes"}
    
    async def handle_premium_status(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra estado premium del usuario"""
        try:
            from services.premium_service import premium_service
            
            status = await premium_service.get_premium_status(user_context["id"])
            
            # Determinar estilo de respuesta basado en preferencia
            language_style = status.get('adhd_language_preference', 'natural')
            
            if language_style == "neural":
                message = f"""🧠 PREMIUM_STATUS_REPORT - User {user_context["id"][:8]}
                
════════════════════════════════════════════
📊 CURRENT_SUBSCRIPTION_STATUS:

🔓 Access Level: {status['plan_type'].upper()}
✅ Premium Status: {'ACTIVE' if status['premium_active'] else 'INACTIVE'}
"""
                
                if status['premium_active']:
                    message += f"""📅 Expiration: {status.get('premium_expires_at', 'LIFETIME')[:10]}
⏰ Days Remaining: {status.get('days_remaining', 'UNLIMITED')}"""
                
                if status.get('trial_days_remaining'):
                    message += f"""
🎁 Trial Active: {status['trial_days_remaining']} days remaining"""
                elif status['trial_available']:
                    message += """
🎁 Trial Available: 7 days FREE_ACCESS"""
                
                message += f"""

📈 ADHD_USAGE_ANALYTICS:
├─ Plans Created: {status['adhd_stats']['total_adhd_plans']}
├─ Tasks Generated: {status['adhd_stats']['total_adhd_tasks']}
├─ Language Mode: {status['adhd_language_preference'].upper()}
└─ System Optimization: ACTIVE

⚡ Available Commands:
• /neural-plans - View upgrade options
• /neural-trial - Activate trial (if available)
• /neural - Access ADHD protocols"""
            else:
                message = f"""🌟 Tu estado premium - Resumen completo

💎 **Plan actual:** {status['plan_type'].title()}
✅ **Premium activo:** {'Sí' if status['premium_active'] else 'No'}
"""
                
                if status['premium_active']:
                    message += f"""📅 **Expira:** {status.get('premium_expires_at', 'Nunca')[:10]}
⏰ **Días restantes:** {status.get('days_remaining', 'Ilimitado')}"""
                
                if status.get('trial_days_remaining'):
                    message += f"""
🎁 **Trial activo:** {status['trial_days_remaining']} días restantes"""
                elif status['trial_available']:
                    message += """
🎁 **Trial disponible:** 7 días gratis"""
                
                message += f"""

📊 **Tu uso de funciones ADHD:**
• Planes creados: {status['adhd_stats']['total_adhd_plans']}
• Tareas generadas: {status['adhd_stats']['total_adhd_tasks']}  
• Estilo preferido: {status['adhd_language_preference'].title()}

🚀 **Comandos disponibles:**
• `/adhd-planes` - Ver opciones de upgrade
• `/adhd-trial` - Activar prueba (si disponible)
• `/adhd` - Acceder a herramientas ADHD"""
            
            return {
                "type": "premium_status",
                "message": message,
                "status": status,
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado premium: {e}")
            return {"error": "Error obteniendo estado premium"}
    
    async def _handle_premium_required(self, access_check: Dict[str, Any], language_style: str, feature_name: str) -> Dict[str, Any]:
        """Maneja cuando se requiere premium para una funcionalidad"""
        
        reason = access_check['reason']
        
        if reason == 'trial_available':
            if language_style == 'neural':
                message = f"""🔒 PREMIUM_PROTOCOL_REQUIRED - {feature_name.upper()}
                
════════════════════════════════════════════
⚠️ ACCESS_DENIED: Feature requires premium access

🎁 TRIAL_OPPORTUNITY_DETECTED:
├─ Duration: 7 days FULL_ACCESS
├─ Features: ALL_ADHD_PROTOCOLS unlocked  
├─ Activation: /neural-trial
└─ Cost: FREE (no payment required)

⚡ ALTERNATIVE_COMMANDS:
• /neural-trial - Activate trial
• /neural-plans - View subscription matrix
• /neural-help - System information"""
            else:
                message = f"""🌟 Funcionalidad Premium: {feature_name.title()}

Esta función está diseñada especialmente para usuarios premium.

🎁 **¡Buenas noticias!** Tienes disponible una prueba gratuita:

✨ **Trial de 7 días incluye:**
• Acceso completo a todas las funciones ADHD
• Ambos estilos de lenguaje  
• Rutinas, atención, dopamina y crisis ilimitadas
• Sin compromisos ni cargos automáticos

🚀 **Para activar:**
• `/adhd-trial` - Activar prueba gratis
• `/adhd-planes` - Ver planes disponibles
• `/adhd-help` - Más información"""
        
        elif reason == 'trial_limit_reached':
            remaining = access_check.get('remaining', 0)
            if language_style == 'neural':
                message = f"""⚠️ TRIAL_QUOTA_EXCEEDED - {feature_name.upper()}
                
════════════════════════════════════════════
🔒 Trial limit reached: Maximum protocols created

📊 USAGE_STATUS:
├─ Trial protocols used: 3/3
├─ Current access: BASIC_MODE only
├─ Upgrade required: PREMIUM_SUBSCRIPTION
└─ Recommendation: FULL_ACTIVATION

⚡ UPGRADE_PROTOCOLS:
• /neural-plans - View pricing matrix
• /neural-upgrade - Activate premium access
• Continue with basic features available"""
            else:
                message = f"""🎁 Límite de trial alcanzado

Has usado los 3 planes gratuitos de tu trial para {feature_name}.

💝 **¿Te gustó la experiencia?**

✨ **Con premium tienes:**
• Planes ADHD ilimitados
• Todas las funciones desbloqueadas
• Soporte especializado
• Inversión mínima en tu bienestar

🚀 **Siguiente paso:**
• `/adhd-planes` - Ver opciones de precio
• Puedes seguir usando las funciones básicas"""
        
        elif reason == 'premium_required':
            if language_style == 'neural':
                message = f"""🔒 PREMIUM_ACCESS_REQUIRED - {feature_name.upper()}
                
════════════════════════════════════════════
⚠️ SYSTEM_RESTRICTION: Advanced ADHD protocols locked

📊 ACCESS_STATUS:
├─ Trial period: USED
├─ Current tier: FREE_ACCESS
├─ Required tier: PREMIUM_SUBSCRIPTION
└─ Available features: BASIC_ONLY

⚡ UNLOCK_PROTOCOLS:
• /neural-plans - View subscription options
• Basic functionality remains available
• Full optimization requires premium key"""
            else:
                message = f"""🔒 Funcionalidad Premium: {feature_name.title()}

Esta función requiere plan premium.

💝 **Las herramientas ADHD especializadas están disponibles con premium:**

✨ **¿Por qué premium?**
• Herramientas desarrolladas específicamente para ADHD
• Investigación y desarrollo continuo
• Tu bienestar mental vale la inversión
• Mejora medible en productividad

🚀 **Opciones:**
• `/adhd-planes` - Ver precios y planes
• Continúa usando las funciones básicas disponibles"""
        
        return {
            "type": "premium_required",
            "message": message,
            "reason": reason,
            "language_style": language_style,
            "access_check": access_check
        }
    
    async def handle_upgrade_premium(self, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Maneja proceso de upgrade a premium"""
        try:
            from services.premium_service import premium_service
            
            # Verificar estado actual
            status = await premium_service.get_premium_status(user_context["id"])
            
            if status['premium_active']:
                if language_style == "neural":
                    message = """🧠 PREMIUM_STATUS: ALREADY_ACTIVE
                    
════════════════════════════════════════════
✅ System Status: PREMIUM_TIER activated

📅 Current subscription expires: {expires}
💡 No upgrade required - full access granted

⚙️ Available Commands:
• /neural-status - View system analytics
• /neural-plans - Manage subscription""".format(
                        expires=status.get('premium_expires_at', 'Never')[:10]
                    )
                else:
                    message = f"""✅ Ya tienes premium activo

Tu plan premium está funcionando perfectamente.

📅 **Expira:** {status.get('premium_expires_at', 'Nunca')[:10]}
⏰ **Días restantes:** {status.get('days_remaining', 'Ilimitado')}

🚀 **Comandos disponibles:**
• `/adhd-status` - Ver estado completo
• `/adhd-planes` - Gestionar suscripción"""
                
                return {
                    "type": "already_premium",
                    "message": message,
                    "status": status
                }
            
            # Usuario necesita upgrade - mostrar opciones
            if language_style == "neural":
                message = """🧠 PREMIUM_UPGRADE_PROTOCOL
                
════════════════════════════════════════════
🔓 UNLOCK_FULL_NEURAL_OPTIMIZATION

💎 UPGRADE_OPTIONS:

⚡ NEURAL_MONTHLY_v2.1:
├─ Price: $9.99/month
├─ Billing: Recurring subscription
├─ Features: ALL_ADHD_PROTOCOLS unlocked
└─ Activation: Immediate

🚀 NEURAL_YEARLY_v2.1 [OPTIMIZED]:
├─ Price: $99.99/year (17% savings)
├─ Billing: Annual subscription  
├─ Features: MONTHLY + bonus analytics
└─ Recommended: MAXIMUM_VALUE

⚙️ UPGRADE_PROTOCOLS:
• /neural-checkout monthly - Start monthly subscription
• /neural-checkout yearly - Start yearly subscription
• Manual payment options available

💡 All transactions secured with enterprise encryption"""
            else:
                message = """🌟 ¡Upgrade a Premium ADHD!

Lleva tu bienestar mental al siguiente nivel.

💝 **Opciones de upgrade:**

🌅 **Plan Mensual - $9.99/mes**
• Perfecto para probar a largo plazo
• Cancela cuando quieras
• Todas las funciones ADHD desbloqueadas

⚡ **Plan Anual - $99.99/año** (¡Recomendado!)
• Ahorra $19.89 al año (17% descuento)
• 2 meses gratis incluidos
• Análisis avanzado de patrones

🚀 **Para upgradar:**
• `/adhd-checkout monthly` - Suscripción mensual
• `/adhd-checkout yearly` - Suscripción anual  
• También aceptamos pagos manuales

💡 **¿Por qué vale la pena?**
Tu bienestar mental y productividad mejorarán significativamente con herramientas diseñadas específicamente para ADHD."""
            
            return {
                "type": "upgrade_options",
                "message": message,
                "language_style": language_style,
                "trial_used": status.get('trial_used', False)
            }
            
        except Exception as e:
            logger.error(f"Error en upgrade premium: {e}")
            return {"error": "Error procesando upgrade"}
    
    async def handle_create_checkout(self, message: str, user_context: Dict[str, Any], language_style: str) -> Dict[str, Any]:
        """Crea sesión de checkout para upgrade"""
        try:
            # Parsear plan seleccionado
            parts = message.split()
            plan_type = parts[1] if len(parts) > 1 else 'monthly'
            
            if plan_type not in ['monthly', 'yearly']:
                return {
                    "error": "Plan inválido. Usa: monthly o yearly"
                }
            
            plan_name = f'adhd_{plan_type}'
            
            # Crear checkout usando payment service
            from services.payment_service import payment_service
            
            # URLs de success y cancel (deberás configurar estas en tu app)
            success_url = os.getenv('APP_BASE_URL', 'https://tu-app.com') + '/payment/success'
            cancel_url = os.getenv('APP_BASE_URL', 'https://tu-app.com') + '/payment/cancel'
            
            checkout_result = await payment_service.create_checkout_session(
                user_id=user_context["id"],
                plan_name=plan_name,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if checkout_result.get('error'):
                return {"error": checkout_result['error']}
            
            # Formatear respuesta según estilo
            if language_style == "neural":
                if checkout_result.get('checkout_url'):
                    message = f"""🧠 CHECKOUT_SESSION_CREATED
                    
════════════════════════════════════════════
✅ Payment gateway: INITIALIZED
🔗 Secure checkout: READY

⚡ UPGRADE_LINK: 
{checkout_result['checkout_url']}

🛡️ SECURITY_PROTOCOL:
├─ Encryption: AES-256
├─ Provider: Stripe/PayPal
├─ Session ID: {checkout_result.get('session_id', 'N/A')[:16]}...
└─ Timeout: 30 minutes

💡 Complete payment to activate NEURAL_PREMIUM"""
                else:
                    # Pago manual
                    message = f"""🧠 MANUAL_PAYMENT_PROTOCOL
                    
════════════════════════════════════════════
💰 Amount: ${checkout_result['amount']} {checkout_result['currency']}
🔢 Reference: {checkout_result['reference_id']}

{checkout_result['instructions']}

⚡ ACTIVATION_TIME: 24-48 hours after payment verification"""
            else:
                if checkout_result.get('checkout_url'):
                    message = f"""✨ ¡Checkout listo para tu upgrade!

Haz clic en el enlace para completar tu pago seguro:

🔗 **Enlace de pago:** 
{checkout_result['checkout_url']}

🛡️ **Totalmente seguro:**
• Procesado por Stripe/PayPal
• Encriptación de nivel bancario
• Sin guardar datos de tarjeta

⏰ **Tienes 30 minutos** para completar el pago

💝 **Después del pago:** Tu premium se activa automáticamente"""
                else:
                    # Pago manual
                    message = f"""💝 Información para tu upgrade premium

{checkout_result['instructions']}

✅ **Después de pagar:** Tu premium se activará en 24-48 horas
📧 **Notificación:** Te avisaremos cuando esté listo"""
            
            return {
                "type": "checkout_created",
                "message": message,
                "checkout_data": checkout_result,
                "language_style": language_style
            }
            
        except Exception as e:
            logger.error(f"Error creando checkout: {e}")
            return {"error": "Error creando checkout"}
    
    # =============================================================
    # BASIC PLAN METHODS
    # =============================================================
    
    async def handle_basic_trial_activation(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Activa trial gratuito de 3 días para plan básico"""
        try:
            from services.premium_service import premium_service
            
            trial_result = await premium_service.activate_basic_trial(user_context["id"])
            
            if trial_result['success']:
                message = f"""🎉 ¡Trial básico activado!

Tienes 3 días para probar todas las funciones principales:

✨ **Ahora puedes usar:**
• Tareas ilimitadas (`/tareas`)
• Todas las integraciones (`/conectar todoist`)
• Estadísticas completas (`/stats`)
• Recordatorios avanzados
• Gestión de gastos y eventos

📅 **Tu trial expira:** {trial_result['expires_at'][:10]}
⏰ **Días restantes:** {trial_result['days_remaining']}

🚀 **Para aprovechar tu trial:**
• Prueba `/conectar todoist` para sincronizar tareas
• Usa `/stats` para ver análisis completos
• Crea todas las tareas que necesites

💡 **¿Te gusta?** Usa `/basic-upgrade` para continuar después del trial"""
                
                return {
                    'type': 'basic_trial_activated',
                    'message': message,
                    'trial_active': True,
                    'expires_at': trial_result['expires_at']
                }
            else:
                return {
                    'type': 'basic_trial_failed',
                    'message': trial_result['message'],
                    'reason': trial_result['reason']
                }
                
        except Exception as e:
            logger.error(f"Error activando trial básico: {e}")
            return {"error": "Error activando trial básico"}
    
    async def handle_basic_upgrade(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra opciones de upgrade al plan básico"""
        try:
            from services.premium_service import premium_service
            
            status = await premium_service.get_premium_status(user_context["id"])
            
            # Si ya tiene plan básico o superior
            if status.get('plan_type') in ['basic_monthly', 'basic_yearly', 'adhd_monthly', 'adhd_yearly']:
                if status.get('premium_active'):
                    # Tiene ADHD premium
                    message = """✅ Ya tienes ADHD Premium

Tu plan actual incluye todas las funciones básicas y ADHD.

🧠 **Tu plan ADHD Premium incluye:**
• Todo del plan básico
• + Herramientas ADHD especializadas
• + Ambos estilos de lenguaje
• + Gestión de crisis
• + Análisis de patrones cognitivos

🚀 **Comandos disponibles:**
• `/adhd-status` - Ver estado completo
• `/adhd` - Acceder a herramientas ADHD"""
                else:
                    # Tiene plan básico
                    message = f"""✅ Ya tienes el Plan Básico activo

📅 **Expira:** {status.get('premium_expires_at', 'Nunca')[:10]}
⏰ **Días restantes:** {status.get('days_remaining', 'Ilimitado')}

🚀 **¿Quieres más?** 
• `/adhd-upgrade` - Upgrade a ADHD Premium ($9.99/mes)
• Todas las funciones básicas + herramientas ADHD especializadas"""
                
                return {
                    "type": "already_have_basic_or_higher",
                    "message": message,
                    "current_plan": status.get('plan_type')
                }
            
            # Usuario necesita upgrade al plan básico
            message = """💼 Plan Básico - Todo lo que necesitas

Upgrade del plan gratuito limitado al servicio completo.

💝 **Plan Básico incluye:**

✅ **Funcionalidades principales:**
• Tareas ilimitadas (vs 5/mes en gratuito)
• Gestión completa de gastos e ingresos
• Eventos y recordatorios avanzados
• Estadísticas y análisis detallados

🔗 **Integraciones premium:**
• Todoist sincronización completa
• Google Calendar integración
• Más integraciones en camino

📊 **Analytics avanzados:**
• Reportes financieros mensuales
• Análisis de productividad
• Trends y patrones personalizados

💰 **Precios:**
• **Mensual:** $4.99/mes
• **Anual:** $49.99/año (¡2 meses gratis!)

🎁 **¿No estás seguro?**
• `/basic-trial` - 3 días gratis para probar

🚀 **Para upgradar:**
• `/basic-checkout monthly` - Plan mensual
• `/basic-checkout yearly` - Plan anual (recomendado)

💡 **¿Necesitas ADHD?** El Plan ADHD ($9.99/mes) incluye todo esto + herramientas especializadas"""
            
            return {
                "type": "basic_upgrade_options",
                "message": message,
                "trial_available": not status.get('basic_trial_used', False)
            }
            
        except Exception as e:
            logger.error(f"Error en basic upgrade: {e}")
            return {"error": "Error procesando upgrade básico"}
    
    async def handle_create_basic_checkout(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Crea checkout para plan básico"""
        try:
            # Parsear plan seleccionado
            parts = message.split()
            plan_type = parts[1] if len(parts) > 1 else 'monthly'
            
            if plan_type not in ['monthly', 'yearly']:
                return {
                    "error": "Plan inválido. Usa: monthly o yearly"
                }
            
            plan_name = f'basic_{plan_type}'
            
            # Crear checkout usando payment service
            from services.payment_service import payment_service
            
            success_url = os.getenv('APP_BASE_URL', 'https://tu-app.com') + '/payment/success'
            cancel_url = os.getenv('APP_BASE_URL', 'https://tu-app.com') + '/payment/cancel'
            
            checkout_result = await payment_service.create_checkout_session(
                user_id=user_context["id"],
                plan_name=plan_name,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            if checkout_result.get('error'):
                return {"error": checkout_result['error']}
            
            # Formatear respuesta
            if checkout_result.get('checkout_url'):
                message = f"""💼 ¡Checkout del Plan Básico listo!

Haz clic en el enlace para completar tu pago seguro:

🔗 **Enlace de pago:** 
{checkout_result['checkout_url']}

💰 **Plan seleccionado:** {'Mensual $4.99' if plan_type == 'monthly' else 'Anual $49.99 (2 meses gratis)'}

🛡️ **Totalmente seguro:**
• Procesado por Stripe/PayPal
• Encriptación de nivel bancario
• Cancela cuando quieras

⏰ **Tienes 30 minutos** para completar el pago

✅ **Después del pago:** 
• Acceso inmediato a todas las funciones
• Tareas y integraciones ilimitadas
• Soporte por email incluido"""
            else:
                # Pago manual
                message = f"""💼 Información para tu Plan Básico

{checkout_result['instructions']}

✅ **Después de pagar:** Tu plan básico se activará en 24-48 horas
📧 **Notificación:** Te avisaremos cuando esté listo
💼 **Acceso:** Todas las funciones principales desbloqueadas"""
            
            return {
                "type": "basic_checkout_created",
                "message": message,
                "checkout_data": checkout_result,
                "plan_type": plan_type
            }
            
        except Exception as e:
            logger.error(f"Error creando checkout básico: {e}")
            return {"error": "Error creando checkout básico"}
    
    async def handle_plan_status(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra estado completo del plan del usuario"""
        try:
            from services.premium_service import premium_service
            
            status = await premium_service.get_premium_status(user_context["id"])
            plan_type = status.get('plan_type', 'free')
            
            # Determinar qué plan tiene
            if plan_type == 'free' or plan_type is None:
                plan_name = "Plan Gratuito"
                plan_emoji = "🆓"
                features = ["Máximo 5 tareas/mes", "Comandos básicos", "Soporte limitado"]
                limitations = "Muchas limitaciones"
            elif plan_type in ['basic_monthly', 'basic_yearly']:
                plan_name = f"Plan Básico ({'Mensual' if 'monthly' in plan_type else 'Anual'})"
                plan_emoji = "💼"
                features = ["Tareas ilimitadas", "Todas las integraciones", "Estadísticas completas", "Soporte por email"]
                limitations = "Sin funciones ADHD"
            elif plan_type in ['adhd_monthly', 'adhd_yearly']:
                plan_name = f"ADHD Premium ({'Mensual' if 'monthly' in plan_type else 'Anual'})"
                plan_emoji = "🧠"
                features = ["Todo del plan básico", "Herramientas ADHD completas", "Ambos estilos de lenguaje", "Gestión de crisis", "Soporte prioritario"]
                limitations = "Sin limitaciones"
            elif 'trial' in plan_type:
                plan_name = f"Trial {'Básico' if 'basic' in plan_type else 'ADHD'}"
                plan_emoji = "🎁"
                features = ["Acceso temporal completo", "Todas las funciones desbloqueadas"]
                limitations = "Expira pronto"
            else:
                plan_name = "Plan Desconocido"
                plan_emoji = "❓"
                features = []
                limitations = "Estado no reconocido"
            
            # Información de expiración
            expires_info = ""
            if status.get('premium_expires_at'):
                expires_info = f"📅 **Expira:** {status['premium_expires_at'][:10]}\n⏰ **Días restantes:** {status.get('days_remaining', 'N/A')}\n"
            elif status.get('trial_expires_at'):
                expires_info = f"🎁 **Trial expira:** {status['trial_expires_at'][:10]}\n⏰ **Días restantes:** {status.get('trial_days_remaining', 'N/A')}\n"
            
            # Construir mensaje
            message = f"""{plan_emoji} **Tu Plan Actual: {plan_name}**

{expires_info}
✨ **Funciones incluidas:**
{chr(10).join(f'• {feature}' for feature in features)}

⚠️ **Limitaciones:** {limitations}

📊 **Tu uso:**
• Planes ADHD creados: {status['adhd_stats']['total_adhd_plans']}
• Tareas ADHD generadas: {status['adhd_stats']['total_adhd_tasks']}"""
            
            # Agregar opciones de upgrade según plan actual
            if plan_type == 'free':
                message += f"""

🚀 **Opciones de upgrade:**
• `/basic-trial` - 3 días de plan básico gratis
• `/basic-upgrade` - Plan básico ($4.99/mes)
• `/adhd-trial` - 7 días de ADHD premium gratis
• `/adhd-upgrade` - ADHD premium ($9.99/mes)"""
            elif plan_type in ['basic_monthly', 'basic_yearly']:
                message += f"""

🧠 **¿Quieres más?**
• `/adhd-upgrade` - Upgrade a ADHD Premium
• Todas tus funciones actuales + herramientas ADHD especializadas"""
            
            return {
                "type": "plan_status",
                "message": message,
                "plan_type": plan_type,
                "status": status
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del plan: {e}")
            return {"error": "Error obteniendo estado del plan"}

# Instancia singleton
command_handler = CommandHandler()