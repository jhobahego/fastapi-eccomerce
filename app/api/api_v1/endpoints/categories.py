from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....database import get_db
from ....core.security import get_current_superuser
from ....models.user import User
from ....schemas.category import (
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate,
    CategoryWithProducts,
    CategoryHierarchy,
)
from ....services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=List[CategorySchema])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(True, description="Filter only active categories"),
) -> Any:
    """
    Retrieve categories.
    """
    category_service = CategoryService(db)
    categories = category_service.get_multi(skip=skip, limit=limit)
    if active_only:
        categories = [cat for cat in categories if cat.is_active]
    return categories


@router.post("/", response_model=CategorySchema)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Create new category (admin only).
    """
    category_service = CategoryService(db)
    category = category_service.create_category(category_in)
    return category


@router.get("/hierarchy", response_model=List[CategoryHierarchy])
def get_category_hierarchy(
    db: Session = Depends(get_db),
    root_category_id: Optional[int] = Query(None, description="Root category ID"),
    max_depth: int = Query(3, description="Maximum depth of hierarchy"),
) -> Any:
    """
    Get category hierarchy tree.
    """
    category_service = CategoryService(db)
    hierarchy = category_service.get_category_hierarchy(
        root_category_id=root_category_id, max_depth=max_depth
    )
    return hierarchy


@router.get("/roots", response_model=List[CategorySchema])
def get_root_categories(
    db: Session = Depends(get_db),
    limit: int = Query(100, description="Limit number of results"),
) -> Any:
    """
    Get root categories (categories without parent).
    """
    category_service = CategoryService(db)
    categories = category_service.get_root_categories(limit=limit)
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get category by ID.
    """
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.get("/{category_id}/subcategories", response_model=List[CategorySchema])
def get_subcategories(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    limit: int = Query(100, description="Limit number of results"),
) -> Any:
    """
    Get subcategories of a category.
    """
    category_service = CategoryService(db)
    subcategories = category_service.get_subcategories(category_id, limit=limit)
    return subcategories


@router.get("/{category_id}/with-products", response_model=CategoryWithProducts)
def get_category_with_products(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get category with its products.
    """
    category_service = CategoryService(db)
    category = category_service.get_category_with_products(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update a category (admin only).
    """
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = category_service.update(id=category_id, obj_in=category_in)
    return category


@router.delete("/{category_id}", response_model=CategorySchema)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    force: bool = Query(
        False, description="Force delete even if category has products"
    ),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a category (admin only).
    """
    category_service = CategoryService(db)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = category_service.delete_category(category_id, force=force)
    return category


@router.get("/search/{query}", response_model=List[CategorySchema])
def search_categories(
    *,
    db: Session = Depends(get_db),
    query: str,
    limit: int = Query(20, description="Limit number of results"),
) -> Any:
    """
    Search categories by name.
    """
    category_service = CategoryService(db)
    categories = category_service.search_categories(query, limit=limit)
    return categories


@router.post("/reorder")
def reorder_categories(
    *,
    db: Session = Depends(get_db),
    category_orders: List[dict],
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Reorder categories (admin only).
    Expected format: [{"id": 1, "sort_order": 1}, {"id": 2, "sort_order": 2}]
    """
    category_service = CategoryService(db)
    success = category_service.reorder_categories(category_orders)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reorder categories")
    return {"message": "Categories reordered successfully"}
