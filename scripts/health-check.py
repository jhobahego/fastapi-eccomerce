#!/usr/bin/env python3
"""
Script para verificar el estado de salud del proyecto Docker
Compatible con Windows, macOS y Linux
"""

import subprocess
import sys
import time
import requests


def run_command(command):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def check_docker_status():
    """Verifica el estado de Docker"""
    print("🐳 Verificando Docker...")

    # Verificar si Docker está ejecutándose
    if run_command("docker info") is None:
        print("❌ Docker no está ejecutándose")
        return False

    print("✅ Docker está ejecutándose")
    return True


def check_containers():
    """Verifica el estado de los contenedores"""
    print("\n📦 Verificando contenedores...")

    # Obtener estado de contenedores
    containers = run_command(
        "docker-compose ps --format json 2>/dev/null || docker compose ps --format json"
    )

    if not containers:
        print("❌ No se encontraron contenedores ejecutándose")
        return False

    # Verificar contenedores específicos
    web_result = run_command(
        "docker-compose ps web 2>/dev/null || docker compose ps web 2>/dev/null || echo ''"
    )
    db_result = run_command(
        "docker-compose ps db 2>/dev/null || docker compose ps db 2>/dev/null || echo ''"
    )
    redis_result = run_command(
        "docker-compose ps redis 2>/dev/null || docker compose ps redis 2>/dev/null || echo ''"
    )

    web_running = web_result and "web" in web_result
    db_running = db_result and "db" in db_result
    redis_running = redis_result and "redis" in redis_result

    if web_running:
        print("✅ Contenedor web está ejecutándose")
    else:
        print("❌ Contenedor web no está ejecutándose")

    if db_running:
        print("✅ Contenedor db está ejecutándose")
    else:
        print("❌ Contenedor db no está ejecutándose")

    if redis_running:
        print("✅ Contenedor redis está ejecutándose")
    else:
        print("❌ Contenedor redis no está ejecutándose")

    return web_running and db_running and redis_running


def check_api_health():
    """Verifica la salud de la API"""
    print("\n🌐 Verificando API...")

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ API responde correctamente")
                return True
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                print(
                    f"⏳ Intento {attempt + 1}/{max_retries} - Esperando respuesta de la API..."
                )
                time.sleep(3)
            else:
                print("❌ API no responde")
                return False

    return False


def check_database_connection():
    """Verifica la conexión a la base de datos"""
    print("\n🗄️  Verificando base de datos...")

    try:
        # Verificar conexión desde el contenedor web
        result = run_command(
            "docker-compose exec -T web python -c \"from app.database import get_db; from app.utils.db_utils import test_db_connection; db = next(get_db()); print('DB connected:', test_db_connection(db))\" 2>/dev/null || docker compose exec -T web python -c \"from app.database import get_db; from app.utils.db_utils import test_db_connection; db = next(get_db()); print('DB connected:', test_db_connection(db))\" 2>/dev/null"
        )

        if result and "True" in result:
            print("✅ Base de datos conectada")
            return True
        else:
            print("❌ Error de conexión a base de datos")
            return False
    except Exception:
        print("❌ No se pudo verificar la conexión a base de datos")
        return False


def check_logs_for_errors():
    """Verifica logs en busca de errores críticos"""
    print("\n📋 Verificando logs...")

    try:
        logs = run_command(
            "docker-compose logs web --tail=50 2>/dev/null || docker compose logs web --tail=50 2>/dev/null"
        )

        if not logs:
            print("⚠️  No se pudieron obtener logs")
            return True

        error_keywords = ["ERROR", "CRITICAL", "Exception", "Failed", "Error"]
        errors_found = []

        for line in logs.split("\n"):
            for keyword in error_keywords:
                if keyword in line and "health" not in line.lower():
                    errors_found.append(line.strip())

        if errors_found:
            print(f"⚠️  Se encontraron {len(errors_found)} errores en logs:")
            for error in errors_found[-3:]:  # Mostrar solo los últimos 3
                print(f"   {error}")
            return False
        else:
            print("✅ No se encontraron errores críticos en logs")
            return True

    except Exception:
        print("⚠️  No se pudieron analizar los logs")
        return True


def main():
    """Función principal"""
    print("🔍 Verificación de Salud del Proyecto")
    print("=" * 40)

    all_checks_passed = True

    # Ejecutar verificaciones
    checks = [
        ("Docker", check_docker_status),
        ("Contenedores", check_containers),
        ("API", check_api_health),
        ("Base de datos", check_database_connection),
        ("Logs", check_logs_for_errors),
    ]

    for check_name, check_func in checks:
        try:
            if not check_func():
                all_checks_passed = False
        except Exception as e:
            print(f"❌ Error en verificación de {check_name}: {e}")
            all_checks_passed = False

    # Resultado final
    print("\n" + "=" * 40)
    if all_checks_passed:
        print("🎉 ¡Todas las verificaciones pasaron exitosamente!")
        print("\n🌐 URLs disponibles:")
        print("   - API: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
    else:
        print("⚠️  Algunas verificaciones fallaron")
        print("\n🛠️  Para solucionar problemas:")
        print("   - Reiniciar: docker-compose restart")
        print("   - Ver logs: docker-compose logs -f")
        print("   - Reconstruir: docker-compose up --build")

    sys.exit(0 if all_checks_passed else 1)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Uso: python scripts/health-check.py")
        print("")
        print("Este script verifica el estado de salud del proyecto Docker:")
        print("  - Estado de Docker")
        print("  - Contenedores ejecutándose")
        print("  - Respuesta de la API")
        print("  - Conexión a base de datos")
        print("  - Análisis de logs")
        sys.exit(0)

    try:
        import requests
    except ImportError:
        print("❌ La librería 'requests' no está instalada.")
        print("   Instala con: pip install requests")
        sys.exit(1)

    main()
