from nacl.public import PrivateKey

private_key = PrivateKey.generate()
public_key = private_key.public_key

print("PUBLIC KEY:", public_key.encode().hex())
print("PRIVATE KEY:", private_key.encode().hex())
