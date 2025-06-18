from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Ecommerce API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend API for Ecommerce platform"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 480 min => 8 horas para desarrollo
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Debug JWT
    JWT_DEBUG: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # File uploads
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_IMAGE_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Admin User (for initial setup)
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
