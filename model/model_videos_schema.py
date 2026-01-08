from pydantic import BaseModel
from typing import List, Optional


class IndexedVideo(BaseModel):
    index: int
    url: str


class VideoResponse(BaseModel):
    videos: List[IndexedVideo] = []
    video_url: List[str] = []

    class Config:
        from_attributes = True
        extra = "forbid"











