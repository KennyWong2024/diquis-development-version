from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AccountBase(BaseModel):
    name: str
    account_type: str = Field(..., pattern="^(checking|saving|cash|digital)$")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Código ISO de 3 letras (ej. USD, CRC)")
    allow_negative_balance: Optional[bool] = False
    theme_color: Optional[str] = 'silver'
    is_system: Optional[bool] = False

class AccountCreate(AccountBase):
    initial_balance: Optional[float] = 0.0

class AccountResponse(AccountBase):
    id: UUID
    user_id: UUID
    current_balance: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    theme_color: Optional[str] = None
    allow_negative_balance: Optional[bool] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)