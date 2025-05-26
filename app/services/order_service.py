from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime

from .base import BaseService
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.user import User
from ..models.cart import Cart
from ..schemas.order import OrderCreate, OrderUpdate
from ..repositories.order_repository import OrderRepository


class OrderService(BaseService[Order, OrderCreate, OrderUpdate, OrderRepository]):
    def __init__(self, db: Session):
        repository = OrderRepository(Order)
        super().__init__(db, repository)

    def create_order_from_cart(
        self,
        cart: Cart,
        user: User,
        order_data: OrderCreate,
    ) -> Order:
        """Crear orden desde un carrito"""
        # Validar que el carrito tenga items
        if not cart.items:
            self._raise_bad_request_error("Cannot create order from empty cart")

        # Validar que el carrito pertenece al usuario
        if cart.user_id != user.id:
            self._raise_forbidden_error("Cart does not belong to user")

        # Validar stock disponible para todos los items
        for cart_item in cart.items:
            product = cart_item.product
            if not product or not product.is_active:
                self._raise_bad_request_error(
                    f"Product {cart_item.product_id} is not available"
                )

            # Type check ensures product is not None from here
            assert product is not None
            if product.stock_quantity < cart_item.quantity:
                self._raise_bad_request_error(
                    f"Insufficient stock for product {product.name}. "
                    f"Available: {product.stock_quantity}, Requested: {cart_item.quantity}"
                )

        # Calcular totales
        subtotal = cart.total_amount
        tax_amount = self._calculate_tax(subtotal)
        shipping_cost = self._calculate_shipping(order_data, cart)
        discount_amount = Decimal(
            "0"
        )  # Implementar lógica de descuentos si es necesario
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount

        # Crear la orden
        order = Order(
            order_number=self._generate_order_number(),
            user_id=user.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            total_amount=total_amount,
            shipping_address=order_data.shipping_address,
            shipping_city=order_data.shipping_city,
            shipping_country=order_data.shipping_country,
            shipping_postal_code=order_data.shipping_postal_code,
            shipping_phone=order_data.shipping_phone,
            billing_address=order_data.billing_address or order_data.shipping_address,
            billing_city=order_data.billing_city or order_data.shipping_city,
            billing_country=order_data.billing_country or order_data.shipping_country,
            billing_postal_code=order_data.billing_postal_code
            or order_data.shipping_postal_code,
            notes=order_data.notes,
            payment_method=order_data.payment_method,
        )

        # Guardar la orden
        self.db.add(order)
        self.db.flush()  # Para obtener el ID

        # Crear los items de la orden
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.subtotal,
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)

        # Actualizar stock de productos
        self._update_product_stock(cart.items)

        return order

    def create_order_direct(
        self,
        user: User,
        order_data: OrderCreate,
    ) -> Order:
        """Crear orden directamente (sin carrito)"""
        if not order_data.items:
            self._raise_bad_request_error("Order must have at least one item")

        # Validar productos y stock
        total_amount = Decimal("0")
        validated_items = []

        for item_data in order_data.items:
            # Obtener producto desde la base de datos
            from ..repositories.product_repository import ProductRepository
            from ..models.product import Product

            product_repo = ProductRepository(Product)
            product = product_repo.get(db=self.db, id=item_data.product_id)

            if not product or not product.is_active:
                self._raise_bad_request_error(
                    f"Product {item_data.product_id} is not available"
                )

            # Type check ensures product is not None from here
            assert product is not None
            if product.stock_quantity < item_data.quantity:
                self._raise_bad_request_error(
                    f"Insufficient stock for product {product.name}"
                )

            item_total = product.current_price * item_data.quantity
            total_amount += item_total

            validated_items.append(
                {
                    "product": product,
                    "quantity": item_data.quantity,
                    "unit_price": product.current_price,
                    "total_price": item_total,
                }
            )

        # Calcular totales
        subtotal = total_amount
        tax_amount = self._calculate_tax(subtotal)
        shipping_cost = self._calculate_shipping_direct(order_data)
        discount_amount = Decimal("0")
        final_total = subtotal + tax_amount + shipping_cost - discount_amount

        # Crear la orden
        order = Order(
            order_number=self._generate_order_number(),
            user_id=user.id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax_amount=tax_amount,
            shipping_cost=shipping_cost,
            discount_amount=discount_amount,
            total_amount=final_total,
            shipping_address=order_data.shipping_address,
            shipping_city=order_data.shipping_city,
            shipping_country=order_data.shipping_country,
            shipping_postal_code=order_data.shipping_postal_code,
            shipping_phone=order_data.shipping_phone,
            billing_address=order_data.billing_address or order_data.shipping_address,
            billing_city=order_data.billing_city or order_data.shipping_city,
            billing_country=order_data.billing_country or order_data.shipping_country,
            billing_postal_code=order_data.billing_postal_code
            or order_data.shipping_postal_code,
            notes=order_data.notes,
            payment_method=order_data.payment_method,
        )

        self.db.add(order)
        self.db.flush()

        # Crear items de la orden
        for item_data in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product"].id,
                product_name=item_data["product"].name,
                product_sku=item_data["product"].sku,
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                total_price=item_data["total_price"],
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)

        return order

    def get_user_orders(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """Obtener órdenes de un usuario"""
        return self.repository.get_by_user(
            db=self.db,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def get_order_with_details(
        self, order_id: int, user: Optional[User] = None
    ) -> Order:
        """Obtener orden con todos sus detalles"""
        order = self.repository.get_order_with_details(
            db=self.db,
            order_id=order_id,
        )

        if not order:
            self._raise_not_found_error("Order not found")

        # Type check ensures order is not None from here
        assert order is not None

        # Validar ownership si se proporciona usuario
        if user and order.user_id != user.id and not user.is_superuser:
            self._raise_forbidden_error("Not authorized to view this order")

        return order

    def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        current_user: User,
    ) -> Order:
        """Actualizar estado de la orden"""
        order = self.validate_exists(order_id, "Order not found")

        # Solo admin/staff pueden cambiar estados
        if not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to update order status")

        # Validar transiciones de estado válidas
        if not self._is_valid_status_transition(order.status, new_status):
            self._raise_bad_request_error(
                f"Invalid status transition from {order.status.value} to {new_status.value}"
            )

        # Actualizar timestamps específicos
        update_data: Dict[str, Any] = {"status": new_status}

        if new_status == OrderStatus.SHIPPED and not order.shipped_at:
            update_data["shipped_at"] = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED and not order.delivered_at:
            update_data["delivered_at"] = datetime.utcnow()

        return self.update(id=order_id, obj_in=update_data)

    def update_payment_status(
        self,
        order_id: int,
        new_payment_status: PaymentStatus,
        payment_reference: Optional[str] = None,
        current_user: Optional[User] = None,
    ) -> Order:
        """Actualizar estado de pago"""
        order = self.validate_exists(order_id, "Order not found")

        # Solo admin/staff pueden cambiar estados de pago manualmente
        if current_user and not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to update payment status")

        update_data: Dict[str, Any] = {"payment_status": new_payment_status}

        if payment_reference:
            update_data["payment_reference"] = payment_reference

        # Si el pago fue exitoso, confirmar la orden automáticamente
        if (
            new_payment_status == PaymentStatus.PAID
            and order.status == OrderStatus.PENDING
        ):
            update_data["status"] = OrderStatus.CONFIRMED

        return self.update(id=order_id, obj_in=update_data)

    def cancel_order(
        self,
        order_id: int,
        reason: Optional[str] = None,
        user: Optional[User] = None,
    ) -> Order:
        """Cancelar orden"""
        order = self.validate_exists(order_id, "Order not found")

        # Validar ownership o permisos
        if user:
            if order.user_id != user.id and not user.is_superuser:
                self._raise_forbidden_error("Not authorized to cancel this order")

        # Validar que se puede cancelar
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            self._raise_bad_request_error("Cannot cancel shipped or delivered orders")

        if order.status == OrderStatus.CANCELLED:
            self._raise_bad_request_error("Order is already cancelled")

        # Restaurar stock si era una orden confirmada
        if order.status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
            self._restore_product_stock(order.items)

        update_data = {
            "status": OrderStatus.CANCELLED,
            "notes": f"{order.notes or ''}\nCancelled: {reason or 'No reason provided'}".strip(),
        }

        return self.update(id=order_id, obj_in=update_data)

    def get_orders_by_status(
        self,
        status: OrderStatus,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """Obtener órdenes por estado"""
        return self.repository.get_orders_by_status(
            db=self.db,
            status=status.value,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def add_tracking_number(
        self,
        order_id: int,
        tracking_number: str,
        current_user: User,
    ) -> Order:
        """Agregar número de seguimiento"""
        self.validate_exists(order_id, "Order not found")

        if not current_user.is_superuser:
            self._raise_forbidden_error("Not authorized to add tracking number")

        return self.update(id=order_id, obj_in={"tracking_number": tracking_number})

    def _generate_order_number(self) -> str:
        """Generar número único de orden"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

    def _calculate_tax(self, subtotal: Decimal) -> Decimal:
        """Calcular impuestos (implementar según reglas de negocio)"""
        # Ejemplo: 21% de IVA
        tax_rate = Decimal("0.21")
        return subtotal * tax_rate

    def _calculate_shipping(self, order_data: OrderCreate, cart: Cart) -> Decimal:
        """Calcular costo de envío basado en carrito"""
        # Implementar lógica de envío según reglas de negocio
        # Ejemplo simple: envío gratis para órdenes > $100
        if cart.total_amount >= Decimal("100"):
            return Decimal("0")
        else:
            return Decimal("10")  # Costo fijo de envío

    def _calculate_shipping_direct(self, order_data: OrderCreate) -> Decimal:
        """Calcular costo de envío para orden directa"""
        # Implementar lógica de envío
        return Decimal("10")  # Costo fijo por defecto

    def _is_valid_status_transition(
        self,
        current_status: OrderStatus,
        new_status: OrderStatus,
    ) -> bool:
        """Validar si la transición de estado es válida"""
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],  # Estado final
            OrderStatus.CANCELLED: [],  # Estado final
            OrderStatus.REFUNDED: [],  # Estado final
        }

        return new_status in valid_transitions.get(current_status, [])

    def _update_product_stock(self, cart_items) -> None:
        """Actualizar stock de productos después de crear orden"""
        from ..repositories.product_repository import ProductRepository
        from ..models.product import Product

        product_repo = ProductRepository(Product)

        for cart_item in cart_items:
            product_repo.update_stock(
                db=self.db,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                operation="subtract",
            )

    def _restore_product_stock(self, order_items) -> None:
        """Restaurar stock de productos al cancelar orden"""
        from ..repositories.product_repository import ProductRepository
        from ..models.product import Product

        product_repo = ProductRepository(Product)

        for order_item in order_items:
            product_repo.update_stock(
                db=self.db,
                product_id=order_item.product_id,
                quantity=order_item.quantity,
                operation="add",
            )
