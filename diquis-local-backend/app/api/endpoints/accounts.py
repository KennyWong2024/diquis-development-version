from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import dependencies as deps
from app.crud import account as crud_account
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate

router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
def read_accounts(
    db: Session = Depends(deps.get_db_with_rls),
    current_user_id: str = Depends(deps.get_current_user)
):
    accounts = crud_account.get_accounts(db, user_id=current_user_id)
    return accounts

@router.post("/", response_model=AccountResponse)
def create_account(
    *,
    db: Session = Depends(deps.get_db_with_rls),
    account_in: AccountCreate,
    current_user_id: str = Depends(deps.get_current_user)
):
    account = crud_account.create_account(db, user_id=current_user_id, obj_in=account_in)
    return account

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    *,
    db: Session = Depends(deps.get_db_with_rls),
    account_id: str,
    account_in: AccountUpdate,
    current_user_id: str = Depends(deps.get_current_user)
):
    try:
        account = crud_account.update_account(db, user_id=current_user_id, account_id=account_id, obj_in=account_in)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada o sin permisos")
        return account
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{account_id}")
def delete_account(
    *,
    db: Session = Depends(deps.get_db_with_rls),
    account_id: str,
    current_user_id: str = Depends(deps.get_current_user)
):
    try:
        account = crud_account.delete_account(db, user_id=current_user_id, account_id=account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada o sin permisos")
        return {"status": "success", "detail": "Cuenta eliminada correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))