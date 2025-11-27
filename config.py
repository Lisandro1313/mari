"""
Archivo de configuración para MARI/MATECA
IMPORTANTE: No subir este archivo a GitHub con credenciales reales
"""
import os

class Config:
    """Configuración base"""
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mateca_gualeguaychu_2025_secret_key_mari'
    
    # Sesión
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora
    
    # Base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL')  # PostgreSQL en Render
    DATABASE_NAME = 'mari.db'  # SQLite local (fallback)
    
    # Credenciales (CAMBIAR EN PRODUCCIÓN)
    USUARIO = os.environ.get('APP_USUARIO') or 'mariateresa'
    PASSWORD = os.environ.get('APP_PASSWORD') or 'mateca'
    
    # Exportación
    EXPORT_FOLDER = 'exports'
    MAX_EXPORT_FILES = 10  # Máximo de archivos de exportación a conservar
    
    # Límites
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    
class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requiere HTTPS
    
    # Obtener credenciales de variables de entorno en producción
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

# Configuración por defecto
config = DevelopmentConfig()
