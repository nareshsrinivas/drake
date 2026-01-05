from pydantic import BaseModel, Field, model_validator
from uuid import UUID


# -------- CREATE / UPDATE --------
class SocialLinkCreate(BaseModel):
    x: str | None = None
    instagram: str | None = None
    tiktok: str | None = None
    snapchat: str | None = None
    pinterest: str | None = None
    linkedin: str | None = None
    youtube: str | None = None

    @model_validator(mode="before")
    @classmethod
    def at_least_one_field(cls, values):
        if not values or not any(v is not None for v in values.values()):
            raise ValueError("At least one social link must be provided")
        return values

    class Config:
        extra = "forbid"


# -------- RESPONSE --------
class SocialLinkResponse(BaseModel):
    uuid: UUID
    x: str | None
    instagram: str | None
    tiktok: str | None
    snapchat: str | None
    pinterest: str | None
    linkedin: str | None
    youtube: str | None

    class Config:
        orm_mode = True
        extra = "forbid"


class SocialLinkPatch(BaseModel):
    twitter: str | None = None
    instagram: str | None = None
    tiktok: str | None = None
    snapchat: str | None = None
    pinterest: str | None = None
    linkedin: str | None = None
    youtube: str | None = None

    @model_validator(mode="before")
    @classmethod
    def at_least_one_field_required(cls, values):
        if not values or not any(v is not None for v in values.values()):
            raise ValueError("At least one social link must be provided")
        return values

    class Config:
        extra = "forbid"


