import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text

from app.db.session import SessionLocal
from app.services.auto_executor import run_auto_execute
from app.services.fx_service import fetch_and_store_rates

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler(timezone="UTC")

def _auto_execute_job():
    """Ejecuta los pagos programados."""
    db = SessionLocal()
    try:
        summary = run_auto_execute(db)
        if summary.get('executed', 0) > 0 or summary.get('failed', 0) > 0:
            logger.info(f"[Scheduler] Lote completado: {summary['executed']} ✅ | {summary['failed']} ❌")
    except Exception as e:
        logger.error(f"[Scheduler] Error en auto-ejecución: {e}")
    finally:
        db.close()

def _cleanup_expired_tokens_job():
    """Elimina de la lista negra los tokens que ya expiraron por sí solos."""
    db = SessionLocal()
    try:
        result = db.execute(text("DELETE FROM app.token_blacklist WHERE expires_at < NOW()"))
        db.commit()
        deleted_count = result.rowcount
        if deleted_count > 0:
            logger.info(f"[Scheduler] 🧹 Limpieza profunda: {deleted_count} tokens expirados borrados de la lista negra.")
    except Exception as e:
        logger.error(f"[Scheduler] Error limpiando tokens: {e}")
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    logger.info("[Scheduler] Ejecutando bootstrap de Tipos de Cambio...")
    db_fx = SessionLocal()
    try:
        fetch_and_store_rates(db_fx)
    except Exception as e:
        logger.error(f"[Scheduler] Error en bootstrap FX: {e}")
    finally:
        db_fx.close()

    scheduler.add_job(
        lambda: fetch_and_store_rates(SessionLocal()),
        trigger=CronTrigger(hour="2,14", minute=0),
        id="fetch_daily_fx",
        name="Actualización Diaria de Divisas",
        replace_existing=True
    )

    scheduler.add_job(
        _auto_execute_job,
        trigger=CronTrigger(minute="*/15"),
        id="auto_execute_scheduled",
        name="Polling de Pagos Automáticos",
        replace_existing=True,
        misfire_grace_time=300 
    )
    
    scheduler.add_job(
        _cleanup_expired_tokens_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_expired_tokens",
        name="Limpieza de Lista Negra de Tokens",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("[Scheduler] ✅ APScheduler iniciado (FX, Pagos y Limpieza).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Detenido.")