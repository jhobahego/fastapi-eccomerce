# Script para inicializar el proyecto con Docker por primera vez en Windows
# Ejecutar desde PowerShell como administrador o con permisos de ejecución

param(
    [switch]$SkipBuild = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Uso: .\scripts\init-project.ps1 [-SkipBuild] [-Help]"
    Write-Host ""
    Write-Host "Parámetros:"
    Write-Host "  -SkipBuild    Omite la construcción de imágenes Docker"
    Write-Host "  -Help         Muestra esta ayuda"
    exit 0
}

# Función para verificar si un comando existe
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

Write-Host "🐳 Inicializando proyecto Ecommerce Backend con Docker..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Verificar si Docker está instalado
if (-not (Test-Command "docker")) {
    Write-Host "❌ Docker no está instalado. Por favor instala Docker Desktop para Windows." -ForegroundColor Red
    Write-Host "   Descarga desde: https://docs.docker.com/desktop/install/windows-install/" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker Compose está disponible
if (-not (Test-Command "docker-compose")) {
    Write-Host "❌ Docker Compose no está disponible. Por favor instala Docker Compose." -ForegroundColor Red
    Write-Host "   O usa 'docker compose' (incluido en Docker Desktop)" -ForegroundColor Yellow
    exit 1
}

# Verificar si Docker está ejecutándose
try {
    docker info | Out-Null
}
catch {
    Write-Host "❌ Docker no está ejecutándose. Por favor inicia Docker Desktop." -ForegroundColor Red
    exit 1
}

# Crear archivo .env si no existe
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.docker") {
        Write-Host "📄 Creando archivo .env desde .env.docker..." -ForegroundColor Yellow
        Copy-Item ".env.docker" ".env"
        Write-Host "✅ Archivo .env creado. Puedes editarlo según tus necesidades." -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Archivo .env.docker no encontrado. Creando .env básico..." -ForegroundColor Yellow
        @"
# Configuración básica para desarrollo
POSTGRES_DB=ecommerce_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SECRET_KEY=your-super-secret-key-for-development
PROJECT_NAME=Ecommerce API
VERSION=1.0.0
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ Archivo .env básico creado." -ForegroundColor Green
    }
}
else {
    Write-Host "📄 El archivo .env ya existe." -ForegroundColor Blue
}

if (-not $SkipBuild) {
    # Construir imágenes
    Write-Host "🔨 Construyendo imágenes Docker..." -ForegroundColor Yellow
    try {
        docker-compose build
        Write-Host "✅ Imágenes construidas exitosamente." -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Error al construir las imágenes Docker." -ForegroundColor Red
        exit 1
    }
}

# Levantar servicios
Write-Host "🚀 Levantando servicios..." -ForegroundColor Yellow
try {
    docker-compose up -d
    Write-Host "✅ Servicios iniciados." -ForegroundColor Green
}
catch {
    Write-Host "❌ Error al levantar los servicios." -ForegroundColor Red
    exit 1
}

# Esperar a que los servicios estén listos
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Verificar estado de los contenedores
Write-Host "📊 Estado de los contenedores:" -ForegroundColor Blue
docker-compose ps

Write-Host ""
Write-Host "✅ ¡Proyecto inicializado exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 La API está disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentación Swagger en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 Documentación ReDoc en: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Comandos útiles:" -ForegroundColor Blue
Write-Host "  docker-compose logs -f     - Ver logs en tiempo real"
Write-Host "  docker-compose exec web bash - Acceder al shell del contenedor"
Write-Host "  docker-compose down        - Parar todos los servicios"
Write-Host ""
Write-Host "💡 Para facilitar el uso, considera instalar 'make' para Windows o usar los comandos de docker-compose directamente." -ForegroundColor Yellow
