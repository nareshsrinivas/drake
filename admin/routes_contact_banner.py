from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException, status, Request
from typing import Optional
from sqlalchemy.orm import Session
from core.deps import get_db,get_current_admin
from admin.schema_contact_banner import ContactBannerOut
from admin.service_contact_banner import (
    create_contact_banner,
    update_contact_banner,
    hard_delete_banner,
    get_contact_banner_any_by_uuid,
    get_contact_banner_by_uuid,
    get_all_contact_banners
)

router = APIRouter(prefix="/admin/contact-banner", tags=["Admin Contact Banner"])

def parse_contact_banner_media(request: Request, banner):
    base = str(request.base_url).rstrip("/")

    banner_image = None
    contact_form_image = None

    if getattr(banner, "banner_image", None):
        banner_image = f"{base}/{banner.banner_image}"

    if getattr(banner, "contact_form_image", None):
        contact_form_image = f"{base}/{banner.contact_form_image}"

    return banner_image, contact_form_image



# ======================
# CREATE
# ======================
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_banner(
    request: Request,
    banner_title: str = Form(...),
    banner_description: str = Form(...),
    banner_image: Optional[UploadFile] = File(None),
    contact_info_email: str = Form(...),
    contact_info_phone: str = Form(...),
    contact_info_day: str = Form(...),
    contact_info_time: str = Form(...),
    contact_form_title: str = Form(...),
    contact_form_small_desc: str = Form(...),
    contact_form_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    data = {
        "banner_title": banner_title,
        "banner_description": banner_description,
        "contact_info_email": contact_info_email,
        "contact_info_phone": contact_info_phone,
        "contact_info_day": contact_info_day,
        "contact_info_time": contact_info_time,
        "contact_form_title": contact_form_title,
        "contact_form_small_desc": contact_form_small_desc
    }

    banner = await create_contact_banner(db, data, banner_image, contact_form_image, current_admin)
    media = parse_contact_banner_media(request, banner)

    return {**banner.__dict__}


# ======================
# GET ALL
# ======================
@router.get("/", response_model=list[ContactBannerOut])
async def get_all_banners(
    db: Session = Depends(get_db),
    user = Depends(get_current_admin)
):
    return await get_all_contact_banners(db)


# ======================
# GET BY UUID
# ======================
@router.get("/{uuid}", response_model=ContactBannerOut)
async def get_banner(
    uuid: str,
    db: Session = Depends(get_db),
    user = Depends(get_current_admin)
):
    banner = await get_contact_banner_by_uuid(db, uuid)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


# ======================
# PUT (FULL UPDATE)
# ======================
@router.put("/{uuid}")
async def update_banner(
    request: Request,
    uuid: str,
    banner_title: str = Form(...),
    banner_description: str = Form(...),
    banner_image: Optional[UploadFile] = File(None),
    contact_info_email: str = Form(...),
    contact_info_phone: str = Form(...),
    contact_info_day: str = Form(...),
    contact_info_time: str = Form(...),
    contact_form_title: str = Form(...),
    contact_form_small_desc: str = Form(...),
    contact_form_image: Optional[UploadFile] = File(None),
    db = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # ✅ STEP 1: FETCH
    banner = await get_contact_banner_by_uuid(db, uuid)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    # ✅ STEP 2: UPDATE
    data = {
        "banner_title": banner_title,
        "banner_description": banner_description,
        "contact_info_email": contact_info_email,
        "contact_info_phone": contact_info_phone,
        "contact_info_day": contact_info_day,
        "contact_info_time": contact_info_time,
        "contact_form_title": contact_form_title,
        "contact_form_small_desc": contact_form_small_desc
    }

    banner = await update_contact_banner(
        db, banner, data, banner_image, contact_form_image, current_admin
    )
    return banner


# ======================
# PATCH (PARTIAL UPDATE)
# ======================
@router.patch("/{uuid}")
async def patch_banner(
    uuid: str,
    data: dict,
    db = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # ✅ FETCH
    banner = await get_contact_banner_by_uuid(db, uuid)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    # ✅ UPDATE (no images)
    banner = await update_contact_banner(
        db, banner, data, None, None, current_admin
    )
    return banner



# ======================
# DELETE (SOFT)
# ======================
@router.delete("/{uuid}")
async def delete_banner(
    uuid: str,
    db = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    # ✅ STEP 1: FETCH ORM OBJECT
    banner = await get_contact_banner_any_by_uuid(db, uuid)
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")

    # ✅ STEP 2: HARD DELETE
    await hard_delete_banner(db, banner)

    return {"message": "Banner permanently deleted"}

