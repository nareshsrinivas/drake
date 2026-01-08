from pydantic import BaseModel
from typing import List, Optional

class IndexedMedia(BaseModel):
    index: int
    url: str

class ImagesVideosResponse(BaseModel):
    images: List[IndexedMedia] = []
    videos: List[IndexedMedia] = []
