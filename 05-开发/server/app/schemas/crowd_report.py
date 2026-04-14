"""水文上报 Schema。"""
from datetime import datetime
from pydantic import BaseModel, Field


class CrowdReportCreate(BaseModel):
    spot_id: int = Field(..., gt=0)
    checkin_id: int = Field(..., gt=0)
    water_temp: float = Field(..., ge=-5.0, le=40.0)
    dissolved_oxygen: float = Field(..., ge=0.0, le=20.0)
    fish_species: str = Field(..., min_length=1, max_length=32)


class CrowdReportResponse(BaseModel):
    id: int
    spot_id: int
    checkin_id: int
    water_temp: float
    dissolved_oxygen: float
    fish_species: str
    report_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True
