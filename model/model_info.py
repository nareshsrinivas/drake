from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.deps import get_current_user
from database import get_db
from models import (
    User,
    ModelProfile,
    ModelProfessional,
    UserSocialLink,
)

router = APIRouter(prefix="/info", tags=["Model Info"])


@router.get("")
async def get_my_model_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    model_id = current_user.id

    # 1️⃣ User
    result_user = await db.execute(select(User).where(User.id == model_id))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Model Not Found")

    # 2️⃣ Physical Profile
    result_profile = await db.execute(
        select(ModelProfile).where(ModelProfile.user_id == model_id)
    )
    profile = result_profile.scalar_one_or_none()

    # 3️⃣ Professional Info
    result_professional = await db.execute(
        select(ModelProfessional).where(ModelProfessional.user_id == model_id)
    )
    professional = result_professional.scalar_one_or_none()

    # 4️⃣ Social Links (NEW)
    result_links = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == model_id)
    )
    social_links = result_links.scalars().all()

    return {
        "basic_info": {
            "id": user.id,
            "uuid": str(user.uuid),
            "user_type": user.user_type,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "country_code": user.country_code,
            "phone": user.phone,
            "dob": user.dob,
            "age": user.age,
            "gender": user.gender,
            "current_city": user.current_city,
            "nationality": user.nationality,
            "home_town": user.home_town,
            "approved": user.approved,
        },

        "physical_profile": {
            "height": profile.height,
            "weight": profile.weight,
            "chest_bust": profile.chest_bust,
            "waist": profile.waist,
            "hips": profile.hips,
            "shoulder": profile.shoulder,
            "shoe_size": profile.shoe_size,
            "complexion": profile.complexion,
            "eye_color": profile.eye_color,
            "hair_color": profile.hair_color,
            "hair_length": profile.hair_length,
            "body_type": profile.body_type,
            "body_shape": profile.body_shape,
            "facial_hair": profile.facial_hair,
            "tattoos_piercings": profile.tattoos_piercings,
            "tattoos_details": profile.tattoos_details,
            "suit_jacket_dress_size": profile.suit_jacket_dress_size,
            "bust_cup_size": profile.bust_cup_size,
        } if profile else None,

        "professional_info": {
            "professional_experience": professional.professional_experience,
            "experience_details": professional.experience_details,
            "languages": professional.languages,
            "skills": professional.skills,
            "interested_categories": professional.interested_categories,
            "willing_to_travel": professional.willing_to_travel,
        } if professional else None,

        "social_links": [
            {
                "uuid": str(link.uuid),
                "platform": link.platform,
                "url": link.url,
            }
            for link in social_links
        ]
    }


