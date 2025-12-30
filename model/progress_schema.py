from pydantic import BaseModel

class ProfileStatusResponse(BaseModel):
    user_basic: bool
    model_profile: bool
    model_professional: bool
    # model_video: bool
    # model_images: bool
    model_media: bool
