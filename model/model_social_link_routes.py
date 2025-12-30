from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database import get_db
from core.security import get_current_user, oauth2_scheme
from .model_social_link_schema import (
    SocialLinkCreateMulti,
    SocialLinkResponse
)
from .model_social_link_service import (
    add_multiple_links,
    get_all_links,
    delete_social_link
)

router = APIRouter(prefix="/social/links", tags=["Social Links"])

# ------------------ ADD MULTIPLE LINKS ------------------
@router.post(
    "/",status_code=status.HTTP_201_CREATED,
    response_model=list[SocialLinkResponse],
    dependencies=[Depends(oauth2_scheme)]
)

async def add_links(
    data: SocialLinkCreateMulti,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await add_multiple_links(db, current_user.id, data.links)


# ------------------ GET ALL LINKS ------------------

@router.get(
    "/",
    response_model=list[SocialLinkResponse],
    dependencies=[Depends(oauth2_scheme)]
)
async def list_links(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return await get_all_links(db, current_user.id)


# ------------------ DELETE LINK BY UUID ------------------
@router.delete(
    "/{link_uuid}",
    dependencies=[Depends(oauth2_scheme)]
)
async def delete_link(
    link_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    await delete_social_link(db, current_user.id, link_uuid)
    return {"message": "Link deleted"}


