from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    role: UserRole = UserRole.member


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True