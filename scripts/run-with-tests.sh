#!/bin/bash

# Script para ejecutar la aplicación con validación previa de tests
# Proporciona diferentes niveles de validación según el contexto

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis para mejor UX
CHECK="✅"
CROSS="❌"
ROCKET="🚀"
TEST="🧪"
POSTGRES="🐘"
LIGHTNING="⚡"
GEAR="⚙️"
SHIELD="🛡️"

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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Función para mostrar header del script
show_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║               ${ROCKET} ECOMMERCE APP LAUNCHER ${ROCKET}                    ║${NC}"
    echo -e "${CYAN}║              Ejecución con Validación de Tests              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info &> /dev/null; then
        log_error "Docker no está corriendo. Por favor, inicia Docker."
        exit 1
    fi
}

# Función para ejecutar tests SQLite
run_sqlite_tests() {
    log_step "${TEST} Ejecutando tests con SQLite (rápido)..."
    if python -m pytest tests/ -v --tb=short; then
        log_success "${CHECK} Tests SQLite pasaron exitosamente"
        return 0
    else
        log_error "${CROSS} Tests SQLite fallaron"
        return 1
    fi
}

# Función para ejecutar tests PostgreSQL
run_postgres_tests() {
    log_step "${POSTGRES} Ejecutando tests con PostgreSQL (producción-like)..."
    if ./scripts/test-with-postgres.sh test; then
        log_success "${CHECK} Tests PostgreSQL pasaron exitosamente"
        return 0
    else
        log_error "${CROSS} Tests PostgreSQL fallaron"
        return 1
    fi
}

# Función para ejecutar tests unitarios únicamente
run_unit_tests() {
    log_step "${LIGHTNING} Ejecutando solo tests unitarios (súper rápido)..."
    if python -m pytest tests/test_models tests/test_schemas tests/test_services -v --tb=short -m "not integration"; then
        log_success "${CHECK} Tests unitarios pasaron exitosamente"
        return 0
    else
        log_error "${CROSS} Tests unitarios fallaron"
        return 1
    fi
}

# Función para ejecutar tests con cobertura
run_coverage_tests() {
    log_step "${SHIELD} Ejecutando tests con cobertura..."
    if python -m pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80; then
        log_success "${CHECK} Tests de cobertura pasaron exitosamente"
        return 0
    else
        log_error "${CROSS} Tests de cobertura fallaron o cobertura insuficiente"
        return 1
    fi
}

# Función para iniciar la aplicación
start_application() {
    local mode="$1"
    
    case "$mode" in
        "dev")
            log_step "${GEAR} Iniciando aplicación en modo desarrollo..."
            make dev
            ;;
        "up")
            log_step "${ROCKET} Iniciando aplicación (solo up)..."
            make up
            ;;
        "prod")
            log_step "${ROCKET} Iniciando aplicación en modo producción..."
            make prod
            ;;
        *)
            log_step "${ROCKET} Iniciando aplicación..."
            make up
            ;;
    esac
}

# Función para mostrar ayuda
show_help() {
    show_header
    echo "Uso: $0 [MODO] [OPCIONES]"
    echo ""
    echo "Modos de ejecución:"
    echo "  quick         ${LIGHTNING} Inicio rápido (solo tests unitarios + up)"
    echo "  safe          ${TEST} Desarrollo seguro (tests SQLite + dev)"
    echo "  postgres      ${POSTGRES} Validación completa (tests PostgreSQL + dev)"
    echo "  deploy        ${SHIELD} Validación de deployment (todos los tests + prod)"
    echo "  coverage      ${SHIELD} Con validación de cobertura (coverage + up)"
    echo ""
    echo "Opciones:"
    echo "  --up-only     Solo ejecutar 'make up' (sin logs)"
    echo "  --prod        Usar modo producción"
    echo "  --no-tests    Saltar tests (solo para emergencias)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 quick                    # Desarrollo diario rápido"
    echo "  $0 safe                     # Desarrollo con validación SQLite"
    echo "  $0 postgres                 # Validación completa con PostgreSQL"
    echo "  $0 deploy                   # Validación completa para deployment"
    echo "  $0 coverage --up-only       # Tests con cobertura + solo up"
    echo ""
}

# Función principal
main() {
    local mode="${1:-safe}"
    local up_only=false
    local prod_mode=false
    local skip_tests=false
    
    # Procesar argumentos
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            --up-only)
                up_only=true
                shift
                ;;
            --prod)
                prod_mode=true
                shift
                ;;
            --no-tests)
                skip_tests=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Opción desconocida: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    show_header
    
    # Verificar Docker
    check_docker
    
    # Determinar el modo de inicio de aplicación
    local app_mode="dev"
    if [[ "$up_only" == true ]]; then
        app_mode="up"
    elif [[ "$prod_mode" == true ]]; then
        app_mode="prod"
    fi
    
    # Ejecutar según el modo seleccionado
    case "$mode" in
        "quick")
            log_info "${LIGHTNING} Modo rápido: Solo tests unitarios"
            if [[ "$skip_tests" == false ]]; then
                run_unit_tests || exit 1
            fi
            start_application "$app_mode"
            ;;
            
        "safe")
            log_info "${TEST} Modo seguro: Tests SQLite completos"
            if [[ "$skip_tests" == false ]]; then
                run_sqlite_tests || exit 1
            fi
            start_application "$app_mode"
            ;;
            
        "postgres")
            log_info "${POSTGRES} Modo PostgreSQL: Validación completa"
            if [[ "$skip_tests" == false ]]; then
                run_postgres_tests || exit 1
            fi
            start_application "$app_mode"
            ;;
            
        "deploy")
            log_info "${SHIELD} Modo deployment: Validación exhaustiva"
            if [[ "$skip_tests" == false ]]; then
                log_step "Validación 1/3: Tests SQLite"
                run_sqlite_tests || exit 1
                
                log_step "Validación 2/3: Tests PostgreSQL"
                run_postgres_tests || exit 1
                
                log_step "Validación 3/3: Cobertura de código"
                run_coverage_tests || exit 1
            fi
            start_application "prod"
            ;;
            
        "coverage")
            log_info "${SHIELD} Modo cobertura: Tests con métricas"
            if [[ "$skip_tests" == false ]]; then
                run_coverage_tests || exit 1
            fi
            start_application "$app_mode"
            ;;
            
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
            
        *)
            log_error "Modo desconocido: $mode"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    log_success "${ROCKET} ¡Aplicación iniciada exitosamente!"
    echo ""
    log_info "Puedes acceder a:"
    log_info "  • API: http://localhost:8000"
    log_info "  • Docs: http://localhost:8000/docs"
    log_info "  • Redoc: http://localhost:8000/redoc"
    echo ""
    log_info "Para ver logs en tiempo real: make logs"
    log_info "Para detener la aplicación: make down"
    echo ""
}

# Verificar si el script se está ejecutando directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
