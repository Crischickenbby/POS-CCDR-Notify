"""
Sistema de Logging/Auditoría para Blancos Valentina
Este módulo registra todas las actividades importantes del sistema
incluyendo navegación, búsquedas, ventas y cambios de módulo.
"""

import json
import time
from datetime import datetime
from functools import wraps
from flask import request, session
from config import get_db_connection

class ActivityLogger:
    """Clase para manejar el logging de actividades del sistema"""
    
    @staticmethod
    def log_activity(action_type, module=None, description=None, details=None, 
                    duration_ms=None, status='SUCCESS', user_id=None):
        """
        Registra una actividad en la base de datos y muestra en consola
        
        Args:
            action_type (str): Tipo de acción (LOGIN, MODULE_CHANGE, PRODUCT_SEARCH, etc.)
            module (str): Módulo donde ocurrió la acción
            description (str): Descripción de la acción
            details (dict): Detalles adicionales en formato dict
            duration_ms (int): Duración en milisegundos
            status (str): Estado de la operación (SUCCESS, ERROR, WARNING)
            user_id (int): ID del usuario (opcional, se toma de la sesión si no se proporciona)
        """
        try:
            # Obtener información del usuario
            current_user_id = user_id or session.get('user_id')
            
            # Obtener información de la request
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            user_agent = request.headers.get('User-Agent', '')
            
            # Convertir details a JSON si existe
            details_json = json.dumps(details) if details else None
            
            # Registrar en base de datos
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO "Activity_Log" 
                ("ID_User", "Action_Type", "Module", "Description", "Details", 
                 "IP_Address", "User_Agent", "Duration_MS", "Status")
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING "ID_Log", "Timestamp"
            """, (current_user_id, action_type, module, description, details_json,
                  ip_address, user_agent, duration_ms, status))
            
            log_id, timestamp = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            # Mostrar en terminal con formato colorido
            ActivityLogger._print_to_console(
                log_id, timestamp, current_user_id, action_type, module, 
                description, details, duration_ms, status, ip_address
            )
            
        except Exception as e:
            print(f"❌ ERROR AL REGISTRAR LOG: {e}")
    
    @staticmethod
    def _print_to_console(log_id, timestamp, user_id, action_type, module, 
                         description, details, duration_ms, status, ip_address):
        """Muestra el log en la consola con formato atractivo"""
        
        # Colores para diferentes tipos de acciones
        colors = {
            'LOGIN': '🔐',
            'LOGOUT': '🚪',
            'MODULE_CHANGE': '📱',
            'PRODUCT_SEARCH': '🔍',
            'PRODUCT_CREATE': '📦',
            'PRODUCT_UPDATE': '✏️',
            'SALE': '💰',
            'INVENTORY_CHECK': '📋',
            'USER_CREATE': '👤',
            'USER_UPDATE': '👥',
            'ERROR': '❌',
            'WARNING': '⚠️'
        }
        
        status_colors = {
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️'
        }
        
        icon = colors.get(action_type, '📝')
        status_icon = status_colors.get(status, '📝')
        
        print("\n" + "="*80)
        print(f"{icon} ACTIVITY LOG #{log_id} {status_icon}")
        print("="*80)
        print(f"🕐 Timestamp:   {timestamp}")
        print(f"👤 Usuario:     {user_id or 'Anónimo'}")
        print(f"🎯 Acción:      {action_type}")
        print(f"📂 Módulo:      {module or 'N/A'}")
        print(f"📝 Descripción: {description or 'N/A'}")
        
        if details:
            print(f"🔍 Detalles:    {json.dumps(details, indent=2, ensure_ascii=False)}")
        
        if duration_ms is not None:
            print(f"⏱️  Duración:    {duration_ms}ms")
        
        print(f"🌐 IP:          {ip_address}")
        print(f"📊 Estado:      {status}")
        print("="*80)

def log_route_access(module_name):
    """
    Decorador para registrar automáticamente el acceso a rutas/módulos
    
    Usage:
        @log_route_access('PUNTO_VENTA')
        @app.route('/punto_venta')
        def punto_venta():
            return render_template('punto_venta.html')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Ejecutar la función original
                result = f(*args, **kwargs)
                
                # Calcular duración
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Registrar el acceso exitoso
                ActivityLogger.log_activity(
                    action_type='MODULE_CHANGE',
                    module=module_name,
                    description=f'Acceso al módulo {module_name}',
                    details={
                        'route': request.endpoint,
                        'method': request.method,
                        'args': dict(request.args)
                    },
                    duration_ms=duration_ms,
                    status='SUCCESS'
                )
                
                return result
                
            except Exception as e:
                # Calcular duración incluso en caso de error
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Registrar el error
                ActivityLogger.log_activity(
                    action_type='MODULE_CHANGE',
                    module=module_name,
                    description=f'Error al acceder al módulo {module_name}: {str(e)}',
                    details={
                        'route': request.endpoint,
                        'method': request.method,
                        'error': str(e)
                    },
                    duration_ms=duration_ms,
                    status='ERROR'
                )
                
                raise e
                
        return wrapped
    return decorator

def log_api_call(action_type, description=None):
    """
    Decorador para registrar llamadas a APIs
    
    Usage:
        @log_api_call('PRODUCT_SEARCH', 'Búsqueda de productos')
        @app.route('/api/productos')
        def api_productos():
            return jsonify(productos)
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Ejecutar la función original
                result = f(*args, **kwargs)
                
                # Calcular duración
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Registrar la llamada exitosa
                ActivityLogger.log_activity(
                    action_type=action_type,
                    module='API',
                    description=description or f'Llamada API {action_type}',
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'args': dict(request.args),
                        'form_data': dict(request.form) if request.form else None
                    },
                    duration_ms=duration_ms,
                    status='SUCCESS'
                )
                
                return result
                
            except Exception as e:
                # Calcular duración incluso en caso de error
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Registrar el error
                ActivityLogger.log_activity(
                    action_type=action_type,
                    module='API',
                    description=f'Error en API {action_type}: {str(e)}',
                    details={
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'error': str(e)
                    },
                    duration_ms=duration_ms,
                    status='ERROR'
                )
                
                raise e
                
        return wrapped
    return decorator

# Funciones auxiliares para logging específico
def log_login(user_id, username, success=True):
    """Registra intentos de login"""
    ActivityLogger.log_activity(
        action_type='LOGIN',
        module='AUTH',
        description=f'Intento de login para usuario: {username}',
        details={'username': username, 'success': success},
        status='SUCCESS' if success else 'ERROR'
    )

def log_logout(user_id):
    """Registra logout de usuarios"""
    ActivityLogger.log_activity(
        action_type='LOGOUT',
        module='AUTH',
        description='Usuario cerró sesión',
        user_id=user_id
    )

def log_product_search(search_term, results_count=None):
    """Registra búsquedas de productos"""
    ActivityLogger.log_activity(
        action_type='PRODUCT_SEARCH',
        module='SEARCH',
        description=f'Búsqueda de productos: "{search_term}"',
        details={
            'search_term': search_term,
            'results_count': results_count
        }
    )

def log_sale(sale_data):
    """Registra ventas realizadas"""
    ActivityLogger.log_activity(
        action_type='SALE',
        module='VENTA',
        description='Nueva venta registrada',
        details=sale_data
    )

def log_product_creation(product_data):
    """Registra creación de productos"""
    ActivityLogger.log_activity(
        action_type='PRODUCT_CREATE',
        module='ALMACEN',
        description='Nuevo producto creado',
        details=product_data
    )