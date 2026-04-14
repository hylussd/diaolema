"""水文上报表模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CrowdReport(Base):
    __tablename__ = "crowd_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    spot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fishing_spots.id"), nullable=False, index=True
    )
    checkin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("spot_checkins.id"), nullable=False
    )
    water_temp: Mapped[float] = mapped_column(Float, nullable=False)
    dissolved_oxygen: Mapped[float] = mapped_column(Float, nullable=False)
    fish_species: Mapped[str] = mapped_column(String(32), nullable=False)
    report_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_reports_user_spot_date", "user_id", "spot_id", "report_time"),
        Index("idx_reports_spot_id", "spot_id"),
    )
