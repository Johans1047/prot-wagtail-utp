#!/bin/bash

# ==============================================================================
# JIC Wagtail CMS - Script de Instalación Automática
# ==============================================================================
# Versión: 1.0.0
# Sistema Operativo: Linux (Ubuntu/Debian recomendado)
# ==============================================================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo ""
    echo -e "${CYAN}===============================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}===============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
clear
echo -e "${CYAN}"
cat << "EOF"
     _ _____  ____   __        __              _        _ _ 
    | |_   _|/ ___|  \ \      / /_ _  __ _  __| |_ __ _(_) |
 _  | | | | | |       \ \ /\ / / _` |/ _` |/ _` | '__/ _` | |
| |_| | | | | |___     \ V  V / (_| | (_| | (_| | | | (_| | |
 \___/  |_|  \____|     \_/\_/ \__,_|\__, |\__,_|_|  \__,_|_|
                                     |___/                   
           CMS con MinIO, PostgreSQL y TailwindCSS
EOF
echo -e "${NC}"

print_header "Verificando Requisitos del Sistema"

# Verificar que estamos en Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "Este script está optimizado para Linux"
    print_info "Puede funcionar en otros sistemas con Docker instalado"
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    print_info "Instalando Docker..."
    
    # Preguntar si desea instalar Docker
    read -p "¿Desea instalar Docker ahora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        print_success "Docker instalado"
        print_warning "Necesitarás cerrar sesión y volver a entrar para usar Docker sin sudo"
    else
        print_error "Docker es requerido para continuar"
        exit 1
    fi
else
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    print_success "Docker encontrado (versión: $DOCKER_VERSION)"
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado"
    print_info "Instalando Docker Compose..."
    
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    print_success "Docker Compose instalado"
else
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f4 | cut -d ',' -f1)
    print_success "Docker Compose encontrado (versión: $COMPOSE_VERSION)"
fi

# Verificar que Docker esté corriendo
if ! docker info &> /dev/null; then
    print_error "Docker no está corriendo"
    print_info "Iniciando Docker..."
    sudo systemctl start docker
    sudo systemctl enable docker
    sleep 2
    
    if ! docker info &> /dev/null; then
        print_error "No se pudo iniciar Docker"
        exit 1
    fi
fi

print_success "Docker está corriendo"

# Verificar Git (opcional)
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d ' ' -f3)
    print_success "Git encontrado (versión: $GIT_VERSION)"
else
    print_warning "Git no está instalado (opcional, pero recomendado)"
fi

print_header "Configurando Proyecto"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    print_info "Creando archivo .env desde .env.example..."
    cp .env.example .env
    print_success "Archivo .env creado"
    
    # Generar SECRET_KEY aleatorio
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())' 2>/dev/null || openssl rand -base64 32)
    
    if [ ! -z "$SECRET_KEY" ]; then
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        print_success "SECRET_KEY generado automáticamente"
    fi
else
    print_warning "Archivo .env ya existe, manteniendo configuración actual"
fi

print_header "Construyendo Imágenes Docker"

print_info "Esto puede tomar varios minutos la primera vez..."
if docker-compose build; then
    print_success "Imágenes construidas exitosamente"
else
    print_error "Error al construir las imágenes"
    exit 1
fi

print_header "Levantando Servicios"

print_info "Iniciando contenedores..."
if docker-compose up -d; then
    print_success "Servicios iniciados"
else
    print_error "Error al iniciar los servicios"
    exit 1
fi

print_info "Esperando a que los servicios estén listos..."
sleep 10

# Verificar que los servicios estén corriendo
print_info "Verificando servicios..."

SERVICES=("jic_postgres" "jic_minio" "jic_wagtail" "jic_tailwind")
ALL_OK=true

for service in "${SERVICES[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
        print_success "Servicio $service está corriendo"
    else
        print_error "Servicio $service no está corriendo"
        ALL_OK=false
    fi
done

if [ "$ALL_OK" = false ]; then
    print_error "Algunos servicios no están corriendo correctamente"
    print_info "Ver logs con: docker-compose logs"
    exit 1
fi

print_header "Configurando Base de Datos"

print_info "Ejecutando migraciones..."
if docker-compose exec -T web python mysite/manage.py migrate; then
    print_success "Migraciones completadas"
else
    print_error "Error al ejecutar migraciones"
    print_info "Verifica los logs con: docker-compose logs web"
    exit 1
fi

print_header "Verificando MinIO"

# Esperar a que MinIO esté listo
print_info "Verificando que MinIO esté listo..."
sleep 5

if curl -f http://localhost:9000/minio/health/live &> /dev/null; then
    print_success "MinIO está funcionando correctamente"
else
    print_warning "MinIO puede no estar completamente listo"
fi

print_header "Configuración Completada"

# Preguntar si desea crear superusuario
echo ""
read -p "¿Deseas crear un superusuario ahora? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    docker-compose exec web python mysite/manage.py createsuperuser
fi

# Información final
print_header "¡Instalación Completada Exitosamente!"

echo -e "${GREEN}"
cat << "EOF"
    ✅ Todos los servicios están corriendo correctamente
EOF
echo -e "${NC}"

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📍 Accesos a la Aplicación${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  🌐 ${YELLOW}Sitio Web:${NC}        http://localhost:8000"
echo -e "  👤 ${YELLOW}Admin Wagtail:${NC}    http://localhost:8000/admin"
echo -e "  💾 ${YELLOW}MinIO Console:${NC}    http://localhost:9001"
echo -e "      Usuario: minioadmin"
echo -e "      Password: minioadmin"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🛠️  Comandos Útiles${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${GREEN}make help${NC}              Ver todos los comandos disponibles"
echo -e "  ${GREEN}make logs${NC}              Ver logs de todos los servicios"
echo -e "  ${GREEN}make shell${NC}             Abrir shell en el contenedor"
echo -e "  ${GREEN}make django-shell${NC}      Abrir Django shell"
echo -e "  ${GREEN}make down${NC}              Detener servicios"
echo -e "  ${GREEN}docker-compose ps${NC}      Ver estado de servicios"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📚 Documentación${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  📖 README.md           Documentación completa"
echo -e "  📦 DEPENDENCIES.md     Detalles de dependencias"
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}¡Feliz desarrollo! 🚀${NC}"
echo ""
