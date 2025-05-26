from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from .base import BaseService
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..repositories.user_repository import UserRepository
from ..core.security import verify_password


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
    def __init__(self, db: Session):
        repository = UserRepository(User)
        super().__init__(db, repository)

    def create_user(self, user_create: UserCreate) -> User:
        """Crear nuevo usuario con validaciones específicas"""
        # Validar que el email sea único
        self.validate_unique_field(
            field_name="email",
            field_value=user_create.email,
            error_message="Email already registered",
        )

        # Validar que el username sea único
        self.validate_unique_field(
            field_name="username",
            field_value=user_create.username,
            error_message="Username already taken",
        )

        # Crear usuario usando el repositorio específico que maneja el hash de password
        return self.repository.create(db=self.db, obj_in=user_create)

    def get_user_by_id(self, user_id: int, raise_404: bool = True) -> Optional[User]:
        """Obtener usuario por ID"""
        user = self.repository.get(db=self.db, id=user_id)

        if not user and raise_404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    def get_user_by_email(self, email: str, raise_404: bool = True) -> Optional[User]:
        """Obtener usuario por email"""
        user = self.repository.get_by_email(db=self.db, email=email)

        if not user and raise_404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    def get_user_by_username(
        self, username: str, raise_404: bool = True
    ) -> Optional[User]:
        """Obtener usuario por username"""
        user = self.repository.get_by_username(db=self.db, username=username)

        if not user and raise_404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    def update_user(
        self, user_id: int, user_update: UserUpdate, current_user: User
    ) -> User:
        """Actualizar usuario con validaciones de autorización"""
        # Obtener usuario a actualizar
        db_user = self.validate_exists(user_id, "User not found")

        # Validar autorización: solo el mismo usuario o superusuario
        if db_user.id != current_user.id and not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to update this user")

        # Validar unicidad del email si se está cambiando
        update_data = user_update.model_dump(exclude_unset=True)

        if "email" in update_data and update_data["email"] != db_user.email:
            self.validate_unique_field(
                field_name="email",
                field_value=update_data["email"],
                exclude_id=user_id,
                error_message="Email already registered by another user",
            )

        # Actualizar usando el método base
        return self.update(id=user_id, obj_in=user_update)

    def delete_user(self, user_id: int, current_user: User) -> User:
        """Eliminar usuario con validaciones de autorización"""
        # Obtener usuario a eliminar
        db_user = self.validate_exists(user_id, "User not found")

        # Validar autorización: solo el mismo usuario o superusuario
        if db_user.id != current_user.id and not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to delete this user")

        # Eliminar usando el método base
        return self.delete(id=user_id)

    def authenticate_user(self, identifier: str, password: str) -> Optional[User]:
        """Autenticar usuario por email o username"""
        user = self.repository.get_by_email_or_username(
            db=self.db, identifier=identifier
        )

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Validar que el usuario esté activo
        self.validate_active_status(user, error_message="Account is deactivated")

        return user

    def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        current_user: User,
    ) -> User:
        """Cambiar contraseña del usuario"""
        # Obtener usuario
        db_user = self.validate_exists(user_id, "User not found")

        # Validar autorización
        if db_user.id != current_user.id and not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to change this user's password")

        # Validar contraseña actual (solo si no es superusuario)
        if not current_user.is_superuser:
            if not verify_password(current_password, db_user.hashed_password):
                self._raise_bad_request_error("Current password is incorrect")

        # Actualizar contraseña
        return self.repository.update_password(
            db=self.db, user=db_user, new_password=new_password
        )

    def deactivate_user(self, user_id: int, current_user: User) -> User:
        """Desactivar usuario"""
        # Solo superusuarios pueden desactivar usuarios
        if not current_user.is_superuser:
            self._raise_forbidden_error("Only superusers can deactivate users")

        db_user = self.validate_exists(user_id, "User not found")

        return self.repository.deactivate(db=self.db, user=db_user)

    def activate_user(self, user_id: int, current_user: User) -> User:
        """Activar usuario"""
        # Solo superusuarios pueden activar usuarios
        if not current_user.is_superuser:
            self._raise_forbidden_error("Only superusers can activate users")

        db_user = self.validate_exists(user_id, "User not found")

        return self.repository.activate(db=self.db, user=db_user)
