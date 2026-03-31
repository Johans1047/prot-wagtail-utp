# JIC Web Page (Django + Wagtail)

> Sitio web para la Jornada de Iniciacion Cientifica (JIC), construida con Django 5.2 y Wagtail 7.0, con administracion de contenido, recursos multimedia y resultados de proyectos.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Django](https://img.shields.io/badge/django-5.2-green)
![Wagtail](https://img.shields.io/badge/wagtail-7.0-purple)

## Features

✨ **Características principales del proyecto**:

### 📝 CMS Integrado (Wagtail)

- **Administración sin código**: Editores no técnicos pueden crear/modificar contenido desde `/panel/admin/`
- **Snippet CRUD**: 15+ tipos de snippets reutilizables (FAQ, Eventos, Premios, Videos, Recursos, Consultores, etc.)
- **Vista previa en directo**: Cambios visibles en tiempo real antes de publicar
- **Historial de versiones**: Cada cambio queda registrado; posibilidad de revertir
- **Ejemplo**: Un organizador puede subir un evento nuevo, asignarlo a una categoría, y aparece automáticamente en `/eventos/` sin que ingeniero toque código

### 🌐 Sitio Institucional Completo

- **Páginas públicas**: Inicio, Aboutus, Participar, Noticias, Proyectos, Resultados, Recursos, Contacto
- **Navegación jerárquica**: Estructura con subpáginas y categorías
- **Búsqueda full-text**: Campo de búsqueda que indexa proyectos, noticias y recursos
- **Blog/Noticias**: Listado cronológico con filtros por autor, categoría, fecha
- **Ejemplo**: Visitante accede `/proyectos/`, ve lista, filtra por año=2024 y categoría=Ingeniería, hace click en proyecto individual

### 🔌 Integración con API Externa

- **Recuperación de datos históricos**: Consulta API de proyectos JIC (externo) sin bloquear sitio
- **Fallback inteligente**: Si API cae, usa datos locales de BD; usuario no ve degradación
- **Circuit breaker + cache**: Evita sobrecargar API; cachea respuestas 24h
- **Sync automático**: Comando que descarga nuevos proyectos cada 7 días (configurable)
- **Ejemplo**: Admin corre `python manage.py sync_projects_api` → trae 100 proyectos nuevos a BD → aparecen en `/proyectos/` sin reiniciar

### 🖼️ Gestión Multimedia Robusta

- **Storage en MinIO (S3-compatible)**: Imagenes y documentos en objeto storage escalable
- **Compresión automática**: Convertir JPEG→WebP, redimensionar automáticamente por devices (mobile, tablet, desktop)
- **Biblioteca centralizada**: Todos los uploads van a `/panel/documents/` y `/panel/images/`
- **Reuso de media**: Reutiliza misma imagen/doc en múltiples lugares sin duplicar
- **Backup fácil**: MinIO soporta S3 replication; facilita disaster recovery
- **Ejemplo**: Editor sube `award-2024.pdf` desde admin → MinIO lo almacena → si sitio migra server, archivo autocontiene URL presignada

### 📦 Despliegue Containerizado (Docker)

- **Dev = Prod**: Al mismo contenedor (Python 3.11-slim) en ambos entornos
- **Servicios orquestados**: PostgreSQL, MinIO, app, Nginx todo en compose (2 comandos: up/down)
- **Replicación BD**: En producción, Master-Slave de PostgreSQL para alta disponibilidad
- **Reverse proxy Nginx**: Compresión gzip, https terminación, cache de estaticos
- **Entrypoint automático**: Migraciones de BD automáticas al startup (entrypoint.prod.sh)
- **Ejemplo**: `docker compose -f docker-compose.prod.yml up -d --build` → 20s después, sitio listo con BD migrada y MinIO disponible

### 🛠️ Comandos de Gestión Avanzados

- **Sincronización**: Se datos entre BD y MinIO, API externa, migraciones
- **Carga de datos**: Seed inicial (FAQ, eventos, premios) desde fixtures o CSV
- **Mantenimiento**: Recomprimir imagenes, verificar integridad, limpiar media huérfana
- **Reporte**: Estadísticas de uso, usuarios activos, proyectos por categoría
- **Ejemplo**: `docker exec jicweb_app python manage.py load_jic_dates --year 2024 --batch-size 100` → Load 100 eventos del 2024 sin bloquear

### 🎯 Optimizaciones Admin Personalizadas

- **Contador "Usos Frontend"**: Cada snippet muestra si está siendo usado en sitio público (is_active=True) → rápido saber qué está "vivo"
- **Ordenamiento automático**: Al mover/eliminar/crear items, sort_order se recalcula automáticamente sin gaps (siempre 0..N)
- **Ordenamiento por categoría**: FAQ ordenadas dentro de su categoría, Events dentro de su grupo, etc.
- **Bulk actions**: Seleccionar 10 eventos, activarlos todos de un click, cambiar categoría en batch
- **Ejemplo**: Admin ve columna "Usos=0" para una FAQ → no está activa en `/preguntas/` → edita, marca is_active=True → página recalcula sort_order, aparece en posición 5

## Stack Tecnico

### Arquitectura de capas

```
┌─────────────────────────────────────────────────────────────┐
│  Cliente (Navegador)                                        │
│  - Accede sitio publico (frontend)                          │
│  - O admin Wagtail (CMS) / Django admin                     │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/HTTPS
┌──────────────▼──────────────────────────────────────────────┐
│  Nginx (Reverse Proxy + Static Server)                      │
│  - Recibe peticiones, rutea a Gunicorn                      │
│  - Sirve archivos CACHE/CSS/JS sin tocar Python            │
│  - SSL/TLS en produccion                                    │
└──────────────┬──────────────────────────────────────────────┘
               │ Proxy local unix
┌──────────────▼──────────────────────────────────────────────┐
│  Gunicorn (App Server)                                      │
│  - Ejecuta aplicacion Django en 4 workers (prod)           │
│  - Maneja vistas, ORM queries, autenticación               │
│  - Timeout: 120s por petición                              │
└──────────────┬──────────────────────────────────────────────┘
               │ Conexiones
     ┌─────────┴─────────┐
     │                   │
┌────▼──────────────┐  ┌▼────────────────────┐
│  PostgreSQL 15    │  │  MinIO S3-compat    │
│  (Master-Slave)   │  │  (Media Storage)    │
│                   │  │                     │
│ - Contenido       │  │ - Imagenes          │
│ - Usuarios        │  │ - Documentos        │
│ - Proyectos       │  │ - PDFs              │
│ - Configuracion   │  │ - Videos            │
└───────────────────┘  └─────────────────────┘

Frontend (HTML/CSS/JS en navegador):
└─ TailwindCSS (compilado a CSS) 
└─ Wagtail JS (CMS interactions)
```

### Componentes principales y responsabilidades

**Django 5.2** (Backend framework):
- Maneja rutas HTTP en [jic/mysite/web/urls.py](jic/mysite/web/urls.py)
- ORM accede PostgreSQL via `models.py`; maneja relaciones, validación, signals
- Views procesa lógica de negocio; renderiza templates HTML o retorna JSON APIs
- Autenticación/autorizacion via `django.contrib.auth`

**Wagtail 7.0** (CMS integrado en Django):
- Interfaz web en `/panel/admin/` para editar contenido sin tocar código
- Snippet system: CRUD para items reutilizables (FAQs, Events, Awards, etc.)
- Page tree: jerarquía de paginas editables (no usado intensivamente aqui)
- Image/Document library: repositorio centralizado con thumbnails automáticos

**PostgreSQL 15** (Base de datos):
- Almacena todas las tablas Django (django_*, auth_*, wagtail*, web_*)
- Master-Slave replication en produccion (redundancia)
- Volumen persistente en Docker (data no se pierde al reiniciar)

**MinIO** (S3-compatible storage):
- Recibe media uploads desde Django app
- Devuelve URLs publicas para imagenes/documentos
- Bucket structure: `jic/` (media) y otros buckets para backups
- Console web en puerto 9001 para inspeccionar buckets

**Gunicorn** (App server produccion):
- Lee Django code y ejecuta en procesos workers
- 4 workers por defecto (paralelismo)
- Timeout 120s; rechaza peticiones que tarden mas
- Logs a stdout para monitoreo

**Nginx** (Reverse proxy + static server):
- Recibe todas las peticiones HTTP/HTTPS (puerto 80/443)
- Rutea `/static/` a disco local (rápido, sin Python)
- Rutea `/` a Gunicorn (mantiene conexion persistente)
- Comprime respuestas con gzip

**TailwindCSS** (Frontend styling):
- Utility-first CSS framework (clasessímplemente aplicadas a HTML)
- Compilado en archivo CSS final empaquetado
- Watcher automático en desarrollo: `.css` regenera al cambiar templates

### Dependencias principales

De [requirements.txt](requirements.txt) (desarrollo) y [requirements-prod.txt](requirements-prod.txt) (produccion):

**Core framework**:
- Django 5.2, Wagtail 7.0 — Framework + CMS
- psycopg2-binary — Driver PostgreSQL
- minio — Cliente SDK para MinIO

**Imagenes y media**:
- Pillow — Procesamiento de imagenes (thumbnails, EXIF)
- django-imagekit — Soporte para image fields con transformaciones

**Compresion y build**:
- django-compressor — Minifica CSS/JS automaticamente
- whitenoise — Sirve estaticos desde Gunicorn sin Nginx (fallback)

**Desarrollo local**:
- django-livereload-server — Recarga automatica al guardar (DevX)
- python-dotenv — Carga variables desde .env local

**Datos y utilitarios**:
- pandas — Procesamiento de datos (reportes, imports)
- Pillow, requests — Utilidades generales

## Quick Start

### Prerrequisitos

- **Python 3.11+** — Lenguaje de desarrollo; verifica con `python --version`.
- **Docker y Docker Compose** (recomendado) — Empaquetan servicios (app, BD, MinIO) en contenedores aislados.
- **PostgreSQL y MinIO** (solo si ejecutas sin Docker) — Servidores necesarios que Docker montará automaticamente.
- **Git** — Para clonar el repo (si aun no lo tienes localmente).

## Opcion A: Desarrollo con Docker (RECOMENDADO)

Mas simple: no instalas PostgreSQL ni MinIO manualmente; Docker lo hace.

1. **Configura variables de entorno**:

   ```bash
   # Copiar desde el ejemplo
   cp .env.prod .env
   # Editar .env con valores locales (DEBUG=True, hosts=localhost, etc.)
   ```

2. **Levanta los servicios** (app, DB, MinIO):

   ```bash
   docker compose up -d --build
   ```

   Esto buildea imagenes y levanta contenedores. Ver logs en tiempo real:
   ```bash
   docker compose logs -f jicweb_app
   ```

3. **Aplicar migraciones** (primera vez o si hay migraciones nuevas):

   ```bash
   docker exec jicweb_app python manage.py migrate
   ```

4. **Crear usuario admin** (primera vez):

   ```bash
   docker exec -it jicweb_app python manage.py createsuperuser
   ```
   Sigue las indicaciones: usuario, email, password.

5. **Cargar datos iniciales** (opcional pero recomendado):

   ```bash
   docker exec jicweb_app python manage.py load_jic_dates
   docker exec jicweb_app python manage.py populate_background
   ```

6. **Accede al sitio**:
   - Sitio publico: http://localhost:8000
   - Admin Django: http://localhost:8000/django-admin/ (login con user/pass creado)
   - Admin Wagtail (CMS): http://localhost:8000/panel/admin/
   - MinIO console: http://localhost:9001 (credentials en .env.prod)

## Opcion B: Ejecucion local sin Docker

Mas manual; requiere instalar BD y MinIO localmente previa.

1. **Crear y activar entorno virtual**:

   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar .env local**:

   ```bash
   # Crear .env en raiz
   DEBUG=True
   POSTGRESQL_HOST=localhost
   POSTGRESQL_PORT=5432
   MINIO_ENDPOINT=localhost:9000
   JIC_PROJECTS_API_URL=http://localhost:8001/api/proyectos-jic
   ```

4. **Ejecutar migraciones**:

   ```bash
   cd jic/mysite
   python manage.py migrate
   ```

5. **Crear usuario admin**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar servidor**:

   ```bash
   python manage.py runserver
   ```

   Sitio accesible en: http://localhost:8000

   **Nota**: manage.py selecciona settings automaticamente segun DEBUG:
   - `DEBUG=True` carga `mysite.settings.dev`
   - `DEBUG=False` carga `mysite.settings.base` (produccion)

## Produccion (Compose)

Para compose de produccion se usa [docker-compose.prod.yml](docker-compose.prod.yml), [Dockerfile.prod](Dockerfile.prod) y [entrypoint.prod.sh](entrypoint.prod.sh).

Comando habitual:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build --force-recreate
```

## Endpoints y Rutas Principales

Las rutas están definidas en [jic/mysite/mysite/urls.py](jic/mysite/mysite/urls.py) (raiz) y [jic/mysite/web/urls.py](jic/mysite/web/urls.py) (app).

### Sitio Público (Frontend)

Todas las rutas devuelven HTML renderizado con templates de Django.

| Ruta | Método | Descripcion |
|------|--------|-------------|
| `/` | GET | Página de inicio (homepage). Muestra banner, secciones destacadas. |
| `/acerca-de/` | GET | Información general sobre JIC, historia, objetivos. |
| `/acerca-de/coordinadores/` | GET | Listado de coordinadores y equipo organizador. |
| `/participar/` | GET | Guia para participantes: como inscribirse, requisitos, plazos. |
| `/noticias/` | GET | Listado de noticias/blog posts con paginación. |
| `/noticias/<slug>/` | GET | Vista detalle de una noticia individual. |
| `/proyectos/` | GET | Listado de proyectos historicos con filtros (categoría, año). |
| `/proyectos/<id>/` | GET | Detalle de proyecto individual: descripción, investigadores, resultados. |
| `/resultados/` | GET | Resumen de resultados del evento (estadísticas, ganadores). |
| `/resultados/selecciones/` | GET | Tabla detallada de selecciones y premios. |
| `/recursos/` | GET | Biblioteca de recursos (guias, plantillas, documentos descargables). |
| `/contacto/` | GET | Formulario de contacto; POST envía email. |
| `/busqueda/` | GET | Busqueda full-text en proyectos, noticias, recursos. Parámetro: `?q=keywords` |

**Acceso**: En local → http://localhost:8000/ruta

### Admin y Gestión

Estas rutas requieren autenticación de usuario administrador.

#### Django Admin (Legacy)

| Ruta | Acceso | Proposito |
|------|--------|-----------|
| `/django-admin/` | Solo staff=True | Admin nativo Django (permisos modelo, usuarios, groups) |
| `/django-admin/auth/user/` | Staff | CRUD de usuarios system |
| `/django-admin/auth/group/` | Staff | Gestión de permisos por grupo |

**Nota**: En produccion, preferir `/panel/admin/` (Wagtail) en lugar de este.

#### Wagtail Admin (CMS Recomendado)

| Ruta | Acceso | Descripcion |
|------|--------|-------------|
| `/panel/admin/` | Logged-in user | Dashboard principal del CMS Wagtail |
| `/panel/admin/snippets/` | Editor | CRUD de snippets: FAQ, Eventos, Awards, Videos, etc. (15+ tipos) |
| `/panel/admin/pages/` | Page Editor | Jerarquía de paginas editables (menos usado aqui) |
| `/panel/documents/` | Editor | Library centralizada de documentos uploadados |
| `/panel/images/` | Editor | Library centralizada de imagenes con thumbnails automáticos |

**Acceso**: http://localhost:8000/panel/admin/

**Features admin**:
- `frontend_usage_count`: Columna que muestra qué items están activos (is_active=True) en frontend
- `sort_order`: Campo automático que mantiene ordenamiento compacto (0..N sin gaps) cuando items se crean, mueven o eliminan
- Bulk actions: Activar/desactivar múltiples items, cambiar categoría, eliminar

### APIs Internas (JSON)

Algunos endpoints devuelven JSON para consumir desde frontend JavaScript o clientes externos.

| Ruta | Método | Descripcion | Response |
|------|--------|-------------|----------|
| `/api/proyectos/` | GET | Listado de proyectos en JSON (paginado) | `{count, next, previous, results: [...]}`|
| `/api/proyectos/<id>/` | GET | Detalle de proyecto JSON | `{id, name, description, ...}` |
| `/api/noticias/` | GET | Listado de noticias en JSON | Igual estructura |
| `/api/categorias/` | GET | Listado de categorias/tags disponibles | `{results: [{id, name}, ...]}` |

**Headers** (si aplica autenticacion futura):
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Parámetros comunes de query**:
- `?page=2` — Paginación
- `?limit=25` — Items por página (default 20)
- `?search=keyword` — Búsqueda
- `?category=1` — Filtro por categoría
- `?year=2024` — Filtro por año

### External Mock API

Servicio FastAPI en [mock_projects_api/](mock_projects_api) que simula datos históricos de proyectos (solo en docker-compose de desarrollo).

| Ruta | Proposito |
|------|-----------|
| `/health` | Health check; devuelve `{"status": "ok"}` |
| `/api/proyectos-jic` | Listado mock de proyectos historicos (responde a `JIC_PROJECTS_API_URL`) |

**Acceso local**: http://localhost:8001/health

**En .env de desarrollo**: `JIC_PROJECTS_API_URL=http://jic_projects_mock_api:8001/api/proyectos-jic`

## Configuracion

### Variables de Entorno

Todas las variables se configuran en archivos `.env` (desarrollo) o via `docker-compose` segun el entorno.

#### Django Core

| Variable | Ejemplo | Descripcion |
|---|---|---|
| **DEBUG** | `True` / `False` | En `True`: servidor de desarrollo, errores detallados, autorecarga. En `False`: settings de produccion, errores seguros. Tambien controla que settings se carguen (`dev` vs `base`). |
| **DJANGO_SECRET_KEY** | `J5u_gSJHz9!wyIe...` | Clave criptografica para sesiones, CSRF, tokens. Cambiar en produccion por seguridad. |
| **DJANGO_ALLOWED_HOSTS** | `localhost,127.0.0.1,example.com` | Hosts validos separados por coma; Django rechaza requests a otros dominios (proteccion HTTP Host Header). |

#### Base de Datos (PostgreSQL)

| Variable | Ejemplo | Descripcion |
|---|---|---|
| **POSTGRESQL_DATABASE** | `db_jicweb` | Nombre de la base de datos que la app consultara. |
| **POSTGRESQL_POSTGRES_USERNAME** | `postgres` | Usuario postgres que la app usa para conectarse. |
| **POSTGRESQL_POSTGRES_PASSWORD** | `1*o63U9JlN5bLp` | Contrasena del usuario de base de datos. |
| **POSTGRESQL_HOST** | `jicweb_master` (docker) o `localhost` (local) | Host del servidor PostgreSQL. En Docker usa el nombre del servicio. |
| **POSTGRESQL_DATABASE_PORT_NUMBER** | `5432` | Puerto de PostgreSQL (estandar 5432). |
| **DB_REPLICATION_ENABLED** | `False` | Habilita logica de replicacion master-slave. Aparentemente desactivado en desarrollo. |

#### Storage de Media (MinIO S3-compatible)

| Variable | Ejemplo | Descripcion |
|---|---|---|
| **MINIO_ENDPOINT** | `jic_minio_storage:9000` | Host y puerto de MinIO. En Docker es el nombre del servicio. |
| **MINIO_ACCESS_KEY** | `k0RjKo7kyRwbswMs...` | ID de acceso S3/MinIO (similar a AWS Access Key ID). |
| **MINIO_SECRET_KEY** | `D8rIiXbK58MXPjyU...` | Clave secreta S3/MinIO (similar a AWS Secret Access Key). |
| **MINIO_BUCKET_NAME** | `jic-media` | Nombre del bucket donde se almacenan imagenes y documentos. |
| **MINIO_USE_SSL** | `False` / `True` | Usa HTTPS para conectarse a MinIO (false localmente, true en produccion). |

#### API de Proyectos JIC

| Variable | Ejemplo | Descripcion |
|---|---|---|
| **JIC_PROJECTS_API_URL** | `http://jic_projects_mock_api:8001/api/proyectos-jic` | URL del endpoint que devuelve proyectos historicos. Si no se define, usa datos mock locales (fallback). Utiliza cache + circuit breaker para evitar bloqueos. |
| **JIC_PROJECTS_API_TIMEOUT** | `5` | Segundos para esperar respuesta de la API antes de timeout. Evita bloquear el sitio si API cae. |
| **JIC_PROJECTS_PREFER_API** | `0` / `1` | Si vale 1, consulta API primero; si 0, usa datos locales de BD. Util para AB testing diferente datos. |
| **JIC_PROJECTS_AUTO_SYNC_DB** | `1` | Si vale 1, comando `sync_projects_api` puede sincronizar API hacia BD localmente. |
| **JIC_PROJECTS_SYNC_INTERVAL** | `604800` | Segundos entre sincronizaciones automaticas programadas (604800 = 7 dias). |

**Ejemplo .env para desarrollo local**:

```bash
DEBUG=True
DJANGO_SECRET_KEY=insecure-dev-key-change-in-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRESQL_DATABASE=db_jicweb
POSTGRESQL_POSTGRES_USERNAME=postgres
POSTGRESQL_POSTGRES_PASSWORD=devpass
POSTGRESQL_HOST=localhost
POSTGRESQL_DATABASE_PORT_NUMBER=5432

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=mast_st_jic
MINIO_SECRET_KEY=KtWzuaY3Uy8F
MINIO_BUCKET_NAME=jic-media
MINIO_USE_SSL=False

JIC_PROJECTS_API_URL=http://localhost:8001/api/proyectos-jic
JIC_PROJECTS_API_TIMEOUT=3
JIC_PROJECTS_PREFER_API=0
JIC_PROJECTS_AUTO_SYNC_DB=1
```

## Comandos de Gestion Utiles

Comandos disponibles en [jic/mysite/web/management/commands](jic/mysite/web/management/commands) para tareas de mantenimiento y sincronizacion de datos:

### Sincronizacion de Proyectos

```bash
python jic/mysite/manage.py sync_projects_api
```

**Proposito**: Sincroniza proyectos desde la API externa (jic_projects_api) a la base de datos local.

**Cuándo usar**: 
- Periodicamente para mantener BD actualizada con proyectos nuevos/modificados.
- Manualmente si se actualizo la API y necesitas traer cambios.
- Se ejecuta automaticamente si `JIC_PROJECTS_AUTO_SYNC_DB=1`.

**Logica**: Consulta `JIC_PROJECTS_API_URL`, normaliza datos (universidades, categories), y almacena en tablas `project`, `consultant`, etc.

### Sincronizacion MinIO

```bash
python jic/mysite/manage.py sync_minio
```

**Proposito**: Sincroniza archivos multimedia (imagenes, documentos) entre storage local y MinIO.

**Cuándo usar**:
- Despues de cargar archivos localmente y necesitas subirlos a MinIO.
- Recovery o backup: descargar desde MinIO a disco local.
- Verificar integridad de archivos entre storages.

### Recompresion de Imagenes Wagtail

```bash
python jic/mysite/manage.py recompress_wagtail_images
```

**Proposito**: Reprocesa todas las imagenes en Wagtail aplicando compresion y optimizacion configurada.

**Cuándo usar**:
- Cambio de parametros de compresion (JPEG_QUALITY, WEBP_QUALITY, etc.).
- Imagenes viejas con diferentes configuraciones necesitan estandarizacion.
- Recuperar espacio: reconvertir a WebP o reducir dimensiones.

### Configurar Flujo de Noticias

```bash
python jic/mysite/manage.py setup_news_workflow
```

**Proposito**: Inicializa workflow/permisos para edicion de Blog (noticias) en Wagtail.

**Cuándo usar**:
- Instalacion inicial del sitio; prepara grupos de editores, publicadores, etc.
- Reset de permisos si se corrompieron.

### Cargar Fechas JIC

```bash
python jic/mysite/manage.py load_jic_dates
```

**Proposito**: Carga datos iniciales de fechas importantes (timeline JIC: inicio convocatoria, cierre, nacional, etc.).

**Cuándo usar**:
- Primera vez que configures el sitio (carga data de referencia).
- Si borras las fechas importantes por error.
- Actualizar fechas para nuevo año JIC.

### Poblar Antecedentes

```bash
python jic/mysite/manage.py populate_background
```

**Proposito**: Carga datos de antecedentes/historia (seccion "Acerca de JIC").

**Cuándo usar**:
- Instalacion inicial; trae timeline historico del programa.
- Reset de datos de background.

### Ejecucion en Docker

Para ejecutar comandos dentro del contenedor:

```bash
docker exec jicweb_app python manage.py sync_projects_api
docker exec jicweb_app python manage.py sync_projects_api --skip-checks
docker exec jicweb_app python manage.py recompress_wagtail_images
docker exec jicweb_app python manage.py setup_news_workflow
```

Tambien puedes entrar en el contenedor interactivamente:

```bash
docker exec -it jicweb_app bash
cd mysite
python manage.py sync_projects_api
```

### Uso en Produccion (dentro de Dockerfile/entrypoint)

Los comandos se ejecutan automaticamente como parte del startup:
- `entrypoint.prod.sh` corre `collectstatic` para compilar assets estaticos.
- `migrate --noinput` aplica migraciones pendientes.

Comandos puntuales en produccion (via SSH o CI/CD):

```bash
# Sincronizar proyectos recientes
docker exec jicweb_app python manage.py sync_projects_api

# Recomprimir imagenes viejas (puede tardar, ejecutar en offpeak)
docker exec jicweb_app python manage.py recompress_wagtail_images --batch-size=10

# Ver estado de sincronizacion
docker exec jicweb_app python manage.py debug_projects
```

## Estructura del Proyecto

### Raíz del repositorio

```text
.
├── docker-compose.yml              # Orquestación local (app, PostgreSQL, MinIO, Redis)
├── docker-compose.prod.yml         # Orquestación produccion (replicacion BD, volumes, networks)
├── Dockerfile                      # Imagen Docker de desarrollo (Python 3.11, deps dev)
├── Dockerfile.prod                 # Imagen Docker produccion (optimizada, sin dependencias dev)
├── entrypoint.prod.sh              # Script que ejecuta migraciones y levanta Gunicorn en prod
├── requirements.txt                # Dependencias Python con extras para desarrollo
├── requirements-prod.txt           # Dependencias Python para produccion (minificadoras)
├── jic/                            # Django project root
└── mock_projects_api/              # Servicio auxiliar FastAPI para simular API externa
```

### Carpeta principal: `jic/mysite/`

**Anatomía de un proyecto Django + Wagtail**:

```text
jic/mysite/
│
├── manage.py                       # Utilidad CLI de Django
│                                     - Cria BD, migraciones, usuarios
│                                     - Levanta runserver
│                                     - Comprime CSS/JS (collectstatic)
│
├── mysite/                         # Configuracion del proyecto Django
│   ├── __init__.py
│   ├── settings/                   # Configuracion por entorno
│   │   ├── __init__.py
│   │   ├── base.py               # Configuracion base (DB, installed apps, middleware, logging)
│   │   ├── dev.py                # Desarrollo: DEBUG=True, livereload, sin HTTPS
│   │   └── production.py         # Produccion: DEBUG=False, HTTPS, cache, compresion
│   │
│   ├── urls.py                     # Rutas HTTP raiz; incluye urls de apps
│   ├── wsgi.py                     # Interfaz WSGI para servidores (Gunicorn)
│   ├── context_processors.py       # Contexto global para templates (variables en todos los context)
│   ├── storage.py                  # Configuracion de storage personalizado (MinIO)
│   │
│   ├── templates/                  # Templates base del sitio
│   │   ├── base.html              # Layout maestro (navbar, footer, main flex-1)
│   │   ├── 404.html               # Pagina error no encontrado
│   │   └── 500.html               # Pagina error servidor
│   │
│   └── static/                     # Archivos estaticos (CSS, JS, imagenes)
│       ├── CACHE/                 # Comprimidos por django-compressor
│       ├── css/                   # Stylesheets compilados
│       └── js/                    # JavaScript
│
├── web/                            # App principal (logica de negocio)
│   ├── models.py                   # 15+ modelos: FAQ, Event, Award, etc.
│   │                                - FrontendUsageMixin (contador admin)
│   │                                - AutoSortOrderMixin (reordenamiento automatico)
│   │
│   ├── views.py                    # Vistas de listado, detalle (home, events, etc.)
│   ├── urls.py                     # Rutas de la app web (/events/, /awards/, etc.)
│   ├── admin.py                    # Configuracion Django admin (solo legacy)
│   ├── wagtail_hooks.py            # 17 ViewSets Wagtail para CRUD admin
│   ├── signals.py                  # Handlers para save/delete (triggers)
│   ├── utils.py                    # Funciones utilitarias
│   ├── policies.py                 # Politicas de acceso, permisos
│   ├── image_pipeline.py           # Procesamiento de imagenes (resize, format)
│   │
│   ├── forms/                      # Formularios Django (search, bulk actions)
│   │   ├── forms.py
│   │   ├── collection_forms.py
│   │   └── image_forms.py
│   │
│   ├── services/                   # Servicios de negocio (capa intermedia)
│   │   ├── __init__.py
│   │   └── [servicios de integracion/procesamiento]
│   │
│   ├── migrations/                 # Versiones de BD (schema changes)
│   │   ├── 0001_initial.py
│   │   ├── ...
│   │   └── NNNN_descripcion.py
│   │
│   ├── management/commands/        # Comandos custom (python manage.py load_jic_dates)
│   │   └── commands/
│   │
│   └── templates/web/              # Templates para vistas (listados, detalles)
│       ├── event_list.html
│       ├── award_list.html
│       └── ...
│
├── home/                           # App de homepage (opcional)
│   └── [templates, migrations]
│
├── search/                         # Integracion busqueda Wagtail (opcional)
│   └── views.py
│
├── theme/                          # App para temas y frontend
│   ├── static/                     # Archivos TailwindCSS compilados
│   │   ├── admin/                 # Overrides de admin styles
│   │   ├── css/                   # TailwindCSS
│   │   ├── js/                    # JavaScript de tema
│   │   ├── src/                   # Fuentes TailwindCSS (antes de compilar)
│   │   └── img/                   # Imagenes de tema
│   │
│   ├── templates/wagtailadmin/    # Customizacion del CMS Wagtail
│   ├── tailwind_watcher.py        # Monitorea cambios en CSS (dev)
│   └── migrations/
│
└── staticfiles/                    # Ruta donde collectstatic guarda todo (prod)
    └── [copia de todos los static/]
```

### App `web/` en detalle

Esta es la app principal donde vive la lógica:

| Archivo | Propósito |
|---------|-----------|
| models.py | 15+ snippets (FAQ, Evento, Award, Video, etc.) con mixins de contador + ordenamiento automático |
| views.py | Vistas de listado, detalle, búsqueda (ej: EventListView renderiza event_list.html) |
| urls.py | Rutas HTTP: `/events/`, `/awards/`, `/search/`, etc. |
| wagtail_hooks.py | 17 ViewSets Wagtail: admin CRUD con frontend_usage_count en list_display |
| forms/ | Formularios de búsqueda, bulk actions, image upload |
| services/ | Integración con API externa de proyectos (HTTP requests, caching) |
| utils.py | Helpers: slugify, formateo de texto, parse de CSV |
| policies.py | Control de acceso por roles (profesor, admin, visitante) |
| management/commands/ | Scripts custom: `python manage.py load_jic_dates` (seed datos iniciales) |

### Carpeta `mock_projects_api/`

Servicio FastAPI independiente que simula la API de proyectos JIC:

```text
mock_projects_api/
├── app.py                 # FastAPI con endpoints /health, /api/proyectos-jic
├── requirements.txt       # fastapi, uvicorn
└── README.md             # Documentacion del mock
```

**Uso**: Cuando la API real (externa) no está disponible, Docker levanta este mock en puerto 8001. 
La variable `JIC_PROJECTS_API_URL` en .env apunta a este endpoint para desarrollo.

## Filtrado Robusto: Categorías y Universidades (Proyectos)

### Conceptualización

El sistema implementa normalización canónica para categorías de proyectos y nombres de universidades, similar a la usada en FAQ. Esto garantiza que:

1. **Un solo nombre oficial para cada categoría/universidad** — No importa cómo se ingrese (mayúsculas, acentos, siglas), se convierte a la forma canónica
2. **Filtros confiables** — Búsquedas/filtros por categoría devuelven todos los proyectos aunque estén catalogados con variantes
3. **Escalabilidad** — Al agregar nuevas categorías/universidades, aliases se amplían automáticamente sin tocar código

### Implementación: Modelo `project`

En [jic/mysite/web/models.py](jic/mysite/web/models.py), la clase `project` define:

**Categorías canónicas**:
```python
CATEGORY_CHOICES = [
    ("Ingeniería", "Ingeniería"),
    ("Ciencias de la Salud", "Ciencias de la Salud"),
    ("Ciencias Naturales y Exactas", "Ciencias Naturales y Exactas"),
    ("Ciencias Sociales y Humanísticas", "Ciencias Sociales y Humanísticas"),
]
```

**Aliases de categorías** (variantes que mapean a canónicas):
```python
CATEGORY_ALIASES = {
    "0": "Ingeniería",                              # Legacy index
    "ingenieria": "Ingeniería",                     # Lowercase
    "ciencias de la salud": "Ciencias de la Salud", # Spanish variants
    # ... más aliases predefinidos
}
```

**Universidades canónicas + aliases** (igual patrón, lista completa de 10 universidades oficiales).

### Métodos de normalización

| Método | Propósito | Entrada | Salida |
|--------|-----------|---------|--------|
| `normalize_category(value)` | Mapea variante a canónica | `"ingenieria"` | `"Ingeniería"` |
| `normalize_university(value)` | Mapea variante a canónica | `"utp"` | `"Universidad Tecnológica de Panamá"` |
| `_normalize_text_key(value)` | Genera key ASCII normalizada para matching | `"Ciências de la Salud"` | `"ciencias de la salud"` |

### Flujo: Creación/Actualización de Proyectos

1. **Admin/API ingresa proyecto** con categoría=`"ingenieria"` o universidad=`"UTP"`
2. **`project.save()`** intercepta y normaliza automáticamente:
   - `category` → `"Ingeniería"`
   - `university` → `"Universidad Tecnológica de Panamá"`
3. **BD almacena valor canónico** → predicible, queryable
4. **Filtros/búsquedas usan valor canónico** → no hay "falsos negativos"

### Migración de datos existentes

**Archivo**: [jic/mysite/web/migrations/0044_normalize_project_categories_universities.py](jic/mysite/web/migrations/0044_normalize_project_categories_universities.py)

Ejecutada al hacer `migrate`:
```bash
docker exec jicweb_app python manage.py migrate web
# Salida: ✓ Normalized 142 projects to canonical categories and universities
```

Revierte duplicados/inconsistencias en datos legados (importados antes de que existiera normalización).

### Integración con `ImportService`

En [jic/mysite/web/services/import_service.py](jic/mysite/web/services/import_service.py):

```python
@staticmethod
def _normalize_category(raw_value) -> str:
    """Delegates to project.normalize_category() to avoid duplication."""
    return project.normalize_category(ImportService._clean_optional_text(raw_value))
```

**Ventaja**: Reutiliza aliases del modelo → 1 único lugar donde mantenerlos. CSV imports automáticamente usan categorías canónicas.

### Agregar nuevas categorías o universidades

**Si surge nueva categoría en futuro** (ej: "Artes"):

1. Agregar a `CATEGORY_CHOICES` en [models.py](jic/mysite/web/models.py):
   ```python
   CATEGORY_CHOICES = [
       # ... existing
       ("Artes y Diseño", "Artes y Diseño"),  # NEW
   ]
   ```

2. Agregar aliases (variantes):
   ```python
   CATEGORY_ALIASES = {
       # ... existing
       "artes": "Artes y Diseño",             # NEW
       "artes y diseno": "Artes y Diseño",    # NEW
   }
   ```

3. **Datos antiguos no requieren cambio** — `normalize_category()` solo usa CATEGORY_ALIASES; valores no-matching se aceptan como fallback.

4. Opcionalmente, crear migración data para "canonicalizar atrás" valores legacy.

### Beneficios de este diseño

✅ **Single source of truth** — Aliases definidos una sola vez en modelo  
✅ **DRY principle** — No duplicar normalización en import_service, views, etc.  
✅ **Escalable** — Agregar categorías no rompe querys existentes  
✅ **Testeable** — `project.normalize_category("ingenieria")` es predecible  
✅ **Compatible con BD** — Valores siempre canónicos → índices efectivos, querys rápidas
