from pydantic import BaseModel
from typing import Optional, Dict

class SocialLinks(BaseModel):
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    x: Optional[str] = None
    threads: Optional[str] = None

class PortfolioCreate(BaseModel):
    media_type: str

