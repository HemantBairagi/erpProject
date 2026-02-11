from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.schema.base import UUIDModel , AuditMixin


from app.models.EmunType import UserRole
class UserCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    phone: Optional[str] = None
    mobile: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

class UserOut(UUIDModel, AuditMixin):
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    is_superuser: bool
    phone: Optional[str] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None
    language: str
    timezone: str
    last_login: Optional[datetime] = None

class UserShort(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: UserRole
    model_config = {"from_attributes": True}

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    phone: str | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut