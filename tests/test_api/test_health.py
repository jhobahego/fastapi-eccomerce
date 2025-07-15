from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test cases for health check endpoints"""

    def test_health_check_basic(self, client: TestClient):
        """Test basic health check endpoint"""
        response = client.get("/api/v1/health/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_db(self, client: TestClient):
        """Test database health check endpoint"""
        response = client.get("/api/v1/health/db")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_root_redirect(self, client: TestClient):
        """Test root endpoint redirects to docs"""
        response = client.get("/", follow_redirects=False)

        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/docs"

    def test_docs_accessible(self, client: TestClient):
        """Test that API documentation is accessible"""
        response = client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert data["info"]["title"] == "Ecommerce API"
