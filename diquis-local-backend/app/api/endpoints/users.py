from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt
from app.core.config import settings
from app.core import security
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserResponse, UserChangePassword, UserUpdateProfile, UserDeleteAccount
from app.crud import user as crud_user

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    user = crud_user.get_user(db, user_id=current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/me", response_model=UserResponse)
def update_user_me(
    user_in: UserUpdateProfile,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    user = crud_user.get_user(db, user_id=current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = user_in.model_dump(exclude_unset=True)
    updated_user = crud_user.update_user(db=db, db_user=user, update_data=update_data)
    return updated_user

@router.post("/me/change-password")
def change_password_me(
    pwd_in: UserChangePassword,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    crud_user.change_user_password(
        db=db, 
        user_id=current_user_id, 
        current_password=pwd_in.current_password, 
        new_password=pwd_in.new_password
    )
    
    return {"detail": "Contraseña actualizada exitosamente"}

@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_account_me(
    request: Request,
    response: Response,
    payload: UserDeleteAccount,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user)
):
    crud_user.delete_user_account(
        db=db, 
        user_id=current_user_id, 
        current_password=payload.current_password
    )

    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    for token in [access_token, refresh_token]:
        if token:
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
                jti = decoded.get("jti")
                exp = decoded.get("exp")
                
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

    return {"detail": "Cuenta eliminada permanentemente. Todo tu historial financiero ha sido borrado."}