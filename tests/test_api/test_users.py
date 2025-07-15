from fastapi.testclient import TestClient
from typing import Dict

from app.models.user import User


class TestUserEndpoints:
    """Test cases for user endpoints"""

    def test_create_user_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test creating user (admin only)"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }

        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert "password" not in data  # Password should not be returned

    def test_create_user_unauthorized(self, client: TestClient):
        """Test creating user without authentication"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }

        response = client.post("/api/v1/users/", json=user_data)

        assert response.status_code == 401

    def test_create_user_regular_user_forbidden(
        self, client: TestClient, user_auth_headers: Dict[str, str]
    ):
        """Test creating user as regular user (should be forbidden)"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }

        response = client.post(
            "/api/v1/users/", json=user_data, headers=user_auth_headers
        )

        # Could be 400 (validation error) or 403 (permission error)
        # depending on which validation runs first
        assert response.status_code in [400, 403]

    def test_get_users_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test getting users list (admin only)"""
        response = client.get("/api/v1/users/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the superuser

    def test_get_users_unauthorized(self, client: TestClient):
        """Test getting users list without authentication"""
        response = client.get("/api/v1/users/")

        assert response.status_code == 401

    def test_get_user_me(self, client: TestClient, user_auth_headers: Dict[str, str]):
        """Test getting current user info"""
        response = client.get("/api/v1/users/me", headers=user_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert "id" in data
        assert "password" not in data

    def test_update_user_me(
        self, client: TestClient, user_auth_headers: Dict[str, str]
    ):
        """Test updating current user info"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "123-456-7890",
        }

        response = client.put(
            "/api/v1/users/me", json=update_data, headers=user_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "123-456-7890"

    def test_get_user_by_id_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str], regular_user: User
    ):
        """Test getting user by ID (admin only)"""
        response = client.get(f"/api/v1/users/{regular_user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == regular_user.id
        assert data["email"] == regular_user.email

    def test_update_user_by_id_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str], regular_user: User
    ):
        """Test updating user by ID (admin only)"""
        update_data = {"first_name": "Admin Updated", "is_active": False}

        response = client.put(
            f"/api/v1/users/{regular_user.id}", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Admin Updated"
        assert data["is_active"] is False

    def test_delete_user_admin_only(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test deleting user (admin only)"""
        # First create a user to delete
        user_data = {
            "email": "todelete@test.com",
            "username": "todelete",
            "first_name": "To",
            "last_name": "Delete",
            "password": "password123",
        }

        create_response = client.post(
            "/api/v1/users/", json=user_data, headers=auth_headers
        )
        assert create_response.status_code == 200
        created_user = create_response.json()

        # Then delete the user
        delete_response = client.delete(
            f"/api/v1/users/{created_user['id']}", headers=auth_headers
        )

        assert delete_response.status_code == 200

        # Verify user is deleted
        get_response = client.get(
            f"/api/v1/users/{created_user['id']}", headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_create_user_invalid_data(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test creating user with invalid data"""
        user_data = {
            "email": "invalid-email",  # Invalid email
            "username": "ab",  # Username too short
            "first_name": "Test",
            "last_name": "User",
            "password": "short",  # Password too short
        }

        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    def test_create_user_duplicate_email(
        self, client: TestClient, auth_headers: Dict[str, str], regular_user: User
    ):
        """Test creating user with duplicate email"""
        user_data = {
            "email": regular_user.email,  # Duplicate email
            "username": "newusername",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }

        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        assert response.status_code in [400, 409]  # Bad request or conflict
