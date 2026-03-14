from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0$hb3)ta6z_952&)u2#zwc)kschwkjf2tmfksd=a^vg4gz^4jj"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += ["livereload"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *
except ImportError:
    pass
