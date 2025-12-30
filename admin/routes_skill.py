from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

import os, time, shutil
from models import Skill
from admin.schema_skill import *
from admin.service_skill import *

from core.deps import get_db, get_current_admin

router = APIRouter(prefix="/admin/skill", tags=["Admin Skill"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_skill_api(
    data: SkillCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    skill, err = await create_skill(db, data, current_admin.id)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return skill


@router.patch("/{uuid}", response_model=SkillOut)
async def update_skill_api(
    uuid: str,
    data: SkillUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    skill, err = await update_skill(db, uuid, data, current_admin.id)
    if err:
        raise HTTPException(status_code=404, detail=err)
    return skill


@router.delete("/{uuid}")
async def delete_skill_api(
    uuid: str,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    ok, err = await delete_skill(db, uuid)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return {"message": "Skill permanently deleted"}



@router.get("/", response_model=list[SkillOut])
async def get_all_skill(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(Skill)
        .where(Skill.is_delete == False)
        .order_by(Skill.is_order.asc())
    )
    return result.scalars().all()


@router.get("/{uuid}", response_model=SkillOut)
async def get_skill_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    result = await db.execute(
        select(Skill).where(
            Skill.uuid == UUID(uuid),
            Skill.is_delete == False
        )
    )
    skill = result.scalar_one_or_none()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill
