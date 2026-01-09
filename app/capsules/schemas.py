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
    def time_held_check(self) -> Self:
        if self.time_held < timedelta(0):
            raise ValueError("The holding time given cannot be negative.")
        return self
    
    @model_validator(mode="after")
    def replying_to_id_check(self) -> Self:
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
    reply_allowed: bool

class CapsuleListSchema(BaseModel):
    capsules: List[CapsuleSchema]