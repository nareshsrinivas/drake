import os
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from models import Image_Videos, ModelVideos

MAX_FREE_MEDIA = 2


# ---------- SAFE JSON ----------

def safe_json_list(value) -> list:
    if not value or not isinstance(value, str):
        return []

    value = value.strip()
    if not value:
        return []

    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


# ---------- MEDIA ----------

async def get_or_create_media(db: AsyncSession, user_id: int) -> Image_Videos:
    res = await db.execute(
        select(Image_Videos).where(Image_Videos.user_id == user_id)
    )
    media = res.scalars().first()

    if media:
        return media

    media = Image_Videos(user_id=user_id, video_url="[]")
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


# ---------- ADD VIDEO FILE ----------

async def add_video(db: AsyncSession, user_id: int, path: str):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelVideos).where(ModelVideos.media_uuid == media.uuid)
    )
    videos = res.scalars().all()

    links = safe_json_list(media.video_url)

    if len(videos) + len(links) >= MAX_FREE_MEDIA:
        raise HTTPException(403, "Subscribe to add more videos or links")

    db.add(ModelVideos(
        media_uuid=media.uuid,
        video_index=len(videos),
        video_path=path
    ))
    await db.commit()


# ---------- ADD VIDEO LINK ----------

async def add_video_link(db: AsyncSession, user_id: int, url: str):
    media = await get_or_create_media(db, user_id)

    links = safe_json_list(media.video_url)

    res = await db.execute(
        select(ModelVideos).where(ModelVideos.media_uuid == media.uuid)
    )
    videos_count = len(res.scalars().all())

    if videos_count + len(links) >= MAX_FREE_MEDIA:
        raise HTTPException(403, "Subscribe to add more videos or links")

    links.append(url)
    media.video_url = json.dumps(links)
    await db.commit()


# --------Patch video link -----
async def update_video_link_by_index(
    db: AsyncSession,
    user_id: int,
    index: int,
    new_url: str
):
    media = await get_or_create_media(db, user_id)

    links = safe_json_list(media.video_url)

    if index < 0 or index >= len(links):
        raise HTTPException(status_code=404, detail="Video link not found")

    links[index] = new_url
    media.video_url = json.dumps(links)
    await db.commit()

# ---------- GET ----------

async def get_videos(db: AsyncSession, user_id: int):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelVideos)
        .where(ModelVideos.media_uuid == media.uuid)
        .order_by(ModelVideos.video_index)
    )
    return media, res.scalars().all()


# ---------- REPLACE VIDEO ----------

async def replace_video_by_index(
    db: AsyncSession,
    user_id: int,
    index: int,
    new_path: str
):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelVideos).where(
            ModelVideos.media_uuid == media.uuid,
            ModelVideos.video_index == index
        )
    )
    video = res.scalars().first()

    if not video:
        raise HTTPException(404, "Video not found")

    if os.path.exists(video.video_path):
        os.remove(video.video_path)

    video.video_path = new_path
    await db.commit()


# ---------- DELETE VIDEO ----------

async def delete_video_by_index(
    db: AsyncSession,
    user_id: int,
    index: int
):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelVideos).where(
            ModelVideos.media_uuid == media.uuid,
            ModelVideos.video_index == index
        )
    )
    video = res.scalars().first()

    if not video:
        raise HTTPException(404, "Video not found")

    if os.path.exists(video.video_path):
        os.remove(video.video_path)

    await db.delete(video)
    await db.commit()



