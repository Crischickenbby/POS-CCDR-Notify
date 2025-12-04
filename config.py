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
# Railway proporciona URL_DE_LA_BASE_DE_DATOS automáticamente
DATABASE_URL = os.getenv('URL_DE_LA_BASE_DE_DATOS')

# Si estamos en desarrollo local, usar variables individuales
if not DATABASE_URL:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'CCDR')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# ========================
# SEGURIDAD
# ========================
SECRET_KEY = os.getenv('SECRET_KEY', 'clave-por-defecto-cambiar-en-produccion')

# ========================
# CONFIGURACIÓN DE CORREO
# ========================
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

# Utilidad para enviar correos
import smtplib
from email.message import EmailMessage

def enviar_correo(destinatario, asunto, mensaje_html):
    remitente = MAIL_USERNAME
    contrasena = MAIL_PASSWORD
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = asunto
    email.set_content(mensaje_html, subtype="html")
    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(remitente, contrasena)
        smtp.send_message(email)
        smtp.quit()
        return True
    except Exception as e:
        print(f"Error al enviar correo a {destinatario}: {e}")
        return False

# Función para obtener una conexión a la base de datos
def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos PostgreSQL.
    Soporta Railway (URL_DE_LA_BASE_DE_DATOS) y desarrollo local.
    
    Returns:
        psycopg.Connection: Objeto de conexión a PostgreSQL
        
    Raises:
        psycopg.Error: Si falla la conexión a la base de datos
    """
    if DATABASE_URL:
        # Usar URL de conexión (Railway)
        return psycopg.connect(DATABASE_URL)
    else:
        # Usar variables individuales (desarrollo local)
        return psycopg.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
