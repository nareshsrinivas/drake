from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.deps import get_current_user, get_db
from model.model_professional_schema import ModelProfessionalSchema
from model.model_professional_service import (
    create_or_update_professional,
    get_professional,
    delete_professional,
    get_professional_by_user_id
)

router = APIRouter(prefix="/professional", tags=["Model Professional"])


# existing POST (unchanged)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_or_update(
    data: ModelProfessionalSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    return await create_or_update_professional(db, user.id, data)



@router.get("/")
async def get_current_user_professional(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    prof = await get_professional_by_user_id(db, user.id)

    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return prof


# existing GET (unchanged)
@router.get("/{uuid}")
async def get(uuid: str, db: AsyncSession = Depends(get_db)):
    prof = await get_professional(db, uuid)
    if not prof:
        raise HTTPException(404, "Not found")
    return prof

@router.patch("/{uuid}")
async def update_professional_by_uuid(
    uuid: str,
    data: ModelProfessionalSchema,
    db: AsyncSession = Depends(get_db),
):
    prof = await get_professional(db, uuid)
    if not prof:
        raise HTTPException(404, "Profile not found")

    # reuse existing logic
    return await create_or_update_professional(
        db=db,
        user_id=prof.user_id,
        data=data,
    )


@router.patch("/")
async def update_my_professional(
    data: ModelProfessionalSchema,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    prof = await get_professional_by_user_id(db, user.id)

    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return await create_or_update_professional(
        db=db,
        user_id=user.id,
        data=data,
    )



@router.delete("/{uuid}")
async def delete(uuid: str, db: AsyncSession = Depends(get_db)):
    deleted = await delete_professional(db, uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}



@router.delete("/")
async def delete_my_professional(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    prof = await get_professional_by_user_id(db, user.id)

    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    await delete_professional(db, str(prof.uuid))

    return {"message": "Profile deleted successfully"}
