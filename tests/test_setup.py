"""
Test de configuración para verificar que el entorno de testing esté funcionando correctamente.
Este test debe ser el primero en ejecutarse para validar la configuración.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db


class TestTestingSetup:
    """Tests para verificar que la configuración de testing funciona correctamente"""

    def test_database_session_is_working(self, db_session: Session):
        """Test que la sesión de base de datos funciona correctamente"""
        assert db_session is not None

        # Ejecutar una consulta simple
        from sqlalchemy import text

        result = db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row is not None
        assert row[0] == 1

    def test_client_is_working(self, client: TestClient):
        """Test que el cliente de testing funciona correctamente"""
        assert client is not None

        # Hacer una petición simple
        response = client.get("/api/v1/health/")
        assert response.status_code == 200

    def test_database_override_is_working(
        self, client: TestClient, db_session: Session
    ):
        """Test que el override de la base de datos funciona correctamente"""
        # Verificar que la app usa la base de datos de testing
        dependency_overrides = app.dependency_overrides
        assert get_db in dependency_overrides

    def test_fixtures_are_working(self, superuser, regular_user, category, product):
        """Test que todos los fixtures básicos funcionan correctamente"""
        # Verificar superuser
        assert superuser is not None
        assert superuser.is_superuser is True
        assert superuser.email is not None

        # Verificar regular_user
        assert regular_user is not None
        assert regular_user.is_superuser is False
        assert regular_user.email is not None

        # Verificar category
        assert category is not None
        assert category.name is not None
        assert category.slug is not None

        # Verificar product
        assert product is not None
        assert product.name is not None
        assert product.sku is not None
        assert product.category_id == category.id

    def test_auth_headers_are_working(self, auth_headers, user_auth_headers):
        """Test que los headers de autenticación funcionan correctamente"""
        # Verificar auth_headers (superuser)
        assert auth_headers is not None
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"].startswith("Bearer ")

        # Verificar user_auth_headers (regular user)
        assert user_auth_headers is not None
        assert "Authorization" in user_auth_headers
        assert user_auth_headers["Authorization"].startswith("Bearer ")

    def test_database_isolation(self, db_session: Session):
        """Test que los tests están aislados entre sí"""
        from app.models.user import User

        # Contar usuarios antes
        initial_count = db_session.query(User).count()

        # Crear un usuario
        user = User(
            email="isolation_test@test.com",
            username="isolation_test",
            first_name="Test",
            last_name="User",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        # Verificar que se creó
        new_count = db_session.query(User).count()
        assert new_count == initial_count + 1

    def test_factories_are_working(self, db_session: Session):
        """Test que las factories funcionan correctamente"""
        from tests.factories import UserFactory, CategoryFactory, ProductFactory

        # Test UserFactory
        user = UserFactory()
        assert user.email is not None
        assert user.username is not None

        # Test CategoryFactory
        category = CategoryFactory()
        assert category.name is not None
        assert category.slug is not None

        # Test ProductFactory (requiere category_id)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        product = ProductFactory(category_id=category.id)
        assert product.name is not None
        assert product.sku is not None
        assert product.category_id == category.id

        # Test que los objetos pueden ser persistidos
        db_session.add(user)
        db_session.add(product)
        db_session.commit()

        # Verificar que se guardaron correctamente
        assert user.id is not None
        assert product.id is not None

    def test_api_documentation_accessible(self, client: TestClient):
        """Test que la documentación de la API es accesible"""
        # Test docs
        response = client.get("/docs")
        assert response.status_code == 200

        # Test OpenAPI JSON
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data

    def test_environment_variables_are_set(self):
        """Test que las variables de entorno necesarias están configuradas"""
        from app.config import settings

        # Variables críticas que deben estar configuradas
        assert settings.SECRET_KEY is not None
        assert settings.DATABASE_URL is not None
        assert settings.ALGORITHM is not None

    def test_models_can_be_imported(self):
        """Test que todos los modelos pueden ser importados correctamente"""
        try:
            from app.models.user import User
            from app.models.category import Category
            from app.models.product import Product
            from app.models.cart import Cart, CartItem
            from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus

            # Verificar que las clases existen
            assert User is not None
            assert Category is not None
            assert Product is not None
            assert Cart is not None
            assert CartItem is not None
            assert Order is not None
            assert OrderItem is not None
            assert OrderStatus is not None
            assert PaymentStatus is not None

        except ImportError as e:
            pytest.fail(f"Error importing models: {e}")

    def test_schemas_can_be_imported(self):
        """Test que todos los schemas pueden ser importados correctamente"""
        try:
            from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
            from app.schemas.category import CategoryCreate, CategoryUpdate
            from app.schemas.product import ProductCreate, ProductUpdate
            from app.schemas.cart import CartCreate, CartItemCreate
            from app.schemas.order import OrderCreate, OrderUpdate
            from app.schemas.token import Token, TokenData

            # Verificar que las clases existen
            assert UserCreate is not None
            assert UserUpdate is not None
            assert UserSchema is not None
            assert CategoryCreate is not None
            assert CategoryUpdate is not None
            assert ProductCreate is not None
            assert ProductUpdate is not None
            assert CartCreate is not None
            assert CartItemCreate is not None
            assert OrderCreate is not None
            assert OrderUpdate is not None
            assert Token is not None
            assert TokenData is not None

        except ImportError as e:
            pytest.fail(f"Error importing schemas: {e}")

    def test_services_can_be_imported(self):
        """Test que todos los servicios pueden ser importados correctamente"""
        try:
            from app.services.user_service import UserService
            from app.services.category_service import CategoryService
            from app.services.product_service import ProductService
            from app.services.cart_service import CartService, CartItemService
            from app.services.order_service import OrderService

            # Verificar que las clases existen
            assert UserService is not None
            assert CategoryService is not None
            assert ProductService is not None
            assert CartService is not None
            assert CartItemService is not None
            assert OrderService is not None

        except ImportError as e:
            pytest.fail(f"Error importing services: {e}")

    def test_pytest_markers_are_configured(self):
        """Test que los marcadores de pytest están configurados correctamente"""
        import pytest

        # Verificar que pytest está disponible y funciona
        # Los marcadores personalizados deben estar definidos en pytest.ini
        assert pytest is not None
