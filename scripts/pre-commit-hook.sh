#!/bin/bash

# Git pre-commit hook que ejecuta tests antes de permitir commits
# Para instalarlo: cp scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔍 Pre-commit hook: Ejecutando tests antes del commit..."

# Verificar si hay cambios en archivos Python
if git diff --cached --name-only | grep -E "\.(py)$" > /dev/null; then
    echo "📁 Detectados cambios en archivos Python, ejecutando tests..."
    
    # Ejecutar tests rápidos (SQLite)
    echo "🧪 Ejecutando tests unitarios..."
    if ! python -m pytest tests/test_models tests/test_schemas tests/test_services -v --tb=short -q; then
        echo "❌ Tests unitarios fallaron. Commit cancelado."
        echo "💡 Tip: Ejecuta 'make test' para ver los detalles completos."
        exit 1
    fi
    
    # Ejecutar tests de API básicos
    echo "🌐 Ejecutando tests de API básicos..."
    if ! python -m pytest tests/test_api/test_auth.py -q; then
        echo "❌ Tests de API fallaron. Commit cancelado."
        echo "💡 Tip: Ejecuta 'make test-api' para ver los detalles completos."
        exit 1
    fi
    
    echo "✅ Todos los tests pre-commit pasaron exitosamente!"
else
    echo "ℹ️  No hay cambios en archivos Python, saltando tests."
fi

echo "🚀 Pre-commit hook completado. Procediendo con el commit..."
