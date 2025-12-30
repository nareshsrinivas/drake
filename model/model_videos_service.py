import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from models import Image_Videos


# ---------------- HELPERS ---------------- #

async def get_media(db: AsyncSession, user_id: int) -> Image_Videos:
    result = await db.execute(
        select(Image_Videos).where(Image_Videos.user_id == user_id)
    )
    media = result.scalars().first()

    if not media:
        media = Image_Videos(user_id=user_id)
        db.add(media)
        await db.commit()
        await db.refresh(media)

    return media


def ensure_single_media(media: Image_Videos, mode: str):
    """
    mode = 'video' or 'link'
    """
    if media.video or media.video_url:
        raise HTTPException(
            status_code=403,
            detail=f"Subscribe to add more {mode}s"
        )


# ---------------- VIDEO FILE ---------------- #

async def save_video_path(db: AsyncSession, user_id: int, path: str):
    media = await get_media(db, user_id)

    ensure_single_media(media, "video")

    media.video = path
    media.video_url = None
    await db.commit()


async def replace_video_path(db: AsyncSession, user_id: int, new_path: str):
    media = await get_media(db, user_id)

    if not media.video:
        raise HTTPException(404, "No video found")

    if media.video and os.path.exists(media.video):
        os.remove(media.video)

    media.video = new_path
    await db.commit()


# ---------------- VIDEO LINK ---------------- #

async def save_video_link(db: AsyncSession, user_id: int, url: str):
    media = await get_media(db, user_id)

    ensure_single_media(media, "link")

    media.video_url = url
    media.video = None
    await db.commit()


async def replace_video_link(
    db: AsyncSession,
    user_id: int,
    new_url: str
):
    media = await get_media(db, user_id)

    if media.video:
        raise HTTPException(
            status_code=400,
            detail="Cannot update link when video file exists"
        )

    if not media.video_url:
        raise HTTPException(
            status_code=404,
            detail="No video link found"
        )

    media.video_url = new_url
    await db.commit()

# ---------------- DELETE ---------------- #
async def delete_video(db: AsyncSession, user_id: int):
    media = await get_media(db, user_id)

    if not media.video and not media.video_url:
        raise HTTPException(404, "No media found")

    if media.video and os.path.exists(media.video):
        os.remove(media.video)

    media.video = None
    media.video_url = None
    await db.commit()
