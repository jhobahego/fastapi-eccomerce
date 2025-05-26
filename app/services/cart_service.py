from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from .base import BaseService
from ..models.cart import Cart, CartItem
from ..models.user import User
from ..schemas.cart import CartCreate, CartItemCreate, CartItemUpdate
from ..repositories.cart_repository import CartRepository, CartItemRepository


class CartService(BaseService[Cart, CartCreate, CartItemUpdate, CartRepository]):
    def __init__(self, db: Session):
        repository = CartRepository(Cart)
        super().__init__(db, repository)
        self.cart_item_repository = CartItemRepository(CartItem)

    def get_or_create_user_cart(self, user_id: int) -> Cart:
        """Obtener carrito activo del usuario o crear uno nuevo"""
        return self.repository.get_or_create_cart(db=self.db, user_id=user_id)

    def get_or_create_session_cart(self, session_id: str) -> Cart:
        """Obtener carrito por session_id o crear uno nuevo"""
        return self.repository.get_or_create_cart(db=self.db, session_id=session_id)

    def get_cart_with_items(self, cart_id: int) -> Cart:
        """Obtener carrito con todos sus items y productos"""
        cart = self.repository.get_cart_with_items(db=self.db, cart_id=cart_id)

        if not cart:
            self._raise_not_found_error("Cart not found")

        return cart

    def add_item_to_cart(
        self,
        cart_id: int,
        product_id: int,
        quantity: int = 1,
    ) -> CartItem:
        """Agregar producto al carrito"""
        # Validar que el carrito existe
        self.validate_exists(cart_id, "Cart not found")

        # Validar cantidad
        if quantity <= 0:
            self._raise_bad_request_error("Quantity must be greater than 0")

        cart_item = self.repository.add_item_to_cart(
            db=self.db,
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity,
        )

        if not cart_item:
            self._raise_bad_request_error(
                "Failed to add item to cart. Product may not exist or insufficient stock."
            )

        return cart_item

    def update_cart_item_quantity(
        self,
        cart_item_id: int,
        quantity: int,
        user: Optional[User] = None,
    ) -> CartItem:
        """Actualizar cantidad de un item del carrito"""
        # Validar cantidad
        if quantity <= 0:
            self._raise_bad_request_error("Quantity must be greater than 0")

        # Obtener el item del carrito
        cart_item = self.cart_item_repository.get(db=self.db, id=cart_item_id)

        if not cart_item:
            self._raise_not_found_error("Cart item not found")

        # Validar ownership si se proporciona usuario
        if user and cart_item:
            cart = cart_item.cart
            if cart and cart.user_id and cart.user_id != user.id:
                self._raise_forbidden_error("Not authorized to modify this cart")

        updated_item = self.repository.update_cart_item(
            db=self.db,
            cart_item_id=cart_item_id,
            quantity=quantity,
        )

        if not updated_item:
            self._raise_bad_request_error("Failed to update item. Insufficient stock.")

        return updated_item

    def remove_item_from_cart(
        self,
        cart_item_id: int,
        user: Optional[User] = None,
    ) -> bool:
        """Eliminar item del carrito"""
        # Obtener el item del carrito
        cart_item = self.cart_item_repository.get(db=self.db, id=cart_item_id)

        if not cart_item:
            self._raise_not_found_error("Cart item not found")

        # Validar ownership si se proporciona usuario
        if user and cart_item:
            cart = cart_item.cart
            if cart and cart.user_id and cart.user_id != user.id:
                self._raise_forbidden_error("Not authorized to modify this cart")

        return self.repository.remove_item_from_cart(
            db=self.db,
            cart_item_id=cart_item_id,
        )

    def remove_product_from_cart(
        self,
        cart_id: int,
        product_id: int,
        user: Optional[User] = None,
    ) -> bool:
        """Eliminar producto del carrito"""
        # Validar que el carrito existe
        cart = self.validate_exists(cart_id, "Cart not found")

        # Validar ownership si se proporciona usuario
        if user and cart.user_id and cart.user_id != user.id:
            self._raise_forbidden_error("Not authorized to modify this cart")

        return self.repository.remove_item_by_product(
            db=self.db,
            cart_id=cart_id,
            product_id=product_id,
        )

    def clear_cart(self, cart_id: int, user: Optional[User] = None) -> bool:
        """Vaciar carrito eliminando todos los items"""
        # Validar que el carrito existe
        cart = self.validate_exists(cart_id, "Cart not found")

        # Validar ownership si se proporciona usuario
        if user and cart.user_id and cart.user_id != user.id:
            self._raise_forbidden_error("Not authorized to modify this cart")

        return self.repository.clear_cart(db=self.db, cart_id=cart_id)

    def get_cart_summary(self, cart_id: int) -> Dict[str, Any]:
        """Obtener resumen del carrito"""
        return self.repository.get_cart_summary(db=self.db, cart_id=cart_id)

    def merge_session_cart_to_user(
        self,
        user_id: int,
        session_cart_id: int,
    ) -> bool:
        """Fusionar carrito de sesión con carrito de usuario al hacer login"""
        # Obtener o crear carrito del usuario
        user_cart = self.get_or_create_user_cart(user_id)

        # Fusionar carritos
        success = self.repository.merge_carts(
            db=self.db,
            user_cart_id=user_cart.id,
            session_cart_id=session_cart_id,
        )

        if not success:
            self._raise_bad_request_error("Failed to merge carts")

        return success

    def validate_cart_stock(self, cart_id: int) -> List[Dict[str, Any]]:
        """Validar disponibilidad de stock para todos los items del carrito"""
        return self.repository.validate_cart_items_stock(
            db=self.db,
            cart_id=cart_id,
        )

    def update_cart_prices(self, cart_id: int) -> bool:
        """Actualizar precios de items del carrito con precios actuales"""
        return self.repository.update_cart_item_prices(
            db=self.db,
            cart_id=cart_id,
        )

    def get_user_active_cart(self, user_id: int) -> Optional[Cart]:
        """Obtener carrito activo del usuario"""
        return self.repository.get_active_cart_by_user(
            db=self.db,
            user_id=user_id,
        )

    def deactivate_cart(self, cart_id: int, user: Optional[User] = None) -> bool:
        """Desactivar carrito"""
        # Validar que el carrito existe
        cart = self.validate_exists(cart_id, "Cart not found")

        # Validar ownership si se proporciona usuario
        if user and cart.user_id and cart.user_id != user.id:
            self._raise_forbidden_error("Not authorized to modify this cart")

        return self.repository.deactivate_cart(db=self.db, cart_id=cart_id)

    def get_cart_items(self, cart_id: int) -> List[CartItem]:
        """Obtener todos los items del carrito"""
        return self.repository.get_cart_items(db=self.db, cart_id=cart_id)

    def cleanup_old_inactive_carts(self, days_old: int = 30) -> int:
        """Limpiar carritos inactivos antiguos"""
        old_carts = self.repository.get_inactive_carts(
            db=self.db,
            days_old=days_old,
            limit=1000,  # Procesar en lotes
        )

        deleted_count = 0
        for cart in old_carts:
            try:
                self.repository.remove(db=self.db, id=cart.id)
                deleted_count += 1
            except Exception:
                # Log error en producción
                continue

        return deleted_count


class CartItemService(
    BaseService[CartItem, CartItemCreate, CartItemUpdate, CartItemRepository]
):
    """Servicio específico para CartItem si se necesitan operaciones adicionales"""

    def __init__(self, db: Session):
        repository = CartItemRepository(CartItem)
        super().__init__(db, repository)

    def get_item_with_product(self, cart_item_id: int) -> CartItem:
        """Obtener item del carrito con información del producto"""
        cart_item = self.repository.get(db=self.db, id=cart_item_id)

        if not cart_item:
            self._raise_not_found_error("Cart item not found")

        return cart_item

    def get_items_by_product(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CartItem]:
        """Obtener todos los items que contienen un producto específico"""
        return self.repository.get_items_by_product(
            db=self.db,
            product_id=product_id,
            skip=skip,
            limit=limit,
        )
