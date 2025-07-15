#!/bin/bash

# run_tests.sh - Script para ejecutar tests del proyecto FastAPI Ecommerce

set -e

echo "🧪 FastAPI Ecommerce - Test Runner"
echo "=================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar ayuda
show_help() {
    echo "Uso: ./run_tests.sh [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  all         Ejecutar todos los tests (por defecto)"
    echo "  unit        Ejecutar solo tests unitarios"
    echo "  api         Ejecutar tests de API"
    echo "  integration Ejecutar tests de integración"
    echo "  coverage    Ejecutar tests con reporte de cobertura"
    echo "  watch       Ejecutar tests en modo watch"
    echo "  install     Instalar dependencias de testing"
    echo "  clean       Limpiar archivos de test"
    echo "  help        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./run_tests.sh unit"
    echo "  ./run_tests.sh coverage"
    echo "  ./run_tests.sh watch"
}

# Función para verificar si pytest está instalado
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}❌ pytest no está instalado${NC}"
        echo -e "${YELLOW}Ejecuta: ./run_tests.sh install${NC}"
        exit 1
    fi
}

# Función para instalar dependencias
install_deps() {
    echo -e "${BLUE}📦 Instalando dependencias de testing...${NC}"
    
    if [ -f "requirements-test.txt" ]; then
        pip install -r requirements-test.txt
        echo -e "${GREEN}✅ Dependencias de testing instaladas${NC}"
    else
        echo -e "${RED}❌ Archivo requirements-test.txt no encontrado${NC}"
        exit 1
    fi
}

# Función para limpiar archivos de test
clean_test_files() {
    echo -e "${BLUE}🧹 Limpiando archivos de test...${NC}"
    
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -f .coverage
    rm -f test.db
    rm -rf tests/__pycache__/
    find tests/ -name "*.pyc" -delete
    find tests/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✅ Archivos de test limpiados${NC}"
}

# Función para ejecutar tests unitarios
run_unit_tests() {
    echo -e "${BLUE}🔬 Ejecutando tests unitarios...${NC}"
    pytest tests/test_models tests/test_schemas tests/test_services -v -m "not integration"
}

# Función para ejecutar tests de API
run_api_tests() {
    echo -e "${BLUE}🌐 Ejecutando tests de API...${NC}"
    pytest tests/test_api -v
}

# Función para ejecutar tests de integración
run_integration_tests() {
    echo -e "${BLUE}🔗 Ejecutando tests de integración...${NC}"
    pytest tests/test_integration -v -m integration
}

# Función para ejecutar todos los tests
run_all_tests() {
    echo -e "${BLUE}🧪 Ejecutando todos los tests...${NC}"
    pytest tests/ -v
}

# Función para ejecutar tests con cobertura
run_coverage_tests() {
    echo -e "${BLUE}📊 Ejecutando tests con cobertura...${NC}"
    pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
    
    if [ -d "htmlcov" ]; then
        echo -e "${GREEN}📋 Reporte de cobertura generado en htmlcov/index.html${NC}"
    fi
}

# Función para ejecutar tests en modo watch
run_watch_tests() {
    echo -e "${BLUE}👀 Ejecutando tests en modo watch...${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para salir${NC}"
    pytest tests/ -v --tb=short -x --ff -f
}

# Función principal
main() {
    local option="${1:-all}"
    
    case $option in
        "help"|"-h"|"--help")
            show_help
            ;;
        "install")
            install_deps
            ;;
        "clean")
            clean_test_files
            ;;
        "unit")
            check_pytest
            run_unit_tests
            ;;
        "api")
            check_pytest
            run_api_tests
            ;;
        "integration")
            check_pytest
            run_integration_tests
            ;;
        "coverage")
            check_pytest
            run_coverage_tests
            ;;
        "watch")
            check_pytest
            run_watch_tests
            ;;
        "all"|"")
            check_pytest
            run_all_tests
            ;;
        *)
            echo -e "${RED}❌ Opción desconocida: $option${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ No se encontró app/main.py. ¿Estás en el directorio correcto?${NC}"
    exit 1
fi

# Ejecutar función principal
main "$@"
