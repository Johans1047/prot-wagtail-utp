"""
Gunicorn configuration for JIC Wagtail CMS production deployment
Archivo de configuración de Gunicorn para producción

Usage:
    gunicorn --config gunicorn_config.py mysite.wsgi:application
    
    O desde Docker:
    docker-compose -f docker-compose.yml up -d
    
Con el Dockerfile configurado apropiadamente.
"""

import os
import multiprocessing
from pathlib import Path

# ===== BASIC CONFIGURATION =====
# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.production")

# ===== WORKER CONFIGURATION =====
# Number of worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class: sync, async, gthread, tornado, gevent, eventlet
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Number of threads per worker (for gthread worker class)
threads = int(os.getenv("GUNICORN_THREADS", 2))

# Max number of requests a worker will process before restarting
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))

# Adds randomness to the max_requests variable
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 100))

# ===== SERVER SOCKET =====
# The socket to bind
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# The backlog size for the listen queue
backlog = int(os.getenv("GUNICORN_BACKLOG", 2048))

# ===== TIMEOUTS =====
# Workers silent for more than this many seconds are killed and restarted
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))

# Timeout for graceful workers restart
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))

# ===== LOGGING =====
# Path to access log file or "-" for stdout
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")

# Path to error log file or "-" for stderr
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")

# The log level for this server
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(M)sms'

# ===== PROCESS NAMING =====
# A base to use with setproctitle for process naming
proc_name = "jic-wagtail-cms"

# ===== SERVER HOOKS =====
# Called just after the master process is initialized
def on_starting(server):
    print("[Gunicorn] Master process started")
    print(f"[Gunicorn] Workers: {workers}, Worker class: {worker_class}")
    print(f"[Gunicorn] Binding to: {bind}")

# Called just before a worker is forked
def on_exit(server):
    print("[Gunicorn] Master process exiting")

# ===== KEEP ALIVE =====
# The number of seconds to wait for requests on a Keep-Alive connection
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 2))

# ===== DEBUGGING =====
# Enable debug logging
debug = os.getenv("GUNICORN_DEBUG", "False").lower() == "true"

# ===== PERFORMANCE TUNING =====
# Directory to use for temporary files
worker_tmp_dir = "/dev/shm"

# Maximum HTTP request body size in bytes
limit_request_line = int(os.getenv("GUNICORN_LIMIT_REQUEST_LINE", 4094))

# Maximum number of headers fields in a request
limit_request_fields = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELDS", 100))

# Limit to the allowed size of an HTTP request header field
limit_request_field_size = int(os.getenv("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# ===== SSL CONFIGURATION (if needed) =====
# Path to SSL keyfile (optional)
keyfile = os.getenv("GUNICORN_KEYFILE", None)

# Path to SSL certificate file (optional)
certfile = os.getenv("GUNICORN_CERTFILE", None)

# SSL version to use
ssl_version = int(os.getenv("GUNICORN_SSL_VERSION", 2))  # TLS v1.2 and later

# ===== REQUEST HANDLERS =====
# Enable automatic reloading of modified modules
reload = os.getenv("GUNICORN_RELOAD", "False").lower() == "true"

# Call app_close_fn on app initialization
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "True").lower() == "true"

print(f"""
===== JIC WAGTAIL CMS - GUNICORN CONFIGURATION =====
Gunicorn Production Server Configuration
Django Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}
Workers: {workers}
Worker Class: {worker_class}
Threads per Worker: {threads}
Bind Address: {bind}
Timeout: {timeout}s
Graceful Timeout: {graceful_timeout}s
Access Log: {accesslog}
Error Log: {errorlog}
Log Level: {loglevel}
===================================================
""")
