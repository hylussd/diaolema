"""用户 Schema。"""
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class UserResponse(BaseModel):
    id: int
    openid: str
    nickname: str | None = None
    avatar_url: str | None = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
