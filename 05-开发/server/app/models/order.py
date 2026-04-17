"""订单模型。"""
import time
import random
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def generate_order_no() -> str:
    """生成唯一订单号：DLM{timestamp}{random4}"""
    return f"DLM{int(time.time() * 1000)}{random.randint(1000, 9999)}"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, default=generate_order_no
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    total_amount: Mapped[int] = mapped_column(Integer, nullable=False)  # 分
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )  # pending/paid/shipped/delivered/cancelled
    address_name: Mapped[str] = mapped_column(String(64), nullable=False)
    address_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    address_detail: Mapped[str] = mapped_column(Text, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    pay_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="unpaid"
    )  # unpaid/paid/refunded
    pay_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
