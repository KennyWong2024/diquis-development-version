from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.user import User
from app.models.auth import SSOProvider
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.logger import custom_logger as logger
from app.core.security import verify_password, verify_password_dummy

def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    logger.debug(f"Buscando usuario por correo: {email}")
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    user_data = user_in.model_dump(exclude={"password"})
    
    db_user = User(**user_data)
    
    try:
        db.add(db_user)
        db.flush()
        
        hashed_password = get_password_hash(user_in.password)
        
        db_sso = SSOProvider(
            user_id=db_user.id,
            provider='local',
            provider_user_id=user_in.email,
            access_token_hash=hashed_password
        )
        db.add(db_sso)
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Usuario registrado exitosamente: {db_user.email}")
        return db_user
        
    except IntegrityError:
        db.rollback()
        logger.warning(f"Intento de registro con correo duplicado: {user_in.email}")
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        verify_password_dummy()
        return None
        
    sso = db.query(SSOProvider).filter(
        SSOProvider.user_id == user.id,
        SSOProvider.provider == 'local'
    ).first()
    
    if not sso:
        verify_password_dummy()
        return None
        
    if not verify_password(password, sso.access_token_hash):
        return None
        
    return user

def update_user(db: Session, db_user: User, update_data: dict) -> User:
    """Actualiza dinámicamente los campos permitidos del usuario."""
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    logger.info(f"Perfil actualizado para usuario: {db_user.id}")
    return db_user

def change_user_password(db: Session, user_id: str, current_password: str, new_password: str) -> bool:
    """Valida la contraseña actual y actualiza el hash en SSOProvider."""
    sso = db.query(SSOProvider).filter(
        SSOProvider.user_id == user_id,
        SSOProvider.provider == 'local'
    ).first()

    if not sso:
        logger.warning(f"Intento de cambio de clave fallido: No hay SSO local para {user_id}")
        raise HTTPException(status_code=404, detail="No se encontró un método de acceso local para este usuario.")

    if not verify_password(current_password, sso.access_token_hash):
        logger.warning(f"Intento de cambio de clave fallido: Contraseña actual incorrecta para {user_id}")
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    try:
        new_hash = get_password_hash(new_password)
        sso.access_token_hash = new_hash
        db.commit()
        logger.info(f"Contraseña actualizada exitosamente para usuario: {user_id}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error interno al actualizar la contraseña para {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar la contraseña.")

def delete_user_account(db: Session, user_id: str, current_password: str) -> bool:
    """
    Ejecuta un Hard Delete del usuario validando primero su contraseña.
    Al borrar el usuario, PostgreSQL limpiará todas sus tablas hijas por ON DELETE CASCADE.
    """
    sso = db.query(SSOProvider).filter(
        SSOProvider.user_id == user_id,
        SSOProvider.provider == 'local'
    ).first()

    if not sso:
        logger.warning(f"Intento de eliminación fallido: No hay SSO local para {user_id}")
        raise HTTPException(status_code=404, detail="No se encontró un método de acceso local para este usuario.")

    if not verify_password(current_password, sso.access_token_hash):
        logger.warning(f"Intento de eliminación fallido: Contraseña incorrecta para {user_id}")
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    try:
        db.delete(user)
        db.commit()
        logger.info(f"💣 HARD DELETE ejecutado: Usuario {user_id} y todos sus datos han sido eliminados.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error crítico al ejecutar Hard Delete para usuario {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar la cuenta.")