import pytest
from fastapi.testclient import TestClient
from typing import Dict


@pytest.mark.integration
class TestEcommerceWorkflow:
    """Integration tests for complete ecommerce workflow"""

    def test_complete_user_registration_and_login_flow(self, client: TestClient):
        """Test complete user registration and login flow"""
        # 1. Register a new user
        user_data = {
            "email": "integration@test.com",
            "username": "integrationuser",
            "first_name": "Integration",
            "last_name": "Test",
            "password": "integrationtest123",
        }

        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200
        user = register_response.json()
        assert user["email"] == user_data["email"]

        # 2. Login with the new user
        login_data = {"username": user_data["email"], "password": user_data["password"]}

        login_response = client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens

        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_response = client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["email"] == user_data["email"]

        # 4. Update user profile
        update_data = {"phone": "123-456-7890", "address": "123 Integration St"}

        update_response = client.put(
            "/api/v1/users/me", json=update_data, headers=headers
        )
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["phone"] == "123-456-7890"

    def test_complete_product_management_flow(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test complete product management flow"""
        # 1. Create a category first
        category_data = {
            "name": "Integration Electronics",
            "description": "Electronics for integration testing",
            "slug": "integration-electronics",
        }

        category_response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert category_response.status_code == 200
        category = category_response.json()

        # 2. Create a product
        product_data = {
            "name": "Integration Phone",
            "description": "A phone for integration testing",
            "short_description": "Integration phone",
            "slug": "integration-phone",
            "sku": "INT-PHONE-001",
            "price": "299.99",
            "stock_quantity": 50,
            "min_stock_level": 10,
            "is_active": True,
            "is_featured": True,
            "category_id": category["id"],
        }

        product_response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_headers
        )
        assert product_response.status_code == 200
        product = product_response.json()
        assert product["name"] == "Integration Phone"

        # 3. Get product by different methods
        # Get by ID
        product_by_id = client.get(f"/api/v1/products/{product['id']}")
        assert product_by_id.status_code == 200
        assert product_by_id.json()["id"] == product["id"]

        # Get by slug
        product_by_slug = client.get(f"/api/v1/products/slug/{product['slug']}")
        assert product_by_slug.status_code == 200
        assert product_by_slug.json()["slug"] == product["slug"]

        # Get by SKU
        product_by_sku = client.get(f"/api/v1/products/sku/{product['sku']}")
        assert product_by_sku.status_code == 200
        assert product_by_sku.json()["sku"] == product["sku"]

        # 4. Update product
        update_data = {"price": "349.99", "is_featured": False, "stock_quantity": 25}

        update_response = client.put(
            f"/api/v1/products/{product['id']}", json=update_data, headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_product = update_response.json()
        assert float(updated_product["price"]) == 349.99
        assert updated_product["is_featured"] is False

        # 5. Update stock using stock endpoint
        stock_update = {"quantity": 10, "operation": "add"}

        stock_response = client.put(  # Cambiado de PATCH a PUT
            f"/api/v1/products/{product['id']}/stock",
            json=stock_update,
            headers=auth_headers,
        )
        assert stock_response.status_code == 200
        stock_updated_product = stock_response.json()
        assert stock_updated_product["stock_quantity"] == 35  # 25 + 10

        # 6. Search for the product
        search_data = {
            "query": "Integration",
            "category_id": category["id"],
            "min_price": "100",
            "max_price": "500",
        }

        search_response = client.post("/api/v1/products/search", json=search_data)
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) >= 1

        # 7. Get products by category
        category_products = client.get(f"/api/v1/products/category/{category['id']}")
        assert category_products.status_code == 200
        category_products_data = category_products.json()
        assert len(category_products_data) >= 1
        assert all(p["category_id"] == category["id"] for p in category_products_data)

    def test_category_hierarchy_flow(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test category hierarchy management"""
        # 1. Create parent category
        parent_data = {
            "name": "Electronics",
            "slug": "electronics",
            "description": "All electronic devices",
        }

        parent_response = client.post(
            "/api/v1/categories/", json=parent_data, headers=auth_headers
        )
        assert parent_response.status_code == 200
        parent_category = parent_response.json()

        # 2. Create child category
        child_data = {
            "name": "Smartphones",
            "slug": "smartphones",
            "description": "Mobile phones",
            "parent_id": parent_category["id"],
        }

        child_response = client.post(
            "/api/v1/categories/", json=child_data, headers=auth_headers
        )
        assert child_response.status_code == 200
        child_category = child_response.json()
        assert child_category["parent_id"] == parent_category["id"]

        # 3. Get categories and verify hierarchy
        categories_response = client.get("/api/v1/categories/")
        assert categories_response.status_code == 200
        categories = categories_response.json()
        assert len(categories) >= 2

        # 4. Get category with children (subcategories)
        parent_with_children = client.get(
            f"/api/v1/categories/{parent_category['id']}/subcategories"  # Cambiado de /children a /subcategories
        )
        assert parent_with_children.status_code == 200
        subcategories = parent_with_children.json()
        assert len(subcategories) >= 1

        # 5. Update category
        update_data = {
            "description": "Updated electronics description",
            "is_active": True,
        }

        update_response = client.put(
            f"/api/v1/categories/{parent_category['id']}",
            json=update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200
        updated_category = update_response.json()
        assert updated_category["description"] == "Updated electronics description"

    def test_error_handling_flow(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test error handling in various scenarios"""
        # 1. Try to access non-existent resource
        response = client.get("/api/v1/products/99999")
        assert response.status_code == 404

        # 2. Try to create product with invalid data
        invalid_product = {
            "name": "Invalid Product",
            "slug": "invalid-product",
            "sku": "INVALID-001",
            "price": "0",  # Invalid price
            "category_id": 99999,  # Non-existent category
        }

        response = client.post(
            "/api/v1/products/", json=invalid_product, headers=auth_headers
        )
        assert response.status_code in [400, 422]  # Bad request or validation error

        # 3. Try to access admin endpoint as regular user
        # First create a regular user
        user_data = {
            "email": "regular@test.com",
            "username": "regular",
            "first_name": "Regular",
            "last_name": "User",
            "password": "regular123",
        }

        client.post("/api/v1/auth/register", json=user_data)

        # Login as regular user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        user_tokens = login_response.json()
        user_headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}

        # Try to create product as regular user
        response = client.post(
            "/api/v1/products/", json={"name": "Test"}, headers=user_headers
        )
        # Could be 400 (validation error) or 403 (permission error)
        # depending on which validation runs first
        assert response.status_code in [400, 403]

    def test_authentication_flow_edge_cases(self, client: TestClient):
        """Test authentication edge cases"""
        # 1. Try to register with existing email
        user_data = {
            "email": "duplicate@test.com",
            "username": "user1",
            "first_name": "User",
            "last_name": "One",
            "password": "password123",
        }

        first_response = client.post("/api/v1/auth/register", json=user_data)
        assert first_response.status_code == 200

        # Try to register again with same email
        user_data["username"] = "user2"
        duplicate_response = client.post("/api/v1/auth/register", json=user_data)
        assert duplicate_response.status_code in [400, 409]

        # 2. Try to login with inactive user
        # This would require admin to deactivate user first

        # 3. Test token refresh
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        tokens = login_response.json()

        refresh_response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
