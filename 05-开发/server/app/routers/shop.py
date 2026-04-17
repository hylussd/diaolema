"""商城路由（/v1/shop/*）。"""
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ProductCategory, Product, CartItem, Order, OrderItem
from app.schemas.shop import (
    ProductCategorySchema,
    ProductSchema,
    ProductListResponse,
    CartAddRequest,
    CartUpdateRequest,
    OrderCreateRequest,
    OrderSchema,
    OrderListResponse,
    OrderCreateResponse,
)
from app.services.shop_service import shop_service

router = APIRouter()


# =====================
# 辅助函数
# =====================


async def get_current_user_id(request: Request) -> int | None:
    """
    尝试从请求中获取当前登录用户ID。
    优先从 header（x-user-id）获取，否则从 cookie（user_id）获取。
    未登录返回 None。
    """
    user_id = request.headers.get("x-user-id")
    if user_id:
        try:
            return int(user_id)
        except ValueError:
            pass
    cookie_val = request.cookies.get("user_id")
    if cookie_val:
        try:
            return int(cookie_val)
        except ValueError:
            pass
    return None


def require_login(user_id: int | None) -> int:
    """要求登录，未登录抛出 401。"""
    if user_id is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return user_id


# =====================
# 商品分类
# =====================


@router.get("/shop/categories", response_model=dict)
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    """分类列表（is_active=1，按 sort_order DESC）。"""
    result = await db.execute(
        select(ProductCategory)
        .where(ProductCategory.is_active == 1)
        .order_by(ProductCategory.sort_order.desc())
    )
    categories = result.scalars().all()
    return {
        "code": 0,
        "data": [ProductCategorySchema.model_validate(c) for c in categories],
        "msg": "",
    }


# =====================
# 商品
# =====================


@router.get("/shop/products", response_model=dict)
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int | None = Query(None),
    keyword: str | None = Query(None),
    is_featured: bool | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """商品列表（支持分类/关键词/精选筛选，支持分页）。"""
    stmt = select(Product).where(Product.is_active == 1)
    count_stmt = select(func.count(Product.id)).where(Product.is_active == 1)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
        count_stmt = count_stmt.where(Product.category_id == category_id)

    if keyword:
        stmt = stmt.where(Product.name.like(f"%{keyword}%"))
        count_stmt = count_stmt.where(Product.name.like(f"%{keyword}%"))

    if is_featured is True:
        stmt = stmt.where(Product.is_featured == 1)
        count_stmt = count_stmt.where(Product.is_featured == 1)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit).order_by(Product.created_at.desc())
    result = await db.execute(stmt)
    products = result.scalars().all()

    return {
        "code": 0,
        "data": {
            "total": total,
            "items": [ProductSchema.from_orm(p) for p in products],
        },
        "msg": "",
    }


@router.get("/shop/products/{product_id}", response_model=dict)
async def get_product(
    product_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    """商品详情。"""
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == 1)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {
        "code": 0,
        "data": ProductSchema.from_orm(product),
        "msg": "",
    }


# =====================
# 购物车
# =====================


@router.get("/shop/cart", response_model=dict)
async def get_cart(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """获取当前用户购物车。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    cart = await shop_service.get_cart_with_items(db, uid)
    return {
        "code": 0,
        "data": cart.model_dump(),
        "msg": "",
    }


@router.post("/shop/cart", response_model=dict)
async def add_to_cart(
    request: Request,
    body: CartAddRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """添加商品到购物车。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        result = await shop_service.create_or_update_cart_item(
            db, uid, body.product_id, body.quantity, body.specs
        )
    except HTTPException:
        raise
    return {
        "code": 0,
        "data": result,
        "msg": "已加入购物车",
    }


@router.put("/shop/cart/{item_id}", response_model=dict)
async def update_cart_item(
    item_id: int,
    request: Request,
    body: CartUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """更新购物车商品数量（quantity=0 等同删除）。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        await shop_service.update_cart_item(db, uid, item_id, body.quantity)
    except HTTPException:
        raise
    return {"code": 0, "data": None, "msg": "更新成功"}


@router.delete("/shop/cart/{item_id}", response_model=dict)
async def delete_cart_item(
    item_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """删除购物车商品。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        await shop_service.delete_cart_item(db, uid, item_id)
    except HTTPException:
        raise
    return {"code": 0, "data": None, "msg": "已删除"}


@router.delete("/shop/cart", response_model=dict)
async def clear_cart(
    request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    """清空购物车。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    await shop_service.clear_cart(db, uid)
    return {"code": 0, "data": None, "msg": "购物车已清空"}


# =====================
# 订单
# =====================


@router.post("/shop/orders", response_model=dict)
async def create_order(
    request: Request,
    body: OrderCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """创建订单（购物车全量结算）。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        order = await shop_service.create_order_from_cart(
            db,
            uid,
            body.address_name,
            body.address_phone,
            body.address_detail,
            body.remark,
            body.pay_status,
        )
    except HTTPException:
        raise
    return {
        "code": 0,
        "data": order.model_dump(),
        "msg": "订单创建成功",
    }


@router.get("/shop/orders", response_model=dict)
async def list_orders(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """订单列表。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    result = await shop_service.get_order_list(db, uid, status, offset, limit)
    return {
        "code": 0,
        "data": result,
        "msg": "",
    }


@router.get("/shop/orders/{order_id}", response_model=dict)
async def get_order(
    order_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """订单详情。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        order = await shop_service.get_order_detail(db, uid, order_id)
    except HTTPException:
        raise
    return {
        "code": 0,
        "data": order.model_dump(),
        "msg": "",
    }


@router.post("/shop/orders/{order_id}/pay", response_model=dict)
async def mock_pay_order(
    order_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    pay_status: str = Query("paid"),
):
    """模拟支付。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        result = await shop_service.mock_pay(db, uid, order_id, pay_status)
    except HTTPException:
        raise
    return {
        "code": 0,
        "data": result,
        "msg": "支付成功",
    }


@router.post("/shop/orders/{order_id}/cancel", response_model=dict)
async def cancel_order(
    order_id: int,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """取消订单（仅 pending 状态）。"""
    user_id = await get_current_user_id(request)
    uid = require_login(user_id)

    try:
        await shop_service.cancel_order(db, uid, order_id)
    except HTTPException:
        raise
    return {"code": 0, "data": None, "msg": "订单已取消"}
