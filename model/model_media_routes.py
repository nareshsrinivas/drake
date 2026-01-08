from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_current_user, get_db
from model.model_media_service import save_media, get_media_by_user_id
from utils.file_upload import save_file

router = APIRouter(prefix="/media", tags=["Model Media"])

def parse_media(request: Request, media):
    base = str(request.base_url).rstrip("/")

    parsed = {}

    for field in [
        "full_body_front",
        "full_body_left_side",
        "full_body_right_side",
        "head_shot",
        "profile_photo",
        "introduction_video",
    ]:
        value = getattr(media, field, None)
        parsed[field] = f"{base}/{value}" if value else None

    return parsed


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(
    kind: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):

    allowed = [
        "full_body_front",
        "full_body_left_side",
        "full_body_right_side",
        "head_shot",
        "profile_photo",
        "introduction_video"
    ]

    if kind not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid field. Allowed fields: {allowed}"
        )

    # Save file
    url = await save_file(file, "media")

    # Save media
    media = await save_media(db, user.id, kind, url)

    return {
        "message": "Uploaded",
        "field": kind,
        "url": url,
    }



@router.get("/")
async def get_current_user_media(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    media = await get_media_by_user_id(db, user.id)

    if not media:
        return {}

    return parse_media(request, media)







