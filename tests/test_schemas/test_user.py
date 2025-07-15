import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate, PasswordChange


class TestUserSchemas:
    """Test cases for User schemas"""

    def test_user_create_valid(self):
        """Test valid UserCreate schema"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }
        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.password == "testpassword123"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email"""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_user_create_password_too_short(self):
        """Test UserCreate with password too short"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "short",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Password must be at least 8 characters long" in str(exc_info.value)

    def test_user_create_username_too_short(self):
        """Test UserCreate with username too short"""
        user_data = {
            "email": "test@example.com",
            "username": "ab",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Username must be at least 3 characters long" in str(exc_info.value)

    def test_user_create_username_not_alphanumeric(self):
        """Test UserCreate with non-alphanumeric username"""
        user_data = {
            "email": "test@example.com",
            "username": "test-user!",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        assert "Username must be alphanumeric" in str(exc_info.value)

    def test_user_update_valid(self):
        """Test valid UserUpdate schema"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "123-456-7890",
            "address": "123 Main St",
            "city": "Test City",
            "country": "Test Country",
            "postal_code": "12345",
        }
        user_update = UserUpdate(**update_data)

        assert user_update.first_name == "Updated"
        assert user_update.last_name == "Name"
        assert user_update.phone == "123-456-7890"
        assert user_update.address == "123 Main St"
        assert user_update.city == "Test City"
        assert user_update.country == "Test Country"
        assert user_update.postal_code == "12345"

    def test_user_update_partial(self):
        """Test partial UserUpdate schema"""
        update_data = {
            "first_name": "Updated",
        }
        user_update = UserUpdate(**update_data)

        assert user_update.first_name == "Updated"
        assert user_update.last_name is None
        assert user_update.phone is None

    def test_password_change_valid(self):
        """Test valid PasswordChange schema"""
        password_data = {
            "current_password": "oldpassword123",
            "new_password": "newpassword123",
        }
        password_change = PasswordChange(**password_data)

        assert password_change.current_password == "oldpassword123"
        assert password_change.new_password == "newpassword123"

    def test_password_change_new_password_too_short(self):
        """Test PasswordChange with new password too short"""
        password_data = {
            "current_password": "oldpassword123",
            "new_password": "short",
        }

        with pytest.raises(ValidationError) as exc_info:
            PasswordChange(**password_data)

        assert "Password must be at least 8 characters long" in str(exc_info.value)

    def test_user_create_with_optional_fields(self):
        """Test UserCreate with optional fields"""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpassword123",
            "phone": "123-456-7890",
            "address": "123 Main St",
            "city": "Test City",
            "country": "Test Country",
            "postal_code": "12345",
        }
        user = UserCreate(**user_data)

        assert user.phone == "123-456-7890"
        assert user.address == "123 Main St"
        assert user.city == "Test City"
        assert user.country == "Test Country"
        assert user.postal_code == "12345"
