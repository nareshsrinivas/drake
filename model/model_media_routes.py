from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_current_user, get_db
from model.model_media_service import save_media, get_media_by_user_id
from utils.file_upload import save_file

router = APIRouter(prefix="/media", tags=["Model Media"])


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
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    media = await get_media_by_user_id(db, user.id)

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    return media







# social links are present here
# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
# import json
# from sqlalchemy.ext.asyncio import AsyncSession
# from core.deps import get_current_user, get_db
# from model.model_media_service import save_media
# from utils.file_upload import save_file
# from model.model_media_service import get_media_by_user_id
#
#
# router = APIRouter(prefix="/media", tags=["Model Media"])
#
# @router.post("/upload", status_code=status.HTTP_201_CREATED)
# async def upload(
#     kind: str = Form(...),
#     file: UploadFile = File(...),
#     social_links: str | None = Form(None),
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user)
# ):
#
#     allowed = [
#         "full_body_front",
#         "full_body_left_side",
#         "full_body_right_side",
#         "head_shot",
#         "profile_photo",
#         "introduction_video"
#     ]
#
#     if kind not in allowed:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid field. Allowed fields: {allowed}"
#         )
#
#     # Save file
#     url = await save_file(file, "media")
#
#     # Parse social links
#     social = None
#     if social_links:
#         try:
#             social = json.loads(social_links)
#         except:
#             raise HTTPException(status_code=400, detail="Invalid JSON in social_links")
#
#     # Save media and social links
#     media = await save_media(db, user.id, kind, url, social)
#
#     return {
#         "message": "Uploaded",
#         "field": kind,
#         "url": url,
#         "social_links": media.social_links
#     }
#
#
#
# @router.get("/")
# async def get_current_user_media(
#     db: AsyncSession = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     media = await get_media_by_user_id(db, user.id)
#
#     if not media:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Media not found",
#         )
#
#     return media
