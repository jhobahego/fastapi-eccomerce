# 🚀 Guía de Inicio Rápido - Multiplataforma

Este proyecto soporta inicialización en **Windows**, **macOS** y **Linux**. Elige la opción que corresponda a tu sistema operativo:

## 📋 Prerrequisitos

- **Docker Desktop** (Windows/macOS) o **Docker Engine** (Linux)
- **Docker Compose** (incluido en Docker Desktop)

### Instalación de Docker por SO:

#### Windows
- Descarga Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
- Requiere Windows 10 Pro/Enterprise/Education o Windows 11

#### macOS
- Descarga Docker Desktop: https://docs.docker.com/desktop/install/mac-install/
- Compatible con macOS 10.15 o superior

#### Linux (Ubuntu/Debian)
```bash
# Instalación rápida
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

## 🎯 Inicialización del Proyecto

### Opción 1: Script de Python (Recomendado - Funciona en todos los OS)
```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd backend-fastapi

# Ejecutar script de inicialización
python scripts/init-project.py
```

### Opción 2: Linux/macOS (Bash)
```bash
# Hacer el script ejecutable
chmod +x scripts/init-project.sh

# Opción A: Usar Makefile
make init

# Opción B: Ejecutar directamente
./scripts/init-project.sh
```

### Opción 3: Windows PowerShell
```powershell
# Ejecutar desde PowerShell (puede requerir cambiar política de ejecución)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\init-project.ps1
```

### Opción 4: Windows Command Prompt
```cmd
# Ejecutar desde CMD
.\scripts\init-project.bat
```

## 🔧 Comandos Útiles Post-Instalación

### Ver logs en tiempo real
```bash
# Docker Compose v2 (recomendado)
docker compose logs -f

# Docker Compose v1 (legacy)
docker-compose logs -f
```

### Acceder al contenedor de la aplicación
```bash
# Docker Compose v2
docker compose exec web bash

# Docker Compose v1
docker-compose exec web bash
```

### Parar todos los servicios
```bash
# Docker Compose v2
docker compose down

# Docker Compose v1
docker-compose down
```

### Reconstruir después de cambios
```bash
# Docker Compose v2
docker compose up --build

# Docker Compose v1
docker-compose up --build
```

## 🌐 URLs Importantes

Una vez iniciado el proyecto:

- **API Principal**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📁 Estructura de Archivos de Inicialización

```
scripts/
├── init-project.sh     # Script de Bash (Linux/macOS)
├── init-project.ps1    # Script de PowerShell (Windows)
├── init-project.bat    # Script de Batch (Windows)
└── init-project.py     # Script de Python (Multiplataforma)
```

## 🛠️ Resolución de Problemas

### Error: "Docker no está ejecutándose"
- **Windows/macOS**: Inicia Docker Desktop
- **Linux**: `sudo systemctl start docker`

### Error: "Permission denied" en Linux
```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
# Reiniciar sesión o ejecutar:
newgrp docker
```

### Error: "docker-compose not found" en Windows
- Docker Desktop incluye `docker compose` (v2)
- Los scripts detectan automáticamente la versión disponible

### Puerto 8000 ya en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar el primer número
```

### Problemas con PowerShell en Windows
```powershell
# Permitir ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# O ejecutar directamente
powershell -ExecutionPolicy Bypass -File .\scripts\init-project.ps1
```

## 🎛️ Variables de Entorno

El archivo `.env` se crea automáticamente con valores por defecto. Puedes modificarlo según tus necesidades:

```env
# Base de datos
POSTGRES_DB=ecommerce_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# JWT
SECRET_KEY=your-super-secret-key-for-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
```

## 📞 Soporte

Si encuentras problemas:

1. Verifica que Docker esté ejecutándose
2. Asegúrate de estar en el directorio raíz del proyecto
3. Revisa los logs: `docker compose logs -f`
4. Para reiniciar completamente: `docker compose down -v && docker compose up --build`

---

**¡Listo!** 🎉 Tu API de e-commerce debería estar funcionando en http://localhost:8000
