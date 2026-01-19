from pydantic import BaseModel, model_validator
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import Field
from typing import List
from typing_extensions import Self

class CapsuleCreateSchema(BaseModel):
    content: str = Field(max_length=250)
    time_held: timedelta
    replying_to_id: UUID | None = None

    @model_validator(mode="after")
    def validate_request(self) -> Self:
        if self.time_held < timedelta(minutes=15):
            raise ValueError("The holding time must be at least 15 minutes.")
        if self.replying_to_id and self.replying_to_id.version != 4:
            raise ValueError("The ID given to reply to must be a UUID4.")
        return self

class CapsuleSchema(BaseModel):
    id: UUID
    content: str
    creation_date: datetime
    time_held: timedelta
    release_date: datetime
    replying_to_id: UUID | None

class CapsuleListSchema(BaseModel):
    capsules: List[CapsuleSchema]

class ConversationSchema(BaseModel):
    id: UUID
    latest_capsule: CapsuleSchema
    reply_allowed: bool

class ConversationListSchema(BaseModel):
    conversations: List[ConversationSchema]