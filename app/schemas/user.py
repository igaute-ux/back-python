from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]

class UserOut(UserBase):
    id: UUID
    class Config:
        from_attributes = True
