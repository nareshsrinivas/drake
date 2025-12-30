from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class JobApplicationCreate(BaseModel):
    job_uuid: UUID
    message: Optional[str] = None
    selected_media: Optional[List[int]] = None


class JobApplicationUpdate(BaseModel):
    message: Optional[str] = None
    selected_media: Optional[List[int]] = None
    status: Optional[str] = None
    admin_notes: Optional[str] = None


class JobApplicationOut(BaseModel):
    uuid: UUID
    job_id: int
    model_id: int
    message: Optional[str]
    selected_media: Optional[List[int]]
    status: str
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
