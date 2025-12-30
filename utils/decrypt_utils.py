from cryptography.fernet import Fernet, InvalidToken
from core.config import get_settings
settings = get_settings()

key = settings.FERNET_KEY

if isinstance(key, str):
    key = key.encode()

# Ensure the key is bytes
cipher = Fernet(settings.FERNET_KEY.encode() if isinstance(settings.FERNET_KEY, str) else settings.FERNET_KEY)
# cipher = Fernet(key)
def decrypt_password(enc_password: str) -> str:
    """
    Decrypts encrypted password received from frontend.
    Raises ValueError if decryption fails.
    """
    try:
        # decrypt expects bytes
        decrypted_bytes = cipher.decrypt(enc_password.encode())
        return decrypted_bytes.decode()
    except InvalidToken:
        raise ValueError("Invalid encrypted password")
