import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from models import ContactBanner, AdminUser
from uuid import UUID
from sqlalchemy import cast, String, select

UPLOAD_DIR = "uploads/contact_banner"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_image(image: UploadFile):
    ext = image.filename.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(image.file.read())

    return file_path.replace("\\", "/")


# ======================
# CREATE
# ======================
async def create_contact_banner(
    db: Session,
    data: dict,
    banner_image: UploadFile | None,
    form_image: UploadFile | None,
    user
):
    banner = ContactBanner(
        banner_title=data["banner_title"],
        banner_description=data["banner_description"],
        banner_image=save_image(banner_image) if banner_image else None,

        contact_info_email=data["contact_info_email"],
        contact_info_phone=data["contact_info_phone"],
        contact_info_day=data["contact_info_day"],
        contact_info_time=data["contact_info_time"],

        contact_form_image=save_image(form_image) if form_image else None,
        contact_form_title=data["contact_form_title"],
        contact_form_small_desc=data["contact_form_small_desc"],

        created_by=user.id,
        updated_by=user.id
    )

    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


# ======================
# GET BY UUID
# ======================
async def get_contact_banner_by_uuid(db: Session, uuid: str):
    result = await db.execute(
        select(ContactBanner).where(
            ContactBanner.uuid == UUID(uuid),
            ContactBanner.is_delete == False
        )
    )
    return result.scalar_one_or_none()


# ======================
# GET ALL
# ======================
async def get_all_contact_banners(db: Session):
    result = await db.execute(
        select(ContactBanner).where(ContactBanner.is_delete == False)
    )
    return result.scalars().all()


# ======================
# UPDATE (PUT / PATCH)
# ======================
async def update_contact_banner(
    db: Session,
    banner: ContactBanner,
    data: dict,
    banner_image: UploadFile | None,
    form_image: UploadFile | None,
    user
):
    for key, value in data.items():
        setattr(banner, key, value)

    if banner_image:
        banner.banner_image = save_image(banner_image)

    if form_image:
        banner.contact_form_image = save_image(form_image)

    banner.updated_by = user.id

    await db.commit()
    await db.refresh(banner)
    return banner




# ======================
# GET ANY (FOR DELETE)
# ======================
async def get_contact_banner_any_by_uuid(db: Session, uuid: str):
    result = await db.execute(
        select(ContactBanner).where(
            ContactBanner.uuid == UUID(uuid)
        )
    )
    return result.scalar_one_or_none()

# ======================
# HARD DELETE
# ======================
async def hard_delete_banner(db: Session, banner: ContactBanner):
    await db.delete(banner)
    await db.commit()
    return True

