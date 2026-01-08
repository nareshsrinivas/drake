import uuid
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from core.security import get_current_user, oauth2_scheme
from .model_images_videos_service import *
from .model_images_videos_schema import ImagesVideosResponse

router = APIRouter(prefix="/images-videos", tags=["Images + Videos"])

IMG_DIR = "uploads/model_images_videos/model_images"
VID_DIR = "uploads/model_images_videos/model_videos"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(VID_DIR, exist_ok=True)


@router.get("/", response_model=ImagesVideosResponse, dependencies=[Depends(oauth2_scheme)])
async def get_media(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    base = str(request.base_url).rstrip("/")
    media = await get_or_create_merge_media(db, current_user.id)

    return {
        "images": [
            {"index": i["index"], "url": f"{base}/{i['path']}"}
            for i in media.images
        ],
        "videos": [
            {"index": v["index"], "url": f"{base}/{v['path']}"}
            for v in media.videos
        ],
    }


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def upload_media(
    images: list[UploadFile] | None = File(None),
    videos: list[UploadFile] | None = File(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not images and not videos:
        raise HTTPException(400, "At least one image or video required")

    media = await get_or_create_merge_media(db, current_user.id)

    if images:
        for file in images:
            name = f"{uuid.uuid4()}_{file.filename}"
            path = f"{IMG_DIR}/{name}"
            with open(path, "wb") as f:
                f.write(await file.read())
            await add_image(db, media, path)

    if videos:
        for file in videos:
            name = f"{uuid.uuid4()}_{file.filename}"
            path = f"{VID_DIR}/{name}"
            with open(path, "wb") as f:
                f.write(await file.read())
            await add_video(db, media, path)

    return {"message": "Images and videos uploaded successfully"}


@router.delete("/", dependencies=[Depends(oauth2_scheme)])
async def delete_by_index(
    media_type: str,
    index: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    media = await get_or_create_merge_media(db, current_user.id)
    await delete_media_by_index(db, media, media_type, index)
    return {"message": "Media deleted"}


@router.delete("/all", dependencies=[Depends(oauth2_scheme)])
async def delete_all(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    media = await get_or_create_merge_media(db, current_user.id)
    await delete_all_media(db, media)
    return {"message": "All media deleted"}
