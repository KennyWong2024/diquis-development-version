from sqlalchemy.orm import Session
from app.models.treasury import Account 
from app.schemas.account import AccountCreate, AccountUpdate
from app.models.user import User
from app.models.ledger import Transaction

def get_accounts(db: Session, user_id: str):
    return db.query(Account).filter(Account.user_id == user_id, Account.is_active == True).order_by(Account.created_at.asc()).all()

def create_account(db: Session, user_id: str, obj_in: AccountCreate):
    account_data = obj_in.model_dump(exclude_unset=True)
    
    if not account_data.get("currency"):
        user = db.query(User).filter(User.id == user_id).first()
        account_data["currency"] = user.default_currency if user else "CRC"
    account_data["currency"] = account_data["currency"].upper()
    account_data['current_balance'] = obj_in.initial_balance
    account_data['is_system'] = False 
    
    db_obj = Account(**account_data, user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_account(db: Session, user_id: str, account_id: str, obj_in: AccountUpdate):
    db_obj = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not db_obj:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    
    if "currency" in update_data:
        update_data["currency"] = update_data["currency"].upper()
        if update_data["currency"] != db_obj.currency:
            has_history = db.query(Transaction).filter(
                (Transaction.account_id == account_id) | 
                (Transaction.transfer_to_account_id == account_id)
            ).first()
            
            if has_history:
                raise ValueError(
                    "Integridad Financiera: No puedes cambiar la moneda de una cuenta que ya tiene movimientos históricos. "
                    "Por favor, crea una nueva cuenta en la moneda deseada y transfiere los fondos."
                )

    if "allow_negative_balance" in update_data and update_data["allow_negative_balance"] is False:
        if db_obj.current_balance < 0:
            raise ValueError(
                "No puedes deshabilitar los saldos negativos porque esta cuenta actualmente tiene un saldo en rojo. "
                "Cubre el saldo deudor antes de cambiar esta configuración."
            )


    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_account(db: Session, user_id: str, account_id: str):
    db_obj = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not db_obj:
        return None
    if db_obj.current_balance != 0:
        raise ValueError(f"No puedes eliminar una cuenta con saldo activo ({db_obj.current_balance}). Transfiere los fondos primero o haz un ajuste a cero.")
        
    db_obj.is_active = False
    db.add(db_obj)
    db.commit()
    return db_obj