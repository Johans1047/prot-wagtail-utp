# 📦 Información de Versiones - JIC Wagtail CMS

Documento que detalla todas las versiones de paquetes y dependencias del proyecto.

## 🐍 Python

- **Versión Requerida**: 3.11+
- **Versión Recomendada**: 3.11.7
- **Versión Máxima Probada**: 3.12

## 🎨 Frameworks & CMS

### Backend

| Paquete | Versión | Tipo | Propósito |
|---------|---------|------|-----------|
| Django | 4.2.9 | Framework | Framework web principal |
| Wagtail | 5.2.2 | CMS | Sistema de gestión de contenidos |
| django-storages | 1.14.2 | Storage | Backend para object storage |
| boto3 | 1.34.20 | SDK | Cliente AWS S3 (MinIO compatible) |
| minio | 7.2.3 | SDK | Cliente MinIO oficial |
| psycopg2-binary | 2.9.9 | Driver | Conector PostgreSQL |
| Pillow | 10.2.0 | Media | Procesamiento de imágenes |
| willow | 1.8 | Media | Librería de imágenes Wagtail |
| python-dotenv | 1.0.0 | Config | Manejo de variables entorno |

### Frontend

| Paquete | Versión | Tipo | Propósito |
|---------|---------|------|-----------|
| tailwindcss | 3.4.1 | Framework CSS | Utility-first CSS framework |
| flowbite | 2.2.1 | Componentes | Biblioteca de componentes UI |
| @tailwindcss/typography | 0.5.10 | Plugin | Estilos tipográficos |
| @tailwindcss/forms | 0.5.7 | Plugin | Estilos para formularios |

### Desarrollo

| Paquete | Versión | Tipo | Propósito |
|---------|---------|------|-----------|
| django-livereload-server | 0.4 | Dev Tool | Hot reload en desarrollo |

### Producción

| Paquete | Versión | Tipo | Propósito |
|---------|---------|------|-----------|
| gunicorn | 21.2.0 | WSGI Server | Servidor de aplicación |
| whitenoise | 6.6.0 | Static Files | Servir archivos estáticos |
| django-cors-headers | 4.3.1 | Security | CORS headers |

## 🐳 Servicios Docker

### Imágenes Base

| Servicio | Imagen | Versión | Puerto(s) |
|----------|--------|---------|-----------|
| PostgreSQL | postgres | 15-alpine | 5432 |
| MinIO | minio/minio | latest | 9000, 9001 |
| MinIO Client | minio/mc | latest | - |
| Python | python | 3.11-slim | - |
| Node.js | node | 18-alpine | - |
| Nginx | nginx | alpine | 80, 443 |

### Versiones Específicas

- **PostgreSQL**: 15.5 (Alpine Linux)
- **MinIO**: Compatible con Amazon S3 API
- **Nginx**: 1.25+ (Alpine)
- **Node.js**: 18.19.0

## 🔧 Herramientas de Sistema

### Requeridas

- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Opcionales

- **Git**: 2.0+
- **Make**: 4.0+

## 📊 Matriz de Compatibilidad

### Python

| Componente | 3.11 | 3.12 | 3.13 |
|------------|------|------|------|
| Django 4.2 | ✅ | ✅ | ⚠️ |
| Wagtail 5.2 | ✅ | ✅ | ⚠️ |
| Pillow | ✅ | ✅ | ✅ |
| psycopg2 | ✅ | ✅ | ✅ |

✅ Totalmente compatible  
⚠️ No probado  
❌ No compatible

### Base de Datos

| PostgreSQL | Django 4.2 | Wagtail 5.2 |
|------------|------------|-------------|
| 13 | ✅ | ✅ |
| 14 | ✅ | ✅ |
| 15 | ✅ | ✅ |
| 16 | ✅ | ✅ |

### Node.js

| Node.js | TailwindCSS 3.4 | Flowbite 2.2 |
|---------|-----------------|--------------|
| 16 | ✅ | ✅ |
| 18 | ✅ | ✅ |
| 20 | ✅ | ✅ |

## 🔄 Historial de Versiones del Proyecto

### v1.0.0 (Enero 2026)
- ✨ Primera versión
- 🚀 Stack completo con MinIO
- 🎨 TailwindCSS + Flowbite
- 🐳 Docker Compose configurado
- 📝 Documentación completa

## 📅 Calendario de Actualizaciones

### Parches de Seguridad
- **Frecuencia**: Inmediata
- **Tipo**: Actualizaciones de seguridad críticas

### Versiones Menores
- **Frecuencia**: Mensual
- **Tipo**: Nuevas características, mejoras

### Versiones Mayores
- **Frecuencia**: Anual
- **Tipo**: Cambios significativos, breaking changes

## 🔐 Vulnerabilidades Conocidas

### Estado Actual (Enero 2026)

✅ **Sin vulnerabilidades críticas conocidas**

Última verificación: Enero 29, 2026

### Cómo Verificar

```bash
# Python
pip-audit

# Node.js
npm audit

# Docker
docker scout cves
```

## 📝 Notas de Versiones

### Django 4.2.9
- LTS (Long Term Support) hasta Abril 2026
- Soporte de seguridad hasta Abril 2026
- [Notas de versión](https://docs.djangoproject.com/en/4.2/releases/4.2.9/)

### Wagtail 5.2.2
- LTS hasta Agosto 2025
- [Notas de versión](https://docs.wagtail.org/en/stable/releases/5.2.2.html)

### PostgreSQL 15
- Soporte hasta Noviembre 2027
- [Notas de versión](https://www.postgresql.org/docs/15/release-15.html)

### TailwindCSS 3.4.1
- Última versión estable
- JIT compiler integrado
- [Notas de versión](https://github.com/tailwindlabs/tailwindcss/releases)

### Flowbite 2.2.1
- Compatible con TailwindCSS 3.x
- [Notas de versión](https://github.com/themesberg/flowbite/releases)

## 🔄 Plan de Actualización

### Q1 2026 (Actual)
- ✅ Instalación inicial
- 📝 Documentación
- 🧪 Testing inicial

### Q2 2026
- 🔄 Actualización a Django 4.2.x (último parche)
- 🔄 Actualización de dependencias menores
- 🧪 Testing completo

### Q3 2026
- 🔄 Evaluar migración a Django 5.0+
- 🔄 Actualización a Wagtail 6.0+
- 🎨 Actualizar TailwindCSS y Flowbite

### Q4 2026
- 🚀 Despliegue de nuevas características
- 📊 Evaluación de rendimiento
- 🔐 Auditoría de seguridad

## 🛡️ Política de Seguridad

### Actualizaciones de Seguridad

1. **Críticas**: Aplicar inmediatamente (< 24 horas)
2. **Altas**: Aplicar en 7 días
3. **Medias**: Aplicar en próxima ventana de mantenimiento
4. **Bajas**: Evaluar y programar

### Proceso de Actualización

1. Revisar changelog
2. Actualizar en desarrollo
3. Ejecutar tests
4. Deploy a staging
5. Deploy a producción
6. Monitorear

## 📞 Soporte

Para consultas sobre versiones o actualizaciones:

- **Email**: dev@jic.gob.pa
- **Documentación**: Ver README.md y DEPENDENCIES.md

---

**Última actualización**: Enero 29, 2026  
**Próxima revisión**: Febrero 29, 2026
