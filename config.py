import psycopg
import os
from dotenv import load_dotenv

"""
POS-CCDR-Notify - Sistema de Punto de Venta con Gestión de Clientes y Notificaciones
Configuración centralizada de la aplicación

Este módulo gestiona:
- Conexión a base de datos PostgreSQL
- Variables de entorno seguras
- Configuración de secretos y claves de API
"""

# Cargar variables de entorno desde archivo .env
load_dotenv()

# ========================
# CONFIGURACIÓN DE BASE DE DATOS
# ========================
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'CCDR')  # Base de datos para sistema de notificaciones
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# ========================
# SEGURIDAD
# ========================
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-por-defecto-cambiar-en-produccion')

# ========================
# CONFIGURACIÓN DE NOTIFICACIONES (Futuras implementaciones)
# ========================
# EMAIL_API_KEY = os.getenv('EMAIL_API_KEY', '')
# SMS_API_KEY = os.getenv('SMS_API_KEY', '')
# WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN', '')

# Función para obtener una conexión a la base de datos
def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos PostgreSQL.
    
    Returns:
        psycopg.Connection: Objeto de conexión a PostgreSQL
        
    Raises:
        psycopg.Error: Si falla la conexión a la base de datos
    """
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
