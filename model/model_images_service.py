import os
import json
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models import Image_Videos, ModelImages, Image_Videos


MAX_FREE_IMAGES = 5  # future: dynamic


async def get_or_create_media(db: AsyncSession, user_id: int) -> Image_Videos:
    res = await db.execute(
        select(Image_Videos).where(Image_Videos.user_id == user_id)
    )
    media = res.scalars().first()
    if media:
        return media

    media = Image_Videos(user_id=user_id)
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def get_next_image_index(
    db: AsyncSession,
    media_uuid,
    limit: int
) -> int:
    res = await db.execute(
        select(ModelImages.image_index)
        .where(ModelImages.media_uuid == media_uuid)
    )
    used = {r[0] for r in res.fetchall()}

    if len(used) >= limit:
        raise HTTPException(
            status_code=403,
            detail="Subscribe to add more images"
        )

    for i in range(limit):
        if i not in used:
            return i

    raise HTTPException(400, "Image limit reached")

async def add_image(
    db: AsyncSession,
    user_id: int,
    image_path: str
):
    media = await get_or_create_media(db, user_id)
    index = await get_next_image_index(db, media.uuid, MAX_FREE_IMAGES)

    img = ModelImages(
        media_uuid=media.uuid,
        image_index=index,
        image_path=image_path
    )
    db.add(img)
    await db.commit()


async def get_images(db: AsyncSession, user_id: int):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelImages)
        .where(ModelImages.media_uuid == media.uuid)
        .order_by(ModelImages.image_index)
    )
    return res.scalars().all()


async def replace_image_by_index(
    db: AsyncSession,
    user_id: int,
    index: int,
    new_path: str
):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelImages)
        .where(
            ModelImages.media_uuid == media.uuid,
            ModelImages.image_index == index
        )
    )
    img = res.scalars().first()

    if not img:
        raise HTTPException(404, "Image not found")

    # delete old file
    if os.path.exists(img.image_path):
        os.remove(img.image_path)

    img.image_path = new_path
    await db.commit()


async def delete_image_by_index(
    db: AsyncSession,
    user_id: int,
    index: int
):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelImages)
        .where(
            ModelImages.media_uuid == media.uuid,
            ModelImages.image_index == index
        )
    )
    img = res.scalars().first()
    if not img:
        raise HTTPException(404, "Image not found")

    if os.path.exists(img.image_path):
        os.remove(img.image_path)

    await db.delete(img)
    await db.commit()


async def delete_all_images(db: AsyncSession, user_id: int):
    media = await get_or_create_media(db, user_id)

    res = await db.execute(
        select(ModelImages.image_path)
        .where(ModelImages.media_uuid == media.uuid)
    )
    for (path,) in res.fetchall():
        if os.path.exists(path):
            os.remove(path)

    await db.execute(
        delete(ModelImages)
        .where(ModelImages.media_uuid == media.uuid)
    )
    await db.commit()
