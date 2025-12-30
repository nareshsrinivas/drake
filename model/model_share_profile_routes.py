from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.deps import get_current_user
from database import get_db
from models import User

router = APIRouter(prefix="/share", tags=["Profile Sharing"])


@router.get("/profile")
async def share_profile_url(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.id

    result_user = await db.execute(select(User).where(User.id == user_id))
    user = result_user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")

    base_url = str(request.base_url).rstrip("/")

    profile_url = f"{base_url}/model/info?user_id={user_id}"

    return {
        "profile_url": profile_url
    }
