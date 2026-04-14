"""天气缓存模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WeatherCache(Base):
    __tablename__ = "weather_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_key: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    now_temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    now_pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    now_wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    now_humidity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    now_weather_text: Mapped[str | None] = mapped_column(String(32), nullable=True)
    now_feels_like: Mapped[float | None] = mapped_column(Float, nullable=True)
    hourly_forecast: Mapped[str | None] = mapped_column(Text, nullable=True)
    cached_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
