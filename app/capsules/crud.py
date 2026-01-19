from app.models import Capsule, Conversation
from app.utils.authentication import authenticate_api_key
from app.utils.encryption import encrypt_content, decrypt_content
from app.utils.helpers import current_time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta
from typing import Optional, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status

async def list_capsules(session: AsyncSession, api_key: str) -> List[Capsule]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    time = current_time()
    capsules = await session.exec(select(Capsule)
                            .where(Capsule.user_id == user.id)
                            .where(Capsule.release_date < time)
                            .order_by(Capsule.release_date.desc())
                            ).all()
    for capsule in capsules:
        capsule.content = decrypt_content(capsule.content)
    return capsules

async def create_capsule(session: AsyncSession, api_key: str, content: str, time_held: timedelta, replying_to_id: Optional[UUID]) -> dict[str, str]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    if not user.email_verified:
        raise HTTPException(detail="You need to verify your email before creating capsules.", status_code=status.HTTP_403_FORBIDDEN)
    time = current_time()
    capsule = Capsule(
        user_id=user.id,
        content=encrypt_content(content),
        time_held=time_held,
        release_date=time + time_held,
    )
    if replying_to_id:
        reply = await session.get(Capsule, replying_to_id)
        if not reply:
            raise HTTPException(detail="Capsule ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
        if reply.user_id != user.id:
            raise HTTPException(detail="Capsule ID given does not belong to you.", status_code=status.HTTP_403_FORBIDDEN)
        if reply.release_date > current_time():
            raise HTTPException(detail="Capsule ID given is still buried.", status_code=status.HTTP_403_FORBIDDEN)
        conversation = reply.conversation
        if not conversation:
            conversation = Conversation(
                user_id=user.id,
                latest_capsule_id=reply.id
            )
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
        capsule.conversation_id = conversation.id
        capsule.replying_to_id = reply.id
        session.add(capsule)
        await session.commit()
        await session.refresh(capsule)
        conversation.latest_capsule_id = capsule.id
        await session.commit()
    else:
        session.add(capsule)
        await session.commit()
        await session.refresh(capsule)
    return {
        "details": "capsule successfully buried.",
        "note": "emailing service currently unavailable."
    }

async def retrieve_capsule(session: AsyncSession, api_key: str, capsule_id: UUID) -> Capsule:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    capsule = await session.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(detail="Capsule ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if capsule.user_id != user.id:
        raise HTTPException(detail="Capsule ID given does not belong to you.", status_code=status.HTTP_403_FORBIDDEN)
    if capsule.release_date > current_time():
        raise HTTPException(detail="Capsule ID given is still buried.", status_code=status.HTTP_403_FORBIDDEN)
    capsule.content = decrypt_content(capsule.content)
    return capsule

async def list_conversations(session: AsyncSession, api_key: str) -> List[Conversation]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    conversations = await session.exec(select(Conversation)
                                      .where(Conversation.user_id == user.id)
                                      .join(Conversation.latest_capsule)
                                      .order_by(Capsule.release_date.desc())
                                      ).all()
    for conversation in conversations:
        conversation.latest_capsule.content = decrypt_content(conversation.latest_capsule.content)
    return conversations

async def retrieve_conversation(session: AsyncSession, api_key: str, conversation_id: UUID) -> Tuple[List[Capsule], bool]:
    key_obj = await authenticate_api_key(session, api_key)
    user = key_obj.user
    conversation = await session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(detail="Conversation ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if conversation.user_id != user.id:
        raise HTTPException(detail="Conversation ID given does not belong to you.", status_code=status.HTTP_403_FORBIDDEN)
    capsule_list = []
    capsule = conversation.latest_capsule
    while capsule:
        capsule.content = decrypt_content(capsule.content)
        capsule_list.append(capsule)
        capsule = capsule.replying_to
    if conversation.reply_allowed:
        return capsule_list
    return capsule_list[1:]