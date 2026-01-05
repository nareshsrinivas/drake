from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ImageOut(BaseModel):
    index: int
    url: str

class ImagesResponse(BaseModel):
    images: List[ImageOut]

    class Config:
        from_attributes = True
        extra = "forbid"

