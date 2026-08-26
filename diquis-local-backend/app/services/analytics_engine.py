from sqlalchemy.orm import Session
from sqlalchemy import func, Date
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import pytz
from app.models.ledger import Transaction
from app.models.forecasting import ScheduledTransaction
from app.models.treasury import Account
from app.models.user import User
from app.services.fx_service import get_latest_rates_map

def _get_next_date(current_date: date, frequency: str) -> date:
    if frequency == 'daily':
        return current_date + timedelta(days=1)
    elif frequency == 'weekly':
        return current_date + timedelta(weeks=1)
    elif frequency == 'biweekly':
        return current_date + timedelta(weeks=2)
    elif frequency == 'monthly':
        return current_date + relativedelta(months=1)
    elif frequency == 'quarterly':
        return current_date + relativedelta(months=3)
    elif frequency == 'yearly':
        return current_date + relativedelta(years=1)
    return current_date

def generate_unified_cashflow(db: Session, user_id: str, start_date: date, end_date: date) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Usuario no encontrado")
    
    tz = pytz.timezone(user.timezone)
    now_utc = func.now()
    today_local = db.query(func.timezone(user.timezone, now_utc).cast(Date)).scalar()

    accounts = db.query(Account).filter(Account.user_id == user_id, Account.is_active == True).all()
    current_balance = sum(float(acc.current_balance) for acc in accounts)
    
    main_currency = accounts[0].currency if accounts else user.default_currency
    
    rates_map = get_latest_rates_map(db, target_currency=user.default_currency)

    daily_matrix = defaultdict(lambda: {'r_in': 0.0, 'r_out': 0.0, 'p_in': 0.0, 'p_out': 0.0})

    schedules = db.query(ScheduledTransaction).filter(
        ScheduledTransaction.user_id == user_id,
        ScheduledTransaction.is_active == True,
        ScheduledTransaction.type.in_(['income', 'expense'])
    ).all()

    anchor_balance = current_balance

    if start_date <= today_local:
        real_txs = db.query(
            func.timezone(user.timezone, Transaction.occurred_at).cast(Date).label('local_date'),
            Transaction.type,
            Transaction.amount_in_account_currency
        ).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False,
            Transaction.type.in_(['income', 'expense']),
            func.timezone(user.timezone, Transaction.occurred_at).cast(Date) >= start_date,
            func.timezone(user.timezone, Transaction.occurred_at).cast(Date) <= today_local
        ).all()

        total_real_net_change = 0.0

        for tx_date, tx_type, amount in real_txs:
            amt = float(amount)
            if tx_type == 'income':
                daily_matrix[tx_date]['r_in'] += amt
                total_real_net_change += amt
            else:
                daily_matrix[tx_date]['r_out'] += amt
                total_real_net_change -= amt

        anchor_balance = current_balance - total_real_net_change

    else:
        gap_balance = current_balance
        
        for sched in schedules:
            current_sim_date = sched.next_due_date
            if current_sim_date < today_local:
                current_sim_date = today_local

            while current_sim_date < start_date:
                if current_sim_date >= today_local:
                    fx_rate = rates_map.get(sched.currency, 1.0)
                    projected_amt = float(sched.expected_amount) * fx_rate
                    
                    if sched.type == 'income':
                        gap_balance += projected_amt
                    else:
                        gap_balance -= projected_amt
                
                if sched.frequency == 'once':
                    break
                
                current_sim_date = _get_next_date(current_sim_date, sched.frequency)
        
        anchor_balance = gap_balance

    for sched in schedules:
        current_sim_date = sched.next_due_date
        
        if current_sim_date < today_local:
            current_sim_date = today_local

        while current_sim_date <= end_date:
            if current_sim_date >= today_local and current_sim_date >= start_date:
                fx_rate = rates_map.get(sched.currency, 1.0)
                projected_amt = float(sched.expected_amount) * fx_rate
                
                if sched.type == 'income':
                    daily_matrix[current_sim_date]['p_in'] += projected_amt
                else:
                    daily_matrix[current_sim_date]['p_out'] += projected_amt
            
            if sched.frequency == 'once':
                break
            
            current_sim_date = _get_next_date(current_sim_date, sched.frequency)

    timeline = []
    running_balance = anchor_balance
    
    current_day = start_date
    while current_day <= end_date:
        is_future = current_day > today_local
        data = daily_matrix[current_day]
        
        if is_future:
            net_change = data['p_in'] - data['p_out']
        else:
            net_change = data['r_in'] - data['r_out']
            
        running_balance += net_change

        timeline.append({
            "date": current_day,
            "real_income": data['r_in'],
            "real_expense": data['r_out'],
            "projected_income": data['p_in'],
            "projected_expense": data['p_out'],
            "balance": round(running_balance, 2), 
            "is_future": is_future
        })
        current_day += timedelta(days=1)

    return {
        "currency": main_currency,
        "start_date": start_date,
        "end_date": end_date,
        "starting_balance": round(anchor_balance, 2),
        "ending_balance": round(running_balance, 2),
        "timeline": timeline
    }