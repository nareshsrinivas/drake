from pydantic import BaseModel
from typing import Optional,List,Dict
from uuid import UUID

class AgencyProfileBase(BaseModel):
    company_name: str
    contact_name: str
    phone: str
    website: Optional[str] = None
    address: Optional[str] = None

    logo: Optional[str] = None
    tagline: Optional[str] = None
    about: Optional[str] = None

    services: Optional[List[str]] = None  # multiple services
    social_links: Optional[Dict[str, str]] = None  # facebook, insta etc.

    verified: Optional[bool] = False


class AgencyProfileCreate(AgencyProfileBase):
    pass


class AgencyProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    logo: Optional[str] = None
    tagline: Optional[str] = None
    about: Optional[str] = None

    services: Optional[List[str]] = None
    social_links: Optional[Dict[str, str]] = None
    verified: Optional[bool] = None


class AgencyProfileResponse(AgencyProfileBase):
    uuid: UUID

    class Config:
        from_attributes  = True
