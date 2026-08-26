from sqlalchemy import Column, String, Boolean, text, ForeignKey, Numeric, DateTime, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.db.base_class import Base

class ScheduledTransaction(Base):
    __tablename__ = "scheduled_transactions"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id"), nullable=False)
    transfer_to_account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id", ondelete="SET NULL"), nullable=True)
    type = Column(ENUM('income', 'expense', 'transfer', name='transaction_type_enum', schema='app'), nullable=False)
    name = Column(String(100), nullable=False)
    expected_amount = Column(Numeric(15,2), nullable=False)
    currency = Column(String(3), nullable=False, default="CRC")
    is_estimated = Column(Boolean, nullable=False, default=False)
    frequency = Column(ENUM('once', 'daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly', name='frequency_enum', schema='app'), nullable=False, default='monthly')
    next_due_date = Column(Date, nullable=False)
    is_essential = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    auto_execute = Column(Boolean, nullable=False, default=False)
    last_transaction_id = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class SavingsGoal(Base):
    __tablename__ = "savings_goals"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(15,2), nullable=False)
    current_amount = Column(Numeric(15,2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="CRC")
    deadline = Column(Date, nullable=True)
    status = Column(ENUM('active', 'reached', 'cancelled', name='goal_status_enum', schema='app'), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id", ondelete="CASCADE"), nullable=False)
    period_month = Column(Date, nullable=False)
    amount = Column(Numeric(15,2), nullable=False)
    currency = Column(String(3), nullable=False, default="CRC")
    alert_threshold_pct = Column(Integer, nullable=False, default=80)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)