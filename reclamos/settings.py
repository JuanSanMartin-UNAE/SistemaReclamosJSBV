"""
Django settings for reclamos project.

Configurado para el Sistema de Atención y Gestión de Reclamos
Junta de Saneamiento de Bella Vista - Itapúa
Proyecto de Grado - UNAE 2026
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from reclamos.hosts import (
    construir_hosts_permitidos,
    construir_origenes_csrf,
    dividir_lista,
    normalizar_hostname,
    normalizar_origen,
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SEGURIDAD Y ENTORNO
# ==============================================================================
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-default-key-para-desarrollo-local-2026'
)

# DEBUG: 1 o True en .env activa el modo de depuración
DEBUG = os.environ.get('DJANGO_DEBUG', '1').lower() in ('1', 'true', 'yes')



def _bandera_entorno(nombre, predeterminado):
    """Lee una bandera de entorno. Vacía o ausente usa el valor por defecto."""
    crudo = os.environ.get(nombre)
    if crudo is None or not str(crudo).strip():
        return predeterminado
    return str(crudo).strip().lower() in ('1', 'true', 'yes', 'si', 'sí')


# El túnel público queda activo en desarrollo. En un servidor real hay que
# poner DJANGO_ALLOW_NGROK=0, salvo que la demostración siga usando ngrok.
ALLOW_NGROK = _bandera_entorno('DJANGO_ALLOW_NGROK', DEBUG)
# Hostname exacto opcional (con o sin https://). Con ALLOW_NGROK=0 es el
# único host del túnel que se acepta.
NGROK_HOSTNAME = normalizar_hostname(os.environ.get('DJANGO_NGROK_DOMAIN', ''))
# ngrok termina TLS y habla HTTP con Django. Sin esto el login, el CSRF y
# los enlaces de recuperación salen como http://.
BEHIND_PROXY = _bandera_entorno(
    'DJANGO_BEHIND_PROXY',
    ALLOW_NGROK or bool(NGROK_HOSTNAME),
)

_hosts_entorno = dividir_lista(os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    'localhost,127.0.0.1,web,0.0.0.0',
))
ALLOWED_HOSTS = construir_hosts_permitidos(
    _hosts_entorno,
    ALLOW_NGROK,
    NGROK_HOSTNAME,
)

_origenes_extra = []
for _crudo in dividir_lista(os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')):
    _origen = normalizar_origen(_crudo)
    if not _origen:
        raise ImproperlyConfigured(
            f'DJANGO_CSRF_TRUSTED_ORIGINS contiene un origen inválido: {_crudo}'
        )
    _origenes_extra.append(_origen)

CSRF_TRUSTED_ORIGINS = construir_origenes_csrf(
    _origenes_extra,
    ALLOW_NGROK,
    NGROK_HOSTNAME,
)

# Se confía en el protocolo solo después de que EncabezadosProxyNgrok deja
# el último valor (el que escribe ngrok) y únicamente para un host del túnel.
# X-Forwarded-Host no se usa: ngrok ya envía el hostname público en Host,
# y el otro encabezado puede venir del cliente.
if BEHIND_PROXY:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
else:
    SECURE_PROXY_SSL_HEADER = None
USE_X_FORWARDED_HOST = False

# ==============================================================================
# APLICACIONES INSTALADAS
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicación principal del sistema
    'reclamos_app',
]

# Modelo de Usuario personalizado del sistema (acceso por número de documento)
AUTH_USER_MODEL = 'reclamos_app.Usuario'

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    # Antes que el resto: define si la petición del túnel es HTTPS.
    'reclamos.middleware.EncabezadosProxyNgrok',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'reclamos.urls'

# ==============================================================================
# PLANTILLAS (TEMPLATES)
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'reclamos.wsgi.application'

# ==============================================================================
# BASE DE DATOS (PostgreSQL en Contenedor Docker)
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB', 'db_reclamos')),
        'USER': os.environ.get('DB_USER', os.environ.get('POSTGRES_USER', 'usuario_django')),
        'PASSWORD': os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD', 'contrasena_segura')),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ==============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# INTERNACIONALIZACIÓN Y ZONA HORARIA
# ==============================================================================
LANGUAGE_CODE = 'es-py'

# Zona horaria estándar sin tildes para evitar ValueError
TIME_ZONE = 'America/Asuncion'

USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES DEL SISTEMA)
# ==============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==============================================================================
# ARCHIVOS MULTIMEDIA (Evidencias fotográficas de reclamos - HU-02)
# ==============================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# REDIRECCIONES DE SESIÓN Y VISTAS
# ==============================================================================
LOGIN_URL = 'reclamos_app:login'
LOGIN_REDIRECT_URL = 'reclamos_app:panel'
LOGOUT_REDIRECT_URL = 'reclamos_app:bienvenida'
PASSWORD_RESET_TIMEOUT = 60 * 60 * 2  # 2 horas

# ==============================================================================
# SEGURIDAD Y CONTROL DE SESIÓN (RNF-01: Cierre por inactividad tras 10 minutos)
# ==============================================================================
# 10 minutos * 60 segundos = 600 segundos
SESSION_COOKIE_AGE = 600
# Reinicia el contador de 10 minutos con cada clic o petición activa del usuario
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# La cookie no lleva la marca Secure: el mismo proceso atiende http://localhost
# y el HTTPS de ngrok. Marcarla cortaría el inicio de sesión local.

# ==============================================================================
# SERVICIO DE CORREO ELECTRÓNICO (Simulación en consola durante desarrollo)
# ==============================================================================
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'
DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'Junta de Saneamiento de Bella Vista <no-responder@juntabellavista.local>'
)

# ==============================================================================
# CONFIGURACIÓN DE CLAVE PRIMARIA
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'