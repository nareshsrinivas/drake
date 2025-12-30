from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database import get_db

from model.model_filters_schema import (
    ModelFilterCreate,
    ModelFilterUpdate,
    ModelFilterResponse,
)
from model.model_filters_service import (
    create_model_filter,
    get_model_filter,
    get_model_filters,
    update_model_filter,
    delete_model_filter,
)

router = APIRouter(
    prefix= "/filters",
    tags=["Model Filters"],
)

# POST: Create a new model filter
@router.post("/", status_code=status.HTTP_201_CREATED,response_model=ModelFilterResponse)
async def create_filter(
    filter_data: ModelFilterCreate, db_session: AsyncSession = Depends(get_db)
):
    return await create_model_filter(db_session, filter_data)


# GET: Get a specific model filter by ID
@router.get("/{filter_id}", response_model=ModelFilterResponse)
async def get_filter(filter_id: int, db_session: AsyncSession = Depends(get_db)):
    db_filter = await get_model_filter(db_session, filter_id)
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    return db_filter


# GET: Get all model filters with optional query parameters
@router.get("/", response_model=List[ModelFilterResponse])
async def get_filters(
    gender: Optional[str] = None,
    age_range_min: Optional[int] = None,
    age_range_max: Optional[int] = None,
    height_min: Optional[float] = None,
    height_max: Optional[float] = None,
    hair_color: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    db_session: AsyncSession = Depends(get_db),
):
    filters = await get_model_filters(
        db_session,
        skip=skip,
        limit=limit,
        gender=gender,
        age_range_min=age_range_min,
        age_range_max=age_range_max,
        height_min=height_min,
        height_max=height_max,
        hair_color=hair_color,
    )
    return filters


# PATCH: Update an existing model filter
@router.patch("/{filter_id}", response_model=ModelFilterResponse)
async def update_filter(
    filter_id: int,
    filter_data: ModelFilterUpdate,
    db_session: AsyncSession = Depends(get_db),
):
    db_filter = await update_model_filter(db_session, filter_id, filter_data)
    if not db_filter:
        raise HTTPException(status_code=404, detail="Filter not found")
    return db_filter


# DELETE: Delete a model filter
@router.delete("/{filter_id}", response_model=bool)
async def delete_filter(filter_id: int, db_session: AsyncSession = Depends(get_db)):
    success = await delete_model_filter(db_session, filter_id)
    if not success:
        raise HTTPException(status_code=404, detail="Filter not found")
    return success


