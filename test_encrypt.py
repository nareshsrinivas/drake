# from cryptography.fernet import Fernet

# key = b"4E9b_wlZsotmBbgnNTM4oXt5fAgDqLeB9g2RGg0hq9k="  # SAME AS BACKEND
# cipher = Fernet(key)

# encrypted = cipher.encrypt("123456".encode()).decode()
# print(encrypted)



from core.aes_encryption import aes_encrypt,aes_decrypt


# print(aes_encrypt("123456"))
# print(aes_decrypt('3JMy1Jl4ToRl/KTsFjaUDw=='))
print(aes_decrypt('F4PgZErfgMvcC6tqRT13vw=='))
print(aes_encrypt("Test@123"))