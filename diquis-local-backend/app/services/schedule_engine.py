from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict

def calculate_next_due_date(current_date: date, frequency: str) -> date:
    mapping = {
        'daily': relativedelta(days=1),
        'weekly': relativedelta(weeks=1),
        'biweekly': relativedelta(weeks=2),
        'monthly': relativedelta(months=1),
        'quarterly': relativedelta(months=3),
        'yearly': relativedelta(years=1)
    }
    return current_date + mapping.get(frequency, relativedelta(months=1))

def generate_projections(current_total_balance: float, account_currency: str, schedules: list, rates_map: dict, days: int = 15):
    start_date = date.today()
    end_date = start_date + timedelta(days=days)
    
    events = []
    for sched in schedules:
        fx_rate = rates_map.get(sched.currency, 1.0)
        projected_impact = float(sched.expected_amount) * fx_rate

        curr_date = sched.next_due_date
        while curr_date <= end_date:
            if curr_date >= start_date:
                events.append({
                    "date": curr_date,
                    "scheduled_id": str(sched.id),
                    "name": sched.name,
                    "type": sched.type,
                    "amount": float(sched.expected_amount),
                    "currency": sched.currency,
                    "projected_account_amount": round(projected_impact, 2),
                    "projected_exchange_rate": round(fx_rate, 4),
                    "projected_fx_source": "system_projection" if sched.currency != account_currency else "none"
                })
            
            if sched.frequency == 'once':
                break
            
            curr_date = calculate_next_due_date(curr_date, sched.frequency)
    
    events_by_date = defaultdict(list)
    for e in events:
        events_by_date[e["date"]].append(e)

    daily_projections = []
    running_balance = current_total_balance

    for i in range(days + 1):
        sim_date = start_date + timedelta(days=i)
        day_events = events_by_date.get(sim_date, [])
        
        for ev in day_events:
            if ev["type"] == 'income':
                running_balance += ev["projected_account_amount"]
            else: 
                running_balance -= ev["projected_account_amount"]

        daily_projections.append({
            "date": sim_date.isoformat(),
            "projected_balance": round(running_balance, 2),
            "events": day_events
        })

    return daily_projections