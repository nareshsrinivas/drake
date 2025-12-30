from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from models import User

async def update_profile(db: AsyncSession, user: User, data):

    result = await db.execute(select(User).where(User.id == user.id))
    db_user = result.scalars().first()

    if not db_user:
        raise HTTPException(404, "User not found")

    # ✅ Clean data (ignore None & empty strings)
    update_data = {
        k: v for k, v in data.dict(exclude_unset=True).items()
        if v not in (None, "")
    }

    # ✅ USE update_data (not data)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)

    return db_user








# previous code updated for profile progress
# async def update_profile(db: AsyncSession, user: User, data):
#
#     # Get real DB user
#     result = await db.execute(select(User).where(User.id == user.id))
#     db_user = result.scalars().first()
#
#     if not db_user:
#         raise HTTPException(404, "User not found")
#
#     # Convert pydantic → dictionary
#     data = data.dict(exclude_unset=True)
#
#     # 🔥 Convert pydantic → dict & ignore None / empty strings
#     update_data = {
#         k: v for k, v in data.dict(exclude_unset=True).items()
#         if v not in (None, "")
#     }
#
#     # Update fields dynamically
#     for key, value in data.items():
#         setattr(db_user, key, value)
#
#     await db.commit()
#     await db.refresh(db_user)
#
#     return db_user
