from app.models import User, APIKey, Verification
from app.utils.encryption import hash_password, verify_password, hash_api_key
from app.utils.authentication import authenticate_api_key
from app.utils.helpers import get_random_string, current_time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, exists
from typing import Optional, Tuple, Dict
from datetime import timedelta
from fastapi import HTTPException, status
from secrets import randbelow

async def create_user(session: AsyncSession, username: str, email: Optional[str], password: str) -> User:
    result = await session.exec(select(exists().where(User.username == username)))
    if result.scalar():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username given already exists.")
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    session.add(user)
    await session.commit() 
    await session.refresh(user)
    return user

async def retrieve_user(session: AsyncSession, api_key: str) -> User:
    key_obj = await authenticate_api_key(session, api_key)
    return key_obj.user

async def update_user(session: AsyncSession, api_key: str, username: Optional[str], email: Optional[str],) -> Dict[str, str]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    if user.last_updated and current_time() < user.last_updated + timedelta(days=3):
        time_left = (user.last_updated + timedelta(days=3)) - current_time()
        raise HTTPException(detail=f"You cannot update your account details with 3 days of your last update. Please wait {time_left}.", status_code=status.HTTP_400_BAD_REQUEST)
    if username:
        user.username = username
    if email:
        user.email = email
        user.email_verified = False
    session.add(user)
    await session.commit()
    if email:
        return {"details": "Update successful. Please verify your new email."}
    return {"details": "Update successful"}

async def update_user_password(session: AsyncSession, api_key: str, old_password: str, new_password: str) -> User:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(detail="Password given is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)
    user.hashed_password = hash_password(new_password)
    session.add(user)
    await session.commit()
    return user

async def destroy_user(session: AsyncSession, api_key: str) -> dict[str]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    session.delete(user)
    await session.commit()
    return {"details": "Account successfully deleted."}

async def create_verification(session: AsyncSession, api_key: str) -> Tuple[str, str]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    code = randbelow(900000) + 100000
    time = current_time()
    verification = user.verification
    if verification:
        if verification.creation_date + timedelta(minutes=1) > current_time():
            raise HTTPException(detail="Please wait at least one minute before requesting another verification code.", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
        verification.code = code
        verification.expires_at = time + timedelta(minutes=15)
        verification.attempts = 0
        verification.creation_date = time
    else:
        verification = Verification(
            user_id=user.id,
            code=code,
            expires_at=time + timedelta(minutes=15)
        )
        user.verification = verification
    session.add(verification)
    await session.commit()
    return user.email, code
    
async def delete_verification(session: AsyncSession, api_key: str, code: int) -> dict[str, str]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    verification = user.verification
    if not verification:
        raise HTTPException(detail="Request a verification code first.", status_code=status.HTTP_409_CONFLICT)
    if verification.expires_at < current_time():
        raise HTTPException(detail="Your code has expired, please request another.", status_code=status.HTTP_410_GONE)
    if verification.attempts >= 3:
        raise HTTPException(detail="Too many incorrect attempts, please request another.", status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    if verification.code == code:
        user.email_verified = True
        session.delete(verification)
        await session.commit()
        return {"details": "Your email has be verified."}
    else:
        verification.attempts += 1
        await session.commit()
        raise HTTPException(detail=f"Incorrect verification code. ({verification.attempts} / 3)", status_code=status.HTTP_400_BAD_REQUEST)

async def create_api_key(session: AsyncSession, username: str, password: str) -> tuple[APIKey, str]:
    user = await session.exec(select(User).where(User.username == username)).first()
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
    await session.commit()
    await session.refresh(key_obj)
    return key_obj, prefix + "-" + raw_key

async def update_api_key(session: AsyncSession, username: str, password: str) -> tuple[APIKey, str]:
    user = await session.exec(select(User).where(User.username == username)).first()
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
    await session.commit()
    return key_obj, prefix + "-" + raw_key



