# routes/model_share_profile_routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from core.deps import get_current_user
from database import get_db
from models import User
from core.aes_encryption import aes_encrypt
from urllib.parse import quote

router = APIRouter(prefix="/share", tags=["Profile Sharing"])


@router.get("/profile")
async def share_profile_url(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, current_user.id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔑 Generate token only once (PLAIN UUID in DB)
    if not user.share_token:
        user.share_token = str(uuid.uuid4())
        db.add(user)
        await db.commit()

    # 🔐 ENCRYPT token for sharing
    encrypted_token = aes_encrypt(user.share_token)
    safe_token = quote(encrypted_token)

    base_url = str(request.base_url).rstrip("/")
    share_url = f"{base_url}/public/profile/{encrypted_token}"
    # share_url = f"{base_url}/drakeapi/public/profile/{safe_token}"

    return {
        "share_url": share_url,
        "token": encrypted_token
    }
