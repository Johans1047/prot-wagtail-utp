.PHONY: help build up down restart logs shell migrate createsuperuser test clean init

help: ## Mostrar esta ayuda
	@echo "==================================================================="
	@echo "  JIC Wagtail CMS - Comandos Disponibles"
	@echo "==================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""

build: ## Construir las imágenes Docker
	@echo "🔨 Construyendo imágenes Docker..."
	docker-compose build

up: ## Levantar los servicios
	@echo "🚀 Levantando servicios..."
	docker-compose up

up-d: ## Levantar los servicios en segundo plano
	@echo "🚀 Levantando servicios en background..."
	docker-compose up -d

down: ## Detener los servicios
	@echo "🛑 Deteniendo servicios..."
	docker-compose down

down-v: ## Detener los servicios y eliminar volúmenes
	@echo "🛑 Deteniendo servicios y eliminando volúmenes..."
	docker-compose down -v

restart: ## Reiniciar los servicios
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart

restart-web: ## Reiniciar solo el servicio web
	@echo "🔄 Reiniciando servicio web..."
	docker-compose restart web

restart-tailwind: ## Reiniciar solo el watcher de TailwindCSS
	@echo "🔄 Reiniciando TailwindCSS watcher..."
	docker-compose restart tailwind

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-web: ## Ver logs del servicio web
	docker-compose logs -f web

logs-tailwind: ## Ver logs de TailwindCSS
	docker-compose logs -f tailwind

logs-db: ## Ver logs de PostgreSQL
	docker-compose logs -f db

logs-minio: ## Ver logs de MinIO
	docker-compose logs -f minio

shell: ## Abrir shell en el contenedor web
	docker-compose exec web bash

django-shell: ## Abrir Django shell
	docker-compose exec web python mysite/manage.py shell

migrate: ## Ejecutar migraciones
	@echo "🔄 Ejecutando migraciones..."
	docker-compose exec web python mysite/manage.py migrate

makemigrations: ## Crear migraciones
	@echo "📝 Creando migraciones..."
	docker-compose exec web python mysite/manage.py makemigrations

createsuperuser: ## Crear superusuario
	@echo "👤 Creando superusuario..."
	docker-compose exec web python mysite/manage.py createsuperuser

collectstatic: ## Recolectar archivos estáticos
	@echo "📦 Recolectando archivos estáticos..."
	docker-compose exec web python mysite/manage.py collectstatic --noinput

test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	docker-compose exec web python mysite/manage.py test

db-shell: ## Conectar a PostgreSQL
	docker-compose exec db psql -U jicuser -d jic_db

db-backup: ## Hacer backup de la base de datos
	@echo "💾 Creando backup de la base de datos..."
	@mkdir -p backups
	docker-compose exec db pg_dump -U jicuser jic_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup creado en backups/"

db-restore: ## Restaurar backup (uso: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "❌ Uso: make db-restore FILE=backup.sql"; exit 1; fi
	@echo "📥 Restaurando backup: $(FILE)"
	docker-compose exec -T db psql -U jicuser jic_db < $(FILE)
	@echo "✅ Backup restaurado"

minio-shell: ## Acceder al cliente MinIO
	docker-compose exec minio-client sh

minio-ls: ## Listar archivos en MinIO
	docker-compose exec minio-client mc ls myminio/jic-media

clean: ## Limpiar contenedores, imágenes y volúmenes
	@echo "🧹 Limpiando Docker..."
	docker-compose down -v
	docker system prune -f

rebuild: ## Reconstruir todo desde cero
	@echo "🔨 Reconstruyendo todo..."
	docker-compose down -v
	docker-compose build --no-cache
	docker-compose up -d

init: ## Inicializar proyecto (primera vez)
	@echo "==================================================================="
	@echo "  🚀 Inicializando JIC Wagtail CMS"
	@echo "==================================================================="
	@if [ ! -f .env ]; then \
		echo "📝 Creando archivo .env..."; \
		cp .env.example .env; \
	fi
	@echo "🔨 Construyendo imágenes..."
	docker-compose build
	@echo "🚀 Levantando servicios..."
	docker-compose up -d
	@echo "⏳ Esperando a que los servicios estén listos..."
	@sleep 10
	@echo "🔄 Ejecutando migraciones..."
	docker-compose exec web python mysite/manage.py migrate
	@echo ""
	@echo "==================================================================="
	@echo "  ✅ Proyecto inicializado exitosamente"
	@echo "==================================================================="
	@echo ""
	@echo "🌐 Accesos:"
	@echo "   - Web: http://localhost:8000"
	@echo "   - Admin: http://localhost:8000/admin"
	@echo "   - MinIO Console: http://localhost:9001"
	@echo ""
	@echo "📝 Siguiente paso:"
	@echo "   make createsuperuser  # Crear usuario administrador"
	@echo ""

status: ## Ver estado de los contenedores
	@echo "📊 Estado de los servicios:"
	docker-compose ps

install-python: ## Instalar nueva dependencia Python (uso: make install-python PKG=nombre)
	@if [ -z "$(PKG)" ]; then echo "❌ Uso: make install-python PKG=nombre_paquete"; exit 1; fi
	@echo "📦 Instalando $(PKG)..."
	@echo "$(PKG)" >> requirements.txt
	docker-compose build web
	docker-compose restart web
	@echo "✅ $(PKG) agregado e instalado"

install-node: ## Instalar nueva dependencia Node (uso: make install-node PKG=nombre)
	@if [ -z "$(PKG)" ]; then echo "❌ Uso: make install-node PKG=nombre_paquete"; exit 1; fi
	@echo "📦 Instalando $(PKG)..."
	docker-compose exec tailwind npm install $(PKG)
	@echo "✅ $(PKG) instalado"

css-build: ## Compilar CSS para producción
	@echo "🎨 Compilando CSS para producción..."
	docker-compose exec tailwind npm run tailwind:build
	@echo "✅ CSS compilado"

help-minio: ## Mostrar comandos útiles de MinIO
	@echo "==================================================================="
	@echo "  MinIO - Comandos Útiles"
	@echo "==================================================================="
	@echo ""
	@echo "Acceder a MinIO Console:"
	@echo "  http://localhost:9001"
	@echo "  Usuario: minioadmin"
	@echo "  Password: minioadmin"
	@echo ""
	@echo "Comandos CLI:"
	@echo "  make minio-shell    # Acceder al cliente"
	@echo "  make minio-ls       # Listar archivos"
	@echo ""
	@echo "Dentro del shell de MinIO:"
	@echo "  mc ls myminio/jic-media"
	@echo "  mc cp archivo.jpg myminio/jic-media/"
	@echo "  mc rm myminio/jic-media/archivo.jpg"
	@echo ""

help-django: ## Mostrar comandos útiles de Django
	@echo "==================================================================="
	@echo "  Django/Wagtail - Comandos Útiles"
	@echo "==================================================================="
	@echo ""
	@echo "Gestión de la aplicación:"
	@echo "  make migrate              # Aplicar migraciones"
	@echo "  make makemigrations       # Crear migraciones"
	@echo "  make createsuperuser      # Crear admin"
	@echo "  make shell                # Bash shell"
	@echo "  make django-shell         # Django shell"
	@echo ""
	@echo "Base de datos:"
	@echo "  make db-shell             # Conectar a PostgreSQL"
	@echo "  make db-backup            # Crear backup"
	@echo "  make db-restore FILE=...  # Restaurar backup"
	@echo ""

prod: ## Levantar en modo producción
	@echo "🚀 Levantando en modo PRODUCCIÓN..."
	docker-compose -f docker-compose.prod.yml up -d

prod-build: ## Construir para producción
	@echo "🔨 Construyendo para PRODUCCIÓN..."
	docker-compose -f docker-compose.prod.yml build

prod-down: ## Detener producción
	@echo "🛑 Deteniendo servicios de PRODUCCIÓN..."
	docker-compose -f docker-compose.prod.yml down

version: ## Mostrar versiones de componentes
	@echo "==================================================================="
	@echo "  Versiones de Componentes"
	@echo "==================================================================="
	@echo "Python:"
	@docker-compose exec web python --version 2>/dev/null || echo "  (servicio no iniciado)"
	@echo ""
	@echo "Django:"
	@docker-compose exec web python -c "import django; print(f'  {django.get_version()}')" 2>/dev/null || echo "  (servicio no iniciado)"
	@echo ""
	@echo "Wagtail:"
	@docker-compose exec web python -c "import wagtail; print(f'  {wagtail.__version__}')" 2>/dev/null || echo "  (servicio no iniciado)"
	@echo ""
	@echo "Node.js:"
	@docker-compose exec tailwind node --version 2>/dev/null || echo "  (servicio no iniciado)"
	@echo ""
	@echo "PostgreSQL:"
	@docker-compose exec db psql --version 2>/dev/null || echo "  (servicio no iniciado)"
	@echo ""
