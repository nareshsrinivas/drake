# admin/routes_slider.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
import os, time, shutil

from admin.schema_slider import SliderCreate, SliderUpdate, SliderOut
from admin.service_slider import (
    create_slider,
    update_slider,
    # set_slider_image,
    soft_delete_slider,
    get_all_sliders_service,
    get_slider_by_uuid_service
)
from core.deps import get_db, get_current_admin
from fastapi import Request
from core.media import parse_media



router = APIRouter(prefix="/admin/slider", tags=["Admin Slider"])

UPLOAD_DIR = "uploads/home_slider"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ----------------------sparse media for slider image -----------------------------
def parse_slider_media(request: Request, slider):
    base = str(request.base_url).rstrip("/")

    image = None
    if getattr(slider, "image", None):
        image = f"{base}/{slider.image}"

    return image


# ---------------------------------------------
# CREATE SLIDER + IMAGE (Multipart)
# ---------------------------------------------

@router.post("/", status_code=201)
async def create_slider_api(
    request: Request,
    slider_title: str = Form(None),
    is_order: int = Form(0),
    slider_type: int = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    data = SliderCreate(
        slider_title=slider_title,
        is_order=is_order,
        slider_type=slider_type
    )

    slider, err = await create_slider(db, data, current_admin.id)
    if err:
        raise HTTPException(400, err)

    # return slider


    if image:
        ts = int(time.time())
        file_name = f"{ts}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        slider.image = file_path.replace("\\", "/")
        await db.commit()
        await db.refresh(slider)

    image_url = parse_slider_media(request, slider)

    return {
        **slider.__dict__,
        "image": image_url
    }


# ---------------------------------------------
# UPDATE SLIDER + IMAGE (Multipart)
# ---------------------------------------------

# @router.patch("/{uuid}", response_model=SliderOut)
@router.patch("/{uuid}")
async def update_slider_api(
    request: Request,
    uuid: str,
    slider_title: str = Form(None),
    is_order: int = Form(None),
    slider_type: int = Form(None),
    image: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    data = SliderUpdate(
        slider_title=slider_title,
        is_order=is_order,
        slider_type=slider_type
    )

    slider, err = await update_slider(db, uuid, data, current_admin.id)
    if err:
        raise HTTPException(status_code=404, detail=err)

    if image:
        ts = int(time.time())
        file_name = f"{ts}_{image.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        slider.image = file_path.replace("\\", "/")
        await db.commit()
        await db.refresh(slider)

    image_url = parse_slider_media(request, slider)

    return {
        **slider.__dict__,
        "image": image_url
    }



# ---------------------------------------------
# SOFT DELETE
# ---------------------------------------------
@router.delete("/{uuid}")
async def delete_slider_api(
    uuid: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    ok, err = await soft_delete_slider(db, uuid)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return {"message": "Slider deleted"}



# ---------------------------------------------
# GET ALL SLIDERS (Admin)
# ---------------------------------------------

# @router.get("/", response_model=list[SliderOut])
@router.get("/")
async def get_all_sliders_api(
    request: Request,
    slider_type: int | None = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    sliders = await get_all_sliders_service(db, slider_type)

    response = []
    for slider in sliders:
        response.append({
            **slider.__dict__,
            "image": parse_slider_media(request, slider)
        })

    return response




# ---------------------------------------------
# GET SLIDER BY UUID (Admin)
# ---------------------------------------------

# @router.get("/{uuid}", response_model=SliderOut)
@router.get("/{uuid}")
async def get_slider_by_uuid_api(
    request: Request,
    uuid: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    slider = await get_slider_by_uuid_service(db, uuid)

    if not slider:
        raise HTTPException(status_code=404, detail="Slider not found")

    return {
        **slider.__dict__,
        "image": parse_slider_media(request, slider)
    }


