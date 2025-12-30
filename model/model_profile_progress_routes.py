from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from core.security import get_current_user
from models import User
from model.model_profile_progress_service import calculate_profile_progress

router = APIRouter(prefix="/user", tags=["Profile Progress"])


@router.get("/profile/progress")
async def get_profile_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    progress = await calculate_profile_progress(db, current_user)

    return {
        "user_uuid": str(current_user.uuid),
        "progress": progress
    }
