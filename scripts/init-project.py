#!/usr/bin/env python3
"""
Script para inicializar el proyecto con Docker por primera vez
Compatible con Windows, macOS y Linux
"""

import os
import sys
import subprocess
import platform
import time
import shutil
from pathlib import Path


class Colors:
    """Códigos de color ANSI para terminales que los soporten"""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_colored(message, color=Colors.END):
    """Imprime mensaje con color si la terminal lo soporta"""
    if platform.system() == "Windows":
        # En Windows, intentar usar colorama si está disponible
        try:
            import colorama

            colorama.init()
            print(f"{color}{message}{Colors.END}")
        except ImportError:
            print(message)
    else:
        print(f"{color}{message}{Colors.END}")


def check_command(command):
    """Verifica si un comando está disponible en el sistema"""
    return shutil.which(command) is not None


def run_command(command, shell=False):
    """Ejecuta un comando y maneja errores"""
    try:
        if isinstance(command, str):
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )
        else:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print_colored(
            f"❌ Error ejecutando comando: {' '.join(command) if isinstance(command, list) else command}",
            Colors.RED,
        )
        print_colored(f"Error: {e.stderr}", Colors.RED)
        return None


def main():
    """Función principal"""
    print_colored(
        "🐳 Inicializando proyecto Ecommerce Backend con Docker...", Colors.CYAN
    )
    print_colored("=" * 56, Colors.CYAN)

    # Cambiar al directorio del proyecto
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)

    # Verificar si Docker está instalado
    if not check_command("docker"):
        print_colored("❌ Docker no está instalado.", Colors.RED)
        if platform.system() == "Windows":
            print_colored(
                "   Descarga Docker Desktop desde: https://docs.docker.com/desktop/install/windows-install/",
                Colors.YELLOW,
            )
        elif platform.system() == "Darwin":
            print_colored(
                "   Descarga Docker Desktop desde: https://docs.docker.com/desktop/install/mac-install/",
                Colors.YELLOW,
            )
        else:
            print_colored(
                "   Instala Docker desde: https://docs.docker.com/engine/install/",
                Colors.YELLOW,
            )
        sys.exit(1)

    # Verificar si Docker Compose está disponible
    has_compose_v2 = (
        check_command("docker") and run_command("docker compose version") is not None
    )
    has_compose_v1 = check_command("docker-compose")

    if not (has_compose_v1 or has_compose_v2):
        print_colored("❌ Docker Compose no está disponible.", Colors.RED)
        print_colored("   Por favor instala Docker Compose.", Colors.YELLOW)
        sys.exit(1)

    # Determinar qué versión de docker-compose usar
    compose_cmd = "docker compose" if has_compose_v2 else "docker-compose"

    # Verificar si Docker está ejecutándose
    if run_command("docker info") is None:
        print_colored(
            "❌ Docker no está ejecutándose. Por favor inicia Docker.", Colors.RED
        )
        sys.exit(1)

    # Crear archivo .env si no existe
    env_file = Path(".env")
    env_docker_file = Path(".env.docker")

    if not env_file.exists():
        if env_docker_file.exists():
            print_colored("📄 Creando archivo .env desde .env.docker...", Colors.YELLOW)
            shutil.copy2(env_docker_file, env_file)
            print_colored(
                "✅ Archivo .env creado. Puedes editarlo según tus necesidades.",
                Colors.GREEN,
            )
        else:
            print_colored(
                "⚠️  Archivo .env.docker no encontrado. Creando .env básico...",
                Colors.YELLOW,
            )
            env_content = """# Configuración básica para desarrollo
POSTGRES_DB=ecommerce_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SECRET_KEY=your-super-secret-key-for-development
PROJECT_NAME=Ecommerce API
VERSION=1.0.0
DESCRIPTION=Backend API for Ecommerce application
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:8000"]
JWT_DEBUG=true
"""
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(env_content)
            print_colored("✅ Archivo .env básico creado.", Colors.GREEN)
    else:
        print_colored("📄 El archivo .env ya existe.", Colors.BLUE)

    # Construir imágenes
    if "--skip-build" not in sys.argv:
        print_colored("🔨 Construyendo imágenes Docker...", Colors.YELLOW)
        if run_command(f"{compose_cmd} build") is None:
            print_colored("❌ Error al construir las imágenes Docker.", Colors.RED)
            sys.exit(1)
        print_colored("✅ Imágenes construidas exitosamente.", Colors.GREEN)

    # Levantar servicios
    print_colored("🚀 Levantando servicios...", Colors.YELLOW)
    if run_command(f"{compose_cmd} up -d") is None:
        print_colored("❌ Error al levantar los servicios.", Colors.RED)
        sys.exit(1)
    print_colored("✅ Servicios iniciados.", Colors.GREEN)

    # Esperar a que los servicios estén listos
    print_colored("⏳ Esperando a que los servicios estén listos...", Colors.YELLOW)
    time.sleep(15)

    # Verificar estado de los contenedores
    print_colored("📊 Estado de los contenedores:", Colors.BLUE)
    run_command(f"{compose_cmd} ps")

    # Mensaje final
    print_colored("", Colors.END)
    print_colored("✅ ¡Proyecto inicializado exitosamente!", Colors.GREEN)
    print_colored("", Colors.END)
    print_colored("🌐 La API está disponible en: http://localhost:8000", Colors.CYAN)
    print_colored(
        "📚 Documentación Swagger en: http://localhost:8000/docs", Colors.CYAN
    )
    print_colored("🔍 Documentación ReDoc en: http://localhost:8000/redoc", Colors.CYAN)
    print_colored("", Colors.END)
    print_colored("📋 Comandos útiles:", Colors.BLUE)
    print_colored(
        f"  {compose_cmd} logs -f        - Ver logs en tiempo real", Colors.END
    )
    print_colored(
        f"  {compose_cmd} exec web bash  - Acceder al shell del contenedor", Colors.END
    )
    print_colored(
        f"  {compose_cmd} down           - Parar todos los servicios", Colors.END
    )
    print_colored("", Colors.END)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Uso: python scripts/init-project.py [--skip-build] [--help]")
        print("")
        print("Opciones:")
        print("  --skip-build    Omite la construcción de imágenes Docker")
        print("  --help, -h      Muestra esta ayuda")
        sys.exit(0)

    main()
