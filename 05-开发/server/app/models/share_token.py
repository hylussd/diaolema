"""分享Token模型。"""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ShareToken(Base):
    __tablename__ = "share_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    spot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fishing_spots.id"), nullable=False
    )
    creator_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    max_valid_days: Mapped[int] = mapped_column(Integer, default=7)
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_share_expires", "expires_at"),
    )
