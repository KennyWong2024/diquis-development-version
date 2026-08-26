import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text, func 
from jose import jwt
from app.api.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest
from app.crud import user as crud_user
from app.core import security
from app.core.logger import custom_logger as logger
from app.core.config import settings
from app.core.limiter import limiter
from app.models.user import User

router = APIRouter()


def enviar_correo_recuperacion(email_destino: str, reset_link: str):
    """
    Modo local: imprime el enlace de recuperación en consola.
    En producción se reemplazaría por un servicio de email real.
    """
    logger.info(f"📧 [LOCAL] Enlace de recuperación de contraseña para {email_destino}:")
    logger.info(f"   🔗 {reset_link}")


@router.post("/registro", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(user_in: UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db=db, user_in=user_in)


@router.post("/login/access-token")
@limiter.limit("5/minute")
def login_access_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud_user.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        logger.warning(f"Intento de login fallido para: {form_data.username}")
        raise HTTPException(status_code=400, detail="Correo electrónico o contraseña incorrectos")
    elif not user.is_active:
        logger.warning(f"Intento de login de usuario inactivo: {form_data.username}")
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=604800, samesite="lax", secure=False)
    
    logger.info(f"Login exitoso (vía Cookies) para: {user.email}")
    return {"mensaje": "Login exitoso"}


@router.post("/login/refresh-token")
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token no encontrado")

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        jti: str = payload.get("jti")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Refresh token inválido")
            
        if jti:
            blacklisted = db.execute(
                text("SELECT 1 FROM app.token_blacklist WHERE token_jti = :jti"), 
                {"jti": jti}
            ).first()
            if blacklisted:
                raise HTTPException(status_code=401, detail="Refresh token revocado (Sesión cerrada)")

    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token expirado o inválido")

    user = crud_user.get_user(db, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo o eliminado")

    new_access_token = security.create_access_token(subject=str(user.id))
    new_refresh_token = security.create_refresh_token(subject=str(user.id))
    
    response.set_cookie(key="access_token", value=new_access_token, httponly=True, max_age=1800, samesite="lax", secure=False)
    response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, max_age=604800, samesite="lax", secure=False)
    
    return {"mensaje": "Tokens actualizados exitosamente"}


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """Invalida AMBOS tokens en la BD y ELIMINA las cookies del navegador."""
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    for token in [access_token, refresh_token]:
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
                jti = payload.get("jti")
                exp = payload.get("exp")
                
                if jti:
                    db.execute(
                        text("INSERT INTO app.token_blacklist (token_jti, expires_at) VALUES (:jti, to_timestamp(:exp)) ON CONFLICT DO NOTHING"),
                        {"jti": jti, "exp": exp}
                    )
            except Exception:
                pass
    
    db.commit()

    response.delete_cookie("access_token", samesite="lax", secure=False)
    response.delete_cookie("refresh_token", samesite="lax", secure=False)
        
    return {"mensaje": "Sesión cerrada y cookies eliminadas"}


@router.post("/forgot-password")
@limiter.limit("3/minute")
def forgot_password(
    request: Request, 
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Solicita un reseteo de contraseña. 
    Se utiliza rate limiting estricto y respuesta ambigua para prevenir enumeración.
    En modo local, el enlace se imprime en la consola del servidor.
    """
    mensaje_exito = {"mensaje": "Si el correo está registrado, en breve recibirás las instrucciones para restablecer tu contraseña."}

    user = db.query(User).filter(User.email == body.email).first()
    
    if not user or not user.is_active:
        logger.warning(f"Intento de recuperación para cuenta inexistente/inactiva: {body.email}")
        return mensaje_exito

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=20)
    
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        db.execute(
            text("""
                INSERT INTO app.password_resets (user_id, token_hash, expires_at, ip_address, user_agent)
                VALUES (:user_id, :token_hash, :expires_at, :ip_address, :user_agent)
            """),
            {
                "user_id": user.id, 
                "token_hash": token_hash, 
                "expires_at": expires_at,
                "ip_address": client_ip,
                "user_agent": user_agent
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error guardando token de reseteo en DB: {e}")
        return mensaje_exito 

    reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={raw_token}"
    background_tasks.add_task(enviar_correo_recuperacion, user.email, reset_link)

    return mensaje_exito


@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Ejecuta el cambio de contraseña validando el token.
    """
    token_hash = hashlib.sha256(body.token.encode()).hexdigest()

    reset_record = db.execute(
        text("""
            SELECT id, user_id, expires_at, used_at 
            FROM app.password_resets 
            WHERE token_hash = :token_hash
        """),
        {"token_hash": token_hash}
    ).fetchone()

    if not reset_record:
        raise HTTPException(status_code=400, detail="Token inválido.")
    
    if reset_record.used_at is not None:
         raise HTTPException(status_code=400, detail="Este enlace ya fue utilizado.")
        
    expires_at = reset_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="El enlace ha expirado. Solicita uno nuevo.")

    user = crud_user.get_user(db, user_id=str(reset_record.user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")

    try:
        hashed_password = security.get_password_hash(body.new_password)
        
        db.execute(
            text("""
                UPDATE app.sso_providers 
                SET access_token_hash = :hp, linked_at = NOW() 
                WHERE user_id = :uid AND provider = 'local'
            """),
            {"hp": hashed_password, "uid": user.id}
        )

        db.execute(
            text("UPDATE app.password_resets SET used_at = NOW() WHERE id = :rid"),
            {"rid": reset_record.id}
        )
        
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error reseteando contraseña: {e}")
        raise HTTPException(status_code=500, detail="Error interno.")

    return {"mensaje": "Contraseña actualizada exitosamente."}