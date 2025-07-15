import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.product import ProductCreate, ProductUpdate, StockUpdate, ProductSearch


class TestProductSchemas:
    """Test cases for Product schemas"""

    def test_product_create_valid(self):
        """Test valid ProductCreate schema"""
        product_data = {
            "name": "Test Product",
            "description": "A test product",
            "short_description": "Test product",
            "sku": "TEST-001",
            "slug": "test-product",
            "price": Decimal("99.99"),
            "sale_price": Decimal("79.99"),
            "cost_price": Decimal("50.00"),
            "stock_quantity": 10,
            "min_stock_level": 5,
            "is_active": True,
            "is_featured": False,
            "weight": Decimal("1.5"),
            "category_id": 1,
        }
        product = ProductCreate(**product_data)

        assert product.name == "Test Product"
        assert product.description == "A test product"
        assert product.sku == "TEST-001"
        assert product.slug == "test-product"
        assert product.price == Decimal("99.99")
        assert product.sale_price == Decimal("79.99")
        assert product.cost_price == Decimal("50.00")
        assert product.stock_quantity == 10
        assert product.min_stock_level == 5
        assert product.is_active is True
        assert product.is_featured is False
        assert product.weight == Decimal("1.5")
        assert product.category_id == 1

    def test_product_create_price_validation(self):
        """Test ProductCreate price validation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "slug": "test-product",
            "price": Decimal("0"),  # Invalid price
            "category_id": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)

        assert "Price must be greater than 0" in str(exc_info.value)

    def test_product_create_sale_price_validation(self):
        """Test ProductCreate sale price validation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "slug": "test-product",
            "price": Decimal("100.00"),
            "sale_price": Decimal("150.00"),  # Sale price higher than regular price
            "category_id": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)

        assert "Sale price must be less than regular price" in str(exc_info.value)

    def test_product_create_stock_validation(self):
        """Test ProductCreate stock validation"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "slug": "test-product",
            "price": Decimal("99.99"),
            "stock_quantity": -5,  # Negative stock
            "category_id": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)

        assert "Stock quantity cannot be negative" in str(exc_info.value)

    def test_product_update_valid(self):
        """Test valid ProductUpdate schema"""
        update_data = {
            "name": "Updated Product",
            "price": Decimal("199.99"),
            "stock_quantity": 20,
            "is_featured": True,
        }
        product_update = ProductUpdate(**update_data)

        assert product_update.name == "Updated Product"
        assert product_update.price == Decimal("199.99")
        assert product_update.stock_quantity == 20
        assert product_update.is_featured is True

    def test_product_update_partial(self):
        """Test partial ProductUpdate schema"""
        update_data = {
            "name": "Updated Product",
        }
        product_update = ProductUpdate(**update_data)  # type: ignore[arg-type]

        assert product_update.name == "Updated Product"
        assert product_update.price is None
        assert product_update.stock_quantity is None

    def test_stock_update_valid(self):
        """Test valid StockUpdate schema"""
        stock_data = {
            "quantity": 10,
            "operation": "add",
        }
        stock_update = StockUpdate(**stock_data)

        assert stock_update.quantity == 10
        assert stock_update.operation == "add"

    def test_stock_update_operation_validation(self):
        """Test StockUpdate operation validation"""
        stock_data = {
            "quantity": 10,
            "operation": "invalid",  # Invalid operation
        }

        with pytest.raises(ValidationError) as exc_info:
            StockUpdate(**stock_data)

        assert "Operation must be add, subtract, or set" in str(exc_info.value)

    def test_product_search_valid(self):
        """Test valid ProductSearch schema"""
        search_data = {
            "query": "test product",
            "category_id": 1,
            "min_price": Decimal("10.00"),
            "max_price": Decimal("100.00"),
            "is_featured": True,
            "in_stock": True,
            "sort_by": "price",
            "sort_order": "asc",
        }
        search = ProductSearch(**search_data)

        assert search.query == "test product"
        assert search.category_id == 1
        assert search.min_price == Decimal("10.00")
        assert search.max_price == Decimal("100.00")
        assert search.is_featured is True
        assert search.in_stock is True
        assert search.sort_by == "price"
        assert search.sort_order == "asc"

    def test_product_search_sort_by_validation(self):
        """Test ProductSearch sort_by validation"""
        search_data = {
            "sort_by": "invalid_field",
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductSearch(**search_data)  # type: ignore[arg-type]

        assert "Sort by must be one of:" in str(exc_info.value)

    def test_product_search_sort_order_validation(self):
        """Test ProductSearch sort_order validation"""
        search_data = {
            "sort_order": "invalid_order",
        }

        with pytest.raises(ValidationError) as exc_info:
            ProductSearch(**search_data)  # type: ignore[arg-type]

        assert "Sort order must be asc or desc" in str(exc_info.value)

    def test_product_create_defaults(self):
        """Test ProductCreate with default values"""
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "slug": "test-product",
            "price": Decimal("99.99"),
            "category_id": 1,
        }
        product = ProductCreate(**product_data)

        assert product.stock_quantity == 0
        assert product.min_stock_level == 5
        assert product.is_active is True
        assert product.is_featured is False
        assert product.description is None
        assert product.short_description is None
