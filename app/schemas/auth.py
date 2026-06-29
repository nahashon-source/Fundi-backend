"""
Pydantic schemas for authentication endpoints.
These define exactly what the API accepts and returns -- never the
raw User ORM model, which would leak password_hash and internal fields.
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    phone: Optional[str] = None
    role: UserRole
    full_name: str  # used to create the CustomerProfile or FundiProfile row


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    email: str
    phone: Optional[str]
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True  # allows building this from an ORM object directly