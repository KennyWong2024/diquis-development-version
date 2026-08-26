from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from enum import Enum

class CategoryDomain(str, Enum):
    grocery = "grocery"
    transport = "transport"
    food_out = "food_out"
    home = "home"
    health = "health"
    entertainment = "entertainment"
    education = "education"
    income = "income"
    savings = "savings"
    utilities = "utilities"
    other = "other"
    shopping = "shopping"
    personal_care = "personal_care"
    family = "family"

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    domain: CategoryDomain
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    domain: CategoryDomain
    icon: Optional[str] = None
    is_system: bool
    is_essential_default: bool
    sort_order: int

    class Config:
        from_attributes = True