# 🚀 Quick Start - JIC Wagtail CMS

Guía rápida para tener el proyecto funcionando en menos de 5 minutos.

## ⚡ Inicio Rápido (Linux)

### Opción 1: Script Automático (Recomendado)

```bash
# 1. Dar permisos de ejecución
chmod +x setup.sh

# 2. Ejecutar
./setup.sh

# 3. ¡Listo! Accede a http://localhost:8000
```

### Opción 2: Usando Make

```bash
# Inicializar proyecto completo
make init

# Crear superusuario
make createsuperuser
```

### Opción 3: Manual

```bash
# 1. Configurar entorno
cp .env.example .env

# 2. Construir y levantar
docker-compose build
docker-compose up -d

# 3. Esperar 10 segundos
sleep 10

# 4. Ejecutar migraciones
docker-compose exec web python mysite/manage.py migrate

# 5. Crear superusuario
docker-compose exec web python mysite/manage.py createsuperuser
```

## 📍 Accesos

Una vez que el proyecto esté corriendo:

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Sitio Web** | http://localhost:8000 | - |
| **Admin Wagtail** | http://localhost:8000/admin | Tu superusuario |
| **Admin Django** | http://localhost:8000/django-admin | Tu superusuario |
| **MinIO Console** | http://localhost:9001 | minioadmin / minioadmin |
| **PostgreSQL** | localhost:5432 | jicuser / jicpass |

## 🎯 Primeros Pasos Después de la Instalación

### 1. Acceder al Admin de Wagtail

```
URL: http://localhost:8000/admin
Usuario: (el que creaste con createsuperuser)
```

### 2. Crear tu Primera Página

1. Ve a **Pages** en el menú lateral
2. Haz clic en **Home**
3. Click en **Add child page**
4. Selecciona el tipo de página
5. Llena el contenido
6. Click en **Publish**

### 3. Subir Imágenes

Las imágenes se almacenarán automáticamente en MinIO:

1. Ve a **Images** en el menú
2. Click en **Add an image**
3. Sube tu imagen
4. ¡Se guardará en MinIO automáticamente!

### 4. Personalizar el Diseño con TailwindCSS

Edita el archivo de entrada de TailwindCSS:

```bash
# El archivo se recarga automáticamente
nano mysite/theme/static/src/input.css
```

El watcher de TailwindCSS compilará automáticamente los cambios.

## 🛠️ Comandos Útiles

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo web
docker-compose logs -f web

# Solo MinIO
docker-compose logs -f minio
```

### Gestión de Servicios

```bash
# Detener todo
docker-compose down

# Reiniciar
docker-compose restart

# Ver estado
docker-compose ps
```

### Django Management

```bash
# Crear app
docker-compose exec web python mysite/manage.py startapp mi_app

# Shell de Django
docker-compose exec web python mysite/manage.py shell

# Shell del contenedor
docker-compose exec web bash
```

## 🐛 Solución de Problemas Rápida

### Error: Puerto 8000 ocupado

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usa 8001 en tu máquina
```

### Servicios no inician

```bash
# Ver qué está pasando
docker-compose logs

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### Cambios en CSS no se reflejan

```bash
# Reiniciar el watcher de TailwindCSS
docker-compose restart tailwind

# Ver logs del watcher
docker-compose logs -f tailwind
```

## 📚 Siguiente Paso

Lee la documentación completa en [README.md](README.md) para:

- Arquitectura del sistema
- Configuración avanzada
- Despliegue en producción
- Troubleshooting detallado

## 🆘 Ayuda

```bash
# Ver todos los comandos disponibles
make help

# Ver comandos de MinIO
make help-minio

# Ver comandos de Django
make help-django
```

---

**¿Problemas?** Revisa [README.md](README.md) o contacta al equipo de desarrollo.
