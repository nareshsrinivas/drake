from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import HomeSlider
from uuid import UUID

# CREATE
async def create_slider(db: AsyncSession, data, admin_id: int):
    slider = HomeSlider(
        slider_title=data.slider_title,
        is_order=data.is_order,
        slider_type=data.slider_type,
        created_by=admin_id,
        updated_by=admin_id
    )

    db.add(slider)
    await db.commit()
    await db.refresh(slider)

    return slider, None


# UPDATE
async def update_slider(db: AsyncSession, uuid: str, data, admin_id: int):

    stmt = select(HomeSlider).where(
        HomeSlider.uuid == UUID(uuid),
        HomeSlider.is_delete == False
    )

    result = await db.execute(stmt)
    slider = result.scalar_one_or_none()

    if not slider:
        return None, "Slider not found"

    if data.slider_title is not None:
        slider.slider_title = data.slider_title
    if data.is_order is not None:
        slider.is_order = data.is_order
    if data.slider_type is not None:
        slider.slider_type = data.slider_type

    slider.updated_by = admin_id

    await db.commit()
    await db.refresh(slider)

    return slider, None


# SOFT DELETE
async def soft_delete_slider(db: AsyncSession, uuid: str):

    stmt = select(HomeSlider).where(HomeSlider.uuid == UUID(uuid))
    result = await db.execute(stmt)
    slider = result.scalar_one_or_none()

    if not slider:
        return None, "Slider not found"

    await db.delete(slider)
    await db.commit()

    return True, None

# async def soft_delete_slider(db: AsyncSession, uuid: str, admin_id: int):

#     stmt = select(HomeSlider).where(HomeSlider.uuid == UUID(uuid))
#     result = await db.execute(stmt)
#     slider = result.scalar_one_or_none()

#     if not slider:
#         return None, "Slider not found"

#     slider.is_delete = True
#     slider.updated_by = admin_id

#     await db.commit()
#     return True, None


# GET ALL
async def get_all_sliders_service(db: AsyncSession, slider_type: int | None):

    stmt = select(HomeSlider).where(HomeSlider.is_delete == False)

    if slider_type is not None:
        stmt = stmt.where(HomeSlider.slider_type == slider_type)

    stmt = stmt.order_by(HomeSlider.is_order.asc())

    result = await db.execute(stmt)
    return result.scalars().all()


# GET BY UUID
async def get_slider_by_uuid_service(db: AsyncSession, uuid: str):

    stmt = select(HomeSlider).where(
        HomeSlider.uuid == UUID(uuid),
        HomeSlider.is_delete == False
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()

