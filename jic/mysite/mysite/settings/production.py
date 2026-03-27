from .base import *

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost:8001,https://localhost:8001").split(",")

try:
    from .local import *
except ImportError:
    pass
