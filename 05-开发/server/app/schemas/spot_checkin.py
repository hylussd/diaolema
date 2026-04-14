"""打卡记录 Schema。"""
from datetime import datetime
from typing import Any
import json
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


class CheckinCreate(BaseModel):
    spot_id: int = Field(..., gt=0)
    fish_caught: list[str] | None = None
    weight_kg: float | None = Field(None, gt=0, le=999)
    notes: str | None = None


class CheckinResponse(BaseModel):
    id: int
    user_id: int
    spot_id: int
    fish_caught: list[str] | None
    weight_kg: float | None
    weather_text: str | None
    temp: float | None
    pressure: float | None
    notes: str | None
    checkin_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            spot_id=obj.spot_id,
            fish_caught=_parse_json(obj.fish_caught),
            weight_kg=obj.weight_kg,
            weather_text=obj.weather_text,
            temp=obj.temp,
            pressure=obj.pressure,
            notes=obj.notes,
            checkin_time=obj.checkin_time,
            created_at=obj.created_at,
        )
