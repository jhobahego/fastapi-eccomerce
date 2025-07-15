from pydantic import BaseModel, field_validator
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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        return v

    @field_validator("is_active", mode="before")
    @classmethod
    def validate_is_active(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("sort_order", mode="before")
    @classmethod
    def validate_sort_order(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("sort_order must be a valid integer")
        return v

    @field_validator("parent_id", mode="before")
    @classmethod
    def validate_parent_id(cls, v):
        if v is None or v == "" or v == "null" or v == "None":
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("parent_id must be a valid integer or None")
        return v


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    parent_id: Optional[int] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        return v

    @field_validator("is_active", mode="before")
    @classmethod
    def validate_is_active(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("sort_order", mode="before")
    @classmethod
    def validate_sort_order(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("sort_order must be a valid integer")
        return v

    @field_validator("parent_id", mode="before")
    @classmethod
    def validate_parent_id(cls, v):
        if v is None or v == "" or v == "null" or v == "None":
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("parent_id must be a valid integer or None")
        return v


class CategoryInDBBase(CategoryBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Esquema básico de categoría sin relaciones circulares
class Category(CategoryInDBBase):
    pass


# Esquema para categoría con información del padre (sin hijos)
class CategoryWithParent(CategoryInDBBase):
    parent: Optional["Category"] = None


# Esquema para categoría con hijos (sin padre)
class CategoryWithChildren(CategoryInDBBase):
    children: List["Category"] = []


# Esquema para jerarquía completa (usado en endpoints específicos)
class CategoryHierarchy(CategoryInDBBase):
    children: List["CategoryHierarchy"] = []
    depth: int = 0


class CategoryWithProducts(Category):
    product_count: int = 0


# Para evitar referencias circulares
CategoryWithParent.model_rebuild()
CategoryWithChildren.model_rebuild()
CategoryHierarchy.model_rebuild()
