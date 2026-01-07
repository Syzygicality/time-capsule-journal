from datetime import datetime, timezone
import secrets
import string

CHARACTERS = string.ascii_letters + string.digits

def get_api_key() -> str:
    return "".join(secrets.choice(CHARACTERS) for _ in range(32))

def current_time() -> datetime:
    return datetime.now(timezone.utc)
