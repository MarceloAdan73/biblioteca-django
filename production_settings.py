"""
Configuración adicional para producción
"""
import os
import dj_database_url

# Configuración para Render
if 'RENDER' in os.environ:
    # Hosts permitidos
    ALLOWED_HOSTS = ['.onrender.com', 'localhost', '127.0.0.1']
    
    # Database de Render (PostgreSQL)
    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///db.sqlite3',
            conn_max_age=600
        )
    }
    
    # Static files configuration
    STATIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'staticfiles')
    STATIC_URL = '/static/'
    
    # Security settings for production
    DEBUG = False
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    # Configuración local
    DEBUG = True
    ALLOWED_HOSTS = []
