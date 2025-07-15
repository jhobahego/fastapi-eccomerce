from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from ....database import get_db
from ....core.security import get_current_superuser
from ....models.user import User
from ....schemas.product import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductWithCategory,
    ProductSearch,
    StockUpdate,
)
from ....services.product_service import ProductService

router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(True, description="Filter only active products"),
) -> Any:
    """
    Retrieve products.
    """
    product_service = ProductService(db)
    products = product_service.get_multi(skip=skip, limit=limit)
    if active_only:
        products = [prod for prod in products if prod.is_active]
    return products


@router.post("/", response_model=ProductSchema)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Create new product (admin only).
    """
    product_service = ProductService(db)
    product = product_service.create_product(product_in)
    return product


@router.get("/search", response_model=List[ProductSchema])
def search_products(
    *,
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    min_price: Optional[Decimal] = Query(None, description="Minimum price"),
    max_price: Optional[Decimal] = Query(None, description="Maximum price"),
    is_featured: Optional[bool] = Query(None, description="Filter featured products"),
    in_stock: Optional[bool] = Query(None, description="Filter products in stock"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Search products with filters.
    """
    product_service = ProductService(db)
    search_params = ProductSearch(
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
        in_stock=in_stock,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    products = product_service.search_products(search_params, skip=skip, limit=limit)
    return products


@router.get("/featured", response_model=List[ProductSchema])
def get_featured_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limit number of results"),
) -> Any:
    """
    Get featured products.
    """
    product_service = ProductService(db)
    products = product_service.get_featured_products(limit=limit)
    return products


@router.get("/low-stock", response_model=List[ProductSchema])
def get_low_stock_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    limit: int = Query(100, description="Limit number of results"),
) -> Any:
    """
    Get products with low stock (admin only).
    """
    product_service = ProductService(db)
    products = product_service.get_low_stock_products(limit=limit)
    return products


@router.get("/category/{category_id}", response_model=List[ProductSchema])
def get_products_by_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(True, description="Filter only active products"),
) -> Any:
    """
    Get products by category.
    """
    product_service = ProductService(db)
    products = product_service.get_products_by_category(
        category_id=category_id, skip=skip, limit=limit, active_only=active_only
    )
    return products


@router.get("/{product_id}", response_model=ProductWithCategory)
def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
) -> Any:
    """
    Get product by ID with category information.
    """
    product_service = ProductService(db)
    product = product_service.get_product_with_category(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update a product (admin only).
    """
    product_service = ProductService(db)
    product = product_service.get_by_id(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = product_service.update_product(product_id, product_in)
    return product


@router.delete("/{product_id}", response_model=ProductSchema)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a product (admin only).
    """
    product_service = ProductService(db)
    product = product_service.get_by_id(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product = product_service.delete(id=product_id)
    return product


@router.put("/{product_id}/stock", response_model=ProductSchema)
def update_product_stock(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    stock_update: StockUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Update product stock (admin only).
    """
    product_service = ProductService(db)
    product = product_service.get_by_id(id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = product_service.update_stock(
        product_id=product_id,
        stock_update=stock_update,
    )

    if not updated_product:
        raise HTTPException(status_code=400, detail="Failed to update stock")

    return updated_product


@router.get("/{product_id}/similar", response_model=List[ProductSchema])
def get_similar_products(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    limit: int = Query(5, description="Limit number of results"),
) -> Any:
    """
    Get similar products based on category.
    """
    # product_service = ProductService(db)
    # products = product_service.get_similar_products(product_id, limit=limit)
    # return products
    pass


@router.get("/slug/{slug}", response_model=ProductWithCategory)
def get_product_by_slug(
    *,
    db: Session = Depends(get_db),
    slug: str,
) -> Any:
    """
    Get product by slug with category information.
    """
    product_service = ProductService(db)
    product = product_service.get_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/sku/{sku}", response_model=ProductWithCategory)
def get_product_by_sku(
    *,
    db: Session = Depends(get_db),
    sku: str,
) -> Any:
    """
    Get product by SKU with category information.
    """
    product_service = ProductService(db)
    product = product_service.get_product_by_sku(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/search", response_model=List[ProductSchema])
def search_products_post(
    *,
    db: Session = Depends(get_db),
    search_data: dict,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Search products with filters using POST method.
    """
    product_service = ProductService(db)
    search_params = ProductSearch(**search_data)
    products = product_service.search_products(search_params, skip=skip, limit=limit)
    return products
