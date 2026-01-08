import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from models import ImageVideoMerge

MAX_IMAGES = 5
MAX_VIDEOS = 2


async def get_or_create_merge_media(db: AsyncSession, user_id: int) -> ImageVideoMerge:
    res = await db.execute(
        select(ImageVideoMerge).where(ImageVideoMerge.user_id == user_id)
    )
    media = res.scalars().first()
    if media:
        return media

    media = ImageVideoMerge(
        user_id=user_id,
        images=[],
        videos=[]
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


def get_next_sparse_index(items: list, limit: int) -> int:
    used = {item["index"] for item in items}
    if len(used) >= limit:
        raise HTTPException(403, "Subscribe for more images and videos")

    for i in range(limit):
        if i not in used:
            return i

    raise HTTPException(403, "Subscribe for more images and videos")


async def add_image(db, media, path):
    idx = get_next_sparse_index(media.images, MAX_IMAGES)
    media.images.append({"index": idx, "path": path})
    await db.commit()


async def add_video(db, media, path):
    idx = get_next_sparse_index(media.videos, MAX_VIDEOS)
    media.videos.append({"index": idx, "path": path})
    await db.commit()


async def delete_media_by_index(db, media, media_type: str, index: int):
    items = media.images if media_type == "image" else media.videos
    found = next((i for i in items if i["index"] == index), None)
    if not found:
        raise HTTPException(404, "Media not found")

    if os.path.exists(found["path"]):
        os.remove(found["path"])

    items.remove(found)
    await db.commit()


async def delete_all_media(db, media):
    for item in media.images + media.videos:
        if os.path.exists(item["path"]):
            os.remove(item["path"])

    media.images = []
    media.videos = []
    await db.commit()
