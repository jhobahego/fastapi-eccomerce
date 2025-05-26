from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....database import get_db
from ....core.security import get_current_user
from ....models.user import User
from ....schemas.cart import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartItemUpdate,
    CartSummary,
)
from ....services.cart_service import CartService

router = APIRouter()


@router.get("/", response_model=CartSchema)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user's active cart.
    """
    cart_service = CartService(db)
    cart = cart_service.get_or_create_user_cart(current_user.id)
    return cart_service.get_cart_with_items(cart.id)


@router.get("/session/{session_id}", response_model=CartSchema)
def get_session_cart(
    *,
    db: Session = Depends(get_db),
    session_id: str,
) -> Any:
    """
    Get cart by session ID (for guest users).
    """
    cart_service = CartService(db)
    cart = cart_service.get_or_create_session_cart(session_id)
    return cart_service.get_cart_with_items(cart.id)


@router.post("/items", response_model=CartItemSchema)
def add_item_to_cart(
    *,
    db: Session = Depends(get_db),
    item_in: CartItemCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Add item to user's cart.
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)

    cart_item = cart_service.add_item_to_cart(
        cart_id=user_cart.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity,
    )
    return cart_item


@router.post("/session/{session_id}/items", response_model=CartItemSchema)
def add_item_to_session_cart(
    *,
    db: Session = Depends(get_db),
    session_id: str,
    item_in: CartItemCreate,
) -> Any:
    """
    Add item to session cart (for guest users).
    """
    cart_service = CartService(db)
    session_cart = cart_service.get_or_create_session_cart(session_id)

    cart_item = cart_service.add_item_to_cart(
        cart_id=session_cart.id,
        product_id=item_in.product_id,
        quantity=item_in.quantity,
    )
    return cart_item


@router.put("/items/{item_id}", response_model=CartItemSchema)
def update_cart_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update cart item quantity.
    """
    cart_service = CartService(db)
    cart_item = cart_service.update_cart_item_quantity(
        cart_item_id=item_id,
        quantity=item_update.quantity,
        user=current_user,
    )
    return cart_item


@router.delete("/items/{item_id}")
def remove_cart_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Remove item from cart.
    """
    cart_service = CartService(db)
    success = cart_service.remove_item_from_cart(
        cart_item_id=item_id,
        user=current_user,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}


@router.delete("/items/product/{product_id}")
def remove_product_from_cart(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Remove all items of a specific product from cart.
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)

    success = cart_service.remove_product_from_cart(
        cart_id=user_cart.id,
        product_id=product_id,
        user=current_user,
    )
    if not success:
        raise HTTPException(status_code=404, detail="Product not found in cart")
    return {"message": "Product removed from cart"}


@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Clear all items from user's cart.
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)

    success = cart_service.clear_cart(cart_id=user_cart.id, user=current_user)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to clear cart")
    return {"message": "Cart cleared successfully"}


@router.get("/summary", response_model=CartSummary)
def get_cart_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get cart summary (totals).
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)
    summary = cart_service.get_cart_summary(user_cart.id)
    return summary


@router.post("/merge/{session_cart_id}")
def merge_session_cart(
    *,
    db: Session = Depends(get_db),
    session_cart_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Merge session cart with user cart (used when guest user logs in).
    """
    cart_service = CartService(db)
    success = cart_service.merge_session_cart_to_user(
        user_id=current_user.id,
        session_cart_id=session_cart_id,
    )
    if not success:
        raise HTTPException(status_code=400, detail="Failed to merge carts")
    return {"message": "Carts merged successfully"}


@router.get("/validate")
def validate_cart_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Validate that all cart items have sufficient stock.
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)

    validation_results = cart_service.validate_cart_stock(user_cart.id)

    # Check if there are any issues
    has_issues = any(not item["available"] for item in validation_results)

    return {
        "valid": not has_issues,
        "items": validation_results,
        "message": "Cart validation completed",
    }


@router.get("/items", response_model=List[CartItemSchema])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get all items in user's cart.
    """
    cart_service = CartService(db)
    user_cart = cart_service.get_or_create_user_cart(current_user.id)
    items = cart_service.get_cart_items(user_cart.id)
    return items
