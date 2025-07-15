import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.category import Category
from app.models.product import Product

# Configuración de base de datos para tests
USE_POSTGRES_FOR_TESTS = os.getenv("USE_POSTGRES_FOR_TESTS", "false").lower() == "true"

if USE_POSTGRES_FOR_TESTS:
    # PostgreSQL para tests
    SQLALCHEMY_DATABASE_URL = (
        "postgresql://test_user:test_password@localhost:5433/ecommerce_test"
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
else:
    # SQLite para tests rápidos (comportamiento actual)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine for testing"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create test client with database session override"""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def superuser_data() -> Dict[str, Any]:
    """Test superuser data"""
    return {
        "email": "admin@test.com",
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "password": "test123456",
        "is_superuser": True,
        "is_active": True,
    }


@pytest.fixture
def regular_user_data() -> Dict[str, Any]:
    """Test regular user data"""
    return {
        "email": "user@test.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "test123456",
        "is_superuser": False,
        "is_active": True,
    }


@pytest.fixture
def superuser(db_session: Session, superuser_data: Dict[str, Any]) -> User:
    """Create test superuser"""
    user = User(
        email=superuser_data["email"],
        username=superuser_data["username"],
        first_name=superuser_data["first_name"],
        last_name=superuser_data["last_name"],
        hashed_password=get_password_hash(superuser_data["password"]),
        is_superuser=superuser_data["is_superuser"],
        is_active=superuser_data["is_active"],
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session: Session, regular_user_data: Dict[str, Any]) -> User:
    """Create test regular user"""
    user = User(
        email=regular_user_data["email"],
        username=regular_user_data["username"],
        first_name=regular_user_data["first_name"],
        last_name=regular_user_data["last_name"],
        hashed_password=get_password_hash(regular_user_data["password"]),
        is_superuser=regular_user_data["is_superuser"],
        is_active=regular_user_data["is_active"],
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def category_data() -> Dict[str, Any]:
    """Test category data"""
    return {
        "name": "Electronics",
        "description": "Electronic devices and accessories",
        "slug": "electronics",
        "is_active": True,
        "sort_order": 1,
    }


@pytest.fixture
def category(db_session: Session, category_data: Dict[str, Any]) -> Category:
    """Create test category"""
    category = Category(**category_data)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def product_data(category: Category) -> Dict[str, Any]:
    """Test product data"""
    return {
        "name": "Test Product",
        "description": "A test product for testing",
        "short_description": "Test product",
        "slug": "test-product",
        "sku": "TEST-001",
        "price": 99.99,
        "stock_quantity": 10,
        "min_stock_level": 5,
        "is_active": True,
        "is_featured": False,
        "category_id": category.id,
    }


@pytest.fixture
def product(db_session: Session, product_data: Dict[str, Any]) -> Product:
    """Create test product"""
    product = Product(**product_data)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def auth_headers(
    client: TestClient, superuser: User, superuser_data: Dict[str, Any]
) -> Dict[str, str]:
    """Get authentication headers for superuser"""
    login_data = {
        "username": superuser_data["email"],
        "password": superuser_data["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_headers(
    client: TestClient, regular_user: User, regular_user_data: Dict[str, Any]
) -> Dict[str, str]:
    """Get authentication headers for regular user"""
    login_data = {
        "username": regular_user_data["email"],
        "password": regular_user_data["password"],
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
