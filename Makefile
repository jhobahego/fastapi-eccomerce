.PHONY: help build up down logs shell migrate seed test clean dev prod init

help: ## Mostrar esta ayuda
	@echo "🐳 Comandos de Docker para Ecommerce Backend API"
	@echo "================================================"
	@echo "📋 Para inicialización multiplataforma, usa:"
	@echo "   - Linux/macOS: make init o ./scripts/init-project.sh"
	@echo "   - Windows (PowerShell): ./scripts/init-project.ps1"
	@echo "   - Windows (CMD): ./scripts/init-project.bat"
	@echo "   - Cualquier OS: python scripts/init-project.py"
	@echo ""
	@echo "🚀 EJECUCIÓN CON VALIDACIÓN (RECOMENDADO):"
	@echo "   - make dev-safe          # Desarrollo con tests SQLite"
	@echo "   - make dev-postgres-safe # Desarrollo con tests PostgreSQL"
	@echo "   - make quick-start       # Inicio rápido (solo tests unitarios)"
	@echo "   - make deploy-safe       # Deployment con validación completa"
	@echo "   - ./scripts/run-with-tests.sh [modo]  # Script avanzado"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

init: ## Inicializar proyecto completo (Linux/macOS)
	@echo "🚀 Inicializando proyecto..."
	@./scripts/init-project.sh

build: ## Construir las imágenes Docker
	@echo "🔨 Construyendo imágenes Docker..."
	docker compose build

up: ## Levantar los servicios
	@echo "🚀 Levantando servicios..."
	docker compose up -d

down: ## Bajar los servicios
	@echo "🛑 Bajando servicios..."
	docker compose down

logs: ## Ver logs en tiempo real
	@echo "📋 Mostrando logs..."
	docker compose logs -f

logs-web: ## Ver logs solo del servicio web
	@echo "📋 Mostrando logs del servicio web..."
	docker compose logs -f web

logs-db: ## Ver logs solo de la base de datos
	@echo "📋 Mostrando logs de la base de datos..."
	docker compose logs -f db

shell: ## Acceder al shell del contenedor web
	@echo "🐚 Accediendo al shell del contenedor web..."
	docker compose exec web bash

shell-db: ## Acceder al shell de PostgreSQL
	@echo "🐚 Accediendo a PostgreSQL..."
	docker compose exec db psql -U postgres -d ecommerce_db

migrate: ## Ejecutar migraciones
	@echo "🔄 Ejecutando migraciones..."
	docker compose exec web alembic upgrade head

migration: ## Crear nueva migración (usar: make migration msg="descripcion")
	@echo "📝 Creando nueva migración..."
	docker compose exec web alembic revision --autogenerate -m "$(msg)"

seed: ## Poblar base de datos
	@echo "🌱 Poblando base de datos..."
	docker compose exec web python -m app.utils.seed_database

superuser: ## Crear superusuario
	@echo "👤 Creando superusuario..."
	docker compose exec web python -m app.utils.make_superuser

test: ## Ejecutar todos los tests (SQLite rápido)
	@echo "🧪 Ejecutando todos los tests con SQLite..."
	python -m pytest tests/ -v

test-postgres: ## Ejecutar tests con PostgreSQL (producción-like)
	@echo "🐘 Configurando PostgreSQL para tests..."
	@docker compose -f docker compose.test.yml up -d postgres-test
	@echo "⏳ Esperando que PostgreSQL esté listo..."
	@sleep 10
	@echo "🧪 Ejecutando tests con PostgreSQL..."
	@USE_POSTGRES_FOR_TESTS=true python -m pytest tests/ -v
	@echo "🛑 Limpiando PostgreSQL de tests..."
	@docker compose -f docker compose.test.yml down

test-postgres-keep: ## Ejecutar tests con PostgreSQL manteniendo la BD
	@echo "🐘 Configurando PostgreSQL para tests..."
	@docker compose -f docker compose.test.yml up -d postgres-test
	@echo "⏳ Esperando que PostgreSQL esté listo..."
	@sleep 10
	@echo "🧪 Ejecutando tests con PostgreSQL (manteniendo BD)..."
	@USE_POSTGRES_FOR_TESTS=true python -m pytest tests/ -v

test-postgres-down: ## Bajar PostgreSQL de tests
	@echo "� Bajando PostgreSQL de tests..."
	@docker compose -f docker compose.test.yml down

test-postgres-clean: ## Limpiar completamente PostgreSQL de tests
	@echo "🧹 Limpiando PostgreSQL de tests..."
	@docker compose -f docker compose.test.yml down -v

test-unit: ## Ejecutar solo tests unitarios
	@echo "�🔬 Ejecutando tests unitarios..."
	python -m pytest tests/test_models tests/test_schemas tests/test_services -v -m "not integration"

test-api: ## Ejecutar tests de API
	@echo "🌐 Ejecutando tests de API..."
	python -m pytest tests/test_api -v

test-integration: ## Ejecutar tests de integración
	@echo "🔗 Ejecutando tests de integración..."
	python -m pytest tests/test_integration -v -m integration

test-coverage: ## Ejecutar tests con reporte de cobertura
	@echo "📊 Ejecutando tests con cobertura..."
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-coverage-postgres: ## Ejecutar tests con cobertura usando PostgreSQL
	@echo "🐘 Configurando PostgreSQL para tests con cobertura..."
	@docker compose -f docker compose.test.yml up -d postgres-test
	@echo "⏳ Esperando que PostgreSQL esté listo..."
	@sleep 10
	@echo "📊 Ejecutando tests con cobertura usando PostgreSQL..."
	@USE_POSTGRES_FOR_TESTS=true python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
	@echo "🛑 Limpiando PostgreSQL de tests..."
	@docker compose -f docker compose.test.yml down

test-watch: ## Ejecutar tests en modo watch
	@echo "👀 Ejecutando tests en modo watch..."
	python -m pytest tests/ -v --tb=short -x --ff

test-install: ## Instalar dependencias de testing
	@echo "📦 Instalando dependencias de testing..."
	pip install -r requirements-test.txt

test-clean: ## Limpiar archivos de test
	@echo "🧹 Limpiando archivos de test..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -f .coverage
	rm -f test.db

lint: ## Ejecutar linting
	@echo "🔍 Ejecutando linting..."
	docker compose exec web flake8 app/
	docker compose exec web black --check app/

format: ## Formatear código
	@echo "✨ Formateando código..."
	docker compose exec web black app/

clean: ## Limpiar contenedores y volúmenes
	@echo "🧹 Limpiando contenedores y volúmenes..."
	docker compose down -v
	docker compose rm -f
	docker system prune -f

dev: ## Modo desarrollo completo (build + up + logs)
	@echo "🚀 Iniciando en modo desarrollo..."
	make build
	make up
	make logs

restart: ## Reiniciar todos los servicios
	@echo "🔄 Reiniciando servicios..."
	make down
	make up

restart-web: ## Reiniciar solo el servicio web
	@echo "🔄 Reiniciando servicio web..."
	docker compose restart web

status: ## Ver estado de los contenedores
	@echo "📊 Estado de los contenedores:"
	docker compose ps

backup-db: ## Hacer backup de la base de datos
	@echo "💾 Creando backup de la base de datos..."
	docker compose exec db pg_dump -U postgres ecommerce_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restaurar backup (usar: make restore-db file=backup.sql)
	@echo "📥 Restaurando backup de la base de datos..."
	docker compose exec -T db psql -U postgres ecommerce_db < $(file)

prod: ## Modo producción
	@echo "🏭 Iniciando en modo producción..."
	docker compose -f docker compose.yml -f docker compose.prod.yml up -d

health: ## Verificar estado de salud del proyecto
	@echo "🔍 Verificando estado de salud..."
	@python scripts/health-check.py

# =============================================================================
# COMANDOS DE EJECUCIÓN CON VALIDACIÓN
# =============================================================================

dev-safe: ## Desarrollo con tests previos (SQLite rápido)
	@echo "🧪 Ejecutando tests antes de iniciar desarrollo..."
	@if make test; then \
		echo "✅ Tests pasaron! Iniciando aplicación..."; \
		make dev; \
	else \
		echo "❌ Tests fallaron! No se iniciará la aplicación."; \
		exit 1; \
	fi

dev-postgres-safe: ## Desarrollo con tests PostgreSQL previos (validación completa)
	@echo "🐘 Ejecutando tests con PostgreSQL antes de iniciar desarrollo..."
	@if make test-postgres; then \
		echo "✅ Tests PostgreSQL pasaron! Iniciando aplicación..."; \
		make dev; \
	else \
		echo "❌ Tests PostgreSQL fallaron! No se iniciará la aplicación."; \
		exit 1; \
	fi

run-safe: ## Solo ejecutar aplicación con tests SQLite previos
	@echo "🧪 Validando código con tests rápidos..."
	@if make test; then \
		echo "✅ Tests pasaron! Iniciando aplicación en modo up..."; \
		make up; \
	else \
		echo "❌ Tests fallaron! No se iniciará la aplicación."; \
		exit 1; \
	fi

run-postgres-safe: ## Solo ejecutar aplicación con tests PostgreSQL previos
	@echo "🐘 Validando código con tests PostgreSQL..."
	@if make test-postgres; then \
		echo "✅ Tests PostgreSQL pasaron! Iniciando aplicación..."; \
		make up; \
	else \
		echo "❌ Tests PostgreSQL fallaron! No se iniciará la aplicación."; \
		exit 1; \
	fi

deploy-safe: ## Deployment con validación completa
	@echo "🚀 Validación completa para deployment..."
	@echo "🧪 Paso 1/3: Tests con SQLite..."
	@if ! make test; then \
		echo "❌ Tests SQLite fallaron!"; \
		exit 1; \
	fi
	@echo "🐘 Paso 2/3: Tests con PostgreSQL..."
	@if ! make test-postgres; then \
		echo "❌ Tests PostgreSQL fallaron!"; \
		exit 1; \
	fi
	@echo "📊 Paso 3/3: Tests con cobertura..."
	@if ! make test-coverage-postgres; then \
		echo "❌ Tests de cobertura fallaron!"; \
		exit 1; \
	fi
	@echo "✅ Todas las validaciones pasaron! Desplegando..."
	@make prod

quick-start: ## Inicio rápido para desarrollo diario
	@echo "⚡ Inicio rápido con validación mínima..."
	@if make test-unit; then \
		echo "✅ Tests unitarios pasaron! Iniciando desarrollo..."; \
		make up; \
		make logs; \
	else \
		echo "❌ Tests unitarios fallaron! Revisa el código."; \
		exit 1; \
	fi
