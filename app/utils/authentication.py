from app.models import APIKey
from .encryption import verify_api_key

from fastapi import Header, HTTPException
from sqlmodel import Session, select


def access_api_key(api_key: str = Header(...)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key credential were not provided.")
    return api_key

def authenticate_api_key(session: Session, api_key: str) -> APIKey:
    key_obj = session.exec(
        select(APIKey)
        .where(verify_api_key(
            api_key, 
            APIKey.hashed_key, 
            APIKey.salt
            ))
    ).first()
    if not key_obj:
        raise ValueError("Invalid/expired API key given.")
    return  key_obj