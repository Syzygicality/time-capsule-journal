from app.users.schemas import (
    UserCreateSchema, 
    UserUpdateSchema, 
    UserSchema, 
    APIKeyCreateSchema, 
    APIKeySchema,
    UserPasswordResetSchema
)

from app.users.crud import (
    create_user,
    retrieve_user,
    update_user,
    update_user_password,
    destroy_user,
    create_verification,
    delete_verification,
    create_api_key,
    update_api_key,
)

from app.database import get_db
from app.utils.authentication import access_api_key
from app.utils.emailing import send_verification_email

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me", response_model=UserSchema)
async def get_user(api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    return await retrieve_user(
        session,
        api_key
    )

@router.post("/me", response_model=UserSchema)
async def post_user(user_data: UserCreateSchema, session: AsyncSession = Depends(get_db)):
    return await create_user(
        session,
        user_data.username,
        user_data.email,
        user_data.password
    )

@router.patch("/me", response_model=UserSchema)
async def patch_user(user_data: UserUpdateSchema, api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    return await update_user(
        session,
        api_key,
        user_data.username,
        user_data.email
    )

@router.post("/me/change-password", response_model=UserSchema)
async def change_user_password(user_data: UserPasswordResetSchema, api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    return await update_user_password(
        session,
        api_key,
        user_data.old_password,
        user_data.new_password
    )

@router.delete("/me")
async def delete_user(api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    return await destroy_user(
        session,
        api_key
    )

@router.post("/verify/request")
async def request_email_verification(background_tasks: BackgroundTasks, api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    email, code =  await create_verification(
        session,
        api_key
    )
    background_tasks.add_task(
        send_verification_email,
        email,
        code
    )
    return {"details": "Verification code sent, please check your email inbox (may be in spam folder)."}

@router.post("/verify")
async def send_verification_code(code: int, api_key: str = Depends(access_api_key), session: AsyncSession = Depends(get_db)):
    return await delete_verification(
        session,
        api_key,
        code
    )

@router.post("/api-key/create", response_model=APIKeySchema)
async def generate_api_key(user_data: APIKeyCreateSchema, session: AsyncSession = Depends(get_db)):
    key_obj, raw_key = await create_api_key(
        session,
        user_data.username,
        user_data.password
    )
    return {"key": raw_key}

@router.post("/api-key/regen", response_model=APIKeySchema)
async def regenerate_api_key(user_data: APIKeyCreateSchema, session: AsyncSession = Depends(get_db)):
    key_obj, raw_key = await update_api_key(
        session,
        user_data.username,
        user_data.password
    )
    return {"key": raw_key}