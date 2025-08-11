"""
Handler para comandos especiales como /register, /help, /stats
"""
from typing import Dict, Any
from loguru import logger
from core.supabase import supabase
from services.gemini import gemini_service

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
            else:
                return {"error": f"Comando no reconocido: {command}"}
                
        except Exception as e:
            logger.error(f"Error procesando comando {command}: {e}")
            return {"error": "Error procesando comando"}
    
    async def handle_register(self, message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa comando de registro
        Ejemplos:
        - "/register Soy desarrollador, me gusta la música y el gaming"
        - "/registro Trabajo como diseñador, hobbies: fotografía, cocinar"
        """
        try:
            # Usar Gemini para extraer información del mensaje
            registration_prompt = f"""
            El usuario quiere registrar su información personal. 
            Extrae y estructura la siguiente información del mensaje:
            
            MENSAJE: "{message}"
            
            Devuelve JSON con esta estructura:
            {{
                "occupation": "trabajo/profesión del usuario o null",
                "hobbies": ["array", "de", "hobbies"],
                "context_summary": "resumen breve de quién es la persona",
                "extracted": true
            }}
            
            Si no hay información suficiente, devuelve {{"extracted": false, "reason": "motivo"}}
            """
            
            # Llamar a Gemini para extraer información
            extracted_info = await gemini_service.model.generate_content(registration_prompt)
            
            # Parsear respuesta
            import json
            try:
                info = json.loads(extracted_info.text.strip())
            except:
                # Fallback manual
                info = {
                    "occupation": None,
                    "hobbies": [],
                    "context_summary": message.replace("/register", "").replace("/registro", "").strip(),
                    "extracted": False
                }
            
            if not info.get("extracted", False):
                return {
                    "type": "registration_help",
                    "message": "Para registrarte, cuéntame un poco sobre ti. Por ejemplo:\n\n'Soy desarrollador, me gusta la música y los videojuegos'\n\nPuedes incluir tu trabajo, hobbies, y cualquier información que me ayude a conocerte mejor."
                }
            
            # Guardar perfil en base de datos
            profile_data = {
                "occupation": info.get("occupation"),
                "hobbies": info.get("hobbies", []),
                "context_summary": info.get("context_summary"),
                "preferences": {}
            }
            
            await supabase.create_user_profile(user_context["id"], profile_data)
            
            return {
                "type": "registration_success",
                "message": f"¡Perfecto! Ya te conozco mejor.\n\n=Ë **Tu perfil:**\n- Trabajo: {info.get('occupation', 'No especificado')}\n- Hobbies: {', '.join(info.get('hobbies', []))}\n\nAhora puedo darte sugerencias más personalizadas <¯",
                "profile": profile_data
            }
            
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            return {
                "type": "error", 
                "message": "L Error procesando tu registro. Intenta de nuevo."
            }
    
    async def handle_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Muestra el perfil actual del usuario"""
        try:
            profile = user_context.get("profile", {})
            
            if not profile or not profile.get("occupation"):
                return {
                    "type": "profile_empty",
                    "message": "=« No tienes un perfil registrado.\n\nUsa `/register` seguido de información sobre ti para comenzar.\n\nEjemplo: `/register Soy diseñador, me gusta el café y leer`"
                }
            
            occupation = profile.get("occupation", "No especificado")
            hobbies = profile.get("hobbies", [])
            context = profile.get("context_summary", "")
            
            profile_text = f"=d **Tu perfil:**\n\n"
            profile_text += f"<â **Ocupación:** {occupation}\n"
            
            if hobbies:
                profile_text += f"<¯ **Hobbies:** {', '.join(hobbies)}\n"
            
            if context:
                profile_text += f"=Ý **Contexto:** {context}\n"
            
            profile_text += f"\n=¡ Para actualizar usa `/register` con nueva información"
            
            return {
                "type": "profile_display",
                "message": profile_text,
                "profile": profile
            }
            
        except Exception as e:
            logger.error(f"Error mostrando perfil: {e}")
            return {"type": "error", "message": "L Error obteniendo perfil"}
    
    async def handle_help(self) -> Dict[str, Any]:
        """Muestra ayuda de comandos"""
        help_text = """> **Comandos de Korei:**

=Ý **Registro:**
" `/register [info]` - Registra tu información personal
" `/profile` - Ver tu perfil actual

=Ê **Estadísticas:**  
" `/stats` - Ver resumen de gastos y tareas

=¡ **Uso normal:**
" Envía mensajes como: "Gasté 50 mil en almuerzo"
" Audio con gastos o tareas
" Fotos de recibos para registrar automáticamente

<¯ Entre más me conozcas, mejores sugerencias te daré!"""

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
                    "message": "=Ê No tienes estadísticas aún.\n\nComienza enviando gastos, tareas o eventos para ver tu resumen."
                }
            
            stats_text = f"""=Ê **Tus estadísticas este mes:**

=° **Finanzas:**
" Gastos: ¡{stats.get('gastos', 0):,.0f}
" Ingresos: ¡{stats.get('ingresos', 0):,.0f}
" Balance: ¡{stats.get('balance', 0):,.0f}

=Ý **Actividad:**
" Total entradas: {stats.get('total_entries', 0)}
" Tareas pendientes: {stats.get('pending_tasks', 0)}

=È **Por tipo:**"""

            by_type = stats.get('by_type', {})
            for entry_type, count in by_type.items():
                stats_text += f"\n" {entry_type.title()}: {count}"
            
            return {
                "type": "stats",
                "message": stats_text,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {"type": "error", "message": "L Error obteniendo estadísticas"}

# Instancia singleton
command_handler = CommandHandler()