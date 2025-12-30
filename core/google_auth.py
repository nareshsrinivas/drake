# core/google_auth.py

import os
from typing import Dict, List
import httpx
from fastapi import HTTPException, status

GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"

# Comma separated client IDs from .env
RAW_CLIENT_IDS = os.getenv("GOOGLE_CLIENT_IDS", "")
ALLOWED_CLIENT_IDS: List[str] = [
    cid.strip() for cid in RAW_CLIENT_IDS.split(",") if cid.strip()
]


async def verify_google_id_token(id_token: str) -> Dict:
    """
    Verify Google ID token using Google's tokeninfo endpoint.
    Returns decoded data if valid, else raises HTTPException.
    """
    if not id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="id_token is required"
        )

    async with httpx.AsyncClient() as client:
        resp = await client.get(GOOGLE_TOKEN_INFO_URL, params={"id_token": id_token})

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token"
        )

    data = resp.json()

    aud = data.get("aud")
    email = data.get("email")
    email_verified = data.get("email_verified")

    if not aud or aud not in ALLOWED_CLIENT_IDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized Google client"
        )

    if email_verified not in ("true", True, "1", 1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email not verified"
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing email"
        )

    return data


