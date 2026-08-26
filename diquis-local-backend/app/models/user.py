from sqlalchemy import Column, String, Date, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True) 
    country_code = Column(String(2), nullable=False, default="CR")
    default_currency = Column(String(3), nullable=False, default="CRC")
    timezone = Column(String(50), nullable=False, default="America/Costa_Rica")
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    sso_providers = relationship("SSOProvider", back_populates="user", cascade="all, delete-orphan")