#!/usr/bin/env python3
"""
Script para hacer a un usuario superusuario
"""

import sys
import os
from dotenv import load_dotenv

# Agregar el directorio padre al path para poder importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

load_dotenv()


def make_superuser(email: str):
    """Hacer a un usuario superusuario"""
    db: Session = SessionLocal()
    try:
        # Buscar el usuario por email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ Usuario con email '{email}' no encontrado")
            return False

        # Actualizar a superusuario
        user.is_superuser = True
        db.commit()
        db.refresh(user)

        print(f"✅ Usuario '{email}' ahora es superusuario")
        print(f"   - ID: {user.id}")
        print(f"   - Username: {user.username}")
        print(f"   - Is Superuser: {user.is_superuser}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    # Hacer superusuario al usuario admin@test.com
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        print("❌ La variable de entorno ADMIN_EMAIL no está configurada")
    else:
        make_superuser(admin_email)
