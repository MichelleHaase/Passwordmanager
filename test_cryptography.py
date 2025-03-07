from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os

key = input("Password? ")

salt = os.urandom(16)

kdf = PBKDF2HMAC(algorithm=hashes.SHA3_256(), length=32, 
                 salt=salt, iterations=100000, backend=default_backend())
kdf_key = kdf.derive(key.encode("utf-8"))

print(base64.urlsafe_b64encode(kdf_key))

cipher = Fernet(kdf_key)

encrypted_data = cipher.encrypt(Database.db)