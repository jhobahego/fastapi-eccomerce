from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_db
from ....core.security import get_current_user, get_current_superuser
from ....models.user import User
from ....models.order import OrderStatus, PaymentStatus
from ....schemas.order import (
    Order as OrderSchema,
    OrderCreate,
    OrderUpdate,
    OrderSummary,
    OrderStats,
)
from ....services.order_service import OrderService
from ....services.cart_service import CartService

router = APIRouter()


@router.get("/", response_model=List[OrderSummary])
def read_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
) -> Any:
    """
    Get current user's orders.
    """
    order_service = OrderService(db)
    orders = order_service.get_user_orders(
        user_id=current_user.id, skip=skip, limit=limit
    )

    # Filter by status if provided
    if status:
        orders = [order for order in orders if order.status == status]

    return orders


@router.get("/all", response_model=List[OrderSchema])
def read_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    payment_status: Optional[PaymentStatus] = Query(
        None, description="Filter by payment status"
    ),
) -> Any:
    """
    Get all orders (admin only).
    """
    order_service = OrderService(db)
    orders = order_service.get_multi(skip=skip, limit=limit)

    # Apply filters
    if status:
        orders = [order for order in orders if order.status == status]
    if payment_status:
        orders = [order for order in orders if order.payment_status == payment_status]

    return orders


@router.post("/", response_model=OrderSchema)
def create_order_from_cart(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create order from user's cart.
    """
    order_service = OrderService(db)
    cart_service = CartService(db)

    # Get user's active cart
    user_cart = cart_service.get_user_active_cart(current_user.id)
    if not user_cart:
        raise HTTPException(status_code=400, detail="No active cart found")

    # Get cart with items
    cart_with_items = cart_service.get_cart_with_items(user_cart.id)
    if not cart_with_items.items:
        raise HTTPException(
            status_code=400, detail="Cannot create order from empty cart"
        )

    order = order_service.create_order_from_cart(
        cart=cart_with_items, user=current_user, order_data=order_in
    )

    # Deactivate cart after successful order creation
    cart_service.deactivate_cart(user_cart.id, current_user)

    return order


@router.post("/direct", response_model=OrderSchema)
def create_order_direct(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create order directly (without cart).
    """
    order_service = OrderService(db)
    order = order_service.create_order_direct(user=current_user, order_data=order_in)
    return order


@router.get("/{order_id}", response_model=OrderSchema)
def read_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get order by ID.
    """
    order_service = OrderService(db)
    order = order_service.get_order_with_details(order_id, current_user)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderSchema)
def update_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    order_in: OrderUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update order (admin only).
    """
    order_service = OrderService(db)
    order = order_service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order = order_service.update(id=order_id, obj_in=order_in)
    return order


@router.put("/{order_id}/status", response_model=OrderSchema)
def update_order_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    new_status: OrderStatus,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update order status (admin only).
    """
    order_service = OrderService(db)
    order = order_service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_order = order_service.update_order_status(
        order_id=order_id,
        new_status=new_status,
        current_user=current_user,
    )
    return updated_order


@router.put("/{order_id}/payment-status", response_model=OrderSchema)
def update_payment_status(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    payment_status: PaymentStatus,
    payment_reference: Optional[str] = None,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update payment status (admin only).
    """
    order_service = OrderService(db)
    order = order_service.get_order_with_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    updated_order = order_service.update_payment_status(
        order_id=order_id,
        new_payment_status=payment_status,
        payment_reference=payment_reference,
        current_user=current_user,
    )
    return updated_order


@router.post("/{order_id}/cancel", response_model=OrderSchema)
def cancel_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Cancel order (user can cancel their own orders, admin can cancel any).
    """
    order_service = OrderService(db)
    order = order_service.get_order_with_details(order_id, current_user)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if user can cancel this order
    if order.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to cancel this order"
        )

    canceled_order = order_service.cancel_order(order_id, reason, current_user)
    return canceled_order


@router.get("/{order_id}/track")
def track_order(
    *,
    db: Session = Depends(get_db),
    order_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Track order status and shipping information.
    """
    # order_service = OrderService(db)
    # order = order_service.get_order_with_details(order_id, current_user)
    # if not order:
    #     raise HTTPException(status_code=404, detail="Order not found")

    # # Check if user can track this order
    # if order.user_id != current_user.id and not current_user.is_superuser:
    #     raise HTTPException(
    #         status_code=403, detail="Not authorized to track this order"
    #     )

    # tracking_info = order_service.get_order_tracking(order_id)
    # return tracking_info
    pass


@router.get("/stats/overview", response_model=OrderStats)
def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> Any:
    """
    Get order statistics (admin only).
    """
    # order_service = OrderService(db)
    # stats = order_service.get_order_statistics(start_date=start_date, end_date=end_date)
    # return stats
    pass


@router.get("/user/{user_id}", response_model=List[OrderSummary])
def get_user_orders_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get orders for a specific user (admin only).
    """
    order_service = OrderService(db)
    orders = order_service.get_user_orders(user_id=user_id, skip=skip, limit=limit)
    return orders
