from sqlmodel import Field
from pydantic import BaseModel, EmailStr, model_validator
from typing_extensions import Self

class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    email: EmailStr | None
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @model_validator(mode="before")
    @classmethod
    def clean_email(cls, data):
        if "email" in data and data["email"]:
            data["email"] = data["email"].strip().lower()
        return data
    
    @model_validator(mode="before")
    @classmethod
    def strip_username(cls, data):
        if "username" in data and data["username"]:
            data["username"] = data["username"].strip()
        return data

    @model_validator(mode="after")
    def username_check(self) -> Self:
        if " " in self.username:
            raise ValueError("Username given cannot contain spaces.")
        return self
    
    @model_validator(mode="after")
    def password_check(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords given are not the same.")
        if self.password == self.password.lower():
            raise ValueError("Password given must contain at least one uppercase character.")
        if not any(char.isdigit() for char in self.password):
            raise ValueError("Password given must contain at least one number")
        if " " in self.password:
            raise ValueError("Password given cannot contain spaces.")
        return self


class UserUpdateSchema(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

    @model_validator(mode="after")
    def username_check(self) -> Self:
        if self.username and " " in self.username:
            raise ValueError("Username given cannot contain spaces.")
        return self

class UserSchema(BaseModel):
    username: str
    email: EmailStr | None

class LoginSchema(BaseModel):
    username: str
    password: str

class APIKeySchema(BaseModel):
    key: str

