from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ModelProfile
from model.model_profile_schema import ModelProfileCreate, ModelProfileUpdate


# Create or Update profile
async def create_or_update_profile(
    db: AsyncSession,
    user_id: int,
    data: ModelProfileCreate
):
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.user_id == user_id)
    )
    profile = result.scalars().first()

    if profile:
        # update existing
        for key, value in data.dict(exclude_none=True).items():
            setattr(profile, key, value)

        await db.commit()
        await db.refresh(profile)
        return profile

    # create new
    profile = ModelProfile(
        user_id=user_id,
        **data.dict(exclude_none=True)
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


# Update profile by uuid
async def update_profile(
    db: AsyncSession,
    uuid: str,
    data: ModelProfileUpdate,
    user_id: int
):
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.uuid == uuid)
    )
    profile = result.scalars().first()

    if not profile:
        return None

    if profile.user_id != user_id:
        return "unauthorized"

    for key, value in data.dict(exclude_none=True).items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)
    return profile


# Get profile by uuid
async def get_profile(db: AsyncSession, uuid: str):
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.uuid == uuid)
    )
    return result.scalars().first()


# Delete profile
async def delete_profile(
    db: AsyncSession,
    uuid: str,
    user_id: int
):
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.uuid == uuid)
    )
    profile = result.scalars().first()

    if not profile:
        return None

    if profile.user_id != user_id:
        return "unauthorized"

    await db.delete(profile)
    await db.commit()
    return True


# Get profile by current user
async def get_profile_by_user_id(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(ModelProfile).where(ModelProfile.user_id == user_id)
    )
    return result.scalars().first()






