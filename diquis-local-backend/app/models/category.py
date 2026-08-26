from sqlalchemy import Column, String, Boolean, Integer, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "app"}
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    domain = Column(ENUM(
        'grocery', 'transport', 'food_out', 'home', 'health', 
        'entertainment', 'education', 'income', 'savings', 'utilities', 
        'shopping', 'personal_care', 'family', 'other', 
        name='category_domain_enum', 
        schema='app',
        create_type=False 
    ), nullable=False)
    
    icon = Column(String(50), nullable=True)
    is_system = Column(Boolean, nullable=False, default=False)
    is_essential_default = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    overrides = relationship("UserCategoryOverride", back_populates="category", cascade="all, delete-orphan")


class Subcategory(Base):
    __tablename__ = "subcategories"
    __table_args__ = {"schema": "app"}

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(100), nullable=False)
    is_system = Column(Boolean, nullable=False, default=False)
    is_essential_default = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    category = relationship("Category", back_populates="subcategories")


class UserCategoryOverride(Base):
    """
    Tabla satélite: Almacena únicamente las personalizaciones del usuario 
    sobre las categorías del sistema (o sus propias categorías).
    """
    __tablename__ = "user_category_overrides"
    __table_args__ = {"schema": "app"}

    user_id = Column(UUID(as_uuid=True), ForeignKey("app.users.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("app.categories.id", ondelete="CASCADE"), primary_key=True)
    
    custom_icon = Column(String(50), nullable=True)
    custom_name = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"), nullable=False)

    category = relationship("Category", back_populates="overrides")