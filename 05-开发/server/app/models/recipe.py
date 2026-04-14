"""配方模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    pressure_min: Mapped[int] = mapped_column(Integer, nullable=False)
    pressure_max: Mapped[int] = mapped_column(Integer, nullable=False)
    water_temp_min: Mapped[float] = mapped_column(Float, nullable=False)
    water_temp_max: Mapped[float] = mapped_column(Float, nullable=False)
    fish_species: Mapped[str] = mapped_column(String(32), nullable=False)
    spot_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_public: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
