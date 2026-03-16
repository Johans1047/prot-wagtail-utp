# Guía de Importación de Asesores y Proyectos

## Descripción General
Esta funcionalidad permite importar datos de asesores/consultores y proyectos desde archivos CSV o XLSX, evitando automáticamente la duplicación de registros.

## Estructura del Sistema de Importación

### Archivo de Servicio: `web/services/import_service.py`
- Maneja la lectura de archivos CSV/XLSX
- Valida y procesa datos
- Previene duplicados basándose en:
  - **Asesores**: nombre único
  - **Proyectos**: combinación de título + año

### Vista de Importación: `web/views/import_views.py`
- Interfaz web para cargar archivos
- Manejo de errores y validación
- Estadísticas de importación

### Template: `web/templates/web/importar_datos.html`
- UI basada en Wagtail admin
- Instrucciones integradas
- Visualización de resultados y errores

---

## Columnas Requeridas

### Para Asesores/Consultores

| Columna | Tipo | Requerido | Descripción |
|---------|------|-----------|-------------|
| **nombre** | texto | ✓ | Nombre del asesor |
| **email** | texto | - | Correo electrónico |
| **institucion** | texto | - | Institución afiliada |
| **activo** | booleano | - | true/false, sí/no (default: true) |

**Ejemplo CSV:**
```
nombre,email,institucion,activo
"Dr. Juan Pérez","juan@example.com","Universidad XYZ",true
"Dra. María García","maria@example.com","Instituto ABC",sí
```

### Para Proyectos

| Columna | Tipo | Requerido | Descripción |
|---------|------|-----------|-------------|
| **titulo** | texto | ✓ | Título del proyecto |
| **año** | número | ✓ | Año del proyecto |
| **universidad** | texto | ✓ | Universidad participante |
| **resumen** | texto | - | Resumen/abstract del proyecto |
| **categoria** | texto | - | Categoría del proyecto |
| **asesor** | texto | - | Nombre del asesor (debe existir) |
| **premio** | número | - | 0=No ganador, 1=Primer lugar, 2=Segundo, 3=Tercero |

**Ejemplo CSV:**
```
titulo,año,universidad,resumen,categoria,asesor,premio
"Investigación de IA",2024,"Universidad XYZ","Este estudio analiza...","Tecnología","Dr. Juan Pérez",1
"Estudio de Sostenibilidad",2024,"Instituto ABC","Análisis ambiental...","Medio Ambiente",,0
```

---

## Guía de Uso

### 1. Preparar el archivo

1. **Crear un nuevo archivo CSV o XLSX** con sus datos
2. **Nombres de columnas**: deben estar en minúsculas, sin acentos o espacios especiales
3. **Nómbrelo significativamente**: 
   - Para asesores: "consultores_2024.csv", "asesores.xlsx"
   - Para proyectos: "proyectos_2024.csv", "projects.xlsx"

### 2. Detectar tipo de archivo

El sistema puede detectar automáticamente si es:
- **Asesores**: si contiene columnas "nombre" y "email"
- **Proyectos**: si contiene columnas "titulo" y "año"
- O puede especificarlo manualmente en el formulario

### 3. Opciones de importación

**Actualizar existentes (sin marcar):**
- Solo crea registros nuevos
- Evita duplicados por completo
- Seguro si ejecuta múltiples veces

**Actualizar existentes (marcado):**
- Crea nuevos registros
- Actualiza existentes:
  - Asesores: si coincide el nombre
  - Proyectos: si coinciden título + año

### 4. Revisar resultados

Después de importar, verá:
- **Resumen de registros creados/actualizados**
- **Lista detallada de errores** (si los hay)
- **Información de fila** donde ocurrió el error

---

## Validaciones y Manejo de Errores

### Validaciones Automáticas

- ✓ Celda vacía en campo requerido → Error de fila
- ✓ Email con formato inválido → Ignorado, campo vacío
- ✓ Año no es número → Error de fila
- ✓ Asesor especificado no existe → Error de fila
- ✓ Premio fuera de rango (0-3) → Convertido a 0

### Manejo de Valores Especiales

| Valor | Interpretación |
|-------|---------------|
| "nan" (cualquier caso) | Celda vacía |
| "true", "1", "sí", "verdadero" | Booleano verdadero |
| "false", "0", "no", "falso" | Booleano falso |
| Vacío | Depende del campo (error si requerido) |

---

## Ejemplos de Importación

### Ejemplo 1: Solo Asesores (Crear)

**Archivo: asesores.csv**
```csv
nombre,email,institucion,activo
Dr. Carlos López,carlos@uni.edu,Universidad Central,true
Ing. Sofia Rodriguez,sofia@uni.edu,Instituto Técnico,true
Dra. Ana Martínez,,Universidad del Sur,false
```

**Resultado (sin Actualizar):**
- 3 asesores creados
- 0 errores

---

### Ejemplo 2: Proyectos con Asesor (Crear)

**Archivo: proyectos_2024.xlsx**
```
titulo | año | universidad | asesor | categoria | premio
Proyecto A | 2024 | Uni X | Dr. Carlos López | Tecnología | 1
Proyecto B | 2024 | Instituto Y | Dr. Carlos López | Sostenibilidad | 0
Proyecto C | 2023 | Uni Z | (vacío) | Educación | 0
```

**Resultado (sin Actualizar):**
- 3 proyectos creados
- 0 errores (asesores ya existen o permiten vacío)

---

### Ejemplo 3: Error - Asesor no existe

Si intenta crear un proyecto con un asesor no existente:

**Fila 2:** Error - Asesor "Dr. Inexistente" no encontrado

**Solución:**
1. Importar primero el asesor
2. Luego importar el proyecto

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| "Formato no soportado" | Use CSV o XLSX solamente |
| "No se pudo detectar el tipo" | Nombre el archivo claramente (consultores/proyectos) o especifique el tipo |
| "Falta la columna 'nombre'" | Verifique que su CSV tenga exactamente esa columna (minúsculas) |
| "Asesor X no encontrado" | Importe primero los asesores antes de los proyectos |
| "Duplicados no se crean" | Desmarque "Actualizar existentes" para usar verificación de duplicados |

---

## Notas de Seguridad

- ✓ Solo administradores pueden importar
- ✓ No se eliminan registros automáticamente
- ✓ Los errores se registran sin procesar esa fila
- ✓ Puede ejecutar múltiples veces sin duplicar si lo hace correctamente

---

## Plantillas de Ejemplo

Ver `web/templates/ejemplos/` para archivos de muestra:
- `consultores_ejemplo.csv`
- `proyectos_ejemplo.xlsx`
