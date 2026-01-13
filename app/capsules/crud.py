from app.models import Capsule
from app.utils.authentication import authenticate_api_key
from app.utils.helpers import current_time

from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional, List, Tuple
from uuid import UUID
from fastapi import HTTPException, status

def create_capsule_entry(session: Session, api_key: str, content: str, time_held: timedelta, replying_to_id: Optional[UUID]) -> dict[str]:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    if replying_to_id:
        reply = session.get(Capsule, replying_to_id)
        if not reply:
            raise HTTPException(detail="Capsule ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
        
    time = current_time()
    capsule = Capsule(
        user_id=user.id,
        content=content,
        time_held=time_held,
        release_date=time + time_held,
        replying_to_id=replying_to_id
    )
    session.add(capsule)
    session.commit()
    session.refresh(capsule)
    return {"details": "capsule successfully buried."}

def retrieve_capsule_entry(session: Session, api_key: str, capsule_id: UUID) -> Capsule:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    capsule = session.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(detail="Capsule ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if capsule.user_id != user.id:
        raise HTTPException(detail="Capsule ID given does not belong to you.", status_code=status.HTTP_403_FORBIDDEN)
    if capsule.release_date != current_time():
        raise HTTPException(detail="Capsule ID given is still buried.", status_code=status.HTTP_403_FORBIDDEN)
    return capsule

def retrieve_capsule_list(session: Session, api_key: str) -> List[Capsule]:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    time = current_time()
    capsules = session.exec(select(Capsule)
                            .where(Capsule.user_id == user.id)
                            .where(Capsule.release_date < time)
                            .order_by(Capsule.release_date)
                            ).all()
    return capsules

def retrieve_conversation(session: Session, api_key: str, capsule_id: UUID) -> Tuple[List[Capsule], bool]:
    key_obj = authenticate_api_key(session, api_key)
    user = key_obj.user
    capsule = session.get(Capsule, capsule_id)
    if not capsule:
        raise HTTPException(detail="Capsule ID given does not exist.", status_code=status.HTTP_404_NOT_FOUND)
    if capsule.user_id != user.id:
        raise HTTPException(detail="Capsule ID given does not belong to you.", status_code=status.HTTP_403_FORBIDDEN)
    if capsule.release_date != current_time():
        raise HTTPException(detail="Capsule ID given is still buried.", status_code=status.HTTP_403_FORBIDDEN)
    capsule_list = []
    head_of_conversation = capsule.reply_allowed
    while capsule:
        capsule_list.append(capsule)
        capsule = capsule.replying_to
    return capsule_list, head_of_conversation