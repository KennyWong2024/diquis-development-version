from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.api.dependencies import get_db_with_rls, get_current_user
from app.schemas.analytics import CashflowReport
from app.services.analytics_engine import generate_unified_cashflow

router = APIRouter()

@router.get("/cashflow", response_model=CashflowReport)
def get_unified_cashflow(
    start_date: date = Query(..., description="Fecha de inicio del análisis"),
    end_date: date = Query(..., description="Fecha de fin del análisis"),
    db: Session = Depends(get_db_with_rls),
    current_user_id: str = Depends(get_current_user)
):
    if (end_date - start_date).days > 366:
        raise ValueError("El rango de análisis no puede superar 1 año.")
        
    report = generate_unified_cashflow(
        db=db, 
        user_id=current_user_id, 
        start_date=start_date, 
        end_date=end_date
    )
    
    return report