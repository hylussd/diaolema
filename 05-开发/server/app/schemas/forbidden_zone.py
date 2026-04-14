"""禁钓区 Schema。"""
from datetime import datetime
from pydantic import BaseModel, Field


class ForbiddenZoneCreate(BaseModel):
    name: str = Field(..., min_length=1)
    polygon: list[list[float]] = Field(...)
    reason: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    source: str | None = None


class ForbiddenZoneResponse(BaseModel):
    id: int
    name: str
    polygon: list[list[float]]
    reason: str | None
    start_time: datetime | None
    end_time: datetime | None
    source: str | None
    distance_km: float | None = None

    class Config:
        from_attributes = True


class ForbiddenZoneListResponse(BaseModel):
    items: list[ForbiddenZoneResponse]
    total: int


class ForbiddenZoneCheckRequest(BaseModel):
    latitude: float = Field(...)
    longitude: float = Field(...)


class ForbiddenZoneCheckResponse(BaseModel):
    inside: bool
    zones: list[ForbiddenZoneResponse]
