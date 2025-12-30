from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import cast, String, select, delete

import os, time, shutil
from models import WorkType
from admin.schema_work import *
from admin.service_work import *

from core.deps import get_db, get_current_admin

router = APIRouter(prefix="/admin/worktype", tags=["Admin Work Type"])

# Create WorkType
# @router.post("/", status_code=status.HTTP_201_CREATED,response_model=WorkTypeOut)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_work_type_api(
    data: WorkTypeCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    worktype, err = await create_work_type(db, data, current_admin.id)
    if err:
        raise HTTPException(status_code=400, detail=err)

    return worktype

# Update WorkType by UUID
@router.patch("/{uuid}")
async def update_work_type_api(
    uuid: str,
    data: WorkTypeUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    worktype, err = await update_work_type(db, uuid, data, current_admin.id)
    if err:
        raise HTTPException(status_code=404, detail=err)
    return worktype


# Soft Delete
@router.delete("/{uuid}")
async def delete_work_type_api(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(WorkType).where(WorkType.uuid == UUID(uuid))
    )
    worktype = result.scalar_one_or_none()

    if not worktype:
        raise HTTPException(status_code=404, detail="Work Type not found")

    await db.delete(worktype)
    await db.commit()

    return {"message": "Work Type permanently deleted"}


# GET all work type (admin)
@router.get("/")
async def get_all_work_type(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(WorkType)
        .where(WorkType.is_delete == False)
        .order_by(WorkType.is_order.asc())
    )
    return result.scalars().all()


# GET slider by UUID (admin)
@router.get("/{uuid}")
async def get_work_type_by_uuid(
    uuid: str,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(WorkType).where(
            WorkType.uuid == UUID(uuid),
            WorkType.is_delete == False
        )
    )
    work_type = result.scalar_one_or_none()

    if not work_type:
        raise HTTPException(status_code=404, detail="Work Type not found")

    return work_type




