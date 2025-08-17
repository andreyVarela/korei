"""
Integración con Todoist
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from loguru import logger

from .base_integration import TaskIntegration


class TodoistIntegration(TaskIntegration):
    """Integración con Todoist"""
    
    BASE_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self, user_id: str, credentials: Dict[str, Any]):
        super().__init__(user_id, credentials)
        self.api_token = credentials.get('api_token')
        self.default_project_id = credentials.get('default_project_id')
        self.session = None
        self._projects_cache = None
        self._cache_timestamp = None
        self._cache_duration = 300  # 5 minutos
    
    async def get_projects(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Obtiene la lista de proyectos del usuario en Todoist con cache"""
        try:
            import time
            
            # Verificar si tenemos cache válido
            if (not force_refresh and 
                self._projects_cache is not None and 
                self._cache_timestamp is not None and 
                time.time() - self._cache_timestamp < self._cache_duration):
                logger.info(f"📦 Usando cache de proyectos ({len(self._projects_cache)} proyectos)")
                return self._projects_cache
            
            # Obtener proyectos frescos de la API
            logger.info("🔄 Obteniendo proyectos de Todoist...")
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}/projects") as response:
                if response.status == 200:
                    projects = await response.json()
                    
                    # Actualizar cache
                    self._projects_cache = projects
                    self._cache_timestamp = time.time()
                    
                    logger.info(f"📁 {len(projects)} proyectos obtenidos de Todoist")
                    
                    # Log de proyectos para debugging
                    for project in projects:
                        logger.info(f"  📂 {project.get('name')} (ID: {project.get('id')})")
                    
                    return projects
                else:
                    logger.error(f"Error obteniendo proyectos de Todoist: {response.status}")
                    return self._projects_cache or []
        except Exception as e:
            logger.error(f"Error en get_projects: {e}")
            return self._projects_cache or []
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene sesión HTTP con headers de autenticación"""
        if not self.session:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def authenticate(self) -> bool:
        """Autentica usando API token de Todoist"""
        try:
            if not self.api_token:
                logger.error(f"No Todoist API token for user {self.user_id}")
                return False
            
            # Probar token obteniendo proyectos
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}/projects") as response:
                if response.status == 200:
                    projects = await response.json()
                    self.is_connected = True
                    logger.info(f"Todoist authenticated for user {self.user_id}, {len(projects)} projects")
                    return True
                else:
                    logger.error(f"Todoist authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error authenticating Todoist for user {self.user_id}: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Prueba la conexión obteniendo tareas"""
        try:
            session = await self._get_session()
            async with session.get(f"{self.BASE_URL}/tasks") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Todoist connection test failed: {e}")
            return False
    
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Crea una tarea en Todoist"""
        try:
            if not self.is_connected:
                await self.authenticate()
            # Convertir datos de Korei a formato Todoist
            todoist_task = self._korei_to_todoist_task(task_data)
            
            # Debug logging para verificar el proyecto
            logger.info(f"TODOIST-CREATE: Creando tarea en proyecto {todoist_task.get('project_id', 'SIN PROYECTO')}")
            logger.info(f"TODOIST-CREATE: Datos de tarea: {todoist_task}")
            
            session = await self._get_session()
            async with session.post(f"{self.BASE_URL}/tasks", json=todoist_task) as response:
                if response.status in [200, 201]:
                    task = await response.json()
                    task_id = task.get('id')
                    logger.info(f"Created Todoist task: {task_id}")
                    return str(task_id) if task_id else None
                else:
                    error_text = await response.text()
                    logger.error(f"Error creating Todoist task: {response.status} - {error_text}")
                    raise Exception(f"Todoist API error: {response.status}")
        except Exception as e:
            logger.error(f"Error creating Todoist task: {e}")
            raise
    
    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Actualiza una tarea existente"""
        try:
            if not self.is_connected:
                await self.authenticate()
            
            todoist_task = self._korei_to_todoist_task(task_data)
            
            session = await self._get_session()
            async with session.post(f"{self.BASE_URL}/tasks/{task_id}", json=todoist_task) as response:
                if response.status == 200:
                    logger.info(f"Updated Todoist task: {task_id}")
                    return True
                else:
                    logger.error(f"Error updating Todoist task {task_id}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating Todoist task {task_id}: {e}")
            return False
    
    async def complete_task(self, task_id: str) -> bool:
        """Marca una tarea como completada"""
        try:
            if not self.is_connected:
                await self.authenticate()
            
            session = await self._get_session()
            async with session.post(f"{self.BASE_URL}/tasks/{task_id}/close") as response:
                if response.status == 204:
                    logger.info(f"Completed Todoist task: {task_id}")
                    return True
                else:
                    logger.error(f"Error completing Todoist task {task_id}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error completing Todoist task {task_id}: {e}")
            return False
    
    async def get_tasks(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene tareas de Todoist"""
        try:
            if not self.is_connected:
                await self.authenticate()
            
            # Construir URL con filtros
            url = f"{self.BASE_URL}/tasks"
            params = {}
            if project_id:
                params['project_id'] = project_id
            
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    tasks = await response.json()
                    
                    # Convertir a formato Korei
                    korei_tasks = []
                    for task in tasks:
                        korei_task = self._todoist_to_korei_task(task)
                        korei_tasks.append(korei_task)
                    
                    return korei_tasks
                else:
                    logger.error(f"Error getting Todoist tasks: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting Todoist tasks: {e}")
            return []
    
    async def sync_to_external(self, data: Dict[str, Any]) -> bool:
        """Sincroniza tarea de Korei a Todoist"""
        try:
            if data.get('type') == 'tarea':
                task_id = await self.create_task(data)
                return bool(task_id)
            return False
            
        except Exception as e:
            logger.error(f"Error syncing to Todoist: {e}")
            return False
    
    async def sync_from_external(self) -> List[Dict[str, Any]]:
        """Importa tareas desde Todoist"""
        try:
            tasks = await self.get_tasks()
            self.last_sync = datetime.utcnow()
            return tasks
            
        except Exception as e:
            logger.error(f"Error syncing from Todoist: {e}")
            return []
    
    def _korei_to_todoist_task(self, korei_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte tarea de Korei a formato Todoist"""
        task = {
            'content': korei_data.get('description', 'Tarea desde Korei')
        }
        
        # Proyecto - usar el project_id específico si está disponible, sino el default
        if korei_data.get('project_id'):
            task['project_id'] = korei_data['project_id']
        elif self.default_project_id:
            task['project_id'] = self.default_project_id
        
        # Fecha de vencimiento
        if korei_data.get('datetime'):
            task['due_string'] = self._format_due_date(korei_data['datetime'])
        
        # Prioridad (1-4 en Todoist, donde 4 es más alta)
        priority_map = {
            'baja': 1,
            'media': 2, 
            'alta': 4
        }
        if korei_data.get('priority'):
            task['priority'] = priority_map.get(korei_data['priority'], 1)
        
        # Etiquetas (Todoist usa 'labels' con nombres, no IDs)
        labels = ['korei']  # Etiqueta para identificar tareas de Korei
        if korei_data.get('task_category'):
            labels.append(korei_data['task_category'].lower().replace(' ', '_'))
        elif korei_data.get('category'):
            labels.append(korei_data['category'].lower().replace(' ', '_'))
        task['labels'] = labels
        
        return task
    
    def _todoist_to_korei_task(self, todoist_task: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte tarea de Todoist a formato Korei"""
        korei_task = {
            'type': 'tarea',
            'description': todoist_task.get('content', 'Tarea importada'),
            'external_id': str(todoist_task.get('id')),
            'external_service': 'todoist',
            'status': 'completed' if todoist_task.get('is_completed') else 'pending'
        }
        
        # Fecha de vencimiento
        due = todoist_task.get('due')
        if due and due.get('datetime'):
            korei_task['datetime'] = due['datetime']
        
        # Prioridad
        priority_map = {1: 'baja', 2: 'media', 3: 'media', 4: 'alta'}
        todoist_priority = todoist_task.get('priority', 1)
        korei_task['priority'] = priority_map.get(todoist_priority, 'media')
        
        # URL para abrir en Todoist
        korei_task['external_url'] = f"https://todoist.com/app/task/{todoist_task.get('id')}"
        
        return korei_task
    
    def _format_due_date(self, datetime_str: str) -> str:
        """Formatea fecha para Todoist usando lenguaje natural"""
        try:
            if isinstance(datetime_str, str):
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime_str
            
            now = datetime.now(dt.tzinfo)
            
            # Determinar formato basado en qué tan lejos está
            if dt.date() == now.date():
                return f"today at {dt.strftime('%H:%M')}"
            elif dt.date() == (now + timedelta(days=1)).date():
                return f"tomorrow at {dt.strftime('%H:%M')}"
            elif dt.date() <= (now + timedelta(days=7)).date():
                day_name = dt.strftime('%A')
                return f"{day_name} at {dt.strftime('%H:%M')}"
            else:
                return dt.strftime('%Y-%m-%d %H:%M')
                
        except Exception as e:
            logger.error(f"Error formatting due date: {e}")
            return datetime_str
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None



# --- Selección inteligente de proyecto óptimo ---
def select_optimal_project(projects: List[Dict[str, Any]], user_context: Dict[str, Any], task_text: str) -> Optional[Dict[str, Any]]:
    """
    Selecciona el proyecto más relevante de Todoist usando análisis inteligente.
    
    Args:
        projects: Lista de proyectos de Todoist
        user_context: Contexto del usuario 
        task_text: Texto de la tarea
        
    Returns:
        Proyecto óptimo o None
    """
    if not projects:
        logger.warning("No hay proyectos disponibles en Todoist")
        return None
    
    logger.info(f"🎯 Analizando {len(projects)} proyectos para: '{task_text}'")
    
    # Mapas de palabras clave por categoría
    category_keywords = {
        'trabajo': [
            'reunión', 'meeting', 'presentación', 'reporte', 'informe', 'cliente', 'proyecto', 
            'deadline', 'entrega', 'revisión', 'desarrollo', 'código', 'programar', 'diseño',
            'planificación', 'strategy', 'estrategia', 'análisis', 'investigación', 'datos',
            'presupuesto', 'propuesta', 'contrato', 'negociación', 'venta', 'marketing',
            'oficina', 'jefe', 'equipo', 'colaborador', 'conferencia', 'capacitación',
            'trabajo', 'laboral', 'professional', 'business', 'empresa', 'corporativo'
        ],
        'personal': [
            'casa', 'hogar', 'familia', 'comprar', 'mercado', 'supermercado', 'leche', 'comida',
            'cocinar', 'limpiar', 'ordenar', 'reparar', 'mantenimiento', 'jardín', 'mascotas',
            'personal', 'privado', 'hobby', 'pasatiempo', 'relajar', 'descansar', 'vacaciones',
            'amigos', 'social', 'cumpleaños', 'regalo', 'celebración', 'viaje', 'turismo',
            'ejercicio', 'gym', 'deporte', 'salud', 'médico', 'dentista', 'cita', 'consulta'
        ],
        'finanzas': [
            'pagar', 'factura', 'cuenta', 'banco', 'dinero', 'presupuesto', 'ahorro', 'inversión',
            'impuestos', 'declaración', 'recibo', 'gasto', 'ingreso', 'tarjeta', 'crédito',
            'préstamo', 'financiero', 'económico', 'contabilidad', 'finanzas', 'money'
        ],
        'salud': [
            'médico', 'doctor', 'hospital', 'clínica', 'cita', 'consulta', 'medicina', 'pastilla',
            'tratamiento', 'terapia', 'ejercicio', 'gym', 'dieta', 'nutrición', 'vitamina',
            'salud', 'bienestar', 'fitness', 'deporte', 'correr', 'caminar', 'yoga'
        ],
        'educación': [
            'estudiar', 'curso', 'clase', 'universidad', 'colegio', 'escuela', 'aprender',
            'leer', 'libro', 'investigar', 'tarea', 'examen', 'proyecto', 'presentación',
            'educación', 'formación', 'capacitación', 'certificación', 'diploma'
        ],
        'tecnología': [
            'programar', 'código', 'software', 'app', 'aplicación', 'web', 'desarrollo',
            'bug', 'fix', 'actualizar', 'instalar', 'configurar', 'servidor', 'base de datos',
            'api', 'frontend', 'backend', 'móvil', 'tecnología', 'digital', 'tech'
        ]
    }
    
    scores = {}
    
    for project in projects:
        project_name = project.get('name', '').lower()
        project_id = project.get('id')
        
        score = 0
        matches = []
        
        # 1. Coincidencia exacta o parcial del nombre
        if project_name in task_text.lower():
            score += 100
            matches.append(f"nombre_exacto({project_name})")
        elif any(word in task_text.lower() for word in project_name.split()):
            score += 50
            matches.append(f"nombre_parcial({project_name})")
        
        # 2. Análisis por palabras clave categorizadas
        task_lower = task_text.lower()
        for category, keywords in category_keywords.items():
            category_matches = sum(1 for keyword in keywords if keyword in task_lower)
            if category_matches > 0:
                # Bonus si el proyecto contiene la categoría en el nombre
                if category in project_name or any(cat_word in project_name for cat_word in category.split()):
                    score += category_matches * 20
                    matches.append(f"categoria_nombre({category}:{category_matches})")
                else:
                    score += category_matches * 10
                    matches.append(f"categoria_kw({category}:{category_matches})")
        
        # 3. Análisis semántico por tipo de acción
        action_patterns = {
            'comprar': ['comprar', 'adquirir', 'conseguir', 'obtener', 'buscar'],
            'pagar': ['pagar', 'abonar', 'cancelar', 'saldar'],
            'llamar': ['llamar', 'contactar', 'telefonear', 'hablar'],
            'reunirse': ['reunión', 'meeting', 'junta', 'encontrarse'],
            'crear': ['crear', 'hacer', 'desarrollar', 'construir'],
            'revisar': ['revisar', 'verificar', 'chequear', 'controlar']
        }
        
        for action, action_words in action_patterns.items():
            if any(word in task_lower for word in action_words):
                if action in project_name:
                    score += 15
                    matches.append(f"accion({action})")
        
        # 4. Proyectos comunes por defecto
        default_project_bonus = {
            'inbox': 5,     # Proyecto por defecto
            'personal': 10, # Muy común
            'trabajo': 10,  # Muy común
            'casa': 8,      # Común para tareas domésticas
            'compras': 12   # Común para compras
        }
        
        for default_name, bonus in default_project_bonus.items():
            if default_name in project_name:
                score += bonus
                matches.append(f"default({default_name})")
        
        # 5. Bonus por popularidad (proyectos con más tareas suelen ser más usados)
        if project.get('comment_count', 0) > 5:  # Proxy de uso frecuente
            score += 5
            matches.append("popular")
        
        scores[project_id] = {
            'project': project,
            'score': score,
            'matches': matches
        }
        
        logger.info(f"📊 {project_name}: score={score}, matches={', '.join(matches)}")
    
    # Seleccionar el mejor proyecto
    if not scores:
        logger.warning("No se pudo calcular score para ningún proyecto")
        return projects[0]  # Fallback al primer proyecto
    
    best_project_data = max(scores.values(), key=lambda x: x['score'])
    best_project = best_project_data['project']
    best_score = best_project_data['score']
    best_matches = best_project_data['matches']
    
    if best_score > 0:
        logger.info(f"🎯 Proyecto seleccionado: '{best_project['name']}' (score: {best_score})")
        logger.info(f"🔍 Criterios: {', '.join(best_matches)}")
        return best_project
    else:
        # Si no hay matches, usar proyecto por defecto inteligente
        fallback_project = _get_fallback_project(projects, task_text)
        logger.info(f"🔄 Sin matches claros, usando fallback: '{fallback_project['name']}'")
        return fallback_project

def _get_fallback_project(projects: List[Dict[str, Any]], task_text: str) -> Dict[str, Any]:
    """Selecciona un proyecto fallback inteligente"""
    
    # Preferencias de fallback por tipo de tarea
    task_lower = task_text.lower()
    
    # 1. Buscar proyectos comunes por nombre
    common_names = ['personal', 'inbox', 'general', 'misc', 'varios', 'casa', 'trabajo']
    for name in common_names:
        for project in projects:
            if name in project.get('name', '').lower():
                return project
    
    # 2. Si hay palabra "comprar", buscar proyecto relacionado con compras
    if any(word in task_lower for word in ['comprar', 'adquirir', 'conseguir']):
        for project in projects:
            project_name = project.get('name', '').lower()
            if any(word in project_name for word in ['compra', 'shopping', 'mercado', 'casa', 'personal']):
                return project
    
    # 3. Fallback final: primer proyecto de la lista
    return projects[0]