from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import (
    ModelProfile,
    ModelProfessional,
    ModelImages,
    Image_Videos,
    UserSocialLink,
    User
)

async def calculate_profile_progress(
    db: AsyncSession,
    user: User
):
    user_id = user.id

    response = {
        "model_basic_info": False,
        "model_profile": False,
        "model_professional": False,
        "model_images": False,
        "model_video": False,
        "user_social_links": False,
        "status": False
    }

    def is_filled(value):
        return value is not None and str(value).strip() != ""

    # 1️⃣ Basic Info
    basic_fields = [
        user.gender,
        user.current_city,
        user.nationality,
        user.home_town
    ]

    if not all(is_filled(v) for v in basic_fields):
        return response

    response["model_basic_info"] = True

    # 2️⃣ Model Profile
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        return response
    response["model_profile"] = True

    # 3️⃣ Model Professional
    result = await db.execute(
        select(ModelProfessional).where(ModelProfessional.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        return response
    response["model_professional"] = True

    # 4️⃣ Video
    video_result = await db.execute(
        select(Image_Videos).where(Image_Videos.user_id == user_id)
    )
    video = video_result.scalar_one_or_none()
    if not video:
        return response
    response["model_video"] = True

    # 5️⃣ Images
    image_result = await db.execute(
        select(ModelImages.id)
        .where(ModelImages.media_uuid == video.uuid)
        .limit(1)
    )
    if not image_result.scalar():
        return response
    response["model_images"] = True

    # 6️⃣ Social Links
    result = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        return response
    response["user_social_links"] = True

    response["status"] = True
    return response





# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from uuid import UUID
#
# from models import (
#     ModelProfile,
#     ModelProfessional,
#     ModelImages,
#     Image_Videos,
#     UserSocialLink,
#     User,
#     ProfileStep
# )
#
# async def calculate_profile_progress(
#     db: AsyncSession,
#     user: User
# ):
#     user_id = user.id
#
#     response = {
#         "model_basic_info": False,
#         "model_profile": False,
#         "model_professional": False,
#         "model_images": False,
#         "model_video": False,
#         "user_social_links": False,
#         "status": False
#     }
#
#     def is_filled(value):
#         return value is not None and str(value).strip() != ""
#
#     # ✅ Safe basic info check
#     basic_fields = [
#         user.gender,
#         user.current_city,
#         user.nationality,
#         # user.languages,
#         # user.home_city,
#         user.home_town
#     ]
#
#     if not all(is_filled(v) for v in basic_fields):
#         return response
#
#
#     response["model_basic_info"] = True
#
#     # 1️⃣ Model Profile
#     result = await db.execute(
#         select(ModelProfile).where(ModelProfile.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["model_profile"] = True
#
#     # 2️⃣ Model Professional
#     result = await db.execute(
#         select(ModelProfessional).where(ModelProfessional.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["model_professional"] = True
#
#     # 3️⃣ Model Video
#     video_result = await db.execute(
#         select(Image_Videos).where(Image_Videos.user_id == user_id)
#     )
#     video = video_result.scalar_one_or_none()
#     if not video:
#         return response
#     response["model_video"] = True
#
#     # 4️⃣ Model Images
#     image_result = await db.execute(
#         select(ModelImages.id)
#         .where(ModelImages.media_uuid == video.uuid)
#         .limit(1)
#     )
#     if not image_result.scalar():
#         return response
#     response["model_images"] = True
#
#     # 5️⃣ Social Links
#     result = await db.execute(
#         select(UserSocialLink).where(UserSocialLink.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["user_social_links"] = True
#
#     response["status"] = True
#     return response
#







# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from uuid import UUID
#
# from models import (
#     ModelProfile,
#     ModelProfessional,
#     ModelImages,
#     Image_Videos,
#     UserSocialLink,
#     User,
#     ProfileStep
# )
#
#
# async def calculate_profile_progress(
#     db: AsyncSession,
#     user: User
# ):
#
#     user_id = user.id
#
#     response = {
#         "model_profile": False,
#         "model_professional": False,
#         "model_images": False,
#         "model_video": False,
#         "user_social_links": False,
#         "status": False
#     }
#
#     # 1️⃣ Model Profile
#     result = await db.execute(
#         select(ModelProfile).where(ModelProfile.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["model_profile"] = True
#
#     # 2️⃣ Model Professional
#     result = await db.execute(
#         select(ModelProfessional).where(ModelProfessional.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["model_professional"] = True
#
#     # 3️⃣ Model Video (parent)
#     video_result = await db.execute(
#         select(Image_Videos).where(Image_Videos.user_id == user_id)
#     )
#     video = video_result.scalar_one_or_none()
#     if not video:
#         return response
#     response["model_video"] = True
#
#     # 4️⃣ Model Images (child via media_uuid)
#     image_result = await db.execute(
#         select(ModelImages.id).where(ModelImages.media_uuid == video.uuid).limit(1)
#     )
#
#     if not image_result.scalar():
#         return response
#
#     response["model_images"] = True
#
#
#     # 5️⃣ Social Links
#     result = await db.execute(
#         select(UserSocialLink).where(UserSocialLink.user_id == user_id)
#     )
#     if not result.scalar_one_or_none():
#         return response
#     response["user_social_links"] = True
#
#     # ✅ All completed
#     response["status"] = True
#     return response
