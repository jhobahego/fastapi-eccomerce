from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
import logging

from ....database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def health_check():
    """Health check básico de la aplicación"""
    return {"status": "healthy"}


@router.get("/db")
def health_check_db():
    """Health check específico para la base de datos"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Error en health check de DB: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )
