from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from ..database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    sku: Mapped[str] = mapped_column(String, unique=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    sale_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    cost_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    stock_quantity: Mapped[int] = mapped_column(default=0)
    min_stock_level: Mapped[int] = mapped_column(default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    dimensions: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # {"length": 10, "width": 5, "height": 2}
    images: Mapped[Optional[List[str]]] = mapped_column(
        JSON, nullable=True
    )  # List of image URLs
    attributes: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # {"color": "red", "size": "M"}
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

    @property
    def current_price(self) -> Decimal:
        """Retorna el precio actual (sale_price si existe, sino price)"""
        return self.sale_price if self.sale_price is not None else self.price

    @property
    def is_in_stock(self) -> bool:
        """Verifica si el producto está en stock"""
        return self.stock_quantity > 0

    @property
    def is_low_stock(self) -> bool:
        """Verifica si el stock está bajo"""
        return self.stock_quantity <= self.min_stock_level
