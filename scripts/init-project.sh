#!/bin/bash

# Script para inicializar el proyecto con Docker por primera vez

set -e

echo "🐳 Inicializando proyecto Ecommerce Backend con Docker..."
echo "========================================================"

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está disponible. Por favor instala Docker Compose."
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env desde .env.docker..."
    cp .env.docker .env
    echo "✅ Archivo .env creado. Puedes editarlo según tus necesidades."
else
    echo "📄 El archivo .env ya existe."
fi

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

# Levantar servicios
echo "🚀 Levantando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los contenedores
echo "📊 Estado de los contenedores:"
docker-compose ps

echo ""
echo "✅ ¡Proyecto inicializado exitosamente!"
echo ""
echo "🌐 La API está disponible en: http://localhost:8000"
echo "📚 Documentación Swagger en: http://localhost:8000/docs"
echo "🔍 Documentación ReDoc en: http://localhost:8000/redoc"
echo ""
echo "📋 Comandos útiles:"
echo "  make logs     - Ver logs en tiempo real"
echo "  make shell    - Acceder al shell del contenedor"
echo "  make health   - Verificar estado de salud del proyecto"
echo "  make down     - Parar todos los servicios"
echo "  make help     - Ver todos los comandos disponibles"
echo ""
echo "🔍 Para verificar que todo funciona correctamente:"
echo "  python scripts/health-check.py"
echo ""
