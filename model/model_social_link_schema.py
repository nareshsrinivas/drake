from pydantic import BaseModel
from typing import List
from uuid import UUID

class SocialLinkBase(BaseModel):
    platform: str
    url: str

class SocialLinkCreateMulti(BaseModel):
    links: List[SocialLinkBase]

class SocialLinkResponse(BaseModel):
    uuid: UUID
    platform: str
    url: str

    class Config:
        orm_mode = True
