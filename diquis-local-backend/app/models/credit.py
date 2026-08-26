from sqlalchemy import Column, String, text, ForeignKey, Numeric, DateTime, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.db.base_class import Base

class CreditPlan(Base):
    __tablename__ = "credit_plans"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id"), nullable=False)
    description = Column(String, nullable=False)
    total_amount = Column(Numeric(15,2), nullable=False)
    interest_rate_pct = Column(Numeric(5,2), nullable=False, default=0)
    total_installments = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    currency = Column(String(3), nullable=False, default="CRC")
    status = Column(ENUM('active', 'paid', 'cancelled', name='credit_status_enum', schema='app'), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class CreditInstallment(Base):
    __tablename__ = "credit_installments"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("app.credit_plans.id", ondelete="CASCADE"), nullable=False)
    installment_number = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Numeric(15,2), nullable=False)
    principal_part = Column(Numeric(15,2), nullable=False, default=0)
    interest_part = Column(Numeric(15,2), nullable=False, default=0)
    status = Column(ENUM('pending', 'paid', 'overdue', name='installment_status_enum', schema='app'), nullable=False, default='pending')
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="SET NULL"), nullable=True)
    payment_currency = Column(String(3), nullable=True)
    payment_exchange_rate = Column(Numeric(12,4), default=1)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)