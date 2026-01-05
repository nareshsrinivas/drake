from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import UserSocialLink
from uuid import UUID

# -------- ADD / UPDATE LINKS --------
async def add_social_links(db: AsyncSession, user_id: int, data):
    # check if already exists
    result = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user_id)
    )
    link = result.scalars().first()

    if link:
        # update
        for field, value in data.dict(exclude_unset=True).items():
            setattr(link, field, value)
    else:
        link = UserSocialLink(
            user_id=user_id,
            **data.dict(exclude_unset=True)
        )
        db.add(link)

    await db.commit()
    await db.refresh(link)
    return link


# -------- GET LINKS --------
async def get_all_links(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user_id)
    )
    link = result.scalars().first()

    if not link:
        raise HTTPException(404, "No social links found")

    return [link]

# ---- patch
async def patch_social_links(
    db: AsyncSession,
    user_id: int,
    data
):
    result = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user_id)
    )
    link = result.scalars().first()

    if not link:
        raise HTTPException(404, "Social links not found")

    # partial update
    for field, value in data.dict(exclude_unset=True).items():
        setattr(link, field, value)

    await db.commit()
    await db.refresh(link)
    return link

# -------- DELETE --------
async def delete_social_link(db: AsyncSession, user_id: int, link_uuid: UUID):
    result = await db.execute(
        select(UserSocialLink)
        .where(UserSocialLink.uuid == link_uuid, UserSocialLink.user_id == user_id)
    )
    link = result.scalars().first()

    if not link:
        raise HTTPException(404, "Link not found")

    await db.delete(link)
    await db.commit()

