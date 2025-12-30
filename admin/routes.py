from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from admin.service import (
    create_admin,
    admin_login,
    update_admin,
    delete_admin,
    admin_update_user_status
)
from auth.schemas import AdminRegister, AdminLogin, AdminUpdate, AdminOut
from core.deps import get_db, get_current_admin
from models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/register", response_model=AdminOut, status_code=201)
async def admin_register(
        data: AdminRegister,
        db: AsyncSession = Depends(get_db)
):
    admin, err = await create_admin(db, data)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return admin


@router.post("/login")
async def admin_login_api(
        data: AdminLogin,
        db: AsyncSession = Depends(get_db)
):
    resp, err = await admin_login(db, data.email, data.password)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return resp


# ---------------- UPDATE ADMIN (BY UUID) ---------------- #

@router.patch("/update/{uuid}")
async def update_admin_api(
        uuid: str,
        data: AdminUpdate,
        db: AsyncSession = Depends(get_db),
):
    admin, err = await update_admin(db, uuid, data)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return {
        "message": "Updated",
        "admin": admin
    }


# ---------------- DELETE ADMIN (BY UUID) ---------------- #

@router.delete("/delete/{uuid}")
async def delete_admin_api(
        uuid: str,
        db: AsyncSession = Depends(get_db),
        current_admin=Depends(get_current_admin)
):
    ok, err = await delete_admin(db, uuid)
    if err:
        raise HTTPException(status_code=404, detail=err)

    return {"message": "Admin deleted"}


@router.patch("/status/{uuid}")
async def update_user_status(
        uuid: str,
        data: dict = Body(...),
        db: AsyncSession = Depends(get_db),
        admin=Depends(get_current_admin)
):
    user = await admin_update_user_status(
        db,
        uuid,
        approved=data.get("approved"),
        verified=data.get("verified")
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Status updated successfully",
        "uuid": user.uuid,
        "approved": user.approved
    }
