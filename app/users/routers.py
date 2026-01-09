from app.users.schemas import (
    UserCreateSchema, 
    UserUpdateSchema, 
    UserSchema, 
    APIKeyCreateSchema, 
    APIKeySchema,
    UserPasswordResetSchema
)

from app.users.crud import (
    create_user_account,
    generate_api_key,
    get_user_details,
    update_user_details,
    regen_api_key,
    update_user_password,
    delete_user_account
)

from app.database import get_db
from app.utils.authentication import access_api_key

from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter(prefix="/users", tags=["User"])

@router.post("/registration", response_model=UserSchema)
def create_user(user_data: UserCreateSchema, session: Session = Depends(get_db)):
    
    return create_user_account(
        session,
        user_data.username,
        user_data.email,
        user_data.password
    )

@router.get("/me", response_model=UserSchema)
def get_user(api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return get_user_details(
        session,
        api_key
    )

@router.patch("/me", response_model=UserSchema)
def update_user(user_data: UserUpdateSchema, api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return update_user_details(
        session,
        api_key,
        user_data.username,
        user_data.email
    )

@router.delete("/me")
def delete_user(api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return delete_user_account(
        session,
        api_key
    )

@router.post("/me/change-password", response_model=UserSchema)
def change_user_password(user_data: UserPasswordResetSchema, api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return update_user_password(
        session,
        api_key,
        user_data.old_password,
        user_data.new_password
    )

@router.post("/api-key/create", response_model=APIKeySchema)
def create_api_key(user_data: APIKeyCreateSchema, session: Session = Depends(get_db)):
    key_obj, raw_key = generate_api_key(
        session,
        user_data.username,
        user_data.password
    )
    return {"key": raw_key}

@router.post("/api-key/regen", response_model=APIKeySchema)
def regenerate_api_key(user_data: APIKeyCreateSchema, session: Session = Depends(get_db)):
    key_obj, raw_key = regen_api_key(
        session,
        user_data.username,
        user_data.password
    )
    return {"key": raw_key}