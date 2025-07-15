import pytest
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
from tests.factories import UserFactory


class TestUserService:
    """Test cases for UserService"""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation"""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )

        user = user_service.create(user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.hashed_password != "testpassword123"  # Should be hashed

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test creating user with duplicate email"""
        user_service = UserService(db_session)

        # Create first user
        user_data1 = UserCreate(
            email="test@example.com",
            username="testuser1",
            first_name="Test",
            last_name="User1",
            password="testpassword123",
        )
        user_service.create(user_data1)

        # Try to create second user with same email
        user_data2 = UserCreate(
            email="test@example.com",
            username="testuser2",
            first_name="Test",
            last_name="User2",
            password="testpassword123",
        )

        with pytest.raises(Exception):  # Should raise exception for duplicate email
            user_service.create(user_data2)

    def test_get_user_by_email(self, db_session: Session):
        """Test getting user by email"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        created_user = user_service.create(user_data)

        # Get user by email
        found_user = user_service.get_by_email("test@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "test@example.com"

    def test_get_user_by_email_not_found(self, db_session: Session):
        """Test getting user by email when not found"""
        user_service = UserService(db_session)

        found_user = user_service.get_by_email("nonexistent@example.com")

        assert found_user is None

    def test_get_user_by_username(self, db_session: Session):
        """Test getting user by username"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        created_user = user_service.create(user_data)

        # Get user by username
        found_user = user_service.get_by_username("testuser")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "testuser"

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        user_service.create(user_data)

        # Authenticate user
        authenticated_user = user_service.authenticate_user(
            "test@example.com", "testpassword123"
        )

        assert authenticated_user is not None
        assert authenticated_user.email == "test@example.com"

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test user authentication with wrong password"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        user_service.create(user_data)

        # Try to authenticate with wrong password
        authenticated_user = user_service.authenticate_user(
            "test@example.com", "wrongpassword"
        )

        assert authenticated_user is None

    def test_authenticate_user_not_found(self, db_session: Session):
        """Test user authentication when user not found"""
        user_service = UserService(db_session)

        # Try to authenticate non-existent user
        authenticated_user = user_service.authenticate_user(
            "nonexistent@example.com", "password"
        )

        assert authenticated_user is None

    def test_update_user(self, db_session: Session):
        """Test updating user"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        created_user = user_service.create(user_data)

        # Update user
        update_data = UserUpdate(
            first_name="Updated", last_name="Name", phone="123-456-7890"
        )
        updated_user = user_service.update(created_user.id, update_data)

        assert updated_user is not None
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.phone == "123-456-7890"
        assert updated_user.email == "test@example.com"  # Unchanged

    def test_delete_user(self, db_session: Session):
        """Test deleting user"""
        user_service = UserService(db_session)

        # Create user
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpassword123",
        )
        created_user = user_service.create(user_data)

        # Delete user
        deleted_user = user_service.delete(created_user.id)

        assert deleted_user is not None
        assert deleted_user.id == created_user.id

        # Verify user is deleted
        found_user = user_service.get_by_id(created_user.id, raise_404=False)
        assert found_user is None

    def test_get_multi_users(self, db_session: Session):
        """Test getting multiple users"""
        user_service = UserService(db_session)

        # Create multiple users
        for i in range(5):
            user_data = UserCreate(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                first_name=f"Test{i}",
                last_name="User",
                password="testpassword123",
            )
            user_service.create(user_data)

        # Get multiple users
        users = user_service.get_multi(skip=0, limit=10)

        assert len(users) == 5
        assert all(isinstance(user, User) for user in users)

    def test_user_service_with_factory(self, db_session: Session):
        """Test user service using factory"""
        user_service = UserService(db_session)

        # Create user using factory
        user = UserFactory()
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Test service methods
        found_user = user_service.get_by_id(user.id)
        assert found_user is not None
        assert found_user.email == user.email
