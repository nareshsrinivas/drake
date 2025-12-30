import uuid
import os
from fastapi import APIRouter, UploadFile, File, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from core.security import get_current_user, oauth2_scheme
from .model_images_service import (
    add_image,
    get_images,
    delete_image_by_index,
    delete_all_images,
    replace_image_by_index
)
from .model_images_schema import ImagesResponse

router = APIRouter(prefix="/images", tags=["Model Images"])

UPLOAD_DIR = "uploads/model_images_videos/model_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {"image/png", "image/jpeg"}


@router.get("/", response_model=ImagesResponse, dependencies=[Depends(oauth2_scheme)])
async def list_images(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    base = str(request.base_url).rstrip("/")
    images = await get_images(db, current_user.id)

    return {
        "images": [
            {"index": img.image_index, "url": f"{base}/{img.image_path}"}
            for img in images
        ]
    }


@router.post("/",status_code=status.HTTP_201_CREATED, dependencies=[Depends(oauth2_scheme)])
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid image type")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    await add_image(db, current_user.id, path)
    return {"message": "Image added"}


@router.patch("/", dependencies=[Depends(oauth2_scheme)])
async def replace_image(
    index: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid image type")

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = f"{UPLOAD_DIR}/{filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    await replace_image_by_index(
        db,
        current_user.id,
        index,
        path
    )

    return {"message": "Image updated"}


@router.delete("/", dependencies=[Depends(oauth2_scheme)])
async def delete_image(
    index: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_image_by_index(db, current_user.id, index)
    return {"message": "Image deleted"}


@router.delete("/all", dependencies=[Depends(oauth2_scheme)])
async def delete_all(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    await delete_all_images(db, current_user.id)
    return {"message": "All images deleted"}
