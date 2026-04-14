"""天文计算响应 Schema。"""
from datetime import date
from pydantic import BaseModel


class BestFishingSlot(BaseModel):
    start: str
    end: str
    label: str


class AstronomyResponse(BaseModel):
    date: str
    moon_phase: str
    moon_phase_text: str
    moon_illumination: float
    sunrise: str
    sunset: str
    dawn: str
    dusk: str
    best_fishing_slots: list[BestFishingSlot]
