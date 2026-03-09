# ==============================================================================
# EJEMPLO DE CONFIGURACIÓN DE SETTINGS.PY PARA WAGTAIL CON MINIO
# ==============================================================================
# Este archivo muestra cómo configurar Django/Wagtail para usar MinIO
# Copia estas secciones a tu mysite/mysite/settings.py
# ==============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ==============================================================================
# DATABASE CONFIGURATION (PostgreSQL)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'jic_db'),
        'USER': os.getenv('DB_USER', 'jicuser'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'jicpass'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ==============================================================================
# MINIO / S3 STORAGE CONFIGURATION
# ==============================================================================

# Usar django-storages para MinIO
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Configuración de AWS S3 (compatible con MinIO)
AWS_ACCESS_KEY_ID = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
AWS_STORAGE_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'jic-media')
AWS_S3_ENDPOINT_URL = f"http://{os.getenv('MINIO_ENDPOINT', 'minio:9000')}"
AWS_S3_USE_SSL = os.getenv('MINIO_USE_SSL', 'false').lower() == 'true'

# Configuración adicional de S3
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'media'
AWS_QUERYSTRING_AUTH = False  # URLs públicas
AWS_DEFAULT_ACL = 'public-read'

# URL pública de MinIO (para acceso externo)
MINIO_EXTERNAL_ENDPOINT = os.getenv('MINIO_EXTERNAL_ENDPOINT', 'localhost:9000')
MEDIA_URL = f"http://{MINIO_EXTERNAL_ENDPOINT}/{AWS_STORAGE_BUCKET_NAME}/"

# ==============================================================================
# STATIC FILES CONFIGURATION
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'theme', 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ==============================================================================
# WAGTAIL SETTINGS
# ==============================================================================

WAGTAIL_SITE_NAME = os.getenv('SITE_NAME', 'JIC Website')
WAGTAIL_ENABLE_UPDATE_CHECK = False

# Configurar Wagtail para usar MinIO
WAGTAILIMAGES_IMAGE_MODEL = 'wagtailimages.Image'

# ==============================================================================
# INSTALLED APPS
# ==============================================================================

INSTALLED_APPS = [
    # Wagtail apps
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    
    'modelcluster',
    'taggit',
    
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'storages',  # Para MinIO/S3
    
    # Custom apps
    'theme',
    'web',
]

# Solo en desarrollo
if DEBUG:
    INSTALLED_APPS += ['livereload']

# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

# Solo en desarrollo
if DEBUG:
    MIDDLEWARE.insert(1, 'livereload.middleware.LiveReloadScript')

# ==============================================================================
# TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
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

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Panama'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==============================================================================
# LOGGING (Opcional)
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ==============================================================================
# NOTAS IMPORTANTES
# ==============================================================================

"""
1. Asegúrate de tener instalado 'storages' y 'boto3' en requirements.txt
2. El bucket 'jic-media' debe existir en MinIO (se crea automáticamente con docker-compose)
3. Para producción, cambia las URLs de MinIO a dominios públicos
4. Configura SSL en producción (MINIO_USE_SSL=true)
5. Usa credenciales seguras en producción (no minioadmin/minioadmin)

ALTERNATIVA: Usar el cliente MinIO directamente
Si prefieres usar el cliente MinIO en lugar de boto3, puedes crear un storage backend personalizado.
Ver: https://docs.wagtail.org/en/stable/advanced_topics/images/custom_image_model.html
"""
