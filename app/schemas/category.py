from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    parent_id: Optional[int] = None
    image_url: Optional[str] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    slug: str

    @validator("name")
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        return v


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryInDBBase(CategoryBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    children: List["Category"] = []
    parent: Optional["Category"] = None


class CategoryWithProducts(Category):
    product_count: int = 0


# Para evitar referencias circulares
Category.model_rebuild()
