from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ContactBannerBase(BaseModel):
    banner_title: str
    banner_description: str


class ContactBannerOut(BaseModel):
    id: int
    uuid: UUID

    banner_title: str
    banner_description: str
    banner_image: str

    contact_info_email: str
    contact_info_phone: str
    contact_info_day: str
    contact_info_time: str

    contact_form_image: str
    contact_form_title: str
    contact_form_small_desc: str

    created_at: datetime
    updated_at: datetime
    is_delete: bool

    class Config:
        from_attributes = True
