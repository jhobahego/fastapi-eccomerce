from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .product import ProductBase


class CartItemBase(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v


class CartItemInDBBase(CartItemBase):
    id: int
    cart_id: int
    unit_price: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartItem(CartItemInDBBase):
    subtotal: Decimal
    product: "ProductBase"


class CartBase(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    is_active: bool = True


class CartCreate(CartBase):
    pass


class CartInDBBase(CartBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Cart(CartInDBBase):
    items: List[CartItem] = []
    total_items: int
    total_amount: Decimal


class CartSummary(BaseModel):
    total_items: int
    total_amount: Decimal
    items_count: int


CartItem.model_rebuild()
