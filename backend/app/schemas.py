"""Request and response models. Kept separate from the DB rows on purpose."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    role: Literal["lecturer", "admin"]


class MeOut(BaseModel):
    user: UserOut


class HealthOut(BaseModel):
    status: Literal["ok"]
    env: str
    database: Literal["ok", "error"]
