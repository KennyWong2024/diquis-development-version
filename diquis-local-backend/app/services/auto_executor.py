import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, Date 
from app.models.forecasting import ScheduledTransaction
from app.models.treasury import Account 
from app.models.user import User
from app.crud import scheduled as crud_scheduled
from app.schemas.scheduled import ScheduledExecute

logger = logging.getLogger("auto_executor")

def run_auto_execute(db: Session) -> dict:
    logger.info("[AutoExecutor] Iniciando ciclo de polling...")

    executed = []
    failed = []

    try:
        user_local_date = func.timezone(User.timezone, func.now()).cast(Date)

        candidates = db.query(ScheduledTransaction).join(User).join(
            Account, ScheduledTransaction.account_id == Account.id
        ).filter(
            ScheduledTransaction.is_active == True,
            ScheduledTransaction.auto_execute == True,
            ScheduledTransaction.next_due_date <= user_local_date,
            ScheduledTransaction.currency == Account.currency
        ).with_for_update(skip_locked=True).all()

        if not candidates:
            return {"executed": 0, "failed": 0}

        logger.info(f"[AutoExecutor] Se encontraron {len(candidates)} pagos pendientes en la misma divisa.")

        for sched in candidates:
            with db.begin_nested():
                try:
                    execution_data = ScheduledExecute(
                        actual_amount=float(sched.expected_amount),
                        occurred_at=datetime.now(timezone.utc).isoformat(), 
                        description=f"Auto-ejecutado: {sched.name}"
                    )
                    
                    tx = crud_scheduled.execute_scheduled(
                        db=db,
                        user_id=str(sched.user_id),
                        sched_id=str(sched.id),
                        execution_data=execution_data
                    )
                    executed.append({"schedule_id": str(sched.id), "transaction_id": str(tx.id)})
                    logger.info(f"  ✅ [ÉXITO] '{sched.name}' (ID: {sched.id})")
                    
                except Exception as e:
                    failed.append({"schedule_id": str(sched.id), "error": str(e)})
                    logger.error(f"  ❌ [FALLO] '{sched.name}': {e}")

        db.commit()

    except Exception as fatal_error:
        db.rollback()
        logger.error(f"[AutoExecutor] ERROR FATAL EN EL CICLO: {fatal_error}")
        raise fatal_error

    return {
        "total_candidates": len(executed) + len(failed),
        "executed": len(executed),
        "failed": len(failed)
    }