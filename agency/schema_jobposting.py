# agency/schema_jobposting.py
from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import datetime


class JobPostingBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_type: Optional[str] = None
    logo: Optional[str] = None

    gender: Optional[str] = "any"
    location: Optional[str] = None

    pay_min: Optional[float] = None
    pay_max: Optional[float] = None
    pay_type: Optional[str] = None
    pay_unit: Optional[str] = None
    is_paid: Optional[bool] = True

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    deadline: Optional[datetime] = None

    requirements: Optional[Dict] = None
    status: Optional[str] = "open"
    visibility: Optional[str] = "public"


class JobPostingCreate(JobPostingBase):
    title: str


class JobPostingUpdate(JobPostingBase):
    pass


class JobPostingOut(JobPostingBase):
    uuid: UUID
    agency_id: int
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True

