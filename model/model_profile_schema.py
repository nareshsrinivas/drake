from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID
class ModelProfileCreate(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    chest_bust: Optional[str] = None
    waist: Optional[str] = None
    hips: Optional[str] = None
    shoulder: Optional[str] = None
    shoe_size: Optional[str] = None
    complexion: Optional[str] = None
    eye_color: Optional[str] = None
    hair_color: Optional[str] = None
    tattoos_piercings: Optional[bool] = None
    tattoos_details: Optional[str] = None
    suit_jacket_dress_size: Optional[str] = None
    hair_length: Optional[str] = None
    body_type: Optional[str] = None
    body_shape: Optional[str] = None
    facial_hair: Optional[str] = None
    bust_cup_size: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_meaningful_input(cls, values):

        for value in values.values():

            # ignore booleans completely
            if isinstance(value, bool):
                continue

            if isinstance(value, str):
                cleaned = value.strip().lower()
                if cleaned and cleaned != "string":
                    return values

        raise ValueError("Fill some information")

class ModelProfileUpdate(ModelProfileCreate):
    pass

    class Config:
        extra = "forbid"


