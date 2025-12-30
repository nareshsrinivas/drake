from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from models import WorkType


async def create_work_type(db: AsyncSession, data, admin_id: int):
    try:
        work_type = WorkType(
            work_type=data.work_type,
            is_order=data.is_order or 0,
            created_by=admin_id,
            updated_by=admin_id
        )
        db.add(work_type)
        await db.commit()
        await db.refresh(work_type)
        return work_type, None
    except Exception as e:
        await db.rollback()
        return None, str(e)


async def update_work_type(db: AsyncSession, uuid: str, data, admin_id: int):
    try:
        result = await db.execute(
            select(WorkType).where(
                WorkType.uuid == UUID(uuid),
                WorkType.is_delete == False
            )
        )
        worktype = result.scalar_one_or_none()

        if not worktype:
            return None, "Work Type not found"

        if data.work_type is not None:
            worktype.work_type = data.work_type

        if data.is_order is not None:
            worktype.is_order = data.is_order

        worktype.updated_by = admin_id

        await db.commit()
        await db.refresh(worktype)
        return worktype, None
    except Exception as e:
        await db.rollback()
        return None, str(e)


async def soft_delete_work_type(db: AsyncSession, uuid: str, admin_id: int):
    try:
        result = await db.execute(
            select(WorkType).where(
                WorkType.uuid == UUID(uuid),
                WorkType.is_delete == False
            )
        )
        worktype = result.scalar_one_or_none()

        if not worktype:
            return None, "Work Type not found"

        worktype.is_delete = True
        worktype.updated_by = admin_id

        await db.commit()
        return True, None
    except Exception as e:
        await db.rollback()
        return None, str(e)


