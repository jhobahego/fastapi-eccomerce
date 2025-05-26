from sqlalchemy.orm import Session
from typing import List, Optional

from .base import BaseService
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate, ProductSearch, StockUpdate
from ..repositories.product_repository import ProductRepository


class ProductService(
    BaseService[Product, ProductCreate, ProductUpdate, ProductRepository]
):
    def __init__(self, db: Session):
        repository = ProductRepository(Product)
        super().__init__(db, repository)

    def create_product(self, product_create: ProductCreate) -> Product:
        """Crear nuevo producto con validaciones específicas"""
        # Validar que el SKU sea único
        self.validate_unique_field(
            field_name="sku",
            field_value=product_create.sku,
            error_message="SKU already exists",
        )

        # Validar que el slug sea único
        self.validate_unique_field(
            field_name="slug",
            field_value=product_create.slug,
            error_message="Slug already exists",
        )

        # Crear producto
        return self.create(obj_in=product_create)

    def get_product_by_slug(
        self, slug: str, raise_404: bool = True
    ) -> Optional[Product]:
        """Obtener producto por slug"""
        product = self.repository.get_by_slug(db=self.db, slug=slug)

        if not product and raise_404:
            self._raise_not_found_error("Product not found")

        return product

    def get_product_by_sku(self, sku: str, raise_404: bool = True) -> Optional[Product]:
        """Obtener producto por SKU"""
        product = self.repository.get_by_sku(db=self.db, sku=sku)

        if not product and raise_404:
            self._raise_not_found_error("Product not found")

        return product

    def get_products_by_category(
        self,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Product]:
        """Obtener productos por categoría"""
        return self.repository.get_by_category(
            db=self.db,
            category_id=category_id,
            skip=skip,
            limit=limit,
            active_only=active_only,
        )

    def search_products(
        self,
        search_params: ProductSearch,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """Buscar productos con filtros avanzados"""
        return self.repository.search(
            db=self.db,
            search_params=search_params,
            skip=skip,
            limit=limit,
        )

    def get_featured_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtener productos destacados"""
        return self.repository.get_featured(db=self.db, skip=skip, limit=limit)

    def get_low_stock_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtener productos con stock bajo"""
        return self.repository.get_low_stock(db=self.db, skip=skip, limit=limit)

    def update_product(
        self,
        product_id: int,
        product_update: ProductUpdate,
    ) -> Product:
        """Actualizar producto con validaciones"""
        # Validar que el producto existe
        db_product = self.validate_exists(product_id, "Product not found")

        # Validar que esté activo (opcional, dependiendo de tus reglas de negocio)
        self.validate_active_status(
            db_product, error_message="Cannot update inactive product"
        )

        update_data = product_update.model_dump(exclude_unset=True)

        # Validar unicidad del SKU si se está cambiando
        if "sku" in update_data and update_data["sku"] != db_product.sku:
            self.validate_unique_field(
                field_name="sku",
                field_value=update_data["sku"],
                exclude_id=product_id,
                error_message="SKU already exists",
            )

        return self.update(id=product_id, obj_in=product_update)

    def update_stock(
        self,
        product_id: int,
        stock_update: StockUpdate,
    ) -> Product:
        """Actualizar stock de producto"""
        # Validar que el producto existe
        db_product = self.validate_exists(product_id, "Product not found")

        # Validar que esté activo
        self.validate_active_status(
            db_product, error_message="Cannot update stock of inactive product"
        )

        # Validar operación de stock
        if (
            stock_update.operation == "subtract"
            and db_product.stock_quantity < stock_update.quantity
        ):
            self._raise_bad_request_error("Insufficient stock")

        updated_product = self.repository.update_stock(
            db=self.db,
            product_id=product_id,
            quantity=stock_update.quantity,
            operation=stock_update.operation,
        )

        if not updated_product:
            self._raise_bad_request_error("Failed to update stock")

        return updated_product

    def check_stock_availability(self, product_id: int, quantity: int) -> bool:
        """Verificar disponibilidad de stock"""
        return self.repository.check_stock_availability(
            db=self.db,
            product_id=product_id,
            quantity=quantity,
        )

    def bulk_update_stock(self, stock_updates: List[dict]) -> bool:
        """Actualizar stock de múltiples productos"""
        # Validar que todos los productos existen
        for update in stock_updates:
            self.validate_exists(update["product_id"], "Product not found")

        return self.repository.bulk_update_stock(
            db=self.db,
            stock_updates=stock_updates,
        )

    def deactivate_product(self, product_id: int) -> Product:
        """Desactivar producto"""
        self.validate_exists(product_id, "Product not found")

        return self.update(id=product_id, obj_in={"is_active": False})

    def activate_product(self, product_id: int) -> Product:
        """Activar producto"""
        self.validate_exists(product_id, "Product not found")

        return self.update(id=product_id, obj_in={"is_active": True})
