"""分类 Schema。"""
from datetime import datetime
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    color: str = Field(default="#3B82F6", max_length=16)
    sort_order: int = Field(default=0)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    color: str | None = Field(default=None, max_length=16)
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryWithCount(CategoryResponse):
    spot_count: int = 0
