from app.utils.helpers import get_random_string

from passlib.context import CryptContext
import hashlib

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

MAX_BCRYPT_BYTES = 72

def hash_password(password: str) -> str:
    # Truncate to 72 bytes safely
    truncated = password.encode()[:MAX_BCRYPT_BYTES]
    safe_pass = truncated.decode(errors="ignore")  # decode back to string
    return password_context.hash(safe_pass)

def verify_password(password: str, hashed: str) -> bool:
    truncated = password.encode()[:MAX_BCRYPT_BYTES]
    safe_pass = truncated.decode(errors="ignore")
    return password_context.verify(safe_pass, hashed)

def hash_api_key(raw_key: str) -> tuple[str, str]:
    salt = get_random_string(16)
    hashed = hashlib.sha256((salt + raw_key).encode()).hexdigest()
    return hashed, salt

def verify_api_key(raw_key: str, hashed_key: str, salt: str) -> bool:
    return hashlib.sha256((salt + raw_key).encode()).hexdigest() == hashed_key