from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from .base import BaseRepository
from ..models.order import Order, OrderItem
from ..models.user import User
from ..schemas.order import OrderCreate, OrderUpdate
from ..models.cart import Cart


class OrderRepository(BaseRepository[Order, OrderCreate, OrderUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        return (
            db.query(Order)
            .filter(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_order_with_details(self, db: Session, *, order_id: int) -> Optional[Order]:
        return (
            db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.id == order_id)
            .first()
        )

    def create_order_from_cart(self, db: Session, *, cart: Cart, user: User) -> Order:
        order = Order(
            user_id=user.id,
            total_amount=cart.get_total_price(),  # Assuming Cart model has a method to calculate total
            status="PENDING",  # Initial status
        )
        db.add(order)
        db.flush()  # Get order.id before creating items

        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price,  # Assuming CartItem has product and product has price
            )
            db.add(order_item)

        db.commit()
        db.refresh(order)
        return order

    def get_orders_by_status(
        self,
        db: Session,
        *,
        status: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """
        Obtener órdenes filtradas por estado y opcionalmente por usuario.

        Args:
            db: La sesión de la base de datos.
            status: El estado de las órdenes a filtrar (e.g., "PENDING", "SHIPPED").
            user_id: Opcional. El ID del usuario para filtrar las órdenes.
            skip: Número de registros a saltar para paginación.
            limit: Número máximo de registros a devolver.

        Returns:
            Una lista de órdenes que coinciden con los criterios.
        """
        query = db.query(Order).filter(Order.status == status)
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


order_repository = OrderRepository(Order)
