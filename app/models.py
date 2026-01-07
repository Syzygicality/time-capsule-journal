from .utils import current_time

from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pydantic import EmailStr
from typing import Optional

class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(max_length=32, index=True, unique=True)
    email: EmailStr | None = Field(nullable=True, unique=True)
    hashed_password: str = Field()
    last_updated: datetime = Field(default_factory=current_time)

    @property
    def updatable(self) -> bool:
        return current_time() > self.last_updated + timedelta(days=7)

class APIKey(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    hashed_key: str = Field(max_length=64, index=True)

class Capsule(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    content: str = Field(max_length=250)
    creation_date: datetime = Field(default_factory=current_time)
    time_held: timedelta = Field()
    replying_to: Optional[UUID] = Field(default=None, foreign_key="capsule.id", nullable=True)
    reply_allowed: bool = Field(default=False)