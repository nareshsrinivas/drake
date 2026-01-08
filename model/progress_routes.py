from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import (
    User,
    ModelProfile,
    ModelProfessional,
    ModelMedia,
)
from utils.validators import is_filled
from model.progress_schema import ProfileStatusResponse

router = APIRouter(
    prefix="/profile",
    tags=["Profile Status"]
)

@router.get(
    "/completion-status/{user_id}",
    response_model=ProfileStatusResponse
)

async def check_profile_completion(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 1️⃣ Fetch User
    user = await db.scalar(
        select(User).where(User.id == user_id)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 2️⃣ Validate User Basic Info
    required_fields = {
        "gender": user.gender,
        "current_city": user.current_city,
        "nationality": user.nationality,
        "home_town": user.home_town,
    }

    missing_fields = [
        field for field, value in required_fields.items()
        if not is_filled(value)
    ]

    user_basic = False if missing_fields else True

    # 3️⃣ Model Profile Exists
    model_profile = await db.scalar(
        select(exists().where(ModelProfile.user_id == user_id))
    )

    # 4️⃣ Model Professional Exists
    model_professional = await db.scalar(
        select(exists().where(ModelProfessional.user_id == user_id))
    )

    # 5️⃣ Model Media Exists
    model_media = await db.scalar(
        select(exists().where(ModelMedia.user_id == user_id))
    )

    # 6️⃣ Final Response
    return ProfileStatusResponse(
        user_basic=user_basic,
        model_profile=model_profile,
        model_professional=model_professional,
        model_media=model_media
    )

