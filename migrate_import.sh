#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults / argument parsing
# ---------------------------------------------------------------------------
COMPOSE_FILE="docker-compose.yml"
BACKUP_SOURCE=""
SKIP_START=false
SKIP_ENV_RESTORE=false

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Options:
  -f, --compose-file FILE    Docker Compose file to use (default: docker-compose.yml)
  -b, --backup-source PATH   ZIP file or directory to restore from
      --skip-start           Do not start the stack after restoring
      --skip-env-restore     Do not restore .env.prod / .env files
  -h, --help                 Show this help message
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--compose-file)    COMPOSE_FILE="$2"; shift 2 ;;
        -b|--backup-source)   BACKUP_SOURCE="$2"; shift 2 ;;
        --skip-start)         SKIP_START=true;  shift ;;
        --skip-env-restore)   SKIP_ENV_RESTORE=true; shift ;;
        -h|--help)            usage ;;
        *) echo "Opción desconocida: $1"; usage ;;
    esac
done

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
run_checked() {
    # run_checked "mensaje de error" cmd arg1 arg2 ...
    local error_msg="$1"; shift
    if ! "$@"; then
        echo "ERROR: $error_msg" >&2
        exit 1
    fi
}

docker_volume_exists() {
    docker volume inspect "$1" &>/dev/null
}

find_latest_backup_source() {
    local cwd="$PWD"

    # Prefer ZIP first
    local zip
    zip=$(find "$cwd" -maxdepth 1 -name "migration_backup_*.zip" -type f \
          -printf "%T@ %p\n" 2>/dev/null \
          | sort -rn | head -1 | awk '{print $2}')
    if [[ -n "$zip" ]]; then
        echo "$zip"
        return
    fi

    # Fall back to directory
    local dir
    dir=$(find "$cwd" -maxdepth 1 -name "migration_backup_*" -type d \
          -printf "%T@ %p\n" 2>/dev/null \
          | sort -rn | head -1 | awk '{print $2}')
    if [[ -n "$dir" ]]; then
        echo "$dir"
        return
    fi
}

ensure_docker_volume() {
    local volume_name="$1"
    if ! docker_volume_exists "$volume_name"; then
        echo "Creando volumen $volume_name"
        run_checked "No se pudo crear el volumen $volume_name" \
            docker volume create "$volume_name"
    fi
}

restore_docker_volume() {
    local project_name="$1"
    local volume_suffix="$2"
    local backup_dir="$3"

    local archive_name="${volume_suffix}.tar.gz"
    local archive_path="${backup_dir}/${archive_name}"

    if [[ ! -f "$archive_path" ]]; then
        echo "ERROR: No se encontro el archivo de backup requerido: $archive_path" >&2
        exit 1
    fi

    local target_volume="${project_name}_${volume_suffix}"
    ensure_docker_volume "$target_volume"

    echo "Limpiando volumen $target_volume"
    run_checked "No se pudo limpiar el volumen $target_volume" \
        docker run --rm \
            -v "${target_volume}:/to" \
            alpine sh -c "find /to -mindepth 1 -maxdepth 1 -exec rm -rf {} +"

    echo "Restaurando ${archive_name} -> ${target_volume}"
    run_checked "No se pudo restaurar ${archive_name} en ${target_volume}" \
        docker run --rm \
            -v "${target_volume}:/to" \
            -v "${backup_dir}:/backup:ro" \
            alpine sh -c "cd /to && tar xzf /backup/${archive_name}"

    echo "$target_volume"
}

# ---------------------------------------------------------------------------
# Validations
# ---------------------------------------------------------------------------
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "ERROR: No se encontro el archivo compose: $COMPOSE_FILE" >&2
    exit 1
fi

if [[ -z "$BACKUP_SOURCE" ]]; then
    BACKUP_SOURCE=$(find_latest_backup_source)
    if [[ -z "$BACKUP_SOURCE" ]]; then
        echo "ERROR: No se encontro BackupSource automaticamente. Pasa -b/--backup-source con ZIP o carpeta." >&2
        exit 1
    fi
fi

PROJECT_NAME="$(basename "$PWD")"
echo "Proyecto destino detectado: $PROJECT_NAME"
echo "Fuente de backup: $BACKUP_SOURCE"

# ---------------------------------------------------------------------------
# Extract ZIP if needed
# ---------------------------------------------------------------------------
RESOLVED_BACKUP_SOURCE="$(realpath "$BACKUP_SOURCE")"
BACKUP_DIR="$RESOLVED_BACKUP_SOURCE"
EXTRACTED_TEMP_DIR=""

if [[ -f "$RESOLVED_BACKUP_SOURCE" ]]; then
    if [[ "${RESOLVED_BACKUP_SOURCE,,}" != *.zip ]]; then
        echo "ERROR: BackupSource debe ser una carpeta o un .zip" >&2
        exit 1
    fi

    TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
    EXTRACTED_TEMP_DIR="${PWD}/migration_import_${TIMESTAMP}"
    mkdir -p "$EXTRACTED_TEMP_DIR"

    echo "Extrayendo backup ZIP..."
    unzip -q "$RESOLVED_BACKUP_SOURCE" -d "$EXTRACTED_TEMP_DIR"
    BACKUP_DIR="$EXTRACTED_TEMP_DIR"
fi

# ---------------------------------------------------------------------------
# Volume lists
# ---------------------------------------------------------------------------
REQUIRED_VOLUME_SUFFIXES=(
    "jicweb_master_data_v1"
    "jicst_storage_data"
)

OPTIONAL_VOLUME_SUFFIXES=(
    "jicweb_master_data_backup_v1"
    "jicst_backup_data"
)

# Build list of available archives
mapfile -t AVAILABLE_ARCHIVES < <(
    find "$BACKUP_DIR" -maxdepth 1 -name "*.tar.gz" -type f -printf "%f\n" 2>/dev/null
)

# Validate required archives exist
for suffix in "${REQUIRED_VOLUME_SUFFIXES[@]}"; do
    archive="${suffix}.tar.gz"
    found=false
    for a in "${AVAILABLE_ARCHIVES[@]}"; do
        [[ "$a" == "$archive" ]] && found=true && break
    done
    if [[ "$found" == false ]]; then
        echo "ERROR: Falta backup requerido en ${BACKUP_DIR}: ${archive}" >&2
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Restore .env files
# ---------------------------------------------------------------------------
if [[ "$SKIP_ENV_RESTORE" == false ]]; then
    for env_name in ".env.prod" ".env"; do
        src="${BACKUP_DIR}/${env_name}"
        if [[ -f "$src" ]]; then
            cp "$src" "${PWD}/${env_name}"
            echo "Restaurado $env_name"
        fi
    done
fi

# ---------------------------------------------------------------------------
# Stop current stack
# ---------------------------------------------------------------------------
echo "Deteniendo stack actual para restaurar datos..."
run_checked "No se pudo detener el stack" \
    docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down

# ---------------------------------------------------------------------------
# Restore volumes
# ---------------------------------------------------------------------------
RESTORED_VOLUMES=()

for suffix in "${REQUIRED_VOLUME_SUFFIXES[@]}"; do
    vol=$(restore_docker_volume "$PROJECT_NAME" "$suffix" "$BACKUP_DIR")
    RESTORED_VOLUMES+=("$vol")
done

for suffix in "${OPTIONAL_VOLUME_SUFFIXES[@]}"; do
    archive="${suffix}.tar.gz"
    found=false
    for a in "${AVAILABLE_ARCHIVES[@]}"; do
        [[ "$a" == "$archive" ]] && found=true && break
    done
    if [[ "$found" == true ]]; then
        vol=$(restore_docker_volume "$PROJECT_NAME" "$suffix" "$BACKUP_DIR")
        RESTORED_VOLUMES+=("$vol")
    fi
done

# ---------------------------------------------------------------------------
# Start stack
# ---------------------------------------------------------------------------
if [[ "$SKIP_START" == false ]]; then
    echo "Levantando stack con build..."
    run_checked "No se pudo iniciar el stack" \
        docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d --build
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Importacion completada."
echo "Volumenes restaurados:"
for vol in "${RESTORED_VOLUMES[@]}"; do
    echo " - $vol"
done

if [[ -n "$EXTRACTED_TEMP_DIR" ]]; then
    echo ""
    echo "Se uso carpeta temporal: $EXTRACTED_TEMP_DIR"
    echo "Puedes eliminarla cuando confirmes que todo funciona."
fi