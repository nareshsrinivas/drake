from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db     # <-- use async get_db
from .schemas import RegisterUser, LoginUser, RefreshSchema, GoogleLogin
from .service import (
    register_user, authenticate_user,
    refresh_access_token, login_with_google
)
from model.model_profile_progress_service import calculate_profile_progress

router = APIRouter(prefix="/auth", tags=["auth"])


# ----------------- Google Login -----------------

@router.post("/google", summary="Login or register using Google ID token")
async def google_login(data: GoogleLogin, db: AsyncSession = Depends(get_db)):
    resp, err = await login_with_google(db, data.id_token)
    if err:
        raise HTTPException(status_code=401, detail=err)
    return resp


@router.get("/google", summary="Login or register using Google ID token")
async def google_login_query(id_token: str, db: AsyncSession = Depends(get_db)):
    resp, err = await login_with_google(db, id_token)
    if err:
        raise HTTPException(status_code=401, detail=err)
    return resp


# ----------------- Register -----------------

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: RegisterUser, db: AsyncSession = Depends(get_db)):
    created_user, err = await register_user(db, user)
    if err:
        raise HTTPException(status_code=400, detail=err)

    return {
        "id": created_user.id,
        "user_type": created_user.user_type,
        "first_name": created_user.first_name,
        "last_name": created_user.last_name,
        "email": created_user.email,
        "country_code": created_user.country_code,
        "phone": created_user.phone,
        "dob": str(created_user.dob),
        "age": created_user.age,
    }


# ----------------- Login -----------------

@router.post("/login")
async def login(data: LoginUser, db: AsyncSession = Depends(get_db)):
    resp, err = await authenticate_user(db, data.email, data.password)
    if err:
        raise HTTPException(status_code=404,detail="Invalid email or password")
    
    # # api for model profile progress
    # user = resp["user_obj"]
    # next_step = await calculate_profile_progress(db, user)
    #
    # # attach progress info
    # resp["next_step"] = next_step
    # resp["user_uuid"] = str (user.uuid)

    return resp  


# ----------------- Refresh Token -----------------
@router.post("/refresh", summary="Generate new access token using refresh token")
async def refresh_token_api(data: RefreshSchema):
    token, err = await refresh_access_token(data.refresh_token)
    if err:
        raise HTTPException(status_code=401, detail=err)

    return {
        "access_token": token,
        "token_type": "bearer"
    }
