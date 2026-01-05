from Crypto.Cipher import AES
import base64
import os

SECRET_KEY = b"12345678901234567890123456789012"  # 32 bytes = AES-256
IV = b"1234567890123456"  # 16 bytes

def pad(data):
    padding = AES.block_size - len(data) % AES.block_size
    return data + chr(padding).encode() * padding

def unpad(data):
    padding_len = data[-1]
    return data[:-padding_len]

def aes_encrypt(text: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    raw = pad(text.encode())
    encrypted = cipher.encrypt(raw)
    return base64.b64encode(encrypted).decode()

def aes_decrypt(enc_text: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decoded = base64.b64decode(enc_text)
    decrypted = cipher.decrypt(decoded)
    return unpad(decrypted).decode()





