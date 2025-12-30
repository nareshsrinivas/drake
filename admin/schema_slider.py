# admin/schema_slider.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SliderCreate(BaseModel):
    slider_title: Optional[str] = None
    is_order: Optional[int] = 0
    slider_type: int = 0


class SliderUpdate(BaseModel):
    slider_title: Optional[str] = None
    is_order: Optional[int] = None
    slider_type: Optional[int] = None


class SliderOut(BaseModel):
    uuid: UUID
    image: Optional[str]
    slider_title: Optional[str]
    is_order: Optional[int]
    slider_type: int
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
