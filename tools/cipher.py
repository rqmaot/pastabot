from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib

def hash(txt):
    m = hashlib.sha256()
    m.update(txt.encode())
    return m.hexdigest()

def encrypt(msg, key):
    key = hash(key).encode()[:16]
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(msg.encode(), 16))
    return iv.hex() + ct.hex()

def decrypt(ct, key):
    key = hash(key).encode()[:16]
    iv = bytes.fromhex(ct[:32])
    ct = bytes.fromhex(ct[32:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ct)
    return unpad(padded, 16).decode()
