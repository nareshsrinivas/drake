from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from database import get_db
from models import User, AgencyProfile
from agency.agency_progress_schema import AgencyProfileStatusResponse
from utils.validators import is_filled

router = APIRouter(
    prefix="/agency/profile",
    tags=["Agency Profile Status"]
)


@router.get(
    "/completion-status/{user_uuid}",
    response_model=AgencyProfileStatusResponse
)
async def check_agency_profile_completion(
    user_uuid: UUID,
    db: AsyncSession = Depends(get_db)
):
    user = await db.scalar(
        select(User).where(User.uuid == user_uuid)
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.user_type == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="only valid for agency form"
        )

    agency_profile = await db.scalar(
        select(AgencyProfile).where(
            AgencyProfile.user_id == user.id
        )
    )

    # ❌ No profile
    if not agency_profile:
        return AgencyProfileStatusResponse(
            agency_profile=False,
            agency_status="incomplete"
        )

    required_fields = {
        "company_name": agency_profile.company_name,
        "contact_name": agency_profile.contact_name,
        "phone": agency_profile.phone,
        "website": agency_profile.website,
        "address": agency_profile.address,
        "about": agency_profile.about,
    }

    missing_fields = [
        field for field, value in required_fields.items()
        if not is_filled(value)
    ]

    agency_profile_completed = False if missing_fields else True

    return AgencyProfileStatusResponse(
        agency_profile=agency_profile_completed,
        agency_status="completed" if agency_profile_completed else "incomplete"
    )












# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from database import get_db
# from models import User, AgencyProfile
# from agency.agency_progress_schema import AgencyProfileStatusResponse
# from utils.validators import is_filled
#
# router = APIRouter(
#     prefix="/agency/profile",
#     tags=["Agency Profile Status"]
# )
#
#
# @router.get(
#     "/completion-status/{user_id}",
#     response_model=AgencyProfileStatusResponse
# )
# async def check_agency_profile_completion(
#     user_id: int,
#     db: AsyncSession = Depends(get_db)
# ):
#     # 1️⃣ Fetch user
#     user = await db.scalar(
#         select(User).where(User.id == user_id)
#     )
#
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#
#     # ❌ BLOCK MODEL USERS
#     if user.user_type == 1:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="only valid for agency form"
#         )
#
#     # 2️⃣ Fetch agency profile
#     profile = await db.scalar(
#         select(AgencyProfile).where(AgencyProfile.user_id == user_id)
#     )
#
#     if not profile:
#         return AgencyProfileStatusResponse(
#             agency_profile=False
#         )
#
#     # 3️⃣ Required agency fields (single form validation)
#     required_fields = {
#         "company_name": profile.company_name,
#         "contact_name": profile.contact_name,
#         "phone": profile.phone,
#     }
#
#     missing_fields = [
#         field for field, value in required_fields.items()
#         if not is_filled(value)
#     ]
#
#     agency_profile = False if missing_fields else True
#
#     # 4️⃣ Final response
#     return AgencyProfileStatusResponse(
#         agency_profile=agency_profile
#     )
