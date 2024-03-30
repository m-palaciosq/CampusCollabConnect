import hashlib

def makeKey():
    secret_key = hashlib.sha256(b'capstone_IS_love').hexdigest()
    return secret_key