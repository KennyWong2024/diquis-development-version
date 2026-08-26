from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.api.dependencies import get_db_with_rls, get_current_user
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionResponse, 
    BalanceResponse, 
    TransactionItemCreate, 
    TransactionItemResponse, 
    TransactionDetailResponse,
    TransactionUpdate
)
from app.crud import transaction as crud_transaction
from app.core.logger import custom_logger as logger

router = APIRouter()

@router.get("/balance", response_model=BalanceResponse)
def read_wallet_balance(
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    result = crud_transaction.get_wallet_balance_and_metrics(db, user_id=current_user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Billetera Principal no encontrada")
    return result


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_new_transaction(
    transaction_in: TransactionCreate,
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    try:
        return crud_transaction.create_transaction(db, user_id=current_user_id, obj_in=transaction_in)
    
    except SQLAlchemyError as e:
        db.rollback() 
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "chk_no_negative_balance" in error_msg:
            logger.warning(f"Fondos insuficientes: Usuario {current_user_id} intentó gastar más de lo disponible en una cuenta restringida.")
            raise HTTPException(
                status_code=400, 
                detail="Fondos insuficientes. No puedes realizar esta transacción porque la cuenta seleccionada no permite saldos negativos."
            )
            
        logger.error(f"Error de integridad al crear transacción: {error_msg}")
        raise HTTPException(
            status_code=400, 
            detail="Error procesando la transacción en la base de datos. Verifica la información enviada."
        )


@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user),
    account_id: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50
):
    return crud_transaction.get_transactions(
        db, 
        user_id=current_user_id, 
        limit=limit, 
        start_date=start_date, 
        end_date=end_date,
        account_id=str(account_id) if account_id else None
    )


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
def read_transaction_detail(
    transaction_id: str,
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    transaction = crud_transaction.get_transaction_detail(db, user_id=current_user_id, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_existing_transaction(
    transaction_id: UUID,
    transaction_in: TransactionUpdate,
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    try:
        transaction = crud_transaction.update_transaction(
            db, user_id=current_user_id, transaction_id=str(transaction_id), obj_in=transaction_in
        )
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction
        
    except SQLAlchemyError as e:
        db.rollback() 
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "chk_no_negative_balance" in error_msg:
            logger.warning(f"Intento de saldo negativo bloqueado en edición para el usuario {current_user_id}")
            raise HTTPException(
                status_code=400, 
                detail="Esta operación dejaría tu cuenta en números rojos. Si quieres mover o alterar este ingreso, primero debes reasignar a otra cuenta los gastos que pagaste con este dinero."
            )
            
        logger.error(f"Error de base de datos en PUT: {error_msg}")
        raise HTTPException(status_code=400, detail="Error procesando la actualización en la base de datos.")


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    try:
        result = crud_transaction.delete_transaction(db, user_id=current_user_id, transaction_id=str(transaction_id))
        if not result:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return None
        
    except SQLAlchemyError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "chk_no_negative_balance" in error_msg:
            logger.warning(f"Intento de saldo negativo bloqueado en eliminación para el usuario {current_user_id}")
            raise HTTPException(
                status_code=400, 
                detail="No puedes eliminar este ingreso porque tu cuenta quedaría en negativo. Elimina o mueve primero los gastos asociados a esta cuenta."
            )
            
        logger.error(f"Error de base de datos en DELETE: {error_msg}")
        raise HTTPException(status_code=400, detail="No se pudo eliminar la transacción debido a dependencias en el sistema.")


@router.post("/{transaction_id}/items", response_model=TransactionItemResponse, status_code=status.HTTP_201_CREATED)
def add_transaction_item(
    transaction_id: str,
    item_in: TransactionItemCreate,
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    return crud_transaction.add_item_to_transaction(
        db, user_id=current_user_id, transaction_id=transaction_id, item_in=item_in
    )