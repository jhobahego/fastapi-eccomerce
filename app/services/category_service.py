from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from .base import BaseService
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate
from ..repositories.category_repository import CategoryRepository
from ..utils.db_utils import db_retry


class CategoryService(
    BaseService[Category, CategoryCreate, CategoryUpdate, CategoryRepository]
):
    def __init__(self, db: Session):
        repository = CategoryRepository(Category)
        super().__init__(db, repository)

    @db_retry(max_retries=3, delay=1.0)
    def create_category(self, category_create: CategoryCreate) -> Category:
        """Crear nueva categoría con validaciones específicas"""
        # Validar que el nombre sea único
        existing_name = self.repository.get_by_name(
            db=self.db, name=category_create.name
        )
        if existing_name:
            self._raise_bad_request_error("Category name already exists")

        # Validar que el slug sea único
        existing_slug = self.repository.get_by_slug(
            db=self.db, slug=category_create.slug
        )
        if existing_slug:
            self._raise_bad_request_error("Category slug already exists")

        # Validar que la categoría padre existe si se especifica
        if category_create.parent_id:
            parent_category = self.repository.get_simple(
                db=self.db, id=category_create.parent_id
            )
            if not parent_category:
                self._raise_bad_request_error("Parent category not found")

            if parent_category and not parent_category.is_active:
                self._raise_bad_request_error("Parent category is not active")

        # Crear categoría sin cargar relaciones
        return self.repository.create_simple(db=self.db, obj_in=category_create)

    def get_category_by_id(
        self, category_id: int, raise_404: bool = True
    ) -> Optional[Category]:
        """Obtener categoría por ID"""
        category = self.repository.get(db=self.db, id=category_id)

        if not category and raise_404:
            self._raise_not_found_error("Category not found")

        return category

    def get_category_by_name(
        self, name: str, raise_404: bool = True
    ) -> Optional[Category]:
        """Obtener categoría por nombre"""
        category = self.repository.get_by_name(db=self.db, name=name)

        if not category and raise_404:
            self._raise_not_found_error("Category not found")

        return category

    def get_all_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Category]:
        """Obtener todas las categorías con filtros opcionales"""
        filters: Dict[str, Any] = {}
        if active_only:
            filters["is_active"] = True

        return self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="sort_order",
        )

    def get_root_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Category]:
        """Obtener categorías raíz (sin padre)"""
        filters: Dict[str, Any] = {"parent_id": None}
        if active_only:
            filters["is_active"] = True

        return self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="sort_order",
        )

    def get_subcategories(
        self,
        parent_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Category]:
        """Obtener subcategorías de una categoría específica"""
        # Validar que la categoría padre existe
        self.validate_exists(parent_id, "Parent category not found")

        filters: Dict[str, Any] = {"parent_id": parent_id}
        if active_only:
            filters["is_active"] = True

        return self.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="sort_order",
        )

    def get_category_with_products(self, category_id: int) -> Category:
        """Obtener categoría con sus productos asociados"""
        category = self.repository.get_category_with_products(
            db=self.db,
            category_id=category_id,
        )

        if not category:
            self._raise_not_found_error("Category not found")

        return category

    def update_category(
        self,
        category_id: int,
        category_update: CategoryUpdate,
    ) -> Category:
        """Actualizar categoría con validaciones"""
        # Validar que la categoría existe
        db_category = self.validate_exists(category_id, "Category not found")

        update_data = category_update.model_dump(exclude_unset=True)

        # Validar unicidad del nombre si se está cambiando
        if "name" in update_data and update_data["name"] != db_category.name:
            self.validate_unique_field(
                field_name="name",
                field_value=update_data["name"],
                exclude_id=category_id,
                error_message="Category name already exists",
            )

        # Validar que la nueva categoría padre existe y no crea un ciclo
        if "parent_id" in update_data and update_data["parent_id"]:
            new_parent_id = update_data["parent_id"]

            # No puede ser su propio padre
            if new_parent_id == category_id:
                self._raise_bad_request_error("Category cannot be its own parent")

            # Validar que el nuevo padre existe
            new_parent = self.validate_exists(
                new_parent_id, "Parent category not found"
            )

            # Validar que el nuevo padre esté activo
            self.validate_active_status(
                new_parent, error_message="Parent category is not active"
            )

            # Validar que no se cree un ciclo (el nuevo padre no puede ser descendiente)
            if self._would_create_cycle(category_id, new_parent_id):
                self._raise_bad_request_error(
                    "Cannot set parent: would create a circular reference"
                )

        return self.update(id=category_id, obj_in=category_update)

    def delete_category(self, category_id: int, force: bool = False) -> Category:
        """
        Eliminar categoría con validaciones

        Args:
            category_id: ID de la categoría a eliminar
            force: Si True, elimina aunque tenga subcategorías o productos
        """
        # Validar que la categoría existe
        self.validate_exists(category_id, "Category not found")

        if not force:
            # Verificar que no tenga subcategorías
            subcategories = self.get_subcategories(category_id, limit=1)
            if subcategories:
                self._raise_bad_request_error(
                    "Cannot delete category with subcategories. Use force=True to override."
                )

            # Verificar que no tenga productos asociados
            category_with_products = self.get_category_with_products(category_id)
            if (
                hasattr(category_with_products, "products")
                and category_with_products.products
            ):
                self._raise_bad_request_error(
                    "Cannot delete category with associated products. Use force=True to override."
                )

        return self.delete(id=category_id)

    def deactivate_category(self, category_id: int) -> Category:
        """Desactivar categoría"""
        self.validate_exists(category_id, "Category not found")

        return self.update(id=category_id, obj_in={"is_active": False})

    def activate_category(self, category_id: int) -> Category:
        """Activar categoría"""
        self.validate_exists(category_id, "Category not found")

        return self.update(id=category_id, obj_in={"is_active": True})

    def reorder_categories(self, category_orders: List[dict]) -> bool:
        """
        Reordenar categorías

        Args:
            category_orders: Lista de dicts con {'id': int, 'sort_order': int}
        """
        try:
            for item in category_orders:
                category_id = item.get("id")
                sort_order = item.get("sort_order")

                if category_id and sort_order is not None:
                    self.update(id=category_id, obj_in={"sort_order": sort_order})

            return True
        except Exception:
            return False

    def get_category_hierarchy(
        self,
        root_category_id: Optional[int] = None,
        max_depth: int = 3,
    ) -> List[dict]:
        """
        Obtener jerarquía de categorías en formato anidado

        Args:
            root_category_id: ID de la categoría raíz (None para todas las raíces)
            max_depth: Profundidad máxima del árbol
        """

        def build_tree(parent_id: Optional[int], current_depth: int = 0) -> List[dict]:
            if current_depth >= max_depth:
                return []

            if parent_id is None:
                categories = self.get_root_categories(limit=1000)
            else:
                categories = self.get_subcategories(parent_id, limit=1000)

            tree = []
            for category in categories:
                category_dict = {
                    "id": category.id,
                    "name": category.name,
                    "slug": category.slug,
                    "description": category.description,
                    "is_active": category.is_active,
                    "sort_order": category.sort_order,
                    "children": build_tree(category.id, current_depth + 1),
                }
                tree.append(category_dict)

            return tree

        if root_category_id:
            # Validar que la categoría raíz existe
            self.validate_exists(root_category_id, "Root category not found")
            return build_tree(root_category_id)
        else:
            return build_tree(None)

    def _would_create_cycle(self, category_id: int, new_parent_id: int) -> bool:
        """
        Verificar si asignar new_parent_id como padre de category_id crearía un ciclo
        """
        current_id = new_parent_id
        visited = set()

        while current_id is not None and current_id not in visited:
            if current_id == category_id:
                return True

            visited.add(current_id)
            category = self.get_by_id(current_id, raise_404=False)

            if not category:
                break

            current_id = category.parent_id

        return False

    def get_active_categories_count(self) -> int:
        """Obtener cantidad de categorías activas"""
        return self.count(filters={"is_active": True})

    def search_categories(self, query: str, limit: int = 20) -> List[Category]:
        """
        Buscar categorías por nombre o descripción

        Args:
            query: Término de búsqueda
            limit: Límite de resultados
        """
        # Implementación simple - en producción podrías usar búsqueda full-text
        categories = self.get_all_categories(limit=1000, active_only=False)

        results = []
        query_lower = query.lower()

        for category in categories:
            if query_lower in category.name.lower() or (
                category.description and query_lower in category.description.lower()
            ):
                results.append(category)

                if len(results) >= limit:
                    break

        return results
