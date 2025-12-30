from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, String

from database import AsyncSessionLocal
from core.security import decode_token
from models import User, AdminUser


auth_scheme = HTTPBearer()


# -------------------------
# DB Dependency (ASYNC)
# -------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# -------------------------
# CURRENT USER (ASYNC)
# -------------------------
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> User:

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # ✅ Use cast to String for UUID comparison
    result = await db.execute(
        select(User).where(cast(User.uuid, String) == str(sub))
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# -------------------------
# CURRENT ADMIN (FIXED - Use HTTPBearer)
# -------------------------
async def get_current_admin(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> AdminUser:
    """
    Extract admin from JWT token
    """
    token = credentials.credentials  # ✅ HTTPBearer automatically strips "Bearer "
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    uuid = payload.get("sub")
    if not uuid:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    # ✅ Use cast to String for UUID comparison
    result = await db.execute(
        select(AdminUser).where(cast(AdminUser.uuid, String) == str(uuid))
    )
    admin = result.scalars().first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Admin not found"
        )

    return admin
