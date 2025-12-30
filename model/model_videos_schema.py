from pydantic import BaseModel, HttpUrl
from typing import Optional


class VideoResponse(BaseModel):
    video: Optional[str]
    video_url: Optional[str]

    class Config:
        from_attributes = True
