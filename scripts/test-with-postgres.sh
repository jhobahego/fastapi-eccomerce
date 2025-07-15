#!/bin/bash

# Script para ejecutar tests con PostgreSQL
# Este script maneja automáticamente el ciclo de vida de PostgreSQL para tests

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si Docker está disponible
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado o no está en PATH"
        exit 1
    fi
    
    # Verificar Docker Compose (tanto standalone como integrado)
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE_CMD="docker compose"
    else
        log_error "Docker Compose no está instalado o no está disponible"
        exit 1
    fi
    
    log_info "Usando Docker Compose: $DOCKER_COMPOSE_CMD"
}

# Función para verificar si PostgreSQL de tests está corriendo
is_postgres_running() {
    $DOCKER_COMPOSE_CMD -f docker-compose.test.yml ps postgres-test | grep -q "Up" 2>/dev/null
}

# Función para esperar que PostgreSQL esté listo
wait_for_postgres() {
    log_info "Esperando que PostgreSQL esté listo para aceptar conexiones..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if $DOCKER_COMPOSE_CMD -f docker-compose.test.yml exec -T postgres-test pg_isready -U test_user &> /dev/null; then
            log_success "PostgreSQL está listo!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    log_error "Timeout esperando que PostgreSQL esté listo"
    return 1
}

# Función para inicializar PostgreSQL para tests
start_postgres() {
    log_info "Iniciando PostgreSQL para tests..."
    
    if is_postgres_running; then
        log_warning "PostgreSQL ya está corriendo"
        return 0
    fi
    
    $DOCKER_COMPOSE_CMD -f docker-compose.test.yml up -d postgres-test
    
    if wait_for_postgres; then
        log_success "PostgreSQL iniciado correctamente"
        return 0
    else
        log_error "Error al iniciar PostgreSQL"
        return 1
    fi
}

# Función para detener PostgreSQL de tests
stop_postgres() {
    log_info "Deteniendo PostgreSQL de tests..."
    $DOCKER_COMPOSE_CMD -f docker-compose.test.yml down
    log_success "PostgreSQL detenido"
}

# Función para limpiar PostgreSQL de tests
clean_postgres() {
    log_info "Limpiando PostgreSQL de tests (incluyendo volúmenes)..."
    $DOCKER_COMPOSE_CMD -f docker-compose.test.yml down -v
    log_success "PostgreSQL limpiado completamente"
}

# Función para ejecutar tests
run_tests() {
    local test_args="$@"
    
    log_info "Ejecutando tests con PostgreSQL..."
    export USE_POSTGRES_FOR_TESTS=true
    
    if python -m pytest tests/ -v $test_args; then
        log_success "Todos los tests pasaron exitosamente"
        return 0
    else
        log_error "Algunos tests fallaron"
        return 1
    fi
}

# Función para mostrar ayuda
show_help() {
    echo "🐘 Script de gestión de tests con PostgreSQL"
    echo "==========================================="
    echo ""
    echo "Uso: $0 [COMANDO] [OPCIONES_PYTEST]"
    echo ""
    echo "Comandos:"
    echo "  start        Iniciar PostgreSQL para tests"
    echo "  stop         Detener PostgreSQL de tests"
    echo "  clean        Limpiar PostgreSQL (incluyendo volúmenes)"
    echo "  test         Ejecutar tests con PostgreSQL (auto start/stop)"
    echo "  test-keep    Ejecutar tests manteniendo PostgreSQL activo"
    echo "  status       Mostrar estado de PostgreSQL de tests"
    echo "  help         Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 test                           # Ejecutar todos los tests"
    echo "  $0 test tests/test_api/          # Ejecutar solo tests de API"
    echo "  $0 test --cov=app               # Ejecutar tests con cobertura"
    echo "  $0 test-keep                    # Ejecutar tests manteniendo BD"
    echo "  $0 start                        # Solo iniciar PostgreSQL"
    echo "  $0 clean                        # Limpiar todo"
}

# Función para mostrar estado
show_status() {
    log_info "Estado de PostgreSQL para tests:"
    
    if is_postgres_running; then
        log_success "PostgreSQL está corriendo"
        echo ""
        $DOCKER_COMPOSE_CMD -f docker-compose.test.yml ps postgres-test
    else
        log_warning "PostgreSQL no está corriendo"
    fi
}

# Función principal
main() {
    local command="${1:-help}"
    shift || true
    
    # Verificar Docker
    check_docker
    
    case "$command" in
        "start")
            start_postgres
            ;;
        "stop")
            stop_postgres
            ;;
        "clean")
            clean_postgres
            ;;
        "test")
            if start_postgres; then
                run_tests "$@"
                local test_result=$?
                stop_postgres
                exit $test_result
            else
                exit 1
            fi
            ;;
        "test-keep")
            if start_postgres; then
                run_tests "$@"
            else
                exit 1
            fi
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "Comando desconocido: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar si el script se está ejecutando directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
