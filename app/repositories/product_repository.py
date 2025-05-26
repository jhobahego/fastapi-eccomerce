from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc

from .base import BaseRepository
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate, ProductSearch
# from ..models.category import Category


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def get_by_slug(self, db: Session, *, slug: str) -> Optional[Product]:
        """Obtener producto por slug"""
        return db.query(Product).filter(Product.slug == slug).first()

    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        """Obtener producto por SKU"""
        return db.query(Product).filter(Product.sku == sku).first()

    def get_with_category(self, db: Session, *, product_id: int) -> Optional[Product]:
        """Obtener producto con información de categoría"""
        return (
            db.query(Product)
            .options(joinedload(Product.category))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_category(
        self,
        db: Session,
        *,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> List[Product]:
        """Obtener productos por categoría"""
        query = db.query(Product).filter(Product.category_id == category_id)

        if active_only:
            query = query.filter(Product.is_active)

        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        *,
        search_params: ProductSearch,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """Buscar productos con filtros avanzados"""
        query = db.query(Product).options(joinedload(Product.category))

        # Filtro de texto
        if search_params.query:
            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search_params.query}%"),
                    Product.description.ilike(f"%{search_params.query}%"),
                    Product.sku.ilike(f"%{search_params.query}%"),
                )
            )

        # Filtro por categoría
        if search_params.category_id:
            query = query.filter(Product.category_id == search_params.category_id)

        # Filtro por rango de precios
        if search_params.min_price is not None:
            query = query.filter(Product.price >= search_params.min_price)

        if search_params.max_price is not None:
            query = query.filter(Product.price <= search_params.max_price)

        # Filtro por productos destacados
        if search_params.is_featured is not None:
            query = query.filter(Product.is_featured == search_params.is_featured)

        # Filtro por stock
        if search_params.in_stock is not None:
            if search_params.in_stock:
                query = query.filter(Product.stock_quantity > 0)
            else:
                query = query.filter(Product.stock_quantity <= 0)

        # Ordenamiento
        if search_params.sort_by and hasattr(Product, search_params.sort_by):
            order_column = getattr(Product, search_params.sort_by)
            if search_params.sort_order == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))

        return query.offset(skip).limit(limit).all()

    def get_featured(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Obtener productos destacados"""
        return (
            db.query(Product)
            .filter(and_(Product.is_featured, Product.is_active))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_low_stock(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Obtener productos con stock bajo"""
        return (
            db.query(Product)
            .filter(Product.stock_quantity <= Product.min_stock_level)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_stock(
        self, db: Session, *, product_id: int, quantity: int, operation: str = "set"
    ) -> Optional[Product]:
        """Actualizar stock de producto"""
        product = self.get(db, product_id)
        if not product:
            return None

        if operation == "add":
            product.stock_quantity += quantity
        elif operation == "subtract":
            product.stock_quantity = max(0, product.stock_quantity - quantity)
        elif operation == "set":
            product.stock_quantity = max(0, quantity)

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def check_stock_availability(
        self, db: Session, *, product_id: int, quantity: int
    ) -> bool:
        """Verificar disponibilidad de stock"""
        product = self.get(db, product_id)
        if not product or not product.is_active:
            return False
        return product.stock_quantity >= quantity

    def bulk_update_stock(self, db: Session, *, stock_updates: List[dict]) -> bool:
        """Actualizar stock de múltiples productos"""
        try:
            for update in stock_updates:
                product = self.get(db, update["product_id"])
                if product:
                    new_quantity = max(0, product.stock_quantity - update["quantity"])
                    product.stock_quantity = new_quantity
                    db.add(product)

            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


product_repository = ProductRepository(Product)
