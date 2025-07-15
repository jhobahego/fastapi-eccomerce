from fastapi.testclient import TestClient
from typing import Dict

from app.models.category import Category
from app.models.product import Product


class TestProductEndpoints:
    """Test cases for product endpoints"""

    def test_get_products(self, client: TestClient):
        """Test getting products list"""
        response = client.get("/api/v1/products/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_products_with_filters(self, client: TestClient, product: Product):
        """Test getting products with filters"""
        # Test active_only filter
        response = client.get("/api/v1/products/?active_only=true")
        assert response.status_code == 200

        # Test pagination
        response = client.get("/api/v1/products/?skip=0&limit=10")
        assert response.status_code == 200

    def test_create_product_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str], category: Category
    ):
        """Test creating product (admin only)"""
        product_data = {
            "name": "New Product",
            "description": "A new product description",
            "short_description": "New product",
            "slug": "new-product",
            "sku": "NEW-001",
            "price": "99.99",
            "stock_quantity": 10,
            "min_stock_level": 5,
            "is_active": True,
            "is_featured": False,
            "category_id": category.id,
        }

        response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Product"
        assert data["slug"] == "new-product"
        assert data["sku"] == "NEW-001"
        assert float(data["price"]) == 99.99
        assert data["category_id"] == category.id

    def test_create_product_unauthorized(self, client: TestClient, category: Category):
        """Test creating product without authentication"""
        product_data = {
            "name": "New Product",
            "slug": "new-product",
            "sku": "NEW-001",
            "price": "99.99",
            "category_id": category.id,
        }

        response = client.post("/api/v1/products/", json=product_data)

        assert response.status_code == 401

    def test_create_product_regular_user_forbidden(
        self, client: TestClient, user_auth_headers: Dict[str, str], category: Category
    ):
        """Test creating product as regular user (should be forbidden)"""
        product_data = {
            "name": "New Product",
            "slug": "new-product",
            "sku": "NEW-001",
            "price": "99.99",
            "category_id": category.id,
        }

        response = client.post(
            "/api/v1/products/", json=product_data, headers=user_auth_headers
        )

        # Could be 400 (validation error) or 403 (permission error)
        # depending on which validation runs first
        assert response.status_code in [400, 403]

    def test_get_product_by_id(self, client: TestClient, product: Product):
        """Test getting product by ID"""
        response = client.get(f"/api/v1/products/{product.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product.id
        assert data["name"] == product.name
        assert data["sku"] == product.sku

    def test_get_product_by_id_not_found(self, client: TestClient):
        """Test getting product by ID when not found"""
        response = client.get("/api/v1/products/99999")

        assert response.status_code == 404

    def test_update_product_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str], product: Product
    ):
        """Test updating product (admin only)"""
        update_data = {
            "name": "Updated Product Name",
            "price": "199.99",
            "is_featured": True,
        }

        response = client.put(
            f"/api/v1/products/{product.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert float(data["price"]) == 199.99
        assert data["is_featured"] is True

    def test_delete_product_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str], category: Category
    ):
        """Test deleting product (admin only)"""
        # First create a product to delete
        product_data = {
            "name": "To Delete Product",
            "slug": "to-delete-product",
            "sku": "DELETE-001",
            "price": "50.00",
            "category_id": category.id,
        }

        create_response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )
        assert create_response.status_code == 200
        created_product = create_response.json()

        # Then delete the product
        delete_response = client.delete(
            f"/api/v1/products/{created_product['id']}", headers=auth_headers
        )

        assert delete_response.status_code == 200

        # Verify product is deleted
        get_response = client.get(f"/api/v1/products/{created_product['id']}")
        assert get_response.status_code == 404

    def test_get_product_by_slug(self, client: TestClient, product: Product):
        """Test getting product by slug"""
        response = client.get(f"/api/v1/products/slug/{product.slug}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product.id
        assert data["slug"] == product.slug

    def test_get_product_by_sku(self, client: TestClient, product: Product):
        """Test getting product by SKU"""
        response = client.get(f"/api/v1/products/sku/{product.sku}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product.id
        assert data["sku"] == product.sku

    def test_update_product_stock(
        self, client: TestClient, auth_headers: Dict[str, str], product: Product
    ):
        """Test updating product stock"""
        # Guardar stock inicial
        initial_stock = product.stock_quantity
        stock_update = {"quantity": 5, "operation": "add"}

        response = client.put(  # Cambiado de PATCH a PUT
            f"/api/v1/products/{product.id}/stock",
            json=stock_update,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stock_quantity"] == initial_stock + 5

    def test_search_products(self, client: TestClient, product: Product):
        """Test searching products"""
        search_params = {
            "query": product.name[:5],  # Search by partial name
            "min_price": "0",
            "max_price": "1000",
            "sort_by": "name",
            "sort_order": "asc",
        }

        response = client.post("/api/v1/products/search", json=search_params)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_products_by_category(self, client: TestClient, product: Product):
        """Test getting products by category"""
        response = client.get(f"/api/v1/products/category/{product.category_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(item["category_id"] == product.category_id for item in data)

    def test_create_product_invalid_data(
        self, client: TestClient, auth_headers: Dict[str, str], category: Category
    ):
        """Test creating product with invalid data"""
        product_data = {
            "name": "Test Product",
            "slug": "test-product",
            "sku": "TEST-001",
            "price": "0",  # Invalid price (must be > 0)
            "stock_quantity": -5,  # Invalid stock (cannot be negative)
            "category_id": category.id,
        }

        response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 422  # Validation error

    def test_create_product_duplicate_sku(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        product: Product,
        category: Category,
    ):
        """Test creating product with duplicate SKU"""
        product_data = {
            "name": "Another Product",
            "slug": "another-product",
            "sku": product.sku,  # Duplicate SKU
            "price": "99.99",
            "category_id": category.id,
        }

        response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )

        assert response.status_code == 400  # Bad request due to duplicate SKU
