from sqlalchemy import Column, String, Boolean, text, ForeignKey, Numeric, DateTime, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
from app.db.base_class import Base

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id", ondelete="SET NULL"), nullable=True)
    type = Column(ENUM('income', 'expense', 'transfer', name='transaction_type_enum', schema='app'), nullable=False) 
    amount = Column(Numeric(15,2), nullable=False)
    currency = Column(String(3), nullable=False, default="CRC")
    exchange_rate = Column(Numeric(12,4), nullable=False, default=1)
    exchange_source = Column(String(10), nullable=False, default='none')
    transfer_to_account_id = Column(UUID(as_uuid=True), ForeignKey("app.accounts.id"), nullable=True)
    amount_in_account_currency = Column(Numeric(15,2), nullable=False, default=0)
    description = Column(String, nullable=True)
    occurred_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    is_essential = Column(Boolean, nullable=False, default=False)
    essential_reason = Column(String, nullable=True)
    payment_method = Column(ENUM('cash', 'debit', 'credit', 'transfer', 'sinpe', 'digital', name='payment_method_enum', schema='app'), nullable=False, default='cash')
    credit_plan_id = Column(UUID(as_uuid=True), ForeignKey("app.credit_plans.id", ondelete="SET NULL"), nullable=True)
    is_refund_of = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="SET NULL"), nullable=True)
    notes = Column(String, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class TransactionItem(Base):
    __tablename__ = "transaction_items"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=True) 
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("app.subcategories.id", ondelete="SET NULL"), nullable=True)  
    quantity = Column(Numeric(10,3), nullable=False, default=1)
    unit = Column(String(20), nullable=False, default='unidad')
    unit_price = Column(Numeric(15,2), nullable=False)
    has_tax = Column(Boolean, nullable=False, default=False)
    tax_rate_id = Column(UUID(as_uuid=True), ForeignKey("app.tax_rates.id", ondelete="SET NULL"), nullable=True)
    tax_amount = Column(Numeric(15,2), nullable=False, default=0)
    line_total = Column(Numeric(15,2), nullable=False)
    is_essential = Column(Boolean, nullable=False, default=False)
    nutrition_flags = Column(JSONB, nullable=True)
    extra_meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    color_hex = Column(String(7), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class ItemTag(Base):
    __tablename__ = "item_tags"
    __table_args__ = {"schema": "app"}
    
    item_id = Column(UUID(as_uuid=True), ForeignKey("app.transaction_items.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("app.tags.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class TransportDetail(Base):
    __tablename__ = "transport_details"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="CASCADE"), nullable=False, unique=True)
    transport_type = Column(ENUM('bus', 'taxi', 'uber', 'train', 'walk', 'bike', 'other', name='transport_type_enum', schema='app'), nullable=False)
    purpose = Column(ENUM('work', 'leisure', 'emergency', 'health', 'education', 'other', name='transport_purpose_enum', schema='app'), nullable=False, default='other')
    origin = Column(String(255), nullable=True)
    destination = Column(String(255), nullable=True)
    distance_km = Column(Numeric(8,2), nullable=True)
    was_planned = Column(Boolean, nullable=False, default=True)
    passengers = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

class IncomeDetail(Base):
    __tablename__ = "income_details"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("app.transactions.id", ondelete="CASCADE"), nullable=False, unique=True)
    income_type = Column(String(50), nullable=False)
    gross_amount = Column(Numeric(15,2), nullable=False)
    deduction_ccss = Column(Numeric(15,2), nullable=False, default=0)
    deduction_ins = Column(Numeric(15,2), nullable=False, default=0)
    deduction_rent_tax = Column(Numeric(15,2), nullable=False, default=0)
    other_deductions = Column(Numeric(15,2), nullable=False, default=0)
    net_amount = Column(Numeric(15,2), nullable=False)
    employer = Column(String(255), nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)