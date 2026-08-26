from sqlalchemy import Column, String, Boolean, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class SSOProvider(Base):
    __tablename__ = "sso_providers"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(ENUM('google', 'outlook', 'local', name='sso_provider_enum', schema='app'), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token_hash = Column(String, nullable=True)
    refresh_token_hash = Column(String, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    linked_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    user = relationship("User", back_populates="sso_providers")