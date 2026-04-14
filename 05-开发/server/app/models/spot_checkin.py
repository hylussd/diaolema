"""打卡记录模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class SpotCheckin(Base):
    __tablename__ = "spot_checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    spot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fishing_spots.id"), nullable=False, index=True
    )
    fish_caught: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    weather_text: Mapped[str | None] = mapped_column(String(32), nullable=True)
    temp: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    checkin_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_checkins_user_spot", "user_id", "spot_id"),
        Index("idx_checkins_time", "checkin_time"),
    )
