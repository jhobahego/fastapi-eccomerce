from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.schemas.category import CategoryBase


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    sku: str
    price: Decimal
    sale_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_quantity: int = 0
    min_stock_level: int = 5
    is_active: bool = True
    is_featured: bool = False
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    category_id: int


class ProductCreate(ProductBase):
    slug: str

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("sale_price")
    @classmethod
    def validate_sale_price(cls, v, values):
        if v is not None and "price" in values and v >= values["price"]:
            raise ValueError("Sale price must be less than regular price")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError("Stock quantity cannot be negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    category_id: Optional[int] = None


class ProductInDBBase(ProductBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Product(ProductInDBBase):
    current_price: Decimal
    is_in_stock: bool
    is_low_stock: bool


class ProductWithCategory(Product):
    category: CategoryBase


# Stock management
class StockUpdate(BaseModel):
    quantity: int
    operation: str  # 'add', 'subtract', 'set'

    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v):
        if v not in ["add", "subtract", "set"]:
            raise ValueError("Operation must be add, subtract, or set")
        return v


class ProductSearch(BaseModel):
    query: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v):
        allowed_fields = ["name", "price", "created_at", "stock_quantity"]
        if v not in allowed_fields:
            raise ValueError(f"Sort by must be one of: {allowed_fields}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be asc or desc")
        return v
