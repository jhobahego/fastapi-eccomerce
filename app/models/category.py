from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Self-referential relationship for subcategories
    # lazy='select' evita carga automática y previene recursión
    parent = relationship(
        "Category", remote_side=[id], back_populates="children", lazy="select"
    )
    children = relationship("Category", back_populates="parent", lazy="select")

    # Relationship with products
    products = relationship("Product", back_populates="category")
