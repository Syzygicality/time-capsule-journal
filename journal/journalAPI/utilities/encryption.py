from cryptography.fernet import Fernet
import os

FERNET_KEY = os.environ.get("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError("FERNET_KEY is not set in environment variables.")

f = Fernet(FERNET_KEY)

def encrypt_message(message):
    return f.encrypt(message.encode()).decode()

def decrypt_message(ciphertext):
    return f.decrypt(ciphertext.encode()).decode()