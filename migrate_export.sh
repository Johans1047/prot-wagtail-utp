#!/usr/bin/env bash
set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults / argument parsing
# ---------------------------------------------------------------------------
COMPOSE_FILE="docker-compose.yml"
OUTPUT_DIR=""
INCLUDE_OPTIONAL=false

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Options:
  -f, --compose-file FILE    Docker Compose file to use (default: docker-compose.yml)
  -o, --output-dir DIR       Directory to write the backup into (default: migration_backup_<timestamp>)
      --include-optional     Also export optional volumes if they exist
  -h, --help                 Show this help message
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -f|--compose-file)   COMPOSE_FILE="$2"; shift 2 ;;
        -o|--output-dir)     OUTPUT_DIR="$2";   shift 2 ;;
        --include-optional)  INCLUDE_OPTIONAL=true; shift ;;
        -h|--help)           usage ;;
        *) echo "Opción desconocida: $1"; usage ;;
    esac
done

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
run_checked() {
    local error_msg="$1"; shift
    if ! "$@"; then
        echo "ERROR: $error_msg" >&2
        exit 1
    fi
}

docker_volume_exists() {
    docker volume inspect "$1" &>/dev/null
}

export_docker_volume() {
    local project_name="$1"
    local volume_suffix="$2"
    local dest_dir="$3"

    local source_volume="${project_name}_${volume_suffix}"
    if ! docker_volume_exists "$source_volume"; then
        echo "ERROR: No existe el volumen requerido: $source_volume" >&2
        exit 1
    fi

    local archive_name="${volume_suffix}.tar.gz"
    echo "Exportando ${source_volume} -> ${archive_name}"

    run_checked "Fallo la exportacion del volumen $source_volume" \
        docker run --rm \
            -v "${source_volume}:/from:ro" \
            -v "${dest_dir}:/backup" \
            alpine sh -c "cd /from && tar czf /backup/${archive_name} ."
}

# ---------------------------------------------------------------------------
# Validations
# ---------------------------------------------------------------------------
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "ERROR: No se encontro el archivo compose: $COMPOSE_FILE" >&2
    exit 1
fi

PROJECT_NAME="$(basename "$PWD")"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="${PWD}/migration_backup_${TIMESTAMP}"
fi

mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(realpath "$OUTPUT_DIR")"

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

# ---------------------------------------------------------------------------
# Stop stack
# ---------------------------------------------------------------------------
echo "Proyecto detectado: $PROJECT_NAME"
echo "Deteniendo stack para congelar datos..."
run_checked "No se pudo detener el stack" \
    docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down

# ---------------------------------------------------------------------------
# Export volumes
# ---------------------------------------------------------------------------
EXPORTED_SUFFIXES=()

for suffix in "${REQUIRED_VOLUME_SUFFIXES[@]}"; do
    export_docker_volume "$PROJECT_NAME" "$suffix" "$OUTPUT_DIR"
    EXPORTED_SUFFIXES+=("$suffix")
done

if [[ "$INCLUDE_OPTIONAL" == true ]]; then
    for suffix in "${OPTIONAL_VOLUME_SUFFIXES[@]}"; do
        volume_name="${PROJECT_NAME}_${suffix}"
        if docker_volume_exists "$volume_name"; then
            export_docker_volume "$PROJECT_NAME" "$suffix" "$OUTPUT_DIR"
            EXPORTED_SUFFIXES+=("$suffix")
        else
            echo "WARN: Se omite volumen opcional no encontrado: $volume_name"
        fi
    done
fi

# ---------------------------------------------------------------------------
# Copy .env files
# ---------------------------------------------------------------------------
for env_file in ".env.prod" ".env"; do
    if [[ -f "$env_file" ]]; then
        cp "$env_file" "${OUTPUT_DIR}/$(basename "$env_file")"
    fi
done

# ---------------------------------------------------------------------------
# Write metadata.json
# ---------------------------------------------------------------------------
EXPORTED_AT_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

volumes_json="["
first=true
for suffix in "${EXPORTED_SUFFIXES[@]}"; do
    [[ "$first" == true ]] && first=false || volumes_json+=","
    volumes_json+="{\"suffix\":\"${suffix}\",\"sourceVolume\":\"${PROJECT_NAME}_${suffix}\",\"archive\":\"${suffix}.tar.gz\"}"
done
volumes_json+="]"

cat > "${OUTPUT_DIR}/metadata.json" <<EOF
{
  "exportedAtUtc": "${EXPORTED_AT_UTC}",
  "sourceProject": "${PROJECT_NAME}",
  "composeFile": "${COMPOSE_FILE}",
  "includeOptional": ${INCLUDE_OPTIONAL},
  "volumes": ${volumes_json}
}
EOF

# ---------------------------------------------------------------------------
# SHA256SUMS.txt
# ---------------------------------------------------------------------------
sha_file="${OUTPUT_DIR}/SHA256SUMS.txt"
> "$sha_file"

while IFS= read -r -d '' archive; do
    hash="$(sha256sum "$archive" | awk '{print $1}')"
    name="$(basename "$archive")"
    echo "${hash}  ${name}" >> "$sha_file"
done < <(find "$OUTPUT_DIR" -maxdepth 1 -name "*.tar.gz" -type f -print0 | sort -z)

# ---------------------------------------------------------------------------
# ZIP the output directory
# ---------------------------------------------------------------------------
ZIP_PATH="${OUTPUT_DIR}.zip"
[[ -f "$ZIP_PATH" ]] && rm -f "$ZIP_PATH"

(cd "$(dirname "$OUTPUT_DIR")" && zip -qr "$ZIP_PATH" "$(basename "$OUTPUT_DIR")")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "Exportacion completada."
echo "Carpeta: $OUTPUT_DIR"
echo "ZIP:     $ZIP_PATH"
echo ""
echo "En la PC destino ejecuta import_backup.sh desde la carpeta del proyecto destino."