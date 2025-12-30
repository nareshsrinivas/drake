from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from database import get_db
from models import (
    User,
    ModelProfile,
    ModelProfessional,
    Image_Videos,
    ModelImages,
    ModelMedia
)
from model.progress_schema import ProfileStatusResponse

router = APIRouter(prefix="/profile", tags=["Profile Status"])

@router.get(
    "/completion-status/{user_id}",
    response_model=ProfileStatusResponse
)
async def check_profile_completion(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):

    # 1️⃣ User Basic
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_basic = True

    # 2️⃣ Model Profile
    model_profile = (
        await db.execute(
            select(ModelProfile).where(ModelProfile.user_id == user_id)
        )
    ).scalar_one_or_none() is not None

    # 3️⃣ Model Professional
    model_professional = (
        await db.execute(
            select(ModelProfessional).where(ModelProfessional.user_id == user_id)
        )
    ).scalar_one_or_none() is not None

    # 4️⃣ Model Video
    video = (
        await db.execute(
            select(Image_Videos).where(Image_Videos.user_id == user_id)
        )
    ).scalar_one_or_none()

    model_video = video is not None

    model_media = (
        await db.execute(
            select(ModelMedia).where(ModelMedia.user_id == user_id)
        )
    ).scalar_one_or_none()

    model_medias = model_media is not None

    # 5️⃣ Model Images
    model_images = False
    if video:
        model_images = (
            await db.execute(
                select(ModelImages).where(ModelImages.media_uuid == video.uuid)
            )
        ).scalar_one_or_none() is not None

    return ProfileStatusResponse(
        user_basic=user_basic,
        model_profile=model_profile,
        model_professional=model_professional,
        model_video=model_video,
        model_images=model_images,
        model_media=model_medias
    )
