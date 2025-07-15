from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, DisconnectionError
import logging
from .config import settings
from .api.api_v1.api import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# Middleware para manejo de errores de base de datos
@app.middleware("http")
async def db_error_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except (OperationalError, DisconnectionError) as e:
        logger.error(f"Error de conexión a base de datos: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Database connection error. Please try again later.",
                "error_type": "database_connection_error",
            },
        )
    except Exception as e:
        logger.error(f"Error no manejado: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_type": "internal_server_error",
            },
        )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    """Redirección a la documentación de la API"""
    return RedirectResponse(url="/docs")


# Soporte para ejecución directa con puerto dinámico
if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    workers = 1 if settings.ENVIRONMENT == "development" else 4

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        reload=settings.ENVIRONMENT == "development",
    )
