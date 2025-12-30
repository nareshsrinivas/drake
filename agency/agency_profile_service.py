from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import uuid as _uuid
import uuid
from uuid import UUID

from models import AgencyProfile
from agency.agency_profile_schema import (
    AgencyProfileCreate,
    AgencyProfileUpdate,
)


# -------------------------------------------------
# CREATE AGENCY PROFILE
# -------------------------------------------------

async def create_agency_profile(
    db: AsyncSession,
    user_id: int,
    data: AgencyProfileCreate
):
    result = await db.execute(
        select(AgencyProfile).where(AgencyProfile.user_id == user_id)
    )
    if result.scalars().first():
        raise HTTPException(400, "Agency profile already exists")

    profile = AgencyProfile(
        uuid=uuid.uuid4(),
        user_id=user_id,
        **data.dict(),
        created_by=user_id,
        updated_by=user_id
    )

    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


# -------------------------------------------------
# UPDATE AGENCY PROFILE
# -------------------------------------------------
async def update_agency_profile(
    db: AsyncSession,
    user_id: int,
    data: AgencyProfileUpdate
) -> AgencyProfile | None:

    result = await db.execute(
        select(AgencyProfile).where(AgencyProfile.user_id == user_id)
    )
    profile = result.scalars().first()

    if not profile:
        return None

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.updated_by = user_id

    await db.commit()
    await db.refresh(profile)

    return profile


# -------------------------------------------------
# GET AGENCY PROFILE BY USER
# -------------------------------------------------
async def get_agency_profile(
    db: AsyncSession,
    user_id: int
) -> AgencyProfile | None:

    result = await db.execute(
        select(AgencyProfile).where(AgencyProfile.user_id == user_id)
    )
    return result.scalars().first()


# -------------------------------------------------
# GET AGENCY PROFILE BY UUID (PUBLIC)
# -------------------------------------------------
async def get_agency_by_uuid(
    db: AsyncSession,
    uuid: UUID
):
    result = await db.execute(
        select(AgencyProfile).where(AgencyProfile.uuid == uuid)
    )
    return result.scalars().first()

# -------------------------------------------------
# GET AGENCY PROFILE BY UUID (PUBLIC)
# -------------------------------------------------
async def delete_agency_profile_service(
    db: AsyncSession,
    user_id: int
) -> bool:

    result = await db.execute(
        select(AgencyProfile).where(
            AgencyProfile.user_id == user_id
        )
    )
    profile = result.scalars().first()

    if not profile:
        return False

    await db.delete(profile)
    await db.commit()

    return True


