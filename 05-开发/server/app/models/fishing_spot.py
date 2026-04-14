"""标点模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class FishingSpot(Base):
    __tablename__ = "fishing_spots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    terrain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fish_species: Mapped[str | None] = mapped_column(Text, nullable=True)
    fishing_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    water_depth: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_clarity: Mapped[str | None] = mapped_column(String(16), nullable=True)
    price_info: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photos: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_public: Mapped[int] = mapped_column(Integer, default=0)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
