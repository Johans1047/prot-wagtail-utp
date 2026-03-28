# Script para levantar producción limpio y sin conflictos
# Uso: .\up-prod.ps1

docker compose -f docker-compose.prod.yml down --remove-orphans

docker compose -f docker-compose.prod.yml build --no-cache jicweb_app

docker compose -f docker-compose.prod.yml up -d

docker compose -f docker-compose.prod.yml ps
