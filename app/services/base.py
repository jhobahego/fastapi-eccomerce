from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from pydantic import BaseModel

from ..database import Base
from ..repositories.base import BaseRepository

ModelType = TypeVar("ModelType", bound="Base")  # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]
):
    """
    Servicio base con operaciones CRUD comunes y lógica de negocio estándar.

    Proporciona:
    - Operaciones CRUD básicas con validaciones
    - Manejo estándar de errores HTTP
    - Métodos de utilidad comunes
    - Estructura consistente para todos los servicios
    """

    def __init__(self, db: Session, repository: RepositoryType):
        self.db = db
        self.repository = repository

    def get_by_id(self, id: int, raise_404: bool = True) -> Optional[ModelType]:
        """
        Obtener entidad por ID con opción de lanzar 404

        Args:
            id: ID de la entidad
            raise_404: Si True, lanza HTTPException 404 si no se encuentra

        Returns:
            La entidad encontrada o None

        Raises:
            HTTPException: 404 si no se encuentra y raise_404=True
        """
        entity = self.repository.get(db=self.db, id=id)

        if not entity and raise_404:
            self._raise_not_found_error()

        return entity

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        Obtener múltiples entidades con paginación y filtros

        Args:
            skip: Número de registros a saltar
            limit: Límite de registros a retornar
            filters: Filtros a aplicar
            order_by: Campo por el cual ordenar

        Returns:
            Lista de entidades
        """
        return self.repository.get_multi(
            db=self.db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
        )

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Crear nueva entidad

        Args:
            obj_in: Datos para crear la entidad

        Returns:
            La entidad creada
        """
        return self.repository.create(db=self.db, obj_in=obj_in)

    def update(
        self,
        id: int,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        raise_404: bool = True,
    ) -> Optional[ModelType]:
        """
        Actualizar entidad existente

        Args:
            id: ID de la entidad a actualizar
            obj_in: Datos de actualización
            raise_404: Si True, lanza 404 si no se encuentra

        Returns:
            La entidad actualizada o None
        """
        db_obj = self.get_by_id(id=id, raise_404=raise_404)

        if not db_obj:
            return None

        return self.repository.update(db=self.db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, id: int, raise_404: bool = True) -> Optional[ModelType]:
        """
        Eliminar entidad

        Args:
            id: ID de la entidad a eliminar
            raise_404: Si True, lanza 404 si no se encuentra

        Returns:
            La entidad eliminada o None
        """
        if raise_404:
            self.get_by_id(id=id, raise_404=True)

        return self.repository.remove(db=self.db, id=id)

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Contar entidades con filtros opcionales

        Args:
            filters: Filtros a aplicar

        Returns:
            Número de entidades que coinciden con los filtros
        """
        return self.repository.count(db=self.db, filters=filters)

    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        Verificar si existe una entidad con los filtros dados

        Args:
            filters: Filtros para la búsqueda

        Returns:
            True si existe, False en caso contrario
        """
        return self.repository.exists(db=self.db, filters=filters)

    def validate_unique_field(
        self,
        field_name: str,
        field_value: Any,
        exclude_id: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Validar que un campo sea único

        Args:
            field_name: Nombre del campo a validar
            field_value: Valor del campo
            exclude_id: ID a excluir de la validación (para actualizaciones)
            error_message: Mensaje de error personalizado

        Raises:
            HTTPException: 400 si el valor ya existe
        """
        filters = {field_name: field_value}

        if self.repository.exists(db=self.db, filters=filters):
            # Si hay un ID a excluir, verificar que no sea el mismo registro
            if exclude_id:
                existing = self.repository.get_multi(
                    db=self.db, filters=filters, limit=1
                )
                if existing and existing[0].id == exclude_id:
                    return

            message = error_message or f"{field_name.title()} already exists"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

    def validate_exists(
        self,
        id: int,
        error_message: Optional[str] = None,
    ) -> ModelType:
        """
        Validar que una entidad existe y retornarla

        Args:
            id: ID de la entidad
            error_message: Mensaje de error personalizado

        Returns:
            La entidad encontrada

        Raises:
            HTTPException: 404 si no se encuentra
        """
        entity = self.repository.get(db=self.db, id=id)

        if not entity:
            message = error_message or "Entity not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        return entity

    def validate_ownership(
        self,
        entity: ModelType,
        user_id: int,
        user_field: str = "user_id",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Validar que una entidad pertenece a un usuario

        Args:
            entity: La entidad a validar
            user_id: ID del usuario
            user_field: Nombre del campo que contiene el user_id
            error_message: Mensaje de error personalizado

        Raises:
            HTTPException: 403 si no es el propietario
        """
        if not hasattr(entity, user_field):
            return

        entity_user_id = getattr(entity, user_field)

        if entity_user_id != user_id:
            message = error_message or "Not authorized to access this resource"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

    def validate_active_status(
        self,
        entity: ModelType,
        status_field: str = "is_active",
        error_message: Optional[str] = None,
    ) -> None:
        """
        Validar que una entidad esté activa

        Args:
            entity: La entidad a validar
            status_field: Nombre del campo de estado
            error_message: Mensaje de error personalizado

        Raises:
            HTTPException: 400 si está inactiva
        """
        if not hasattr(entity, status_field):
            return

        is_active = getattr(entity, status_field)

        if not is_active:
            message = error_message or "Entity is not active"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )

    def _raise_not_found_error(self, message: Optional[str] = None) -> None:
        """
        Lanzar error HTTP 404

        Args:
            message: Mensaje de error personalizado
        """
        default_message = f"{self.repository.model.__name__} not found"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message or default_message,
        )

    def _raise_bad_request_error(self, message: str) -> None:
        """
        Lanzar error HTTP 400

        Args:
            message: Mensaje de error
        """
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    def _raise_forbidden_error(self, message: Optional[str] = None) -> None:
        """
        Lanzar error HTTP 403

        Args:
            message: Mensaje de error personalizado
        """
        default_message = "Access forbidden"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message or default_message,
        )

    def _raise_conflict_error(self, message: str) -> None:
        """
        Lanzar error HTTP 409

        Args:
            message: Mensaje de error
        """
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )
