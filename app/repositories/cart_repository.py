from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime, timedelta

from .base import BaseRepository
from ..models.cart import Cart, CartItem
from ..models.product import Product
from ..schemas.cart import CartCreate, CartItemCreate, CartItemUpdate


class CartRepository(BaseRepository[Cart, CartCreate, CartItemUpdate]):
    def get_active_cart_by_user(self, db: Session, *, user_id: int) -> Optional[Cart]:
        """Obtener carrito activo del usuario"""
        return (
            db.query(Cart)
            .filter(and_(Cart.user_id == user_id, Cart.is_active.is_(True)))
            .first()
        )

    def get_cart_with_items(self, db: Session, *, cart_id: int) -> Optional[Cart]:
        """Obtener carrito con items y productos"""
        return (
            db.query(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.product))
            .filter(Cart.id == cart_id)
            .first()
        )

    def create_cart_for_user(self, db: Session, *, user_id: int) -> Cart:
        """Crear nuevo carrito para usuario"""
        cart = Cart(user_id=user_id, is_active=True)
        db.add(cart)
        db.commit()
        db.refresh(cart)
        return cart

    def get_or_create_cart(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> Cart:
        """Obtener carrito activo o crear uno nuevo"""
        if user_id:
            cart = self.get_active_cart_by_user(db, user_id=user_id)
            if not cart:
                cart = self.create_cart_for_user(db, user_id=user_id)
        else:
            cart = (
                db.query(Cart)
                .filter(and_(Cart.session_id == session_id, Cart.is_active.is_(True)))
                .first()
            )
            if not cart:
                cart = Cart(session_id=session_id, is_active=True)
                db.add(cart)
                db.commit()
                db.refresh(cart)
        return cart

    def add_item_to_cart(
        self,
        db: Session,
        *,
        cart_id: int,
        product_id: int,
        quantity: int,
    ) -> Optional[CartItem]:
        """Agregar producto al carrito o actualizar cantidad si ya existe"""
        # Verificar que el producto existe y está activo
        product = (
            db.query(Product)
            .filter(and_(Product.id == product_id, Product.is_active.is_(True)))
            .first()
        )

        if not product:
            return None

        # Verificar disponibilidad de stock
        if product.stock_quantity < quantity:
            return None

        # Buscar si el item ya existe en el carrito
        existing_item = (
            db.query(CartItem)
            .filter(
                and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            )
            .first()
        )

        if existing_item:
            # Actualizar cantidad del item existente
            new_quantity = existing_item.quantity + quantity
            if product.stock_quantity < new_quantity:
                return None

            existing_item.quantity = new_quantity
            db.add(existing_item)
        else:
            # Crear nuevo item en el carrito
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                unit_price=product.current_price,
            )
            db.add(cart_item)
            existing_item = cart_item

        db.commit()
        db.refresh(existing_item)
        return existing_item

    def update_cart_item(
        self,
        db: Session,
        *,
        cart_item_id: int,
        quantity: int,
    ) -> Optional[CartItem]:
        """Actualizar cantidad de un item del carrito"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

        if not cart_item:
            return None

        # Verificar disponibilidad de stock
        product = cart_item.product
        if not product or not product.is_active:
            return None

        if product.stock_quantity < quantity:
            return None

        cart_item.quantity = quantity
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    def remove_item_from_cart(
        self,
        db: Session,
        *,
        cart_item_id: int,
    ) -> bool:
        """Eliminar item del carrito"""
        cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()

        if not cart_item:
            return False

        db.delete(cart_item)
        db.commit()
        return True

    def remove_item_by_product(
        self,
        db: Session,
        *,
        cart_id: int,
        product_id: int,
    ) -> bool:
        """Eliminar item del carrito por producto"""
        cart_item = (
            db.query(CartItem)
            .filter(
                and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            )
            .first()
        )

        if not cart_item:
            return False

        db.delete(cart_item)
        db.commit()
        return True

    def clear_cart(self, db: Session, *, cart_id: int) -> bool:
        """Vaciar carrito eliminando todos los items"""
        try:
            db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    def get_cart_item(self, db: Session, *, cart_item_id: int) -> Optional[CartItem]:
        """Obtener item específico del carrito con producto"""
        return (
            db.query(CartItem)
            .options(joinedload(CartItem.product))
            .filter(CartItem.id == cart_item_id)
            .first()
        )

    def get_cart_items(self, db: Session, *, cart_id: int) -> List[CartItem]:
        """Obtener todos los items del carrito con productos"""
        return (
            db.query(CartItem)
            .options(joinedload(CartItem.product))
            .filter(CartItem.cart_id == cart_id)
            .all()
        )

    def get_cart_summary(self, db: Session, *, cart_id: int) -> Dict[str, Any]:
        """Obtener resumen del carrito"""
        cart = self.get_cart_with_items(db, cart_id=cart_id)

        if not cart:
            return {
                "total_items": 0,
                "total_amount": Decimal("0"),
                "items_count": 0,
            }

        return {
            "total_items": cart.total_items,
            "total_amount": cart.total_amount,
            "items_count": len(cart.items),
        }

    def merge_carts(
        self,
        db: Session,
        *,
        user_cart_id: int,
        session_cart_id: int,
    ) -> bool:
        """Fusionar carrito de sesión con carrito de usuario"""
        try:
            session_items = self.get_cart_items(db, cart_id=session_cart_id)

            for session_item in session_items:
                # Buscar si el producto ya existe en el carrito del usuario
                existing_item = (
                    db.query(CartItem)
                    .filter(
                        and_(
                            CartItem.cart_id == user_cart_id,
                            CartItem.product_id == session_item.product_id,
                        )
                    )
                    .first()
                )

                if existing_item:
                    # Sumar las cantidades
                    existing_item.quantity += session_item.quantity
                    db.add(existing_item)
                else:
                    # Crear nuevo item en el carrito del usuario
                    new_item = CartItem(
                        cart_id=user_cart_id,
                        product_id=session_item.product_id,
                        quantity=session_item.quantity,
                        unit_price=session_item.unit_price,
                    )
                    db.add(new_item)

            # Eliminar carrito de sesión
            self.deactivate_cart(db, cart_id=session_cart_id)

            db.commit()
            return True
        except Exception:
            db.rollback()
            return False

    def deactivate_cart(self, db: Session, *, cart_id: int) -> bool:
        """Desactivar carrito"""
        cart = self.get(db, cart_id)
        if not cart:
            return False

        cart.is_active = False
        db.add(cart)
        db.commit()
        return True

    def get_inactive_carts(
        self,
        db: Session,
        *,
        days_old: int = 30,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Cart]:
        """Obtener carritos inactivos antiguos para limpieza"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        return (
            db.query(Cart)
            .filter(
                and_(
                    Cart.is_active.is_(False),
                    Cart.updated_at < cutoff_date,
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def validate_cart_items_stock(
        self, db: Session, *, cart_id: int
    ) -> List[Dict[str, Any]]:
        """Validar disponibilidad de stock para todos los items del carrito"""
        cart_items = self.get_cart_items(db, cart_id=cart_id)
        unavailable_items = []

        for item in cart_items:
            product = item.product
            if not product or not product.is_active:
                unavailable_items.append(
                    {
                        "item_id": item.id,
                        "product_id": item.product_id,
                        "reason": "Product not available",
                        "available_quantity": 0,
                    }
                )
            elif product.stock_quantity < item.quantity:
                unavailable_items.append(
                    {
                        "item_id": item.id,
                        "product_id": item.product_id,
                        "reason": "Insufficient stock",
                        "available_quantity": product.stock_quantity,
                        "requested_quantity": item.quantity,
                    }
                )

        return unavailable_items

    def update_cart_item_prices(self, db: Session, *, cart_id: int) -> bool:
        """Actualizar precios de items del carrito con precios actuales"""
        try:
            cart_items = self.get_cart_items(db, cart_id=cart_id)

            for item in cart_items:
                product = item.product
                if product and product.is_active:
                    item.unit_price = product.current_price
                    db.add(item)

            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


class CartItemRepository(BaseRepository[CartItem, CartItemCreate, CartItemUpdate]):
    """Repositorio específico para CartItem si se necesitan operaciones adicionales"""

    def get_by_cart_and_product(
        self,
        db: Session,
        *,
        cart_id: int,
        product_id: int,
    ) -> Optional[CartItem]:
        """Obtener item específico por carrito y producto"""
        return (
            db.query(CartItem)
            .filter(
                and_(
                    CartItem.cart_id == cart_id,
                    CartItem.product_id == product_id,
                )
            )
            .first()
        )

    def get_items_by_product(
        self,
        db: Session,
        *,
        product_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CartItem]:
        """Obtener todos los items que contienen un producto específico"""
        return (
            db.query(CartItem)
            .filter(CartItem.product_id == product_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


# Instancias para usar en la aplicación
cart_repository = CartRepository(Cart)
cart_item_repository = CartItemRepository(CartItem)
