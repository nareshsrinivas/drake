from pydantic import BaseModel

class ProfileStatusResponse(BaseModel):
    user_basic: bool
    model_profile: bool
    model_professional: bool
    model_media: bool
    # profile_Status: bool


# class agencyProfileStatus(BaseModel):
#         profile_Status: bool