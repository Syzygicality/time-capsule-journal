from app.models import User, APIKey, Capsule
from app.utils.encryption import hash_password, verify_password, hash_api_key
from app.utils.authentication import authenticate_api_key
from app.utils.helpers import get_random_string, current_time

from sqlmodel import Session, select, exists
from typing import Optional
from datetime import timedelta
from fastapi import HTTPException, status

def create_user_account(session: Session, username: str, email: Optional[str], password: str) -> User:
    if session.exec(select(exists().where(User.username == username))).one():
        raise HTTPException(detail="Username given already exists.", status_code=status.HTTP_400_BAD_REQUEST)
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def generate_api_key(session: Session, username: str, password: str) -> tuple[APIKey, str]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(detail="Username given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(detail="Password given is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)
    if user.api_key:
        raise HTTPException(detail="Your API key already exists. If you have lost/forgotten your key, you can regenerate a new key.", status_code=status.HTTP_400_BAD_REQUEST)
    prefix = get_random_string(12)
    raw_key = get_random_string(48)
    hashed_key, salt = hash_api_key(raw_key)
    key_obj = APIKey(
        user_id=user.id,
        prefix=prefix,
        hashed_key=hashed_key,
        salt=salt
    )
    session.add(key_obj)
    session.commit()
    session.refresh(key_obj)
    return key_obj, prefix + "-" + raw_key

def get_user_details(session: Session, api_key: str) -> User:
    key_obj = authenticate_api_key(session, api_key)
    return key_obj.user

def update_user_details(session: Session, api_key: str, username: Optional[str], email: Optional[str],) -> User:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    if user.last_updated and current_time() < user.last_updated + timedelta(days=3):
        time_left = (user.last_updated + timedelta(days=3)) - current_time()
        raise HTTPException(detail=f"You cannot update your account details with 3 days of your last update. Please wait {time_left}.", status_code=status.HTTP_400_BAD_REQUEST)
    if username:
        user.username = username
    if email:
        user.email = email
    user.last_updated = current_time()
    session.add(user)
    session.commit()
    return user

def regen_api_key(session: Session, username: str, password: str) -> tuple[APIKey, str]:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(detail="Username given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if not verify_password(password, user.hashed_password):
        raise HTTPException(detail="Password given is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)
    if not user.api_key:
        raise HTTPException(detail="Your API key does not exist. You have to create your key before you can regenerate a new key.", status_code=status.HTTP_400_BAD_REQUEST)
    key_obj = user.api_key
    prefix = get_random_string(12)
    raw_key = get_random_string(48)
    key_obj.prefix = prefix
    key_obj.hashed_key, key_obj.salt = hash_api_key(raw_key)
    session.add(key_obj)
    session.commit()
    return key_obj, prefix + "-" + raw_key

def update_user_password(session: Session, api_key: str, old_password: str, new_password: str) -> User:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(detail="Password given is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()
    return user

def delete_user_account(session: Session, api_key: str):
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    session.delete(user)
    session.commit()
    return {"details": "Account successfully deleted."}