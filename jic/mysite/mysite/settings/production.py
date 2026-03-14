from .base import *

DEBUG = False

# Use WhiteNoise for static files management instead of ManifestStaticFilesStorage
# WhiteNoise is more robust and handles compression automatically
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

try:
    from .local import *
except ImportError:
    pass
