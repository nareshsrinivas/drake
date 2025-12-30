import os
import uuid
from fastapi import (
    status,
    APIRouter,
    UploadFile,
    File,
    Depends,
    Request,
    HTTPException
)
from sqlalchemy.ext.asyncio import AsyncSession
# from moviepy.editor import VideoFileClip
from moviepy import VideoFileClip
from pydantic import HttpUrl

from database import get_db
from core.security import get_current_user, oauth2_scheme
from .model_videos_service import (
    get_media,
    save_video_path,
    replace_video_path,
    save_video_link,
    replace_video_link,
    delete_video
)
from .model_videos_schema import VideoResponse


router = APIRouter(prefix="/video", tags=["Model Video"])

UPLOAD_DIR = "uploads/model_images_videos/model_videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime"}
MAX_VIDEO_MB = 10
MIN_DURATION = 15
MAX_DURATION = 60


# ---------------- GET ---------------- #

@router.get("/", response_model=VideoResponse, dependencies=[Depends(oauth2_scheme)])
async def get_video(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    media = await get_media(db, current_user.id)
    base = str(request.base_url).rstrip("/")

    return {
        "video": f"{base}/{media.video}" if media.video else None,
        "video_url": media.video_url
    }


# ---------------- UPLOAD VIDEO ---------------- #

@router.post("/", status_code=status.HTTP_201_CREATED,dependencies=[Depends(oauth2_scheme)])
async def upload_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(400, "Invalid video type")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_VIDEO_MB:
        raise HTTPException(400, "Max video limit is 10 MB")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as f:
        f.write(content)

    clip = VideoFileClip(path)
    if not (MIN_DURATION <= clip.duration <= MAX_DURATION):
        clip.close()
        os.remove(path)
        raise HTTPException(400, "Video must be 15–60 seconds")
    clip.close()

    await save_video_path(db, current_user.id, path)
    return {"message": "Video uploaded successfully"}


# ---------------- ADD VIDEO LINK ---------------- #

@router.post("/link", status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def add_video_link(
    video_url: HttpUrl,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await save_video_link(db, current_user.id, str(video_url))
    return {"message": "Video link added successfully"}


@router.patch("/link", dependencies=[Depends(oauth2_scheme)])
async def update_video_link(
    video_url: HttpUrl,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await replace_video_link(db, current_user.id, str(video_url))
    return {"message": "Video link updated successfully"}


# ---------------- REPLACE VIDEO ---------------- #

@router.patch("/", dependencies=[Depends(oauth2_scheme)])
async def replace_video(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(400, "Invalid video type")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)

    if size_mb > MAX_VIDEO_MB:
        raise HTTPException(400, "Max video limit is 10 MB")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as f:
        f.write(content)

    clip = VideoFileClip(path)
    if not (MIN_DURATION <= clip.duration <= MAX_DURATION):
        clip.close()
        os.remove(path)
        raise HTTPException(400, "Video must be 15–60 seconds")
    clip.close()

    await replace_video_path(db, current_user.id, path)
    return {"message": "Video updated successfully"}

# ---------------- DELETE ---------------- #

@router.delete("/", dependencies=[Depends(oauth2_scheme)])
async def remove_video(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_video(db, current_user.id)
    return {"message": "Video removed successfully"}

