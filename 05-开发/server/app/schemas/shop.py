"""商城相关 Schema。"""
import json
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


def _parse_json(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


# =====================
# 商品分类
# =====================


class ProductCategorySchema(BaseModel):
    id: int
    name: str
    icon: str | None = None
    sort_order: int = 0

    class Config:
        from_attributes = True


# =====================
# 商品
# =====================


class ProductSchema(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None = None
    price: int  # 分
    stock: int
    images: list[str] | None = None
    specs: list[dict] | None = None
    is_active: int = 1
    is_featured: int = 0
    sales_count: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            category_id=obj.category_id,
            name=obj.name,
            description=obj.description,
            price=obj.price,
            stock=obj.stock,
            images=_parse_json(obj.images),
            specs=_parse_json(obj.specs),
            is_active=obj.is_active,
            is_featured=obj.is_featured,
            sales_count=obj.sales_count,
            created_at=obj.created_at,
        )


class ProductListResponse(BaseModel):
    total: int
    items: list[ProductSchema]


# =====================
# 购物车
# =====================


class CartItemSchema(BaseModel):
    id: int
    product_id: int
    name: str
    price: int  # 分
    images: list[str] | None = None
    specs: dict | None = None
    quantity: int
    subtotal: int  # 分

    class Config:
        from_attributes = True


class CartSchema(BaseModel):
    id: int
    items: list[CartItemSchema]
    total_amount: int  # 分
    total_count: int


class CartAddRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    specs: dict | None = None
    user_id: int | None = Field(default=None)  # 前端放 body 里


class CartUpdateRequest(BaseModel):
    quantity: int = Field(..., ge=0)  # 0 等同删除


# =====================
# 订单
# =====================


class OrderItemSchema(BaseModel):
    product_id: int
    name: str
    price: int  # 分
    quantity: int
    specs: dict | None = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            product_id=obj.product_id,
            name=obj.product_name,
            price=obj.product_price,
            quantity=obj.quantity,
            specs=_parse_json(obj.specs),
        )


class OrderSchema(BaseModel):
    order_id: int
    order_no: str
    total_amount: int  # 分
    status: str
    pay_status: str
    address_name: str | None = None
    address_phone: str | None = None
    address_detail: str | None = None
    remark: str | None = None
    items: list[OrderItemSchema] = []
    created_at: datetime | None = None
    pay_time: datetime | None = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    total: int
    items: list[OrderSchema]


class OrderCreateRequest(BaseModel):
    address_name: str = Field(..., min_length=1, max_length=64)
    address_phone: str = Field(..., min_length=1, max_length=32)
    address_detail: str = Field(..., min_length=1)
    remark: str | None = None
    pay_status: str = Field(default="unpaid")  # 传 paid 时模拟支付成功
    user_id: int | None = Field(default=None)  # 前端放 body 里


class OrderCreateResponse(BaseModel):
    order_id: int
    order_no: str
    total_amount: int
    status: str
    pay_status: str
