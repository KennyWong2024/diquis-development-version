from sqlalchemy import Column, String, text, Numeric, DateTime, Date
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class TaxRate(Base):
    __tablename__ = "tax_rates"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    country_code = Column(String(2), nullable=False)
    rate_name = Column(String(100), nullable=False)
    rate_pct = Column(Numeric(5,2), nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    from_currency = Column(String(3), nullable=False)
    to_currency = Column(String(3), nullable=False)
    rate = Column(Numeric(12,4), nullable=False)
    rate_date = Column(Date, nullable=False)
    source = Column(String(50), nullable=False, default='BCCR')
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)