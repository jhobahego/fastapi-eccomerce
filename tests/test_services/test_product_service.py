import pytest
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, StockUpdate, ProductSearch
from app.models.product import Product
from app.models.category import Category
from tests.factories import ProductFactory, CategoryFactory


class TestProductService:
    """Test cases for ProductService"""

    def test_create_product_success(self, db_session: Session, category: Category):
        """Test successful product creation"""
        product_service = ProductService(db_session)
        product_data = ProductCreate(
            name="Test Product",
            description="A test product",
            slug="test-product",
            sku="TEST-001",
            price=Decimal("99.99"),
            stock_quantity=10,
            category_id=category.id,
        )

        product = product_service.create_product(product_data)

        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.slug == "test-product"
        assert product.sku == "TEST-001"
        assert product.price == Decimal("99.99")
        assert product.stock_quantity == 10
        assert product.category_id == category.id

    def test_create_product_duplicate_sku(
        self, db_session: Session, category: Category
    ):
        """Test creating product with duplicate SKU"""
        product_service = ProductService(db_session)

        # Create first product
        product_data1 = ProductCreate(
            name="Product 1",
            slug="product-1",
            sku="DUPLICATE-SKU",
            price=Decimal("99.99"),
            category_id=category.id,
        )
        product_service.create_product(product_data1)

        # Try to create second product with same SKU
        product_data2 = ProductCreate(
            name="Product 2",
            slug="product-2",
            sku="DUPLICATE-SKU",
            price=Decimal("149.99"),
            category_id=category.id,
        )

        with pytest.raises(HTTPException) as exc_info:
            product_service.create_product(product_data2)

        assert exc_info.value.status_code == 400
        assert "SKU already exists" in str(exc_info.value.detail)

    def test_create_product_duplicate_slug(
        self, db_session: Session, category: Category
    ):
        """Test creating product with duplicate slug"""
        product_service = ProductService(db_session)

        # Create first product
        product_data1 = ProductCreate(
            name="Product 1",
            slug="duplicate-slug",
            sku="SKU-001",
            price=Decimal("99.99"),
            category_id=category.id,
        )
        product_service.create_product(product_data1)

        # Try to create second product with same slug
        product_data2 = ProductCreate(
            name="Product 2",
            slug="duplicate-slug",
            sku="SKU-002",
            price=Decimal("149.99"),
            category_id=category.id,
        )

        with pytest.raises(HTTPException) as exc_info:
            product_service.create_product(product_data2)

        assert exc_info.value.status_code == 400
        assert "Slug already exists" in str(exc_info.value.detail)

    def test_get_product_by_slug(self, db_session: Session, product: Product):
        """Test getting product by slug"""
        product_service = ProductService(db_session)

        found_product = product_service.get_product_by_slug(product.slug)

        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.slug == product.slug

    def test_get_product_by_slug_not_found(self, db_session: Session):
        """Test getting product by slug when not found"""
        product_service = ProductService(db_session)

        found_product = product_service.get_product_by_slug(
            "nonexistent-slug", raise_404=False
        )

        assert found_product is None

    def test_get_product_by_sku(self, db_session: Session, product: Product):
        """Test getting product by SKU"""
        product_service = ProductService(db_session)

        found_product = product_service.get_product_by_sku(product.sku)

        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.sku == product.sku

    def test_get_products_by_category(self, db_session: Session, category: Category):
        """Test getting products by category"""
        product_service = ProductService(db_session)

        # Create multiple products in the same category
        for i in range(3):
            product_data = ProductCreate(
                name=f"Product {i}",
                slug=f"product-{i}",
                sku=f"SKU-{i:03d}",
                price=Decimal("99.99"),
                category_id=category.id,
            )
            product_service.create_product(product_data)

        products = product_service.get_products_by_category(category.id)

        assert len(products) == 3
        assert all(product.category_id == category.id for product in products)

    def test_update_product_stock(self, db_session: Session, product: Product):
        """Test updating product stock"""
        product_service = ProductService(db_session)
        initial_stock = product.stock_quantity

        # Add stock
        stock_update = StockUpdate(quantity=5, operation="add")
        updated_product = product_service.update_stock(product.id, stock_update)

        assert updated_product.stock_quantity == initial_stock + 5

        # Subtract stock
        stock_update = StockUpdate(quantity=3, operation="subtract")
        updated_product = product_service.update_stock(product.id, stock_update)

        assert updated_product.stock_quantity == initial_stock + 5 - 3

        # Set stock
        stock_update = StockUpdate(quantity=20, operation="set")
        updated_product = product_service.update_stock(product.id, stock_update)

        assert updated_product.stock_quantity == 20

    def test_search_products(self, db_session: Session, category: Category):
        """Test searching products"""
        product_service = ProductService(db_session)

        # Create test products
        products_data = [
            ProductCreate(
                name="iPhone 15",
                slug="iphone-15",
                sku="IPHONE-15",
                price=Decimal("999.99"),
                is_featured=True,
                category_id=category.id,
                stock_quantity=10,  # Explicitly set stock
            ),
            ProductCreate(
                name="Samsung Galaxy",
                slug="samsung-galaxy",
                sku="SAMSUNG-001",
                price=Decimal("799.99"),
                is_featured=False,
                category_id=category.id,
                stock_quantity=5,  # Explicitly set stock
            ),
            ProductCreate(
                name="Google Pixel",
                slug="google-pixel",
                sku="PIXEL-001",
                price=Decimal("699.99"),
                stock_quantity=0,  # Out of stock
                category_id=category.id,
            ),
        ]

        for product_data in products_data:
            product_service.create_product(product_data)

        # Search by name
        results = product_service.search_products(query="iPhone")
        assert len(results) == 1
        assert results[0].name == "iPhone 15"

        # Search featured products
        search_params = ProductSearch(is_featured=True)
        results = product_service.search_products(search_params)
        assert len(results) >= 1
        assert any(result.name == "iPhone 15" for result in results)

        # Simple search to verify basic functionality
        search_params = ProductSearch()
        results = product_service.search_products(search_params)
        assert len(results) >= 3  # At least our three products

    def test_update_product(self, db_session: Session, product: Product):
        """Test updating product"""
        product_service = ProductService(db_session)

        update_data = ProductUpdate(
            name="Updated Product Name", price=Decimal("199.99"), is_featured=True
        )

        updated_product = product_service.update(product.id, update_data)

        assert updated_product is not None
        assert updated_product.name == "Updated Product Name"
        assert updated_product.price == Decimal("199.99")
        assert updated_product.is_featured is True
        assert updated_product.slug == product.slug  # Unchanged

    def test_delete_product(self, db_session: Session, product: Product):
        """Test deleting product"""
        product_service = ProductService(db_session)

        deleted_product = product_service.delete(product.id)

        assert deleted_product is not None
        assert deleted_product.id == product.id

        # Verify product is deleted
        found_product = product_service.get_by_id(product.id, raise_404=False)
        assert found_product is None

    def test_get_product_with_category(self, db_session: Session, product: Product):
        """Test getting product with category information"""
        product_service = ProductService(db_session)

        product_with_category = product_service.get_product_with_category(product.id)

        assert product_with_category is not None
        assert product_with_category.id == product.id
        assert hasattr(product_with_category, "category")
        assert product_with_category.category is not None

    def test_product_service_with_factory(self, db_session: Session):
        """Test product service using factory"""
        # Create category using factory
        category = CategoryFactory()
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Create product using factory
        product = ProductFactory(category_id=category.id)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        product_service = ProductService(db_session)

        # Test service methods
        found_product = product_service.get_by_id(product.id)
        assert found_product is not None
        assert found_product.name == product.name
