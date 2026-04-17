"""订单项模型。"""
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Text, String
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=False
    )
    product_name: Mapped[str] = mapped_column(String(128), nullable=False)
    product_price: Mapped[int] = mapped_column(Integer, nullable=False)  # 分
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    specs: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
