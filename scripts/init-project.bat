@echo off
REM Script para inicializar el proyecto con Docker por primera vez en Windows
REM Ejecutar desde Command Prompt o PowerShell

setlocal enabledelayedexpansion

echo 🐳 Inicializando proyecto Ecommerce Backend con Docker...
echo ========================================================

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está instalado. Por favor instala Docker Desktop para Windows.
    echo    Descarga desde: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Verificar si Docker Compose está disponible
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if !errorlevel! neq 0 (
        echo ❌ Docker Compose no está disponible.
        echo    Por favor instala Docker Compose o usa Docker Desktop que lo incluye.
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker no está ejecutándose. Por favor inicia Docker Desktop.
    pause
    exit /b 1
)

REM Crear archivo .env si no existe
if not exist ".env" (
    if exist ".env.docker" (
        echo 📄 Creando archivo .env desde .env.docker...
        copy ".env.docker" ".env" >nul
        echo ✅ Archivo .env creado. Puedes editarlo según tus necesidades.
    ) else (
        echo ⚠️  Archivo .env.docker no encontrado. Creando .env básico...
        (
            echo # Configuración básica para desarrollo
            echo POSTGRES_DB=ecommerce_db
            echo POSTGRES_USER=postgres
            echo POSTGRES_PASSWORD=postgres
            echo SECRET_KEY=your-super-secret-key-for-development
            echo PROJECT_NAME=Ecommerce API
            echo VERSION=1.0.0
            echo DESCRIPTION=Backend API for Ecommerce application
            echo ALGORITHM=HS256
            echo ACCESS_TOKEN_EXPIRE_MINUTES=30
            echo ADMIN_EMAIL=admin@example.com
            echo ADMIN_PASSWORD=admin123
            echo BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8000"]
            echo JWT_DEBUG=true
        ) > ".env"
        echo ✅ Archivo .env básico creado.
    )
) else (
    echo 📄 El archivo .env ya existe.
)

REM Verificar si se debe omitir la construcción
if "%1"=="--skip-build" goto :skip_build
if "%1"=="/skip-build" goto :skip_build

REM Construir imágenes
echo 🔨 Construyendo imágenes Docker...
%COMPOSE_CMD% build
if %errorlevel% neq 0 (
    echo ❌ Error al construir las imágenes Docker.
    pause
    exit /b 1
)
echo ✅ Imágenes construidas exitosamente.

:skip_build
REM Levantar servicios
echo 🚀 Levantando servicios...
%COMPOSE_CMD% up -d
if %errorlevel% neq 0 (
    echo ❌ Error al levantar los servicios.
    pause
    exit /b 1
)
echo ✅ Servicios iniciados.

REM Esperar a que los servicios estén listos
echo ⏳ Esperando a que los servicios estén listos...
timeout /t 15 /nobreak >nul

REM Verificar estado de los contenedores
echo 📊 Estado de los contenedores:
%COMPOSE_CMD% ps

echo.
echo ✅ ¡Proyecto inicializado exitosamente!
echo.
echo 🌐 La API está disponible en: http://localhost:8000
echo 📚 Documentación Swagger en: http://localhost:8000/docs
echo 🔍 Documentación ReDoc en: http://localhost:8000/redoc
echo.
echo 📋 Comandos útiles:
echo   %COMPOSE_CMD% logs -f        - Ver logs en tiempo real
echo   %COMPOSE_CMD% exec web bash  - Acceder al shell del contenedor
echo   %COMPOSE_CMD% down           - Parar todos los servicios
echo.

pause
