from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core import security
from app.db.session import SessionLocal
from app.core.logger import custom_logger as logger
from app.crud import user as crud_user

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    logger.debug("Abriendo nueva sesión de DB para la petición")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Sesión de DB cerrada")

def get_token_from_cookie(request: Request) -> str:
    """Extrae el token JWT directamente de la cookie HttpOnly."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado (Cookie no encontrada)"
        )
    return token

def get_current_user(
    token: str = Depends(get_token_from_cookie), 
    db: Session = Depends(get_db)
) -> str:
    """Valida el token y extrae el ID del usuario verificando la lista negra."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Intento de acceso rechazado: Token sin subject (sub).")
            raise HTTPException(status_code=401, detail="Token inválido")

        jti = payload.get("jti")
        if jti:
            blacklisted = db.execute(
                text("SELECT 1 FROM app.token_blacklist WHERE token_jti = :jti"), 
                {"jti": jti}
            ).first()

            if blacklisted:
                raise HTTPException(status_code=401, detail="Token revocado (Sesión cerrada)")

    except (JWTError, ValidationError) as e:
        logger.warning(f"Intento de acceso rechazado: Fallo de validación de token -> {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el acceso"
        )
    
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    return str(user.id)

def get_db_with_rls(
    user_id: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
) -> Session:
    """Inyecta el user_id en la sesión de PostgreSQL para activar RLS."""
    try:
        db.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"), 
            {"user_id": user_id}
        )
        logger.debug(f"Seguridad RLS activada en DB para el usuario: {user_id}")
        return db
    except Exception as e:
        logger.error(f"Fallo crítico al configurar RLS en base de datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno de seguridad")