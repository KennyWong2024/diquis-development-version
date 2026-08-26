from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8)
    date_of_birth: Optional[date] = None
    country_code: Optional[str] = "CR"
    default_currency: Optional[str] = "CRC"
    timezone: Optional[str] = "America/Costa_Rica"

class UserUpdateProfile(BaseModel):
    full_name: Optional[str] = None
    country_code: Optional[str] = None
    default_currency: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    date_of_birth: Optional[date] = None
    country_code: str
    default_currency: str
    timezone: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserDeleteAccount(BaseModel):
    current_password: str = Field(..., description="Contraseña requerida para confirmar el Hard Delete")