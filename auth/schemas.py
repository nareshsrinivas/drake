from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from uuid import UUID


# ---------------- REGISTER USER ---------------- #

class RegisterUser(BaseModel):
    user_type: int = Field(..., ge=1, le=2, description="1=Model, 2=Casting Agency")
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    country_code: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=4)
    password: str = Field(..., min_length=6)
    confirm_password: str
    dob: date

    @field_validator("confirm_password")
    def passwords_match(cls, v, info):
        if info.data.get("password") != v:
            raise ValueError("password and confirm_password do not match")
        return v


# ---------------- UPDATE PROFILE ---------------- #

class UpdateUserInfo(BaseModel):
    gender: str | None = None
    current_city: str | None = None
    nationality: str | None = None
    home_town: str | None = None

# ---------------- LOGIN ---------------- #

class LoginUser(BaseModel):
    email: EmailStr
    password: str


# ---------------- REFRESH TOKEN ---------------- #

class RefreshSchema(BaseModel):
    refresh_token: str


# ---------------- ADMIN SCHEMAS ---------------- #

class AdminRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None


class AdminOut(BaseModel):
    id: int
    uuid: UUID
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# ---------------- GOOGLE LOGIN ---------------- #

class GoogleLogin(BaseModel):
    id_token: str = Field(..., description="Google ID token from client")


