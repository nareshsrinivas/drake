from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class ContactCreate(BaseModel):
    name: str = Field(..., max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=250)
    message: str = Field(..., max_length=2000)

class ContactOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    subject: Optional[str]
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True