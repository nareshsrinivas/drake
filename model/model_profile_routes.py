from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_current_user, get_db
from models import User
from model.model_profile_schema import ModelProfileCreate, ModelProfileUpdate
from model.model_profile_service import (
    create_or_update_profile,
    update_profile,
    delete_profile,
    get_profile,
    get_profile_by_user_id
)

router = APIRouter(prefix="/profile", tags=["Model Profile"])


# Create or Update profile
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_or_update(
    data: ModelProfileCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    profile = await create_or_update_profile(db, user.id, data)
    return profile


@router.get("/")
async def get_current_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = await get_profile_by_user_id(db, current_user.id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile

# Update profile
@router.patch("/{uuid}")
async def update(
    uuid: str,
    data: ModelProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    profile = await update_profile(db, uuid, data, user.id)

    if profile == "unauthorized":
        raise HTTPException(status_code=403, detail="Not allowed")

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# Get profile
@router.get("/{uuid}")
async def get(
    uuid: str,
    db: AsyncSession = Depends(get_db)
):
    profile = await get_profile(db, uuid)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# Delete profile
@router.delete("/{uuid}")
async def delete(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await delete_profile(db, uuid, user.id)

    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="Not allowed")

    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"message": "Profile deleted"}








