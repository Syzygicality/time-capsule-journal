from .helpers import get_random_string

from passlib.context import CryptContext
import hashlib

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)

def hash_api_key(raw_key: str) -> tuple[str, str]:
    salt = get_random_string(16)
    hashed = hashlib.sha256((salt + raw_key).encode()).hexdigest()
    return hashed, salt

def verify_api_key(raw_key: str, hashed_key: str, salt: str) -> bool:
    return hashlib.sha256((salt + raw_key).encode()).hexdigest() == hashed_key