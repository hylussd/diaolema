"""标点 Schema。"""
import json
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


def _parse_json(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


class SpotCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    latitude: float = Field(...)
    longitude: float = Field(...)
    category_id: int | None = None
    terrain: str | None = None
    fish_species: list[str] | None = None
    fishing_method: str | None = None
    water_depth: float | None = None
    water_clarity: str | None = None
    price_info: str | None = None
    description: str | None = None
    photos: list[str] | None = None
    is_public: int = Field(default=0)
    extra: dict | None = None


class SpotUpdate(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    category_id: int | None = None
    terrain: str | None = None
    fish_species: list[str] | None = None
    fishing_method: str | None = None
    water_depth: float | None = None
    water_clarity: str | None = None
    price_info: str | None = None
    description: str | None = None
    photos: list[str] | None = None
    is_public: int | None = None
    extra: dict | None = None


class SpotResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    category_id: int | None
    terrain: str | None
    fish_species: list[str] | None
    fishing_method: str | None
    water_depth: float | None
    water_clarity: str | None
    price_info: str | None
    description: str | None
    photos: list[str] | None
    is_public: int
    extra: dict | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = {}
        for field, info in obj.__class__.__annotations__.items():
            val = getattr(obj, field)
            if field in ("fish_species", "photos"):
                val = _parse_json(val)
            elif field == "extra":
                val = _parse_json(val)
            data[field] = val
        return cls(**data)


class PageMeta(BaseModel):
    total: int
    offset: int
    limit: int


class SpotListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[SpotResponse]


class BatchDeleteRequest(BaseModel):
    spot_ids: list[int]


class BatchDeleteResponse(BaseModel):
    deleted: int
