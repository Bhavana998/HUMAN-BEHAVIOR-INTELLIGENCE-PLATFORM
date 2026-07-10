from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from database.models.user import UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    # Pydantic v2 configuration
    model_config = ConfigDict(from_attributes=True)