from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class TransactionCreate(BaseModel):
    type: str = Field(..., pattern="^(income|expense|transfer)$", description="Debe ser 'income', 'expense' o 'transfer'")
    amount: float = Field(..., gt=0, description="El monto debe ser mayor a 0")
    account_id: Optional[UUID] = None
    transfer_to_account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    currency: Optional[str] = "CRC"
    payment_method: Optional[str] = Field("cash", pattern="^(cash|debit|credit|transfer|sinpe|digital)$")
    is_essential: Optional[bool] = False
    notes: Optional[str] = None
    exchange_rate: Optional[float] = Field(
        None, description="Tasa de cambio aplicada (override del usuario)"
    )
    exchange_source: Optional[str] = Field(
        "none", description="De dónde salió la tasa: 'user', 'api', 'bccr'"
    )

class TransactionResponse(BaseModel):
    id: UUID
    type: str
    amount: float
    currency: str
    amount_in_account_currency: float
    exchange_rate: float
    exchange_source: str
    description: Optional[str]
    category_id: Optional[UUID]
    account_id: UUID
    transfer_to_account_id: Optional[UUID]
    occurred_at: datetime
    is_essential: bool
    payment_method: str
    notes: Optional[str]
    is_deleted: bool

    class Config:
        from_attributes = True

# --- MODELOS PARA EL BALANCE ---
class BalanceMetrics(BaseModel):
    monthly_income: float
    monthly_expense: float

class BalanceResponse(BaseModel):
    wallet_name: str
    currency: str
    current_balance: float
    metrics: BalanceMetrics

# --- MODELOS PARA EL DETALLE (ÍTEMS) ---
class TransactionItemCreate(BaseModel):
    product_name: str = Field(..., min_length=1, description="Nombre del producto")
    subcategory_id: Optional[UUID] = None
    quantity: float = Field(1.0, gt=0, description="Cantidad comprada")
    line_total: float = Field(..., ge=0, description="Monto total pagado por esta línea")
    is_essential: bool = False

class TransactionItemResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    product_name: str
    subcategory_id: Optional[UUID]
    quantity: float
    unit_price: float
    line_total: float
    is_essential: bool

    class Config:
        from_attributes = True

class TransactionDetailResponse(TransactionResponse):
    items: List[TransactionItemResponse] = []

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    category_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    transfer_to_account_id: Optional[UUID] = None
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    type: Optional[str] = Field(None, pattern="^(income|expense|transfer)$")
    payment_method: Optional[str] = Field(None, pattern="^(cash|debit|credit|transfer|sinpe|digital)$")
    is_essential: Optional[bool] = None
    notes: Optional[str] = None
    exchange_rate: Optional[float] = Field(None, description="Permite corregir la tasa aplicada")
    exchange_source: Optional[str] = Field(None, description="Actualizar el origen si es necesario")