from sqlalchemy import Column, String, Boolean, text, ForeignKey, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.db.base_class import Base

class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = {"schema": "app"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    account_type = Column(ENUM('checking', 'saving', 'cash', 'digital', name='account_type_enum', schema='app'), nullable=False)
    currency = Column(String(3), nullable=False, default="CRC")
    initial_balance = Column(Numeric(15,2), nullable=False, default=0)
    current_balance = Column(Numeric(15,2), nullable=False, default=0)
    allow_negative_balance = Column(Boolean, nullable=False, default=False)
    theme_color = Column(String(20), nullable=False, server_default='silver')
    is_system = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)