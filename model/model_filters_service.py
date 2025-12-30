from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import ModelFilter
from model.model_filters_schema import ModelFilterCreate, ModelFilterUpdate


async def create_model_filter(db: AsyncSession, data: ModelFilterCreate) -> ModelFilter:
    new_filter = ModelFilter(**data.dict())
    db.add(new_filter)
    await db.commit()
    await db.refresh(new_filter)
    return new_filter


async def get_model_filter(db: AsyncSession, filter_id: int) -> ModelFilter | None:
    return await db.get(ModelFilter, filter_id)


async def get_model_filters(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    gender: str | None = None,
    age_range_min: int | None = None,
    age_range_max: int | None = None,
    height_min: float | None = None,
    height_max: float | None = None,
    hair_color: str | None = None,
):
    query = select(ModelFilter)

    if gender is not None:
        query = query.where(ModelFilter.gender == gender)

    if age_range_min is not None:
        query = query.where(ModelFilter.age_range_min >= age_range_min)

    if age_range_max is not None:
        query = query.where(ModelFilter.age_range_max <= age_range_max)

    if height_min is not None:
        query = query.where(ModelFilter.height_min >= height_min)

    if height_max is not None:
        query = query.where(ModelFilter.height_max <= height_max)

    if hair_color is not None:
        query = query.where(ModelFilter.hair_color == hair_color)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_model_filter(
    db: AsyncSession, filter_id: int, data: ModelFilterUpdate
) -> ModelFilter | None:
    db_filter = await db.get(ModelFilter, filter_id)
    if not db_filter:
        return None

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_filter, key, value)

    await db.commit()
    await db.refresh(db_filter)
    return db_filter

async def delete_model_filter(db: AsyncSession, filter_id: int) -> bool:
    db_filter = await db.get(ModelFilter, filter_id)
    if not db_filter:
        return False

    await db.delete(db_filter)
    await db.commit()
    return True
