#!/bin/bash
set -e

echo "🚀 Iniciando deployment en Render..."

# Verificar que las variables de entorno estén configuradas
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY no está configurada"
    exit 1
fi

echo "✅ Variables de entorno verificadas"

# Ejecutar migraciones
echo "📦 Ejecutando migraciones de base de datos..."
alembic upgrade head

# Poblar datos iniciales si es necesario
echo "🌱 Poblando datos iniciales..."
python -m app.utils.seed_database

echo "✅ Deployment completado exitosamente!"
echo "🌐 API disponible en: https://$RENDER_EXTERNAL_HOSTNAME"
echo "📚 Documentación en: https://$RENDER_EXTERNAL_HOSTNAME/docs"
