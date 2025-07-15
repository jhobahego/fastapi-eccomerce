import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.category import Category


class TestProductModel:
    """Test cases for Product model"""

    def test_create_product(self, db_session: Session, category: Category):
        """Test creating a product"""
        product = Product(
            name="iPhone 15",
            description="Latest iPhone model",
            short_description="New iPhone",
            slug="iphone-15",
            sku="IPHONE-15-001",
            price=Decimal("999.99"),
            stock_quantity=10,
            min_stock_level=5,
            is_active=True,
            is_featured=True,
            category_id=category.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        assert product.id is not None
        assert product.name == "iPhone 15"
        assert product.description == "Latest iPhone model"
        assert product.short_description == "New iPhone"
        assert product.slug == "iphone-15"
        assert product.sku == "IPHONE-15-001"
        assert product.price == Decimal("999.99")
        assert product.stock_quantity == 10
        assert product.min_stock_level == 5
        assert product.is_active is True
        assert product.is_featured is True
        assert product.category_id == category.id
        assert product.created_at is not None
        assert isinstance(product.created_at, datetime)

    def test_product_category_relationship(
        self, db_session: Session, category: Category
    ):
        """Test product-category relationship"""
        product = Product(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            price=Decimal("99.99"),
            category_id=category.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        assert product.category == category
        assert product in category.products

    def test_product_current_price_property(
        self, db_session: Session, category: Category
    ):
        """Test current_price property"""
        # Test with sale_price
        product_with_sale = Product(
            name="Sale Product",
            slug="sale-product",
            sku="SALE-001",
            price=Decimal("100.00"),
            sale_price=Decimal("80.00"),
            category_id=category.id,
        )
        db_session.add(product_with_sale)
        db_session.commit()

        assert product_with_sale.current_price == Decimal("80.00")

        # Test without sale_price
        product_no_sale = Product(
            name="Regular Product",
            slug="regular-product",
            sku="REG-001",
            price=Decimal("100.00"),
            category_id=category.id,
        )
        db_session.add(product_no_sale)
        db_session.commit()

        assert product_no_sale.current_price == Decimal("100.00")

    def test_product_is_in_stock_property(
        self, db_session: Session, category: Category
    ):
        """Test is_in_stock property"""
        # Test in stock
        product_in_stock = Product(
            name="In Stock Product",
            slug="in-stock-product",
            sku="STOCK-001",
            price=Decimal("50.00"),
            stock_quantity=10,
            category_id=category.id,
        )
        db_session.add(product_in_stock)
        db_session.commit()

        assert product_in_stock.is_in_stock is True

        # Test out of stock
        product_out_of_stock = Product(
            name="Out of Stock Product",
            slug="out-of-stock-product",
            sku="STOCK-002",
            price=Decimal("50.00"),
            stock_quantity=0,
            category_id=category.id,
        )
        db_session.add(product_out_of_stock)
        db_session.commit()

        assert product_out_of_stock.is_in_stock is False

    def test_product_is_low_stock_property(
        self, db_session: Session, category: Category
    ):
        """Test is_low_stock property"""
        # Test not low stock
        product_good_stock = Product(
            name="Good Stock Product",
            slug="good-stock-product",
            sku="LOW-001",
            price=Decimal("50.00"),
            stock_quantity=10,
            min_stock_level=5,
            category_id=category.id,
        )
        db_session.add(product_good_stock)
        db_session.commit()

        assert product_good_stock.is_low_stock is False

        # Test low stock
        product_low_stock = Product(
            name="Low Stock Product",
            slug="low-stock-product",
            sku="LOW-002",
            price=Decimal("50.00"),
            stock_quantity=3,
            min_stock_level=5,
            category_id=category.id,
        )
        db_session.add(product_low_stock)
        db_session.commit()

        assert product_low_stock.is_low_stock is True

    def test_product_unique_slug(self, db_session: Session, category: Category):
        """Test that product slug must be unique"""
        product1 = Product(
            name="Product 1",
            slug="unique-product",
            sku="UNIQUE-001",
            price=Decimal("50.00"),
            category_id=category.id,
        )
        db_session.add(product1)
        db_session.commit()

        product2 = Product(
            name="Product 2",
            slug="unique-product",
            sku="UNIQUE-002",
            price=Decimal("60.00"),
            category_id=category.id,
        )
        db_session.add(product2)

        with pytest.raises(Exception):  # IntegrityError will be raised
            db_session.commit()

    def test_product_unique_sku(self, db_session: Session, category: Category):
        """Test that product SKU must be unique"""
        product1 = Product(
            name="Product 1",
            slug="product-1",
            sku="UNIQUE-SKU",
            price=Decimal("50.00"),
            category_id=category.id,
        )
        db_session.add(product1)
        db_session.commit()

        product2 = Product(
            name="Product 2",
            slug="product-2",
            sku="UNIQUE-SKU",
            price=Decimal("60.00"),
            category_id=category.id,
        )
        db_session.add(product2)

        with pytest.raises(Exception):  # IntegrityError will be raised
            db_session.commit()

    def test_product_defaults(self, db_session: Session, category: Category):
        """Test default values for product fields"""
        product = Product(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            price=Decimal("99.99"),
            category_id=category.id,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)

        assert product.stock_quantity == 0
        assert product.min_stock_level == 5
        assert product.is_active is True
        assert product.is_featured is False
        assert product.description is None
        assert product.short_description is None
        assert product.sale_price is None
        assert product.cost_price is None
        assert product.weight is None

    def test_product_str_representation(self, db_session: Session, category: Category):
        """Test string representation of product"""
        product = Product(
            name="Test Product",
            slug="test-product",
            sku="TEST-001",
            price=Decimal("99.99"),
            category_id=category.id,
        )
        db_session.add(product)
        db_session.commit()

        assert str(product) == "Test Product"
