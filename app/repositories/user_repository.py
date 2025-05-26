from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .base import BaseRepository
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(
        self, db: Session, *, identifier: str
    ) -> Optional[User]:
        """Obtener usuario por email o username"""
        return (
            db.query(User)
            .filter(or_(User.email == identifier, User.username == identifier))
            .first()
        )

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Crear nuevo usuario con contraseña hasheada"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            hashed_password=get_password_hash(obj_in.password),
            phone=obj_in.phone,
            address=obj_in.address,
            city=obj_in.city,
            country=obj_in.country,
            postal_code=obj_in.postal_code,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = self.get_by_email_or_username(db, identifier=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Verificar si el usuario está activo"""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Verificar si el usuario es superusuario"""
        return user.is_superuser

    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """Actualizar contraseña del usuario"""
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def deactivate(self, db: Session, *, user: User) -> User:
        """Desactivar usuario"""
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def activate(self, db: Session, *, user: User) -> User:
        """Activar usuario"""
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository(User)
