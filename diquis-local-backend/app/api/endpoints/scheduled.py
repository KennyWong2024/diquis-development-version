from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import dependencies as deps
from app.crud import scheduled as crud_scheduled
from app.crud import account as crud_account
from app.schemas.scheduled import ScheduledCreate, ScheduledResponse, ScheduledExecute, ScheduledUpdate
from app.services.schedule_engine import generate_projections
from app.services.fx_service import get_latest_rates_map

router = APIRouter()

def _hydrate_auto_execute_flag(db: Session, user_id: str, schedules: list):
    accounts = crud_account.get_accounts(db, user_id=user_id)
    acc_currency_map = {acc.id: acc.currency for acc in accounts}
    
    for sched in schedules:
        acc_currency = acc_currency_map.get(sched.account_id)
        setattr(sched, 'can_auto_execute', sched.currency == acc_currency)
    return schedules

@router.get("/", response_model=List[ScheduledResponse])
def get_active_schedules(db: Session = Depends(deps.get_db_with_rls), current_user_id: str = Depends(deps.get_current_user)):
    schedules = crud_scheduled.get_active_schedules(db, user_id=current_user_id)
    return _hydrate_auto_execute_flag(db, current_user_id, schedules)

@router.get("/pending", response_model=List[ScheduledResponse])
def get_pending_tray(db: Session = Depends(deps.get_db_with_rls), current_user_id: str = Depends(deps.get_current_user)):
    schedules = crud_scheduled.get_pending_tray(db, user_id=current_user_id)
    return _hydrate_auto_execute_flag(db, current_user_id, schedules)

@router.post("/", response_model=ScheduledResponse)
def create_scheduled_transaction(
    sched_in: ScheduledCreate,
    db: Session = Depends(deps.get_db_with_rls), 
    current_user_id: str = Depends(deps.get_current_user)
):
    if sched_in.auto_execute:
        accounts = crud_account.get_accounts(db, user_id=current_user_id)
        target_account = next((a for a in accounts if str(a.id) == str(sched_in.account_id)), None)
        if target_account and target_account.currency != sched_in.currency:
            raise HTTPException(
                status_code=400, 
                detail="No se puede auto-ejecutar una transacción con divisas cruzadas. Desactiva la auto-ejecución."
            )
            
    sched = crud_scheduled.create_schedule(db, user_id=current_user_id, obj_in=sched_in)
    return _hydrate_auto_execute_flag(db, current_user_id, [sched])[0]

@router.post("/{sched_id}/execute")
def execute_scheduled_transaction(
    sched_id: str,
    execution_data: ScheduledExecute,
    db: Session = Depends(deps.get_db_with_rls), 
    current_user_id: str = Depends(deps.get_current_user)
):
    try:
        tx = crud_scheduled.execute_scheduled(db, user_id=current_user_id, sched_id=sched_id, execution_data=execution_data)
        db.commit() 
        return {"status": "success", "transaction_id": tx.id}
    except ValueError as e:
        db.rollback() 
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{sched_id}/skip")
def skip_scheduled_transaction(
    sched_id: str,
    db: Session = Depends(deps.get_db_with_rls), 
    current_user_id: str = Depends(deps.get_current_user)
):
    try:
        crud_scheduled.skip_scheduled(db, user_id=current_user_id, sched_id=sched_id)
        return {"status": "success", "message": "Ciclo saltado con éxito"}
    except ValueError as e:
        db.rollback() 
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projections")
def get_cashflow_projections(
    days: int = 15,
    db: Session = Depends(deps.get_db_with_rls), 
    current_user_id: str = Depends(deps.get_current_user)
):
    accounts = crud_account.get_accounts(db, user_id=current_user_id)
    
    from app.crud.user import get_user
    user = get_user(db, current_user_id)
    
    total_balance = sum(float(acc.current_balance) for acc in accounts)
    schedules = crud_scheduled.get_active_schedules(db, user_id=current_user_id)
    
    rates_map = get_latest_rates_map(db, target_currency=user.default_currency)
    projections = generate_projections(
        current_total_balance=total_balance, 
        account_currency=user.default_currency,
        schedules=schedules, 
        rates_map=rates_map,
        days=days
    )
    
    return {
        "current_balance": total_balance,
        "days_projected": days,
        "timeline": projections
    }

@router.put("/{sched_id}", response_model=ScheduledResponse)
def update_scheduled_transaction(
    sched_id: str,
    sched_in: ScheduledUpdate,
    db: Session = Depends(deps.get_db_with_rls),
    current_user_id: str = Depends(deps.get_current_user)
):
    if sched_in.auto_execute:
        accounts = crud_account.get_accounts(db, user_id=current_user_id)
        current_sched = crud_scheduled.get_active_schedules(db, user_id=current_user_id) 
        target_sched = next((s for s in current_sched if str(s.id) == str(sched_id)), None)
        
        if target_sched:
            acc_id = sched_in.account_id or target_sched.account_id
            currency = sched_in.currency or target_sched.currency
            target_account = next((a for a in accounts if str(a.id) == str(acc_id)), None)
            
            if target_account and target_account.currency != currency:
                raise HTTPException(
                    status_code=400, 
                    detail="No se puede auto-ejecutar una transacción con divisas cruzadas."
                )

    updated = crud_scheduled.update_schedule(db, user_id=current_user_id, sched_id=sched_id, obj_in=sched_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Transacción programada no encontrada")
    return _hydrate_auto_execute_flag(db, current_user_id, [updated])[0]

@router.delete("/{sched_id}")
def delete_scheduled_transaction(
    sched_id: str,
    db: Session = Depends(deps.get_db_with_rls),
    current_user_id: str = Depends(deps.get_current_user)
):
    deleted = crud_scheduled.delete_schedule(db, user_id=current_user_id, sched_id=sched_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transacción programada no encontrada")
    return {"status": "success", "detail": "Programación eliminada (Soft Delete)"}