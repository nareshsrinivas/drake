from pydantic_settings import BaseSettings
from pydantic import PrivateAttr
from nacl.public import PrivateKey
from typing import ClassVar, Optional

class Settings(BaseSettings):
    # FERNET_KEY: str = ""
    FERNET_KEY: str

    GOOGLE_CLIENT_IDS: Optional[str] = None
    DATABASE_URL: str
    SECRET_KEY: str
    PRIVATE_KEY_HEX: str
    PUBLIC_KEY_HEX: str
    sendgrid_api_key: str
    sendgrid_from_email: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    UPLOAD_DIR: ClassVar[str] = "uploads"

    # ✅ Pydantic v2 compatible private attribute
    _private_key: Optional[PrivateKey] = PrivateAttr(default=None)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()

        try:
            _settings._private_key = PrivateKey(
                bytes.fromhex(_settings.PRIVATE_KEY_HEX)
            )
        except Exception as e:
            raise RuntimeError(f"Invalid PRIVATE_KEY_HEX: {e}")

    return _settings
