from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logger import custom_logger as logger
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_access_token(subject: Union[str, Any]) -> str:
    """Crea un token firmado con el ID del usuario"""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {"exp": expire, "sub": str(subject), "type": "access", "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    logger.debug(f"Nuevo token de acceso generado para sujeto: {subject}")
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Crea un token de refresco de larga duración"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh", "jti": str(uuid.uuid4())}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña escrita con la encriptada en la DB"""
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.debug("Verificación de contraseña exitosa")
    else:
        logger.warning("Intento de verificación de contraseña fallido")
    return is_valid

def get_password_hash(password: str) -> str:
    """Convierte una contraseña en un hash ilegible para guardar en DB"""
    return pwd_context.hash(password)

def verify_password_dummy() -> None:
    """Ejecuta un ciclo de verificación ficticio (dummy) para igualar tiempos de respuesta"""
    pwd_context.dummy_verify()