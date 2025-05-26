from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from typing import Generator
import redis
import logging

from .config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy setup with improved connection handling
engine_kwargs = {
    "echo": settings.DEBUG,
    "pool_pre_ping": True,  # Verifica conexiones antes de usarlas
    "pool_recycle": 300,  # Recicla conexiones cada 5 minutos
    "pool_timeout": 20,  # Timeout para obtener conexión del pool
    "max_overflow": 0,  # No permite conexiones extras
}

if "sqlite" in settings.DATABASE_URL:
    engine_kwargs.update(
        {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
    )
else:
    # Para PostgreSQL con mejor manejo de conexiones
    engine_kwargs.update(
        {
            "poolclass": QueuePool,
            "pool_size": 5,  # Número de conexiones en el pool
            "connect_args": {
                "connect_timeout": 10,
                "application_name": settings.PROJECT_NAME,
            },
        }
    )

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Redis setup
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de base de datos con manejo de errores"""
    from sqlalchemy import text

    db = SessionLocal()
    try:
        # Verifica la conexión antes de usarla
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.error(f"Error en conexión a base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_redis() -> redis.Redis:
    """Dependency para obtener cliente Redis"""
    return redis_client
