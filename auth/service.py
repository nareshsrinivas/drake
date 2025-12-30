# auth/service.py
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    verify_refresh_token
)
from core.google_auth import verify_google_id_token
from models import User
from core.aes_encryption import aes_decrypt
# removed unused decrypt_password import
from .schemas import RegisterUser, LoginUser
from models import ProfileStep

# ---------------- Helper ---------------- #

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


# ---------------- REGISTER USER ---------------- #

async def register_user(db: AsyncSession, data: RegisterUser):
    # Check email
    email_check = await db.execute(
        select(User).where(User.email == data.email)
    )
    if email_check.scalars().first():
        return None, "Email already registered"

    # Check phone
    phone_check = await db.execute(
        select(User).where(User.phone == data.phone)
    )
    if phone_check.scalars().first():
        return None, "Phone already registered"

    # Decrypt password
    try:
        decrypted_password = aes_decrypt(data.password)
    except Exception:
        return None, "Invalid encrypted password"

    # empty ya corrupted password reject karo
    if not decrypted_password or decrypted_password.strip() == "":
        return None, "Invalid encrypted password"

    # Create new user
    user = User(
        user_type=data.user_type,
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        email=data.email,
        country_code=data.country_code,
        phone=data.phone,
        password=hash_password(decrypted_password),
        dob=data.dob,
        age=calculate_age(data.dob)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user, None


# ---------------- LOGIN & AUTH USER ---------------- #

async def authenticate_user(db: AsyncSession, email: str, password: str):
    # Fetch user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalars().first()

    if not user:
        # Keep generic message so we don't leak existence
        return None, "Invalid email or password"

    # Block Google-only users (no password stored)
    if getattr(user, "password", None) is None:
        return None, "This account uses Google login. Please login using Google."

    # AES decrypt incoming password
    try:
        decrypted_password = aes_decrypt(password)
    except Exception:
        return None, "Invalid encrypted password"

    # Prevent empty/invalid decrypt
    if not decrypted_password or decrypted_password.strip() == "":
        return None, "Invalid encrypted password"

    # bcrypt verify
    if not verify_password(decrypted_password, user.password):
        return None, "Invalid email or password"

    # Generate tokens
    access_token = create_access_token(subject=str(user.uuid))
    refresh_token = create_refresh_token(subject=str(user.uuid))

    user_info = {
        "uuid": str(user.uuid),
        "id": str(user.id),
        "user_type": user.user_type,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "country_code": user.country_code,
        "phone": user.phone,
        "dob": str(user.dob) if getattr(user, "dob", None) else None,
        "age": user.age
    }

    response = {
        "refresh_token": refresh_token,
        "access_token": access_token,
        "user": user_info,
        # "user_obj": user,
        "token_type": "bearer"
    }

    return response, None


# ---------------- REFRESH TOKEN ---------------- #

async def refresh_access_token(refresh_token: str):
    user_id, err = verify_refresh_token(refresh_token)
    if err:
        return None, err

    new_access_token = create_access_token(subject=user_id)
    return new_access_token, None


# ---------------- GOOGLE LOGIN ---------------- #

async def login_with_google(db: AsyncSession, id_token: str):
    # 1. Verify token with Google
    token_info = await verify_google_id_token(id_token)

    email = token_info["email"]
    given_name = token_info.get("given_name") or ""
    family_name = token_info.get("family_name") or ""
    name = token_info.get("name") or ""

    first_name = given_name or (name.split(" ")[0] if name else email.split("@")[0])
    last_name = family_name or " "

    # 2. Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        # Naya user create karo.
        # IMPORTANT: Neeche wale fields apne User model ke hisaab se adjust karo.
        user = User(
            user_type=1,                 # default: Model (ya jo bhi tu chaahe)
            first_name=first_name,
            last_name=last_name,
            email=email,
            country_code="",             # optional / default
            phone="",                    # optional / default
            password=None,               # Google user, no password (DB me nullable karo)
            dob=None,                    # Google se dob nahi milta by default
            age=None,
            # is_google_user=True  # optional flag if model supports it
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

    # 3. Generate tokens (same as normal login)
    access_token = create_access_token(subject=str(user.uuid))
    refresh_token = create_refresh_token(subject=str(user.uuid))

    user_info = {
        "uuid": str(user.uuid),
        "user_type": user.user_type,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "country_code": user.country_code,
        "phone": user.phone,
        "dob": str(user.dob) if getattr(user, "dob", None) else None,
        "age": user.age,
    }

    response = {
        "refresh_token": refresh_token,
        "access_token": access_token,
        "user": user_info,
        "token_type": "bearer"
    }

    return response, None



