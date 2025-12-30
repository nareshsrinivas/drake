from pydantic import BaseModel
from typing import Optional


class AvailabilitySchema(BaseModel):
    advertisement: Optional[bool] = None
    series: Optional[bool] = None
    reels: Optional[bool] = None
    movies: Optional[bool] = None
    short_movies: Optional[bool] = None
    youtube_videos: Optional[bool] = None
    photo_shoot: Optional[bool] = None


class ModelFilterBase(BaseModel):
    gender: Optional[str] = None
    height_min: Optional[float] = None
    height_max: Optional[float] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    age_range_min: Optional[int] = None
    age_range_max: Optional[int] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    availability: Optional[AvailabilitySchema] = None


class ModelFilterCreate(ModelFilterBase):
    pass


class ModelFilterUpdate(ModelFilterBase):
    pass


class ModelFilterResponse(ModelFilterBase):
    id: int

    class Config:
        orm_mode = True




