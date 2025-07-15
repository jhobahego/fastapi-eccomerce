from fastapi.testclient import TestClient
from typing import Dict
from sqlalchemy.orm import Session

from app.models.user import User


class TestAuthEndpoints:
    """Test cases for authentication endpoints"""

    def test_login_success(
        self, client: TestClient, superuser: User, superuser_data: Dict[str, str]
    ):
        """Test successful login"""
        login_data = {
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_login_with_username(
        self, client: TestClient, superuser: User, superuser_data: Dict[str, str]
    ):
        """Test login with username instead of email"""
        login_data = {
            "username": superuser_data["username"],
            "password": superuser_data["password"],
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_wrong_password(
        self, client: TestClient, superuser: User, superuser_data: Dict[str, str]
    ):
        """Test login with wrong password"""
        login_data = {"username": superuser_data["email"], "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        login_data = {"username": "nonexistent@test.com", "password": "password123"}

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_inactive_user(
        self,
        client: TestClient,
        regular_user: User,
        regular_user_data: Dict[str, str],
        db_session: Session,
    ):
        """Test login with inactive user"""
        # First deactivate the user directly in database
        regular_user.is_active = False
        db_session.add(regular_user)
        db_session.commit()

        # Try to login with inactive user
        login_data = {
            "username": regular_user_data["email"],
            "password": regular_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", data=login_data)

        assert (
            response.status_code == 400
        )  # Changed to 400 as per the auth endpoint code

    def test_register_user(self, client: TestClient):
        """Test user registration"""
        user_data = {
            "email": "newuser@test.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "newpassword123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert "password" not in data

    def test_register_duplicate_email(self, client: TestClient, regular_user: User):
        """Test registration with duplicate email"""
        user_data = {
            "email": regular_user.email,
            "username": "anotheruser",
            "first_name": "Another",
            "last_name": "User",
            "password": "password123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code in [400, 409]  # Bad request or conflict

    def test_register_duplicate_username(self, client: TestClient, regular_user: User):
        """Test registration with duplicate username"""
        user_data = {
            "email": "another@test.com",
            "username": regular_user.username,
            "first_name": "Another",
            "last_name": "User",
            "password": "password123",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code in [400, 409]  # Bad request or conflict

    def test_register_invalid_data(self, client: TestClient):
        """Test registration with invalid data"""
        user_data = {
            "email": "invalid-email",
            "username": "ab",  # Too short
            "first_name": "Test",
            "last_name": "User",
            "password": "short",  # Too short
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    def test_refresh_token(
        self, client: TestClient, superuser: User, superuser_data: Dict[str, str]
    ):
        """Test token refresh"""
        # First login to get tokens
        login_data = {
            "username": superuser_data["email"],
            "password": superuser_data["password"],
        }

        login_response = client.post("/api/v1/auth/login", data=login_data)
        login_tokens = login_response.json()

        # Use refresh token to get new access token
        refresh_data = {"refresh_token": login_tokens["refresh_token"]}

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test token refresh with invalid token"""
        refresh_data = {"refresh_token": "invalid_refresh_token"}

        response = client.post("/api/v1/auth/refresh", json=refresh_data)

        assert response.status_code == 401

    def test_protected_endpoint_with_valid_token(
        self, client: TestClient, auth_headers: Dict[str, str]
    ):
        """Test accessing protected endpoint with valid token"""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200

    def test_protected_endpoint_without_token(self, client: TestClient):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client: TestClient):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users/me", headers=headers)

        assert response.status_code == 401

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        # Missing password
        login_data = {"username": "test@test.com"}

        response = client.post("/api/v1/auth/login", data=login_data)

        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing fields"""
        user_data = {
            "email": "test@test.com",
            # Missing required fields
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error
