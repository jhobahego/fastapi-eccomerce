"""
Utilidades para manejo de base de datos con reintentos y manejo de errores
"""

import time
import logging
from typing import Callable, Any
from functools import wraps
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def db_retry(max_retries: int = 3, delay: float = 1.0):
    """
    Decorador para reintentar operaciones de base de datos en caso de errores de conexión
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_exception = e
                    logger.warning(
                        f"Intento {attempt + 1}/{max_retries} falló para {func.__name__}: {e}"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(delay * (2**attempt))  # Backoff exponencial
                        continue
                    else:
                        logger.error(
                            f"Todos los intentos fallaron para {func.__name__}: {e}"
                        )
                        raise
                except Exception as e:
                    # Para otros errores, no reintentamos
                    logger.error(f"Error no recuperable en {func.__name__}: {e}")
                    raise

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def test_db_connection(db: Session) -> bool:
    """
    Prueba la conexión a la base de datos
    """
    from sqlalchemy import text

    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Error al probar conexión DB: {e}")
        return False


def ensure_db_connection(db: Session) -> None:
    """
    Asegura que la conexión a la base de datos esté activa
    """
    if not test_db_connection(db):
        logger.info("Intentando reconectar a la base de datos...")
        db.rollback()
        # Forzar una nueva conexión
        db.close()
        raise OperationalError(
            "Database connection lost", None, BaseException("Reconnecting...")
        )
