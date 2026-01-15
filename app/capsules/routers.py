from app.database import get_db
from app.utils.authentication import access_api_key
from app.capsules.schemas import (
    CapsuleCreateSchema,
    CapsuleListSchema,
    CapsuleSchema,
    ConversationSchema,
    ConversationListSchema
)

from app.capsules.crud import (
    list_capsules,
    create_capsule,
    retrieve_capsule,
    list_conversations,
    retrieve_conversation
)

from fastapi import APIRouter, Depends
from sqlmodel import Session
from uuid import UUID

router = APIRouter(prefix="/capsules")

@router.get("", response_model=CapsuleListSchema)
def get_capsule_list(api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return list_capsules(
        session,
        api_key
    )

@router.post("/post")
def post_capsule(user_data: CapsuleCreateSchema, api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return create_capsule(
        session,
        api_key,
        user_data.content,
        user_data.time_held,
        user_data.replying_to_id
    )

@router.get("{capsule_id}", response_model=CapsuleSchema)
def get_capsule_entry(capsule_id: UUID, api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return retrieve_capsule(
        session,
        api_key,
        capsule_id
    )

@router.get("/conversations", response_model=ConversationListSchema)
def get_conversation_list(api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return list_conversations(
        session,
        api_key
    )

@router.get("/conversations/{conversation_id}", response_model=ConversationSchema)
def get_conversation_entry(conversation_id: UUID, api_key: str = Depends(access_api_key), session: Session = Depends(get_db)):
    return retrieve_conversation(
        session,
        api_key,
        conversation_id
    )