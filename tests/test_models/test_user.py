import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import get_password_hash, verify_password


class TestUserModel:
    """Test cases for User model"""

    def test_create_user(self, db_session: Session):
        """Test creating a user"""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_password_hashing(self):
        """Test password hashing functionality"""
        password = "mysecretpassword"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_user_full_name_property(self, db_session: Session):
        """Test full_name property"""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="John",
            last_name="Doe",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user)
        db_session.commit()

        assert user.full_name == "John Doe"

    def test_user_unique_email(self, db_session: Session):
        """Test that email must be unique"""
        user1 = User(
            email="test@example.com",
            username="testuser1",
            first_name="Test",
            last_name="User1",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            email="test@example.com",
            username="testuser2",
            first_name="Test",
            last_name="User2",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError will be raised
            db_session.commit()

    def test_user_unique_username(self, db_session: Session):
        """Test that username must be unique"""
        user1 = User(
            email="test1@example.com",
            username="testuser",
            first_name="Test",
            last_name="User1",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            email="test2@example.com",
            username="testuser",
            first_name="Test",
            last_name="User2",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # IntegrityError will be raised
            db_session.commit()

    def test_user_defaults(self, db_session: Session):
        """Test default values for user fields"""
        user = User(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword"),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is True
        assert user.is_superuser is False
        assert user.phone is None
        assert user.address is None
        assert user.city is None
        assert user.country is None
        assert user.postal_code is None
