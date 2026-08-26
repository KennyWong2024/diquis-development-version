from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime
import calendar
from app.models.ledger import Transaction, TransactionItem
from app.models.treasury import Account
from app.schemas.transaction import TransactionCreate, TransactionItemCreate, TransactionUpdate

def create_transaction(db: Session, user_id: str, obj_in: TransactionCreate):
    """Crea una transacción asociada a la cuenta especificada."""
    
    if obj_in.account_id:
        account = db.query(Account).filter(Account.user_id == user_id, Account.id == obj_in.account_id).first()
    else:
        account = db.query(Account).filter(Account.user_id == user_id, Account.name == "Billetera Principal").first()
        
    if not account:
        raise HTTPException(status_code=404, detail="Cuenta origen no encontrada.")

    if obj_in.type == 'transfer':
        if not obj_in.transfer_to_account_id:
            raise HTTPException(status_code=400, detail="Transferencia necesita cuenta destino.")
        account_dest = db.query(Account).filter(Account.id == obj_in.transfer_to_account_id, Account.user_id == user_id).first()
        if not account_dest:
            raise HTTPException(status_code=404, detail="Cuenta destino no encontrada.")

    tx_data = obj_in.model_dump(exclude_unset=True)
    tx_data["account_id"] = account.id
    tx_data["user_id"] = user_id
    
    if not obj_in.occurred_at:
        tx_data["occurred_at"] = datetime.now()

    db_obj = Transaction(**tx_data)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj

def get_transactions(
    db: Session, 
    user_id: str, 
    limit: int = 50, 
    start_date: datetime = None, 
    end_date: datetime = None,
    account_id: str = None
):
    query = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.is_deleted == False)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
        
    if start_date:
        query = query.filter(Transaction.occurred_at >= start_date)
    if end_date:
        query = query.filter(Transaction.occurred_at <= end_date)
        
    return query.order_by(Transaction.occurred_at.desc()).limit(limit).all()

def get_wallet_balance_and_metrics(db: Session, user_id: str):
    accounts = db.query(Account).filter(Account.user_id == user_id, Account.is_active == True).all()
    
    if not accounts:
        return None

    total_balance = sum([float(a.current_balance) for a in accounts])
    main_currency = accounts[0].currency if accounts else "CRC"

    now = datetime.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = calendar.monthrange(now.year, now.month)[1]
    end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    income_sum = db.query(func.sum(Transaction.amount_in_account_currency)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.is_deleted == False,
        Transaction.occurred_at >= start_of_month,
        Transaction.occurred_at <= end_of_month
    ).scalar() or 0.0

    expense_sum = db.query(func.sum(Transaction.amount_in_account_currency)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.is_deleted == False,
        Transaction.occurred_at >= start_of_month,
        Transaction.occurred_at <= end_of_month
    ).scalar() or 0.0

    return {
        "wallet_name": "Patrimonio Total",
        "currency": main_currency,
        "current_balance": float(total_balance),
        "metrics": {
            "monthly_income": float(income_sum),
            "monthly_expense": float(expense_sum)
        }
    }

def add_item_to_transaction(db: Session, user_id: str, transaction_id: str, item_in: TransactionItemCreate):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id,
        Transaction.is_deleted == False
    ).with_for_update().first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transacción padre no encontrada")

    current_sum = db.query(func.sum(TransactionItem.line_total)).filter(
        TransactionItem.transaction_id == transaction_id
    ).scalar() or 0.0

    current_sum_float = float(current_sum)
    transaction_amount_float = float(transaction.amount)

    if (current_sum_float + item_in.line_total) > transaction_amount_float:
        raise HTTPException(
            status_code=400,
            detail=f"Descuadre financiero: El total de los ítems ({(current_sum_float + item_in.line_total):.2f}) no puede exceder el monto original ({transaction_amount_float:.2f})"
        )

    item_data = item_in.model_dump(exclude_unset=True)
    item_data["transaction_id"] = transaction_id
    item_data["user_id"] = user_id
    item_data["unit_price"] = item_in.line_total / item_in.quantity

    db_item = TransactionItem(**item_data)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

def get_transaction_detail(db: Session, user_id: str, transaction_id: str):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id,
        Transaction.is_deleted == False
    ).first()

    if not transaction:
        return None

    items = db.query(TransactionItem).filter(
        TransactionItem.transaction_id == transaction_id,
        TransactionItem.user_id == user_id
    ).order_by(TransactionItem.created_at.asc()).all()

    return {
        "id": transaction.id,
        "type": transaction.type,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "amount_in_account_currency": transaction.amount_in_account_currency,
        "exchange_rate": transaction.exchange_rate,
        "exchange_source": transaction.exchange_source,
        "description": transaction.description,
        "category_id": transaction.category_id,
        "account_id": transaction.account_id,
        "transfer_to_account_id": transaction.transfer_to_account_id,
        "occurred_at": transaction.occurred_at,
        "is_essential": transaction.is_essential,
        "payment_method": transaction.payment_method,
        "notes": transaction.notes,
        "is_deleted": transaction.is_deleted,
        "items": items
    }

def update_transaction(db: Session, user_id: str, transaction_id: str, obj_in: TransactionUpdate):
    db_obj = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user_id).first()
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_transaction(db: Session, user_id: str, transaction_id: str):
    db_obj = db.query(Transaction).filter(Transaction.id == transaction_id, Transaction.user_id == user_id).first()
    if not db_obj:
        return None
    
    db_obj.is_deleted = True
    db_obj.deleted_at = datetime.now()
    
    db.add(db_obj)
    db.commit()
    return db_obj