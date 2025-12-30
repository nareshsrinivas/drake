from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UpdateUserInfo
from model.service import update_profile
from core.deps import get_current_user, get_db
from models import User

router = APIRouter(prefix="/user", tags=["Model User"])


@router.patch("/update-profile")
async def update_user_profile(
    data: UpdateUserInfo,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    updated_user = await update_profile(db, current_user, data)

    return {
        "message": "Profile updated successfully",
        "user": {
            "uuid": str(updated_user.uuid),
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "email": updated_user.email,
            "country_code": updated_user.country_code,
            "phone": updated_user.phone,
            "dob": str(updated_user.dob),
            "age": updated_user.age,
            "gender": updated_user.gender,
            "current_city": updated_user.current_city,
            "nationality": updated_user.nationality,
            "home_town": updated_user.home_town,
        }
    }




@router.get("/update-profile")
async def get_user_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "Profile fetched successfully",
        "user": {
            # "uuid": str(current_user.uuid),
            # "first_name": current_user.first_name,
            # "last_name": current_user.last_name,
            # "email": current_user.email,
            # "country_code": current_user.country_code,
            # "phone": current_user.phone,
            # "dob": str(current_user.dob) if current_user.dob else None,
            # "age": current_user.age,
            "gender": current_user.gender,
            "current_city": current_user.current_city,
            "nationality": current_user.nationality,
            "home_town": current_user.home_town,
        }
    }




















# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from auth.schemas import UpdateUserInfo
# from model.service import update_profile
# from core.deps import get_current_user, get_db
# from models import User
#
# router = APIRouter(prefix="/user", tags=["Model User"])
#
# @router.patch("/update-profile")
# async def update_user_profile(
#     data: UpdateUserInfo,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#
#     updated_user = await update_profile(db, current_user, data)
#
#     return {
#         "message": "Profile updated successfully",
#         "user": {
#             "uuid": str(updated_user.uuid),
#             "first_name": updated_user.first_name,
#             "last_name": updated_user.last_name,
#             "email": updated_user.email,
#             "country_code": updated_user.country_code,
#             "phone": updated_user.phone,
#             "dob": str(updated_user.dob),
#             "age": updated_user.age,
#             "gender": updated_user.gender,
#             "current_city": updated_user.current_city,
#             "nationality": updated_user.nationality,
#             "languages": updated_user.languages,
#             "home_city": updated_user.home_city,
#         }
#     }
#
#
#
#
#
#
#
#
#
#
