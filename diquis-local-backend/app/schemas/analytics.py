from pydantic import BaseModel
from typing import List
from datetime import date

class DailyCashflow(BaseModel):
    date: date
    real_income: float
    real_expense: float
    projected_income: float
    projected_expense: float
    balance: float
    is_future: bool

class CashflowReport(BaseModel):
    currency: str 
    start_date: date
    end_date: date
    starting_balance: float
    ending_balance: float
    timeline: List[DailyCashflow]