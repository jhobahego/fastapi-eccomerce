from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Ecommerce API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Backend API for Ecommerce platform"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql://eccomerce_owner:npg_ZG59dIFlOBga@ep-ancient-pine-ac91ogbe-pooler.sa-east-1.aws.neon.tech/eccomerce?sslmode=require"

    # Security
    SECRET_KEY: str = "31c9718c8dcfc793b27d7f7ebd6fff4a530bdf005c193585ed980f763fb1df4acb0e2734fb376a3b4a5069c6291ad5707c2037574d357c27fc1ad1a57121d4e867e51f7da578aed435f08b4945e3f6c1e44be892df667e1391ba509a15ed51a8a29440d4e08478bd271ea60fa02372d94a88b1ad600342874e59db1b8fdbaa7e154fe4f84c57d72a3a5388ea5a59936ee5df3164d240bebdddb2f24668cb9bcd1e43b507e696ce7efc71c6f556fc6d28889990eea53129bfff3c6391f0e7e41d0cf0526b53acf31261f4645db25b98a092d9b2b7dc108de7e9b1320d7407d325fa2c6c02ea18d5ef0337988aca72581dd3ad39c1707757d343e0c367f4a7873d"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
