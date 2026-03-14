# 🚀 Guía de Despliegue en Producción - JIC Wagtail CMS

## Resumen de Cambios Realizados

Se ha configurado la aplicación para ejecutarse en producción usando **Gunicorn** como servidor WSGI y **Nginx** como reverso proxy. Todas las variables están centralizadas en el archivo `.env`.

### 📋 Archivos Modificados/Creados

1. **`.env`** - Archivo centralizado con todas las variables de entorno
2. **`docker-compose.yml`** - Actualizado para usar variables desde `.env` (desarrollo)
3. **`docker-compose.prod.yml`** - Nueva configuración para producción con Gunicorn
4. **`Dockerfile`** - Actualizado con soporte para Gunicorn y script de entrada
5. **`entrypoint.sh`** - Script que inicia en desarrollo o producción
6. **`gunicorn_config.py`** - Configuración completa de Gunicorn
7. **`mysite/settings/production.py`** - Ampliado con configuración de seguridad y Gunicorn
8. **`nginx/nginx.conf`** - Configuración principal de Nginx
9. **`nginx/conf.d/default.conf`** - Configuración del sitio con reverse proxy

---

## 🔧 Variables de Entorno (`.env`)

### Django Configuration
```env
DEBUG=True/False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,example.com
```

### Database
```env
DB_ENGINE=postgresql
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=password
DB_HOST=host
DB_PORT=5432
DB_SSLMODE=require
DB_CHANNEL_BINDING=require
```

### MinIO Storage
```env
MINIO_ENDPOINT=172.20.0.75:9000
MINIO_ROOT_USER=username
MINIO_ROOT_PASSWORD=password
MINIO_ACCESS_KEY=key
MINIO_SECRET_KEY=secret
MINIO_USE_SSL=False
MINIO_BUCKET_NAME=jic-media
```

### Gunicorn Configuration
```env
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_WORKER_CLASS=sync
GUNICORN_TIMEOUT=60
GUNICORN_GRACEFUL_TIMEOUT=30
GUNICORN_BIND=0.0.0.0:8000
```

### Security Settings
```env
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
USE_X_FORWARDED_HOST=True
```

---

## 🏃 Ejecución

### Modo Desarrollo (runserver)
```bash
# Con docker-compose normal
docker-compose up -d

# Verificar logs
docker-compose logs -f jicweb_app
```

### Modo Producción (Gunicorn + Nginx)
```bash
# Levantar stack de producción
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f jicweb_app_prod

# Ver estado de servicios
docker-compose -f docker-compose.prod.yml ps
```

---

## 📊 Configuración de Gunicorn

### Worker Classes
- **`sync`** - Tradicional, recomendado para la mayoría de casos
- **`gthread`** - Multi-threaded, útil con DB connection pooling
- **`gevent`** - Async, requiere instalación adicional
- **`tornado`** - Async, requiere instalación adicional

### Cálculo de Workers
- **Regla**: `(2 × CPU_cores) + 1`
- Defecto: 4 workers
- Máximo: No más de 8 workers en producción (usar load balancing)

### Performance Tuning
```env
GUNICORN_MAX_REQUESTS=1000        # Reiniciar worker después de N requests (evita memory leaks)
GUNICORN_MAX_REQUESTS_JITTER=100  # Añade aleatoriedad para evitar "thundering herd"
GUNICORN_TIMEOUT=60               # Timeout de workers (segundos)
```

---

## 🛡️ Seguridad en Producción

### SSL/HTTPS (en nginx/conf.d/default.conf)
```nginx
# Descomentar y configurar:
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
}
```

### Django Security Settings
En `.env`:
```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Headers de Seguridad (en Nginx)
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)

---

## 📝 Migraciones y Estáticos

El `entrypoint.sh` automáticamente:
1. ✅ Ejecuta migraciones ("python manage.py migrate")
2. ✅ Recolecta archivos estáticos ("python manage.py collectstatic")
3. ✅ Inicia el servidor (Gunicorn en prod, runserver en dev)

Para ejecutar manualmente:
```bash
# Dentro del contenedor
docker-compose exec jicweb_app python mysite/manage.py migrate
docker-compose exec jicweb_app python mysite/manage.py collectstatic --no-input
```

---

## 🔍 Monitoreo y Debugging

### Ver logs en tiempo real
```bash
# Desarrollo
docker-compose logs -f jicweb_app

# Producción
docker-compose -f docker-compose.prod.yml logs -f jicweb_app_prod
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Healthcheck
```bash
# Desarrollo
curl http://localhost:8000/

# Producción (con Nginx)
curl http://localhost/
curl http://localhost/health
```

### Estadísticas de Gunicorn
El archivo `gunicorn_config.py` registra:
- Número de workers
- Worker class utilizado
- Configuración de timeout
- Bind address

---

## 📦 Variables Compartidas Entre Servicios

| Variable | Servicio | Descripción |
|----------|----------|-------------|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | App + DB | Credenciales de base de datos |
| `MINIO_ENDPOINT`, `MINIO_ROOT_USER` | App + MinIO | Configuración de almacenamiento |
| `GUNICORN_*` | App | Configuración del servidor WSGI |
| `SECURE_*` | App | Settings de seguridad |

---

## 🚦 Checklist de Producción

- [ ] ✅ `.env` configurado con valores reales
- [ ] ✅ `DEBUG=False` en `.env`
- [ ] ✅ `SECRET_KEY` cambiado a valor seguro
- [ ] ✅ `ALLOWED_HOSTS` configurado correctamente
- [ ] ✅ SSL/HTTPS configurado en Nginx
- [ ] ✅ Base de datos remota configurada (Neon)
- [ ] ✅ MinIO accesible y bucket creado
- [ ] ✅ Backups configurados (automáticos cada 24h)
- [ ] ✅ Logs centralizados (verificar `GUNICORN_ACCESS_LOG`)
- [ ] ✅ Health checks activos

---

## 🆘 Troubleshooting

### Error: "Address already in use"
```bash
# Encontrar proceso en puerto
lsof -i :8000
kill -9 <PID>

# O cambiar puerto en .env
GUNICORN_BIND=0.0.0.0:9000
```

### Database connection errors
```bash
# Verificar conexión
docker-compose exec jicweb_app python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()"
```

### Estáticos no cargando
```bash
# Recolectar estáticos
docker-compose exec jicweb_app python mysite/manage.py collectstatic --no-input --clear

# Verificar volumen
docker volume ls | grep static
```

### AngioDB/Neon timeout
```bash
# Aumentar timeout en .env
DB_CONN_MAX_AGE=600  # 10 minutos
GUNICORN_TIMEOUT=90   # 90 segundos
```

---

## 📚 Referencias

- [Gunicorn Docs](https://docs.gunicorn.org/)
- [Django Deployment with Gunicorn](https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/gunicorn/)
- [Nginx Best Practices](https://www.nginx.com/resources/wiki/best_practices/)
- [Docker Compose Production](https://docs.docker.com/compose/production/)

---

**Last Updated**: 2026-03-13
**Version**: 1.0.0
