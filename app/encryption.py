from passlib.context import CryptContext

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)
