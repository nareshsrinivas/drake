from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class WorkTypeCreate(BaseModel):
    work_type: Optional[str] = None
    is_order: Optional[int] = 0


class WorkTypeUpdate(BaseModel):
    work_type: Optional[str] = None
    is_order: Optional[int] = None



class WorkTypeOut(BaseModel):
    # uuid: UUID
    uuid: Optional[str]
    work_type: Optional[str]
    is_order: Optional[int]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
