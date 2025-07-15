#!/usr/bin/env python3
"""
Script para probar la conexión a Redis
"""

import redis
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def test_redis_connection():
    """Probar conexión a Redis"""
    try:
        redis_url = os.getenv("REDIS_URL")
        print(f"🔗 Conectando a Redis: {redis_url}")

        # Crear conexión
        r = redis.from_url(redis_url, decode_responses=True)

        # Probar conexión
        r.ping()
        print("✅ Conexión a Redis exitosa!")

        # Probar operaciones básicas
        success = r.set("test_key", "test_value")
        print(f"📝 Set operation: {success}")

        result = r.get("test_key")
        print(f"📖 Get operation: {result}")

        # Limpiar
        r.delete("test_key")
        print("🧹 Test key eliminada")

        return True

    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False


if __name__ == "__main__":
    test_redis_connection()
