from datetime import datetime, timezone
import secrets
import string

CHARACTERS = string.ascii_letters + string.digits

def get_random_string(length: int) -> str:
    return "".join(secrets.choice(CHARACTERS) for _ in range(length))

def current_time() -> datetime:
    return datetime.now(timezone.utc)
