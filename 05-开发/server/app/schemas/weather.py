"""天气 Schema。"""
from datetime import datetime
from pydantic import BaseModel


class HourlyForecast(BaseModel):
    time: str
    temp: float
    weather_text: str


class WeatherResponse(BaseModel):
    location_key: str
    temp: float | None
    feels_like: float | None
    pressure: float | None
    wind_speed: float | None
    humidity: int | None
    weather_text: str | None
    hourly: list[HourlyForecast] | None
    cached: bool
    cached_at: datetime | None
