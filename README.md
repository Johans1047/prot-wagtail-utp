# JIC Wagtail CMS - Documentación Técnica 🚀

Sistema de gestión de contenidos (CMS) para JIC basado en Wagtail, con TailwindCSS, Flowbite, PostgreSQL y MinIO.

## 📋 Stack Tecnológico

### Backend
- **Python**: 3.11+
- **Framework**: Django 4.2.9
- **CMS**: Wagtail 5.2.2
- **Base de datos**: PostgreSQL 15

### Frontend
- **CSS Framework**: TailwindCSS 3.4.1
- **Componentes UI**: Flowbite 2.2.1
- **Plugins**: @tailwindcss/typography, @tailwindcss/forms

### Infraestructura
- **Object Storage**: MinIO (S3-compatible)
- **Contenedores**: Docker & Docker Compose
- **Proxy Reverso**: Nginx (producción)
- **Sistema Operativo**: Linux (Ubuntu/Debian recomendado)

## 🎯 Dependencias Detalladas

### Python (requirements.txt)
```
Django==4.2.9              # Framework web
wagtail==5.2.2            # CMS
psycopg2-binary==2.9.9    # Driver PostgreSQL
django-storages==1.14.2   # Soporte para storage backends
boto3==1.34.20            # AWS SDK (para MinIO/S3)
minio==7.2.3              # Cliente MinIO
Pillow==10.2.0            # Procesamiento de imágenes
willow==1.8               # Librería de imágenes de Wagtail
django-livereload-server==0.4  # Hot reload en desarrollo
python-dotenv==1.0.0      # Manejo de variables de entorno
```

### Node.js (package.json)
```
tailwindcss: ^3.4.1           # Framework CSS
flowbite: ^2.2.1              # Componentes UI
@tailwindcss/typography: ^0.5.10  # Plugin tipografía
@tailwindcss/forms: ^0.5.7    # Plugin formularios
```

### Servicios Docker
```
PostgreSQL: 15-alpine
MinIO: latest
MinIO Client (mc): latest
Python: 3.11-slim
Node.js: 18-alpine
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente (Navegador)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Nginx (Proxy Reverso)                       │
│                    Puerto 80/443                            │
└────────┬────────────────────────────┬───────────────────────┘
         │                            │
         ▼                            ▼
┌────────────────────┐       ┌─────────────────┐
│  Django/Wagtail    │       │  Static Files   │
│   Puerto 8000      │       │  /staticfiles   │
└────────┬───────────┘       └─────────────────┘
         │
         ├──────────┬──────────────┬─────────────┐
         ▼          ▼              ▼             ▼
    ┌────────┐ ┌─────────┐  ┌──────────┐  ┌──────────┐
    │  DB    │ │  MinIO  │  │ Tailwind │  │  Media   │
    │  5432  │ │ 9000/01 │  │  Watcher │  │  Files   │
    └────────┘ └─────────┘  └──────────┘  └──────────┘
```

## 🚀 Instalación y Configuración

### Requisitos Previos

1. **Docker Desktop** instalado
   - [Descargar para Linux](https://docs.docker.com/desktop/install/linux-install/)
   
2. **Git** (opcional, recomendado)
   ```bash
   sudo apt-get update
   sudo apt-get install git
   ```

### Instalación Paso a Paso

#### 1. Clonar/Descargar el Proyecto
```bash
git clone <url-del-repositorio>
cd jic-wagtail-cms
```

#### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
nano .env
```

#### 3. Iniciar el Proyecto

**Opción A: Setup Automático (Recomendado)**
```bash
chmod +x setup.sh
./setup.sh
```

**Opción B: Manual**
```bash
# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Esperar a que PostgreSQL esté listo
sleep 5

# Ejecutar migraciones
docker-compose exec web python mysite/manage.py migrate

# Crear superusuario
docker-compose exec web python mysite/manage.py createsuperuser
```

**Opción C: Usando Makefile**
```bash
make init
```

### 4. Acceder a la Aplicación

- **Sitio web**: http://localhost:8000
- **Admin Wagtail**: http://localhost:8000/admin
- **Admin Django**: http://localhost:8000/django-admin
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **PostgreSQL**: localhost:5432 (jicuser/jicpass)

## 📁 Estructura del Proyecto

```
jic-wagtail-cms/
├── docker-compose.yml          # Configuración de servicios
├── Dockerfile                  # Imagen Django/Wagtail
├── Dockerfile.node            # Imagen Node/TailwindCSS
├── requirements.txt           # Dependencias Python
├── package.json               # Dependencias Node
├── tailwind.config.js         # Config TailwindCSS + Flowbite
├── .env                       # Variables de entorno (no incluir en git)
├── .env.example              # Ejemplo de variables
├── README.md                  # Esta documentación
├── DEPENDENCIES.md           # Documentación detallada de dependencias
├── Makefile                  # Comandos útiles
├── setup.sh                  # Script de instalación automática
│
└── mysite/                   # Proyecto Django/Wagtail
    ├── manage.py
    ├── mysite/              # Configuración del proyecto
    │   ├── settings.py      # Configuración principal
    │   ├── settings/        # Settings por ambiente
    │   │   ├── base.py     # Configuración base
    │   │   ├── dev.py      # Desarrollo
    │   │   └── prod.py     # Producción
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── theme/               # App de tema
    │   └── static/src/
    │       ├── input.css    # CSS de entrada
    │       └── output.css   # CSS compilado
    │
    ├── web/                 # App principal
    │   ├── models.py       # Modelos de páginas
    │   ├── views.py
    │   └── templates/
    │
    └── static/             # Archivos estáticos compilados
```

## 🔧 Comandos Útiles

### Docker Compose

```bash
# Iniciar servicios
docker-compose up

# Iniciar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio
docker-compose logs -f web
docker-compose logs -f tailwind
docker-compose logs -f minio

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reconstruir
docker-compose up --build
```

### Django/Wagtail

```bash
# Migraciones
docker-compose exec web python mysite/manage.py makemigrations
docker-compose exec web python mysite/manage.py migrate

# Crear superusuario
docker-compose exec web python mysite/manage.py createsuperuser

# Django shell
docker-compose exec web python mysite/manage.py shell

# Recolectar estáticos
docker-compose exec web python mysite/manage.py collectstatic

# Crear nueva app
docker-compose exec web python mysite/manage.py startapp nombre_app
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U jicuser -d jic_db

# Backup
docker-compose exec db pg_dump -U jicuser jic_db > backup.sql

# Restaurar
docker-compose exec -T db psql -U jicuser jic_db < backup.sql
```

### MinIO

```bash
# Acceder al cliente MinIO
docker-compose exec minio-client mc ls myminio

# Listar archivos en el bucket
docker-compose exec minio-client mc ls myminio/jic-media

# Subir archivo
docker-compose exec minio-client mc cp archivo.jpg myminio/jic-media/
```

### TailwindCSS

```bash
# Compilar CSS manualmente
docker-compose exec tailwind npm run tailwind:build

# Ver logs del watcher
docker-compose logs -f tailwind
```

## 🔐 Configuración de MinIO

### Acceso Programático

El proyecto está configurado para usar MinIO con las siguientes credenciales por defecto:

```python
MINIO_ENDPOINT = 'minio:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET_NAME = 'jic-media'
```

### Bucket Automático

El servicio `minio-client` crea automáticamente el bucket `jic-media` al iniciar.

### Políticas de Acceso

Por defecto, el bucket tiene política de lectura pública (download). Puedes cambiarla:

```bash
# Hacer privado
docker-compose exec minio-client mc anonymous set private myminio/jic-media

# Hacer público
docker-compose exec minio-client mc anonymous set download myminio/jic-media
```

## 🎨 Trabajando con Flowbite

### Importar Componentes

En tus templates:

```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
    <link href="{% static 'src/output.css' %}" rel="stylesheet">
</head>
<body>
    <!-- Ejemplo: Modal de Flowbite -->
    <button data-modal-target="default-modal" data-modal-toggle="default-modal">
        Abrir Modal
    </button>
    
    <div id="default-modal" class="hidden">
        <!-- Contenido del modal -->
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/flowbite@2.2.1/dist/flowbite.min.js"></script>
</body>
</html>
```

### Componentes Disponibles

- Dropdowns
- Modals
- Tooltips
- Carousels
- Navbars
- Forms
- Y más...

Ver documentación: https://flowbite.com/docs/

## 📊 Monitoring y Debugging

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo web
docker-compose logs -f web

# Solo PostgreSQL
docker-compose logs -f db
```

### Inspeccionar Contenedor

```bash
# Entrar al contenedor web
docker-compose exec web bash

# Ver variables de entorno
docker-compose exec web env

# Ver procesos
docker-compose exec web ps aux
```

### Health Checks

```bash
# Estado de los servicios
docker-compose ps

# Health check de PostgreSQL
docker-compose exec db pg_isready -U jicuser

# Health check de MinIO
curl http://localhost:9000/minio/health/live
```

## 🚀 Despliegue en Producción

### Configuración para Servidor JIC

1. **Actualizar docker-compose.prod.yml**
2. **Configurar Nginx con SSL**
3. **Usar variables de entorno seguras**
4. **Compilar CSS para producción**

```bash
# Compilar TailwindCSS
npm run tailwind:build

# Recolectar estáticos
docker-compose exec web python mysite/manage.py collectstatic --noinput

# Usar docker-compose de producción
docker-compose -f docker-compose.prod.yml up -d
```

### Checklist Pre-Producción

- [ ] DEBUG=False en .env
- [ ] SECRET_KEY único y seguro
- [ ] Configurar ALLOWED_HOSTS
- [ ] SSL configurado en Nginx
- [ ] Backups automáticos configurados
- [ ] Logs configurados
- [ ] MinIO con credenciales seguras
- [ ] PostgreSQL con contraseña fuerte

## 🐛 Solución de Problemas

### Error: Puerto 8000 ocupado

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"
```

### MinIO no accesible

```bash
# Verificar que el contenedor esté corriendo
docker-compose ps minio

# Reiniciar MinIO
docker-compose restart minio
```

### TailwindCSS no compila

```bash
# Verificar logs
docker-compose logs tailwind

# Reinstalar node_modules
docker-compose down
docker volume rm jic-wagtail-cms_node_modules
docker-compose up --build
```

### Error de permisos en Linux

```bash
sudo chown -R $USER:$USER .
```

## 📚 Recursos

- [Wagtail Docs](https://docs.wagtail.org/)
- [Django Docs](https://docs.djangoproject.com/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Flowbite Components](https://flowbite.com/docs/getting-started/introduction/)
- [MinIO Python Client](https://min.io/docs/minio/linux/developers/python/minio-py.html)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## 👥 Equipo

Desarrollado para JIC por el equipo de desarrollo.

## 📄 Licencia

Uso interno de JIC.

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2026  
**Python**: 3.11+  
**Sistema Operativo**: Linux
