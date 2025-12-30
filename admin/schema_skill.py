from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SkillCreate(BaseModel):
    title: Optional[str] = None
    other_title: Optional[str] = None
    is_order: Optional[int] = 0


class SkillUpdate(BaseModel):
    title: Optional[str] = None
    other_title: Optional[str] = None
    is_order: Optional[int] = None



class SkillOut(BaseModel):
    uuid: UUID
    title: Optional[str]
    other_title: Optional[str]
    is_order: Optional[int]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
