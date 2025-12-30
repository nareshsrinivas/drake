from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, cast, String


from models import AdminUser, User
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from core.aes_encryption import aes_decrypt



# ---------------- CREATE ADMIN ---------------- #

async def create_admin(db: AsyncSession, data):
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == data.email)
    )
    if result.scalar_one_or_none():
        return None, "Email already exists"

    # ✅ AES decrypt (FIX)
    try:
        decrypted_password = aes_decrypt(data.password)
    except Exception:
        return None, "Invalid encrypted password"

    if not decrypted_password or decrypted_password.strip() == "":
        return None, "Invalid encrypted password"

    admin = AdminUser(
        username=data.username,
        email=data.email,
        password=hash_password(decrypted_password)
    )

    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    return admin, None


# ---------------- ADMIN LOGIN ---------------- #

async def admin_login(db: AsyncSession, email: str, password: str):
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == email)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return None, "Invalid email or password"

    try:
        decrypted_password = aes_decrypt(password)
    except Exception:
        return None, "Invalid encrypted password"

    if not verify_password(decrypted_password, admin.password):
        return None, "Invalid email or password"

    return {
        "access_token": create_access_token(subject=str(admin.uuid)),
        "refresh_token": create_refresh_token(str(admin.uuid)),
        "user": {
            "uuid": admin.uuid,
            "username": admin.username,
            "email": admin.email
        },
        "token_type": "bearer"
    }, None


# ---------------- UPDATE ADMIN ---------------- #

async def update_admin(db: AsyncSession, admin_id: int, data):
    result = await db.execute(
        select(AdminUser).where(AdminUser.id == admin_id)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return None, "Admin not found"

    if data.username:
        admin.username = data.username
    if data.email:
        admin.email = data.email
    if data.password:
        admin.password = hash_password(
            aes_decrypt(data.password)
        )
    if data.role:
        admin.role = data.role

    await db.commit()
    await db.refresh(admin)

    return admin, None


# ---------------- UPDATE ADMIN (BY UUID) ---------------- #

async def update_admin(
    db: AsyncSession,
    uuid: str,
    data
):
    result = await db.execute(
        select(AdminUser).where(
            cast(AdminUser.uuid, String) == uuid
        )
    )
    admin = result.scalar_one_or_none()

    if not admin:
        return None, "Admin not found"

    if data.username:
        admin.username = data.username

    if data.email:
        admin.email = data.email

    if data.password:
        decrypted_password = aes_decrypt(data.password)
        admin.password = hash_password(decrypted_password)

    if data.role:
        admin.role = data.role

    await db.commit()
    await db.refresh(admin)

    return admin, None


# ---------------- DELETE ADMIN (HARD DELETE BY UUID) ---------------- #

async def delete_admin(
    db: AsyncSession,
    uuid: str
):
    result = await db.execute(
        delete(AdminUser).where(
            cast(AdminUser.uuid, String) == uuid
        )
    )

    if result.rowcount == 0:
        return None, "Admin not found"

    await db.commit()
    return True, None



# ---------------- UPDATE USER STATUS ---------------- #

async def admin_update_user_status(
    db: AsyncSession,
    uuid: str,
    approved=None,
    verified=None
):
    result = await db.execute(
        select(User).where(cast(User.uuid, String) == uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    if approved is not None:
        user.approved = approved
    if verified is not None:
        user.verified = verified

    await db.commit()
    await db.refresh(user)
    return user

