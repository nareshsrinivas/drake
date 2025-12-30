from sqlalchemy.orm import Session
from sqlalchemy import cast, String, select
from datetime import datetime
from models import Skill
from fastapi.concurrency import run_in_threadpool
from uuid import UUID

async def create_skill(db: Session, data, admin_id: int):
    try:
        skill = Skill(
            title=data.title,
            other_title=data.other_title,
            is_order=data.is_order or 0,
            created_by=admin_id,
            updated_by=admin_id
        )
        db.add(skill)
        await db.commit()
        await db.refresh(skill)
        return skill, None
    except Exception as e:
        await db.rollback()
        return None, str(e)


async def update_skill(db: Session, uuid: str, data, admin_id: int):
    try:
        result = await db.execute(
            select(Skill).where(
                Skill.uuid == UUID(uuid),
                Skill.is_delete == False
            )
        )
        skill = result.scalar_one_or_none()

        if not skill:
            return None, "Skill not found"

        if data.title is not None:
            skill.title = data.title
        if data.other_title is not None:
            skill.other_title = data.other_title
        if data.is_order is not None:
            skill.is_order = data.is_order

        skill.updated_by = admin_id

        await db.commit()
        await db.refresh(skill)
        return skill, None
    except Exception as e:
        await db.rollback()
        return None, str(e)


async def delete_skill(db: Session, uuid: str):
    try:
        result = await db.execute(
            select(Skill).where(Skill.uuid == UUID(uuid))
        )
        skill = result.scalar_one_or_none()

        if not skill:
            return None, "Skill not found"

        await db.delete(skill)
        await db.commit()
        return True, None

    except Exception as e:
        await db.rollback()
        return None, str(e)




