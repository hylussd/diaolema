"""分类 CRUD 路由。"""
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.models.fishing_spot import FishingSpot
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithCount,
)

router = APIRouter()


@router.post("/categories", response_model=dict)
async def create_category(
    data: CategoryCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """创建分类。"""
    db_cat = Category(
        user_id=1,  # TODO: 从认证上下文获取
        name=data.name,
        color=data.color,
        sort_order=data.sort_order,
    )
    db.add(db_cat)
    await db.commit()
    await db.refresh(db_cat)
    return {"code": 0, "data": CategoryResponse.model_validate(db_cat).model_dump(), "msg": "创建成功"}


@router.get("/categories", response_model=dict)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """查询分类列表（带标点数量）。"""
    stmt = select(Category).order_by(Category.sort_order, Category.id)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    items = []
    for cat in categories:
        count_result = await db.execute(
            select(func.count(FishingSpot.id)).where(
                FishingSpot.category_id == cat.id
            )
        )
        count = count_result.scalar() or 0
        item = CategoryWithCount(
            id=cat.id,
            name=cat.name,
            color=cat.color,
            sort_order=cat.sort_order,
            created_at=cat.created_at,
            spot_count=count,
        )
        items.append(item.model_dump())

    return {"code": 0, "data": {"items": items, "total": len(items)}, "msg": ""}


@router.get("/categories/{category_id}", response_model=dict)
async def get_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """查询单个分类。"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"code": 0, "data": CategoryResponse.model_validate(cat).model_dump(), "msg": ""}


@router.put("/categories/{category_id}", response_model=dict)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """更新分类。"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")

    if data.name is not None:
        cat.name = data.name
    if data.color is not None:
        cat.color = data.color
    if data.sort_order is not None:
        cat.sort_order = data.sort_order

    await db.commit()
    await db.refresh(cat)
    return {"code": 0, "data": CategoryResponse.model_validate(cat).model_dump(), "msg": "更新成功"}


@router.delete("/categories/{category_id}", response_model=dict)
async def delete_category(
    category_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """删除分类（不做级联删除标点）。"""
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    await db.delete(cat)
    await db.commit()
    return {"code": 0, "data": {"id": category_id}, "msg": "删除成功"}
