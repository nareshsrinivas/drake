from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ModelMedia

async def save_media(
        db: AsyncSession, 
        user_id: int, 
        field_name: str, 
        file_url: str, 
        social_links: dict | None = None
    ):

    # Find existing media row
    result = await db.execute(
        select(ModelMedia).where(ModelMedia.user_id == user_id)
    )
    media = result.scalars().first()

    # Create new media row if not exists
    if not media:
        media = ModelMedia(
            user_id=user_id,
            created_by=user_id
        )
        db.add(media)
        await db.commit()
        await db.refresh(media)

    # Update required media field (image/video)
    setattr(media, field_name, file_url)

    # Update social links if provided
    if social_links is not None:
        media.social_links = social_links

    media.updated_by = user_id
    await db.commit()
    await db.refresh(media)

    return media


# Get media by current user
async def get_media_by_user_id(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(ModelMedia).where(ModelMedia.user_id == user_id)
    )
    return result.scalars().first()



