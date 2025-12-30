# model_info_Login_schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum

class ExperienceLevelEnum(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    professional = "Professional"
    expert = "Expert"

# --- Input schemas ---
class UserRegisterIn(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    country_code: str
    phone: str
    password: str

class UserLoginIn(BaseModel):
    email: EmailStr
    password: str

class ModelProfileIn(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    chest_bust: Optional[str] = None
    waist: Optional[str] = None
    hips: Optional[str] = None
    shoe_size: Optional[str] = None
    # add other optional fields as needed

class ModelProfessionalIn(BaseModel):
    professional_experience: Optional[bool] = None
    experience_details: Optional[str] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    languages: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    interested_categories: Optional[List[str]] = None
    availability: Optional[List[str]] = None
    willing_to_travel: Optional[bool] = None

# --- Response schemas (sensitive fields omitted) ---
class Tokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserPublic(BaseModel):
    uuid: str
    first_name: str
    last_name: str
    gender: Optional[str] = None
    current_city: Optional[str] = None
    nationality: Optional[str] = None
    languages: Optional[str] = None
    home_city: Optional[str] = None

class ModelProfileOut(BaseModel):
    height: Optional[str] = None
    weight: Optional[str] = None
    chest_bust: Optional[str] = None
    waist: Optional[str] = None
    hips: Optional[str] = None
    shoe_size: Optional[str] = None
    tattoos_piercings: Optional[bool] = None

class ModelProfessionalOut(BaseModel):
    professional_experience: Optional[bool] = None
    experience_details: Optional[str] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    languages: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    interested_categories: Optional[List[str]] = None
    availability: Optional[List[str]] = None
    willing_to_travel: Optional[bool] = None

class CombinedProfileOut(BaseModel):
    user: UserPublic
    profile: Optional[ModelProfileOut] = None
    professional: Optional[ModelProfessionalOut] = None

class ProgressOut(BaseModel):
    has_user_basic: bool
    has_profile: bool
    has_professional: bool
