import os
import uuid
from typing import Optional

from fastapi import (
    APIRouter, UploadFile, File,
    Depends, Request, HTTPException,
    status, Form
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import HttpUrl

from database import get_db
from core.security import get_current_user, oauth2_scheme
from .model_videos_service import (
    add_video,
    get_videos,
    replace_video_by_index,
    delete_video_by_index,
    add_video_link,
    safe_json_list,
    update_video_link_by_index
)
from .model_videos_schema import VideoResponse

router = APIRouter(prefix="/video", tags=["Model Video"])

UPLOAD_DIR = "uploads/model_images_videos/model_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime"}
MAX_VIDEO_MB = 10
MAX_VIDEO_BYTES = MAX_VIDEO_MB * 1024 * 1024


# ---------- HELPERS ----------

async def save_upload_file(file: UploadFile, path: str):
    size = 0
    with open(path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_VIDEO_BYTES:
                f.close()
                os.remove(path)
                raise HTTPException(
                    status_code=400,
                    detail="Video size must not exceed 10 MB"
                )
            f.write(chunk)


# ---------- GET ----------

@router.get("/", response_model=VideoResponse, dependencies=[Depends(oauth2_scheme)])
async def get_video(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    base = str(request.base_url).rstrip("/")
    media, videos = await get_videos(db, current_user.id)

    return {
        "videos": [
            {"index": v.video_index, "url": f"{base}/{v.video_path}"}
            for v in videos
        ],
        "video_url": safe_json_list(media.video_url)
    }


# ---------- UPLOAD VIDEO ----------

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(400, "Invalid video type")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    await save_upload_file(file, path)

    await add_video(db, current_user.id, path)
    return {"message": "Video uploaded successfully"}


# ---------- ADD LINK ----------

@router.post("/link", status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def add_link(
    video_url: HttpUrl,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await add_video_link(db, current_user.id, str(video_url))
    return {"message": "Video link added successfully"}


# ---------- PATCH LINK ----------

@router.patch("/link", dependencies=[Depends(oauth2_scheme)])
async def update_video_link(
    index: int,
    video_url: HttpUrl,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await update_video_link_by_index(
        db=db,
        user_id=current_user.id,
        index=index,
        new_url=str(video_url),
    )
    return {"message": "Video link updated successfully"}


# ---------- REPLACE VIDEO ----------

@router.patch("/", dependencies=[Depends(oauth2_scheme)])
async def replace_video(
    index: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(400, "Invalid video type")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    await save_upload_file(file, path)

    await replace_video_by_index(db, current_user.id, index, path)
    return {"message": "Video updated successfully"}


# ---------- DELETE ----------

@router.delete("/", dependencies=[Depends(oauth2_scheme)])
async def delete_video(
    index: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_video_by_index(db, current_user.id, index)
    return {"message": "Video deleted successfully"}


# ---------- VIDEO + LINK ----------

@router.post(
    "/video-link",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(oauth2_scheme)]
)
async def upload_video_and_or_link(
    request: Request,
    file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    form = await request.form()
    has_video_url = "video_url" in form
    raw_video_url = form.get("video_url")

    if not file and not has_video_url:
        raise HTTPException(
            status_code=400,
            detail="Either video file or video_url is required"
        )

    if file:
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(400, "Invalid video type")

        filename = f"{uuid.uuid4()}_{file.filename}"
        path = f"{UPLOAD_DIR}/{filename}"

        await save_upload_file(file, path)
        await add_video(db, current_user.id, path)

    if has_video_url:
        cleaned_url = str(raw_video_url).strip()
        if cleaned_url and cleaned_url != "https://example.com/":
            await add_video_link(db, current_user.id, cleaned_url)

    return {"message": "Video and/or video link added successfully"}























