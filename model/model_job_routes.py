from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.deps import get_db, get_current_user
from model.model_job_service import smart_search_jobs

router = APIRouter(prefix="/jobs", tags=["Model Jobs"])


@router.get("")
async def search_jobs_for_model(
    search: Union[str, int, float, None] = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.user_type != 1:
        raise HTTPException(status_code=403, detail="Only models allowed")

    return await smart_search_jobs(
        db=db,
        search=search
    )


