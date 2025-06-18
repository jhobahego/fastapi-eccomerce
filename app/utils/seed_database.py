#!/usr/bin/env python3
"""
Script para hacer seeding inicial de la base de datos.
Se puede ejecutar con: python -m app.utils.seed_database
"""

import sys
import os
from dotenv import load_dotenv
import asyncio

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.database import SessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserCreate
# from app.config import settings

# Cargar variables de entorno desde .env
load_dotenv()


async def create_superuser():
    """Crear superusuario inicial si no existe."""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_email or not admin_password:
            print(
                "❌ Las variables de entorno ADMIN_EMAIL y ADMIN_PASSWORD deben estar configuradas."
            )
            return

        existing_user = user_service.get_user_by_email(admin_email, raise_404=False)
        if existing_user:
            print(f"✅ El superusuario con email '{admin_email}' ya existe.")
            return

        # Se crea el usuario con el schema UserCreate, que no incluye is_superuser
        user_in = UserCreate(
            email=admin_email,
            password=admin_password,
            username="admin",
            first_name="Admin",
            last_name="User",
        )
        # El servicio crea el usuario con is_superuser=False por defecto
        user = user_service.create_user(user_in)

        # Se actualiza el usuario recién creado para darle privilegios de superusuario
        user.is_superuser = True
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Superusuario '{admin_email}' creado exitosamente.")

    except Exception as e:
        print(f"❌ Error al crear el superusuario: {e}")
    finally:
        db.close()


async def seed_database():
    """Función principal para poblar la base de datos con datos iniciales."""
    print("🌱 Empezando el seeding de la base de datos...")
    await create_superuser()
    # Aquí se pueden añadir otras funciones de seeding, como crear categorías por defecto.
    print("✅ Seeding de la base de datos completado.")


if __name__ == "__main__":
    # Para ejecutar este script directamente
    # python -m app.utils.seed_database
    asyncio.run(seed_database())
