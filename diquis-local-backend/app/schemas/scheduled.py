from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime

class ScheduledBase(BaseModel):
    account_id: UUID
    transfer_to_account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    type: str
    name: str
    expected_amount: float
    currency: Optional[str] = 'CRC'
    is_estimated: Optional[bool] = False
    frequency: str = Field(..., pattern="^(once|daily|weekly|biweekly|monthly|quarterly|yearly)$")
    next_due_date: date
    is_essential: Optional[bool] = False
    auto_execute: Optional[bool] = False
    projected_account_amount: Optional[float] = None
    projected_exchange_rate: Optional[float] = None
    projected_fx_source: Optional[str] = None

class ScheduledCreate(ScheduledBase):
    pass

class ScheduledResponse(ScheduledBase):
    id: UUID
    user_id: UUID
    is_active: bool
    last_transaction_id: Optional[UUID] = None
    created_at: datetime
    can_auto_execute: Optional[bool] = False

    class Config:
        from_attributes = True

class ScheduledExecute(BaseModel):
    actual_amount: float
    occurred_at: datetime
    description: Optional[str] = None
    exchange_rate: Optional[float] = Field(None, description="Tasa aplicada por el banco")
    exchange_source: Optional[str] = "user"

class ScheduledUpdate(BaseModel):
    account_id: Optional[UUID] = None
    transfer_to_account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    expected_amount: Optional[float] = None
    currency: Optional[str] = None
    frequency: Optional[str] = Field(None, pattern="^(once|daily|weekly|biweekly|monthly|quarterly|yearly)$")
    next_due_date: Optional[date] = None
    is_estimated: Optional[bool] = None
    is_essential: Optional[bool] = None
    is_active: Optional[bool] = None
    auto_execute: Optional[bool] = None

