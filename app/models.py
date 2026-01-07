from .utils.helpers import current_time

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pydantic import EmailStr
from typing import Optional, List

class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    username: str = Field(max_length=32, index=True, unique=True)
    email: EmailStr | None = Field(nullable=True, unique=True)
    hashed_password: str = Field()
    last_updated: datetime = Field(default_factory=current_time)

    api_key: Optional["APIKey"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    capsules: List["Capsule"] = Relationship(back_populates="user")

    @property
    def updatable(self) -> bool:
        return current_time() > self.last_updated + timedelta(days=7)

class APIKey(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    hashed_key: str = Field(max_length=64, index=True)

    user: "User" = Relationship(back_populates="api_key")

class Capsule(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE", index=True)
    content: str = Field(max_length=250)
    creation_date: datetime = Field(default_factory=current_time)
    time_held: timedelta = Field()
    replying_to: Optional[UUID] = Field(default=None, foreign_key="capsule.id", nullable=True)
    reply_allowed: bool = Field(default=True)

    user: "User" = Relationship(back_populates="capsules")
    replying_to: Optional["Capsule"] = Relationship(back_populates="replies", sa_relationship_kwargs={"remote_side": "Capsule.id"})