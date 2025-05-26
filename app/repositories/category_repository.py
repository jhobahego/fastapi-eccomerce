from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .base import BaseRepository
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Category]:
        return db.query(Category).filter(Category.slug == slug).first()

    def get_simple(self, db: Session, *, id: int) -> Optional[Category]:
        """Obtener categoría sin relaciones para evitar recursión"""
        return db.query(Category).filter(Category.id == id).first()

    def get_all_categories(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        return db.query(Category).offset(skip).limit(limit).all()

    def create_simple(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        """Crear categoría sin cargar relaciones"""
        db_obj = Category(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        # Limpiar sesión para evitar cargar relaciones automáticamente
        db.expunge(db_obj)
        return db_obj

    def get_category_with_products(
        self, db: Session, *, category_id: int
    ) -> Optional[Category]:
        """
        Obtener una categoría específica junto con sus productos asociados.

        Args:
            db: La sesión de la base de datos.
            category_id: El ID de la categoría a obtener.

        Returns:
            La categoría con sus productos, o None si no se encuentra.
        """
        return (
            db.query(Category)
            .options(
                joinedload(Category.products)
            )  # Asume que la relación se llama 'products' en el modelo Category
            .filter(Category.id == category_id)
            .first()
        )


category_repository = CategoryRepository(Category)
