from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ModelProfessional
from model.model_professional_schema import ModelProfessionalSchema


def merge_arrays(existing, base, extra):
    result = []
    if existing:
        result.extend(existing)
    if base:
        result.extend(base)
    if extra:
        result.extend(extra)
    return list(set(result)) if result else None


async def create_or_update_professional(
    db: AsyncSession, user_id: int, data: ModelProfessionalSchema
):
    result = await db.execute(
        select(ModelProfessional).where(ModelProfessional.user_id == user_id)
    )
    prof = result.scalars().first()

    if not prof:
        prof = ModelProfessional(user_id=user_id)
        db.add(prof)

    payload = data.model_dump(exclude_none=True)

    # merge arrays
    prof.languages = merge_arrays(
        prof.languages,
        payload.get("languages"),
        payload.get("other_languages"),
    )

    prof.skills = merge_arrays(
        prof.skills,
        payload.get("skills"),
        payload.get("other_skills"),
    )

    prof.interested_categories = merge_arrays(
        prof.interested_categories,
        payload.get("interested_categories"),
        payload.get("other_interested_categories"),
    )

    # normal fields
    for field in [
        "professional_experience",
        "experience_details",
        "willing_to_travel",
    ]:
        if field in payload:
            setattr(prof, field, payload[field])

    await db.commit()
    await db.refresh(prof)
    return prof


async def get_professional(db: AsyncSession, uuid: str):
    result = await db.execute(
        select(ModelProfessional).where(ModelProfessional.uuid == uuid)
    )
    return result.scalars().first()


async def delete_professional(db: AsyncSession, uuid: str):
    prof = await get_professional(db, uuid)
    if not prof:
        return False

    await db.delete(prof)
    await db.commit()
    return True



# Get professional profile by current user
async def get_professional_by_user_id(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(ModelProfessional).where(ModelProfessional.user_id == user_id)
    )
    return result.scalars().first()

