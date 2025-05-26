from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from .product import ProductBase
from .user import UserBase
from ..models.order import OrderStatus, PaymentStatus


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemInDBBase(OrderItemBase):
    id: int
    order_id: int
    product_name: str
    product_sku: str
    total_price: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDBBase):
    product: Optional["ProductBase"] = None


class OrderBase(BaseModel):
    shipping_address: str
    shipping_city: str
    shipping_country: str
    shipping_postal_code: str
    shipping_phone: Optional[str] = None
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None
    billing_postal_code: Optional[str] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class OrderInDBBase(OrderBase):
    id: int
    order_number: str
    user_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    tracking_number: Optional[str] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    items: List[OrderItem] = []
    total_items: int
    user: Optional["UserBase"] = None


class OrderSummary(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: Decimal
    total_items: int
    created_at: datetime


class OrderStats(BaseModel):
    total_orders: int
    pending_orders: int
    completed_orders: int
    total_revenue: Decimal
    average_order_value: Decimal


OrderItem.model_rebuild()
Order.model_rebuild()
