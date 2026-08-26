from sqlalchemy.orm import Session
from datetime import date
from app.models.forecasting import ScheduledTransaction
from app.models.ledger import Transaction
from app.schemas.scheduled import ScheduledCreate, ScheduledExecute, ScheduledUpdate
from app.services.schedule_engine import calculate_next_due_date

def get_active_schedules(db: Session, user_id: str):
    return db.query(ScheduledTransaction).filter(
        ScheduledTransaction.user_id == user_id,
        ScheduledTransaction.is_active == True
    ).all()

def get_pending_tray(db: Session, user_id: str):
    today = date.today()
    return db.query(ScheduledTransaction).filter(
        ScheduledTransaction.user_id == user_id,
        ScheduledTransaction.is_active == True,
        ScheduledTransaction.next_due_date <= today
    ).order_by(ScheduledTransaction.next_due_date.asc()).all()

def create_schedule(db: Session, user_id: str, obj_in: ScheduledCreate):
    sched_data = obj_in.model_dump(exclude_unset=True)
    db_obj = ScheduledTransaction(**sched_data, user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def execute_scheduled(db: Session, user_id: str, sched_id: str, execution_data: ScheduledExecute):
    sched = db.query(ScheduledTransaction).filter(ScheduledTransaction.id == sched_id, ScheduledTransaction.user_id == user_id).first()
    if not sched:
        raise ValueError("Transacción programada no encontrada.")

    new_tx = Transaction(
        user_id=user_id,
        account_id=sched.account_id,
        transfer_to_account_id=sched.transfer_to_account_id,
        category_id=sched.category_id,
        type=sched.type,
        amount=execution_data.actual_amount,
        currency=sched.currency,
        exchange_rate=execution_data.exchange_rate or 1.0,
        exchange_source=execution_data.exchange_source or 'none',
        occurred_at=execution_data.occurred_at,
        description=execution_data.description or f"Automático: {sched.name}",
        is_essential=sched.is_essential,
        payment_method='digital' 
    )
    db.add(new_tx)
    db.flush() 

    sched.last_transaction_id = new_tx.id
    
    if sched.frequency == 'once':
        sched.is_active = False
    else:
        sched.next_due_date = calculate_next_due_date(sched.next_due_date, sched.frequency)
    
    db.add(sched)
    db.flush() 
    
    return new_tx

def skip_scheduled(db: Session, user_id: str, sched_id: str):
    sched = db.query(ScheduledTransaction).filter(ScheduledTransaction.id == sched_id, ScheduledTransaction.user_id == user_id).first()
    if not sched:
        raise ValueError("Transacción programada no encontrada.")

    if sched.frequency == 'once':
        sched.is_active = False
    else:
        sched.next_due_date = calculate_next_due_date(sched.next_due_date, sched.frequency)

    db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched

def update_schedule(db: Session, user_id: str, sched_id: str, obj_in: ScheduledUpdate):
    db_obj = db.query(ScheduledTransaction).filter(
        ScheduledTransaction.id == sched_id, 
        ScheduledTransaction.user_id == user_id
    ).first()
    
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_schedule(db: Session, user_id: str, sched_id: str):
    db_obj = db.query(ScheduledTransaction).filter(
        ScheduledTransaction.id == sched_id, 
        ScheduledTransaction.user_id == user_id
    ).first()
    if not db_obj:
        return None
        
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj