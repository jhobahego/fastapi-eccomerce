#!/usr/bin/env python3
"""
Script para crear todas las tablas en la base de datos
"""

from app.database import engine, Base


def create_tables():
    """Crear todas las tablas en la base de datos"""
    print("Creating database tables...")

    # Esto creará todas las tablas definidas en los modelos
    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
