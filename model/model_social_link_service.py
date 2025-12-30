from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models import UserSocialLink
from uuid import UUID

async def add_multiple_links(db: AsyncSession, user_id: int, links: list):
    saved = []
    for item in links:
        link = UserSocialLink(
            user_id=user_id,
            platform=item.platform,
            url=item.url
        )
        db.add(link)
        saved.append(link)

    await db.commit()

    for link in saved:
        await db.refresh(link)

    return saved


async def get_all_links(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(UserSocialLink).where(UserSocialLink.user_id == user_id)
    )
    return result.scalars().all()


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
    return True


