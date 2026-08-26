import httpx
import logging
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func
from datetime import date
from app.models.system import ExchangeRate

logger = logging.getLogger("fx_service")

def fetch_and_store_rates(db: Session, base_currency: str = "USD"):
    logger.info(f"[FX Service] Descargando tasas de cambio pivote: {base_currency}...")
    url = f"https://open.er-api.com/v6/latest/{base_currency}"
    
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            logger.error("[FX Service] La API respondió pero indicó error en los datos.")
            return

        rates = data.get("rates", {})
        today = date.today()

        for to_currency_code, rate_value in rates.items():
            if to_currency_code == base_currency:
                continue 
            
            if rate_value > 0:
                stmt = insert(ExchangeRate).values(
                    from_currency=base_currency,     
                    to_currency=to_currency_code,    
                    rate=rate_value,                 
                    rate_date=today,
                    source='er-api'
                )
                
                stmt = stmt.on_conflict_do_update(
                    index_elements=['from_currency', 'to_currency', 'rate_date', 'source'],
                    set_={'rate': rate_value}
                )
                db.execute(stmt)
                
        db.commit()
        logger.info("[FX Service] Tasas de cambio globales actualizadas correctamente en DB.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"[FX Service] Falló la obtención de divisas globales: {e}")

def get_latest_rates_map(db: Session, target_currency: str = "CRC", pivot_currency: str = "USD") -> dict:
    subquery = db.query(
        ExchangeRate.to_currency,
        func.max(ExchangeRate.rate_date).label('max_date')
    ).filter(ExchangeRate.from_currency == pivot_currency).group_by(ExchangeRate.to_currency).subquery()

    latest_usd_rates = db.query(ExchangeRate).join(
        subquery,
        (ExchangeRate.to_currency == subquery.c.to_currency) & 
        (ExchangeRate.rate_date == subquery.c.max_date)
    ).filter(ExchangeRate.from_currency == pivot_currency).all()

    usd_rates_dict = {r.to_currency: float(r.rate) for r in latest_usd_rates}
    usd_rates_dict[pivot_currency] = 1.0

    target_rate_vs_usd = usd_rates_dict.get(target_currency)
    
    if not target_rate_vs_usd:
        logger.warning(f"[FX Service] Moneda objetivo {target_currency} no encontrada. Cayendo a 1.0")
        target_rate_vs_usd = 1.0

    rates_map = {target_currency: 1.0}
    
    for currency_code, rate_vs_usd in usd_rates_dict.items():
        if currency_code == target_currency:
            continue
        cross_rate = target_rate_vs_usd / rate_vs_usd
        rates_map[currency_code] = cross_rate
        
    return rates_map