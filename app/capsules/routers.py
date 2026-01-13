from app.database import get_db
from app.utils.authentication import access_api_key
from app.capsules.schemas import (
    CapsuleListSchema
)

from app.capsules.crud import (
    retrieve_capsule_list
)

from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter()

@router.post("/conversation", response_model=CapsuleListSchema)
def get_conversation(api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    capsule_list, head_of_conversation = retrieve_capsule_list(
        api_key,
        session
    )
    if head_of_conversation:
        return {
            "capsules": capsule_list,
            "note": "This is the latest conversation."
        }
    return {
            "capsules": capsule_list,
            "note": "This conversation is out of date."
    }