from app.utils.helpers import current_time

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pydantic import EmailStr
from typing import Optional, List

class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(max_length=32, index=True, unique=True)
    email: EmailStr = Field(unique=True)
    hashed_password: str = Field()
    email_verified: bool = Field(default=False)

    verification: Optional["Verification"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    api_key: Optional["APIKey"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    capsules: List["Capsule"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")

class Verification(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    code: int = Field()
    expires_at: datetime = Field()
    creation_date: datetime = Field(default_factory=current_time)
    attempts: int = Field(default=0)

    user: "User" = Relationship(back_populates="verification")

class APIKey(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    prefix: str = Field(max_length=12, index=True)
    hashed_key: str = Field(max_length=64, index=True)
    salt: str = Field()

    user: "User" = Relationship(back_populates="api_key")

class Capsule(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    conversation_id: Optional[UUID] = Field(foreign_key="conversation.id", nullable=True, index=True, default=None)
    content: str = Field()
    creation_date: datetime = Field(default_factory=current_time)
    time_held: timedelta = Field()
    release_date: datetime = Field()
    replying_to_id: Optional[UUID] = Field(default=None, foreign_key="capsule.id", nullable=True)
    sent: bool = Field(default=False)

    user: "User" = Relationship(back_populates="capsules")
    conversation: Optional["Conversation"] = Relationship(back_populates="capsules")
    replying_to: Optional["Capsule"] = Relationship(sa_relationship_kwargs={"remote_side": "Capsule.id"})

class Conversation(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    latest_capsule_id: UUID = Field(foreign_key="capsule.id")

    user: "User" = Relationship(back_populates="conversations")
    capsules: List["Capsule"] = Relationship(back_populates="conversation")
    latest_capsule: Optional["Capsule"] = Relationship(sa_relationship_kwargs={"remote_side": "Capsule.id"})

    @property
    def reply_allowed(self):
        return current_time() > self.latest_capsule.release_date