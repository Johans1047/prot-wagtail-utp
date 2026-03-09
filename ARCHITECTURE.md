# 🏗️ Arquitectura del Sistema - JIC Wagtail CMS

Documento técnico de la arquitectura del sistema.

## 📐 Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUARIO FINAL                               │
│                         (Navegador)                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NGINX (Proxy Reverso)                            │
│                    Puerto 80/443                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  SSL/TLS     │  │  Static      │  │  Load        │             │
│  │  Termination │  │  Files       │  │  Balancer    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
┌──────────────────────────────┐  ┌─────────────────┐
│  Django/Wagtail Application  │  │  Static Files   │
│  (Gunicorn)                  │  │  /staticfiles   │
│  Puerto 8000                 │  │                 │
└──────────┬───────────────────┘  └─────────────────┘
           │
           │ Conexiones a:
           │
    ┌──────┼──────────┬────────────┬──────────────┐
    │      │          │            │              │
    ▼      ▼          ▼            ▼              ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│  DB    │ │ MinIO  │ │Tailwind │ │  Media   │ │  Cache   │
│  5432  │ │9000/01 │ │ Watcher │ │  Files   │ │ (Redis)  │
└────────┘ └────────┘ └─────────┘ └──────────┘ └──────────┘
```

## 🔧 Componentes del Sistema

### 1. Frontend Layer

#### Nginx (Producción)
- **Propósito**: Proxy reverso, terminación SSL, servir archivos estáticos
- **Puerto**: 80 (HTTP), 443 (HTTPS)
- **Características**:
  - Terminación SSL/TLS
  - Compresión gzip
  - Cacheo de archivos estáticos
  - Load balancing (si se escala)
  - Rate limiting
  - Security headers

#### TailwindCSS Watcher
- **Propósito**: Compilación automática de CSS
- **Proceso**: Monitorea cambios en archivos fuente
- **Input**: `theme/static/src/input.css`
- **Output**: `theme/static/src/output.css`
- **Modo desarrollo**: Watch mode con hot reload
- **Modo producción**: Compilación minificada única

### 2. Application Layer

#### Django/Wagtail
- **Framework**: Django 4.2.9
- **CMS**: Wagtail 5.2.2
- **WSGI Server**: Gunicorn (producción) / runserver (desarrollo)
- **Puerto**: 8000 (interno)
- **Funcionalidades**:
  - Gestión de contenido
  - Autenticación y autorización
  - Admin interface
  - API REST (opcional)
  - Gestión de imágenes
  - StreamFields
  - Page models

#### Apps Django

```
mysite/
├── mysite/           # Configuración del proyecto
│   ├── settings.py   # Configuración principal
│   ├── urls.py       # Routing principal
│   └── wsgi.py       # WSGI application
├── theme/            # App de tema
│   ├── static/       # Archivos CSS/JS
│   └── templates/    # Templates base
└── web/              # App principal
    ├── models.py     # Modelos de páginas
    ├── views.py      # Vistas
    └── templates/    # Templates específicos
```

### 3. Data Layer

#### PostgreSQL
- **Versión**: 15 (Alpine)
- **Puerto**: 5432
- **Características**:
  - ACID compliance
  - JSON/JSONB support
  - Full-text search
  - Extensiones (pg_trgm para búsqueda)
- **Datos almacenados**:
  - Modelos de páginas
  - Usuarios y permisos
  - Configuración del sitio
  - Metadata de imágenes
  - Registros de revisiones

#### MinIO Object Storage
- **Versión**: Latest
- **Puertos**: 9000 (API), 9001 (Console)
- **Protocolo**: S3-compatible
- **Características**:
  - Almacenamiento distribuido
  - Versionado de objetos
  - Políticas de acceso
  - Encriptación
- **Datos almacenados**:
  - Imágenes subidas por usuarios
  - Documentos
  - Archivos multimedia
  - Backups (opcional)

### 4. Build & Development Tools

#### Docker Compose
- **Propósito**: Orquestación de contenedores
- **Servicios gestionados**:
  - web (Django/Wagtail)
  - db (PostgreSQL)
  - minio (Object Storage)
  - minio-client (Inicialización)
  - tailwind (CSS watcher)
  - nginx (producción)
  - certbot (SSL)

#### Node.js/NPM
- **Propósito**: Gestión de dependencias frontend
- **Paquetes principales**:
  - TailwindCSS
  - Flowbite
  - Plugins de Tailwind

## 🔄 Flujos de Datos

### Flujo de Request HTTP

```
1. Usuario → Nginx
   ↓
2. Nginx valida request y SSL
   ↓
3. Nginx → Django/Gunicorn (puerto 8000)
   ↓
4. Django procesa request
   ↓
5. Django consulta PostgreSQL (datos)
   ↓
6. Django genera URLs de MinIO (imágenes)
   ↓
7. Django renderiza template con TailwindCSS
   ↓
8. Response → Nginx → Usuario
```

### Flujo de Upload de Imagen

```
1. Usuario sube imagen en Admin
   ↓
2. Wagtail procesa imagen (resize, optimize)
   ↓
3. django-storages + boto3 conecta a MinIO
   ↓
4. Imagen se almacena en bucket 'jic-media'
   ↓
5. Metadata se guarda en PostgreSQL
   ↓
6. URL pública se genera
   ↓
7. Usuario puede acceder vía URL MinIO
```

### Flujo de Desarrollo CSS

```
1. Developer edita archivo .html o input.css
   ↓
2. TailwindCSS watcher detecta cambio
   ↓
3. Watcher recompila CSS
   ↓
4. output.css se actualiza
   ↓
5. LiveReload recarga navegador (desarrollo)
   ↓
6. Cambios visibles inmediatamente
```

## 🔐 Modelo de Seguridad

### Capas de Seguridad

```
┌─────────────────────────────────────────┐
│  1. Network Layer (Firewall)            │
├─────────────────────────────────────────┤
│  2. SSL/TLS (Nginx)                     │
├─────────────────────────────────────────┤
│  3. Application (Django Security)        │
│     - CSRF Protection                    │
│     - XSS Protection                     │
│     - SQL Injection Protection           │
├─────────────────────────────────────────┤
│  4. Authentication (Wagtail)            │
│     - User permissions                   │
│     - Admin access control               │
├─────────────────────────────────────────┤
│  5. Data Layer (PostgreSQL)             │
│     - Encrypted connections              │
│     - User isolation                     │
└─────────────────────────────────────────┘
```

### Headers de Seguridad (Nginx)

```nginx
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

## 📊 Escalabilidad

### Escalamiento Horizontal

```
┌─────────────────────────────────────────────────────┐
│              Load Balancer (Nginx)                  │
└──────┬────────────┬────────────┬────────────────────┘
       │            │            │
       ▼            ▼            ▼
   ┌──────┐    ┌──────┐    ┌──────┐
   │ App1 │    │ App2 │    │ App3 │
   └───┬──┘    └───┬──┘    └───┬──┘
       │           │            │
       └───────────┴────────────┘
                   │
            ┌──────┴──────┐
            │             │
            ▼             ▼
        ┌──────┐      ┌──────┐
        │  DB  │      │MinIO │
        └──────┘      └──────┘
```

### Puntos de Escalamiento

1. **Django App**: Múltiples instancias detrás de load balancer
2. **PostgreSQL**: Read replicas para queries pesados
3. **MinIO**: Modo distribuido para más almacenamiento
4. **Cache**: Redis para sesiones y queries frecuentes
5. **CDN**: CloudFlare/CloudFront para archivos estáticos

## 🔄 Alta Disponibilidad

### Componentes Críticos

| Componente | Estrategia HA | RPO | RTO |
|------------|---------------|-----|-----|
| Django App | Multiple instances + LB | N/A | <5 min |
| PostgreSQL | Streaming replication | <5 min | <15 min |
| MinIO | Distributed mode | <1 min | <5 min |
| Nginx | Multiple instances + DNS | N/A | <1 min |

**RPO**: Recovery Point Objective (pérdida máxima de datos)  
**RTO**: Recovery Time Objective (tiempo máximo de recuperación)

### Backup Strategy

```
┌─────────────────────────────────────────┐
│  Componente      Frecuencia    Retención│
├─────────────────────────────────────────┤
│  PostgreSQL      Diario        30 días  │
│  MinIO           Continuo      30 días  │
│  Config files    Semanal       90 días  │
│  Code            Git            ∞       │
└─────────────────────────────────────────┘
```

## 🌐 Networking

### Red Docker Interna

```
jic_network (bridge)
├── jic_wagtail      (172.18.0.2)
├── jic_postgres     (172.18.0.3)
├── jic_minio        (172.18.0.4)
├── jic_tailwind     (172.18.0.5)
└── jic_nginx        (172.18.0.6)
```

### Puertos Expuestos

| Servicio | Puerto Interno | Puerto Externo | Protocolo |
|----------|----------------|----------------|-----------|
| Nginx | 80/443 | 80/443 | HTTP/HTTPS |
| Django | 8000 | - | HTTP |
| PostgreSQL | 5432 | 5432* | TCP |
| MinIO API | 9000 | 9000 | HTTP |
| MinIO Console | 9001 | 9001 | HTTP |

*Solo para desarrollo, cerrar en producción

## 📈 Monitoreo

### Métricas Clave

1. **Application**
   - Request rate
   - Response time
   - Error rate
   - Active users

2. **Database**
   - Connection pool usage
   - Query performance
   - Lock waits
   - Disk usage

3. **Storage (MinIO)**
   - Upload/download rate
   - Storage usage
   - Object count
   - Bandwidth usage

4. **System**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

### Herramientas Recomendadas

- **Logs**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Metrics**: Prometheus + Grafana
- **APM**: Sentry (errores de aplicación)
- **Uptime**: UptimeRobot o StatusCake

## 🔧 Deployment Pipeline

### CI/CD Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     Git     │────▶│   GitHub    │────▶│  CI/CD      │
│   Commit    │     │   Actions   │     │  Pipeline   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    │
        ┌───────────┴──────────┬────────────────┐
        ▼                      ▼                ▼
┌───────────────┐    ┌──────────────┐   ┌─────────────┐
│     Build     │    │     Test     │   │   Deploy    │
│   Container   │    │   - Unit     │   │   to Prod   │
│               │    │   - Integration│   │            │
└───────────────┘    └──────────────┘   └─────────────┘
```

### Ambientes

1. **Development**: Local con Docker Compose
2. **Staging**: Réplica de producción para testing
3. **Production**: Servidor dedicado JIC

---

**Última actualización**: Enero 2026  
**Mantenido por**: JIC Development Team
