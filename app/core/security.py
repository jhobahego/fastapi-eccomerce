from datetime import datetime, timedelta
from typing import Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, DisconnectionError
import logging

from ..config import settings
from ..database import get_db
from ..models.user import User

logger = logging.getLogger(__name__)


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def create_access_token(
    subject: Union[str, int], expires_delta: Optional[timedelta] = None
) -> str:
    """Crear token de acceso JWT"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    if settings.JWT_DEBUG:
        logger.info(f"Token de acceso creado para usuario {subject}, expira: {expire}")

    return encoded_jwt


def create_refresh_token(subject: Union[str, int]) -> str:
    """Crear token de refresco"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    if settings.JWT_DEBUG:
        logger.info(f"Refresh token creado para usuario {subject}, expira: {expire}")

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[str]:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None


def verify_token_with_type(token: str, expected_type: str = "access") -> Optional[str]:
    """Verificar token JWT y validar su tipo (access/refresh)"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        user_id: Optional[str] = payload.get("sub")
        token_type: Optional[str] = payload.get("type")

        if user_id is None or token_type != expected_type:
            if settings.JWT_DEBUG:
                logger.warning(
                    f"Token inválido: user_id={user_id}, type={token_type}, expected={expected_type}"
                )
            return None

        if settings.JWT_DEBUG:
            logger.info(f"Token {expected_type} válido para usuario {user_id}")

        return user_id
    except JWTError as e:
        if settings.JWT_DEBUG:
            logger.warning(f"Error de JWT al verificar token {expected_type}: {e}")
        return None


def verify_refresh_token(token: str) -> Optional[str]:
    """Verificar específicamente un refresh token"""
    return verify_token_with_type(token, "refresh")


def get_user_from_refresh_token(refresh_token: str, db: Session) -> Optional[User]:
    """Obtener usuario desde refresh token con manejo de errores de DB"""
    user_id = verify_refresh_token(refresh_token)
    if user_id is None:
        return None

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None or not user.is_active:
            return None
        return user

    except (OperationalError, DisconnectionError) as e:
        logger.error(
            f"Error de conexión a base de datos al obtener usuario desde refresh token: {e}"
        )
        # Intentar reconectar y reintentar una vez
        try:
            db.rollback()
            user = db.query(User).filter(User.id == user_id).first()
            if user is None or not user.is_active:
                return None
            return user
        except Exception as retry_error:
            logger.error(
                f"Error en reintento de conexión con refresh token: {retry_error}"
            )
            return None

    except Exception as e:
        logger.error(f"Error inesperado al obtener usuario desde refresh token: {e}")
        return None


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """Obtener usuario actual desde token JWT con manejo de errores de DB"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = verify_token_with_type(token, "access")
    if user_id is None:
        raise credentials_exception

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return user

    except (OperationalError, DisconnectionError) as e:
        logger.error(f"Error de conexión a base de datos al obtener usuario: {e}")
        # Intentar reconectar y reintentar una vez
        try:
            db.rollback()
            user = db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise credentials_exception

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )

            return user
        except Exception as retry_error:
            logger.error(f"Error en reintento de conexión: {retry_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection error. Please try again later.",
            )

    except Exception as e:
        logger.error(f"Error inesperado al obtener usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """Obtener superusuario actual"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
