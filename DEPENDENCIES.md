# Documentación de Dependencias - JIC Wagtail CMS

Este documento detalla todas las dependencias externas del proyecto, sus versiones y propósitos.

## 📦 Requisitos del Sistema

### Sistema Operativo
- **Requerido**: Linux (Ubuntu 20.04+ o Debian 11+ recomendado)
- **Alternativas**: Puede ejecutarse en macOS o Windows usando Docker Desktop
- **Razón**: Mejor compatibilidad con herramientas de desarrollo y producción

### Python
- **Versión**: 3.11+
- **Requerido**: Sí
- **Instalación**:
  ```bash
  sudo apt-get update
  sudo apt-get install python3.11 python3.11-venv python3-pip
  ```

### Docker
- **Versión**: 20.10+
- **Docker Compose**: 2.0+
- **Requerido**: Sí
- **Instalación**:
  ```bash
  # Instalar Docker Engine
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  
  # Instalar Docker Compose
  sudo apt-get install docker-compose-plugin
  ```

## 🐍 Dependencias Python

### Framework Core

#### Django (4.2.9)
- **Propósito**: Framework web principal
- **Tipo**: Framework
- **Licencia**: BSD
- **Documentación**: https://docs.djangoproject.com/
- **Características usadas**:
  - ORM para base de datos
  - Sistema de autenticación
  - Admin interface
  - Template engine
  - URL routing

#### Wagtail (5.2.2)
- **Propósito**: CMS (Content Management System)
- **Tipo**: Framework CMS
- **Licencia**: BSD
- **Documentación**: https://docs.wagtail.org/
- **Características usadas**:
  - Page models
  - Rich text editor
  - Image management
  - StreamField
  - Admin UI customizado

### Base de Datos

#### psycopg2-binary (2.9.9)
- **Propósito**: Adaptador PostgreSQL para Python
- **Tipo**: Database Driver
- **Licencia**: LGPL
- **Documentación**: https://www.psycopg.org/
- **Por qué esta versión**: 
  - Incluye binarios precompilados
  - Compatible con PostgreSQL 15
  - Mejor rendimiento

### Object Storage

#### django-storages (1.14.2)
- **Propósito**: Soporte para backends de almacenamiento
- **Tipo**: Storage Backend
- **Licencia**: BSD
- **Documentación**: https://django-storages.readthedocs.io/
- **Backends soportados**:
  - Amazon S3
  - MinIO (S3-compatible)
  - Azure Storage
  - Google Cloud Storage

#### boto3 (1.34.20)
- **Propósito**: AWS SDK para Python
- **Tipo**: SDK
- **Licencia**: Apache 2.0
- **Documentación**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **Uso en el proyecto**:
  - Comunicación con MinIO (S3-compatible)
  - Upload/download de archivos
  - Gestión de buckets

#### minio (7.2.3)
- **Propósito**: Cliente MinIO oficial para Python
- **Tipo**: SDK
- **Licencia**: Apache 2.0
- **Documentación**: https://min.io/docs/minio/linux/developers/python/minio-py.html
- **Ventajas sobre boto3**:
  - API más simple para MinIO
  - Mejor integración con MinIO
  - Funciones específicas de MinIO

### Procesamiento de Medios

#### Pillow (10.2.0)
- **Propósito**: Procesamiento de imágenes
- **Tipo**: Librería de imágenes
- **Licencia**: HPND
- **Documentación**: https://pillow.readthedocs.io/
- **Formatos soportados**:
  - JPEG, PNG, GIF, BMP
  - WebP, TIFF
  - Manipulación: resize, crop, rotate
  - Filtros y efectos

#### Willow (1.8)
- **Propósito**: Librería de imágenes de Wagtail
- **Tipo**: Image Library
- **Licencia**: BSD
- **Documentación**: https://github.com/wagtail/Willow
- **Características**:
  - Abstracción sobre Pillow
  - Optimización para Wagtail
  - Operaciones de imagen simplificadas

### Utilidades

#### django-livereload-server (0.4)
- **Propósito**: Hot reload en desarrollo
- **Tipo**: Development Tool
- **Licencia**: BSD
- **Solo en**: Desarrollo
- **Funcionalidad**:
  - Recarga automática del navegador
  - Detección de cambios en archivos
  - WebSocket para comunicación

#### python-dotenv (1.0.0)
- **Propósito**: Cargar variables de entorno desde .env
- **Tipo**: Configuration
- **Licencia**: BSD
- **Documentación**: https://github.com/theskumar/python-dotenv
- **Uso**:
  - Gestión de configuración
  - Separación de secrets
  - Diferentes ambientes (dev/prod)

## 📦 Dependencias Node.js

### CSS Framework

#### tailwindcss (^3.4.1)
- **Propósito**: Framework CSS utility-first
- **Tipo**: CSS Framework
- **Licencia**: MIT
- **Documentación**: https://tailwindcss.com/docs
- **Características**:
  - Utility classes
  - JIT (Just-In-Time) compiler
  - PurgeCSS integrado
  - Responsive design
  - Dark mode

### Componentes UI

#### flowbite (^2.2.1)
- **Propósito**: Componentes UI para TailwindCSS
- **Tipo**: Component Library
- **Licencia**: MIT
- **Documentación**: https://flowbite.com/docs/
- **Componentes incluidos**:
  - Modals
  - Dropdowns
  - Navbars
  - Forms
  - Cards
  - Tooltips
  - Carousels
  - Y más...

### Plugins TailwindCSS

#### @tailwindcss/typography (^0.5.10)
- **Propósito**: Estilos tipográficos para contenido
- **Tipo**: Plugin
- **Licencia**: MIT
- **Documentación**: https://tailwindcss.com/docs/typography-plugin
- **Uso**:
  - Artículos de blog
  - Contenido CMS
  - Documentación
- **Clases**: `prose`, `prose-lg`, `prose-slate`

#### @tailwindcss/forms (^0.5.7)
- **Propósito**: Estilos base para formularios
- **Tipo**: Plugin
- **Licencia**: MIT
- **Documentación**: https://tailwindcss.com/docs/plugins#forms
- **Mejoras**:
  - Inputs estilizados
  - Checkboxes y radios personalizados
  - Selectores mejorados
  - Consistencia cross-browser

## 🐳 Servicios Docker

### PostgreSQL (15-alpine)
- **Propósito**: Base de datos relacional
- **Versión**: 15 (Alpine Linux)
- **Puerto**: 5432
- **Documentación**: https://www.postgresql.org/docs/15/
- **Características**:
  - ACID compliant
  - JSON/JSONB support
  - Full-text search
  - Extensiones (PostGIS, pg_trgm)

### MinIO (latest)
- **Propósito**: Object storage S3-compatible
- **Versión**: Latest
- **Puertos**: 9000 (API), 9001 (Console)
- **Documentación**: https://min.io/docs/minio/linux/
- **Características**:
  - S3-compatible API
  - Multi-tenancy
  - Versioning
  - Replication
  - Encryption

### MinIO Client (mc) (latest)
- **Propósito**: Cliente de línea de comandos para MinIO
- **Versión**: Latest
- **Uso**:
  - Crear buckets automáticamente
  - Configurar políticas
  - Gestión de archivos

## 🔄 Dependencias de Desarrollo (Adicionales)

### Recomendadas para Desarrollo Local

```txt
# Testing
pytest==7.4.3
pytest-django==4.7.0
coverage==7.3.4

# Code Quality
black==23.12.1
flake8==7.0.0
isort==5.13.2

# Debugging
django-debug-toolbar==4.2.0
ipython==8.19.0
```

## 🚀 Dependencias de Producción (Adicionales)

### Para Despliegue

```txt
# WSGI Server
gunicorn==21.2.0

# Static Files
whitenoise==6.6.0

# Monitoring
sentry-sdk==1.39.1

# Performance
django-redis==5.4.0
```

## 📊 Matriz de Compatibilidad

| Componente | Versión Mínima | Versión Probada | Versión Máxima |
|------------|----------------|-----------------|----------------|
| Python | 3.11 | 3.11 | 3.12 |
| Django | 4.2 | 4.2.9 | 4.2.x |
| Wagtail | 5.2 | 5.2.2 | 5.2.x |
| PostgreSQL | 13 | 15 | 16 |
| Node.js | 18 | 18 | 20 |
| TailwindCSS | 3.0 | 3.4.1 | 3.x |

## 🔒 Consideraciones de Seguridad

### Dependencias con Vulnerabilidades Conocidas

Ninguna al momento de esta documentación (Enero 2026).

### Actualizaciones Recomendadas

```bash
# Verificar vulnerabilidades en Python
pip-audit

# Verificar vulnerabilidades en Node.js
npm audit

# Actualizar dependencias de seguridad
pip install --upgrade <paquete>
npm update
```

### Políticas de Actualización

- **Parches de seguridad**: Aplicar inmediatamente
- **Versiones menores**: Revisar y aplicar mensualmente
- **Versiones mayores**: Planificar y probar antes de aplicar

## 🌐 Dependencias Externas (CDN/Servicios)

### Flowbite CDN (Opcional)
```html
<script src="https://cdn.jsdelivr.net/npm/flowbite@2.2.1/dist/flowbite.min.js"></script>
```

### Fuentes (Opcional)
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## 📝 Notas Adicionales

### Por qué PostgreSQL y no SQLite

- **Concurrencia**: Mejor manejo de múltiples escrituras
- **Tipos de datos**: JSON, Arrays, Full-text search
- **Producción**: Estándar de la industria
- **Wagtail**: Optimizado para PostgreSQL

### Por qué MinIO y no S3

- **Auto-hospedado**: Control total de los datos
- **Compatible S3**: Fácil migración si es necesario
- **Costos**: Sin costos de almacenamiento cloud
- **Privacidad**: Datos en servidores propios

### Por qué TailwindCSS + Flowbite

- **Desarrollo rápido**: Componentes pre-hechos
- **Consistencia**: Design system unificado
- **Responsive**: Mobile-first por defecto
- **Customizable**: Fácil de personalizar
- **Mantenimiento**: CSS mínimo custom

## 🔄 Actualización de Dependencias

### Proceso Recomendado

1. **Revisar changelog** de la dependencia
2. **Actualizar en ambiente de desarrollo**
3. **Ejecutar tests**
4. **Revisar deprecation warnings**
5. **Actualizar documentación**
6. **Deploy a staging**
7. **Deploy a producción**

### Comandos

```bash
# Ver dependencias desactualizadas (Python)
pip list --outdated

# Ver dependencias desactualizadas (Node)
npm outdated

# Actualizar (Python)
pip install --upgrade <paquete>

# Actualizar (Node)
npm update <paquete>
```

---

**Última actualización**: Enero 2026  
**Mantenido por**: JIC Development Team
