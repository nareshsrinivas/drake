from pydantic import BaseModel
from typing import Optional

from datetime import datetime
from uuid import UUID

class ProfileStatusResponse(BaseModel):
    user_basic: bool
    model_profile: bool
    model_professional: bool
    model_video: bool
    model_images: bool
