from app.models import APIKey
from app.utils.encryption import verify_api_key

from fastapi import Header, HTTPException
from sqlmodel import Session, select


def access_api_key(api_key: str = Header(...)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key credential were not provided.")
    return api_key

def authenticate_api_key(session: Session, api_key: str) -> APIKey:
    exploded_key = api_key.split("-")
    if len(exploded_key) != 2:
        raise ValueError("Invalid API key format.")
    key_obj = session.exec(select(APIKey).where(APIKey.prefix == exploded_key[0])).first()
    if not key_obj or not verify_api_key(exploded_key[1], key_obj.hashed_key, key_obj.salt):
        raise ValueError("Invalid/expired API key given.")
    return key_obj