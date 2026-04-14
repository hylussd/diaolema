"""标点 CRUD 路由。"""
import json
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.fishing_spot import FishingSpot
from app.schemas.fishing_spot import (
    SpotCreate,
    SpotUpdate,
    SpotResponse,
    SpotListResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)

router = APIRouter()


def _spot_to_dict(spot) -> dict:
    """将 ORM 对象转为字典，处理 JSON 字段。"""
    data = {}
    for field in (
        "id", "user_id", "category_id", "name", "latitude", "longitude",
        "terrain", "fish_species", "fishing_method", "water_depth",
        "water_clarity", "price_info", "description", "photos",
        "is_public", "extra", "created_at", "updated_at",
    ):
        val = getattr(spot, field)
        if field in ("fish_species", "photos", "extra") and val:
            try:
                val = json.loads(val)
            except Exception:
                pass
        data[field] = val
    return data


def _json_field(spot: SpotCreate | SpotUpdate, field: str):
    val = getattr(spot, field, None)
    if val is None:
        return None
    if isinstance(val, (list, dict)):
        return json.dumps(val, ensure_ascii=False)
    return val


@router.post("/spots", response_model=dict)
async def create_spot(
    spot: SpotCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """创建标点。"""
    db_spot = FishingSpot(
        user_id=1,  # TODO: 从认证上下文获取
        name=spot.name,
        latitude=spot.latitude,
        longitude=spot.longitude,
        category_id=spot.category_id,
        terrain=spot.terrain,
        fish_species=_json_field(spot, "fish_species"),
        fishing_method=spot.fishing_method,
        water_depth=spot.water_depth,
        water_clarity=spot.water_clarity,
        price_info=spot.price_info,
        description=spot.description,
        photos=_json_field(spot, "photos"),
        is_public=spot.is_public,
        extra=_json_field(spot, "extra"),
    )
    db.add(db_spot)
    await db.commit()
    await db.refresh(db_spot)
    return {"code": 0, "data": _spot_to_dict(db_spot), "msg": "创建成功"}


@router.get("/spots", response_model=dict)
async def list_spots(
    db: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int | None = None,
    keyword: str | None = None,
):
    """查询标点列表。"""
    stmt = select(FishingSpot)
    count_stmt = select(func.count(FishingSpot.id))

    if category_id is not None:
        stmt = stmt.where(FishingSpot.category_id == category_id)
        count_stmt = count_stmt.where(FishingSpot.category_id == category_id)
    if keyword:
        stmt = stmt.where(FishingSpot.name.ilike(f"%{keyword}%"))
        count_stmt = count_stmt.where(FishingSpot.name.ilike(f"%{keyword}%"))

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit).order_by(FishingSpot.updated_at.desc())
    result = await db.execute(stmt)
    spots = result.scalars().all()

    items = [_spot_to_dict(s) for s in spots]
    return {
        "code": 0,
        "data": {"total": total, "offset": offset, "limit": limit, "items": items},
        "msg": "",
    }


@router.get("/spots/{spot_id}", response_model=dict)
async def get_spot(
    spot_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """查询单个标点。"""
    result = await db.execute(select(FishingSpot).where(FishingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    if not spot:
        raise HTTPException(status_code=404, detail="标点不存在")
    return {"code": 0, "data": _spot_to_dict(spot), "msg": ""}


@router.put("/spots/{spot_id}", response_model=dict)
async def update_spot(
    spot_id: int,
    data: SpotUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """更新标点。"""
    result = await db.execute(select(FishingSpot).where(FishingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    if not spot:
        raise HTTPException(status_code=404, detail="标点不存在")

    update_fields = [
        ("name", data.name),
        ("latitude", data.latitude),
        ("longitude", data.longitude),
        ("category_id", data.category_id),
        ("terrain", data.terrain),
        ("fish_species", _json_field(data, "fish_species")),
        ("fishing_method", data.fishing_method),
        ("water_depth", data.water_depth),
        ("water_clarity", data.water_clarity),
        ("price_info", data.price_info),
        ("description", data.description),
        ("photos", _json_field(data, "photos")),
        ("is_public", data.is_public),
        ("extra", _json_field(data, "extra")),
    ]
    for field, value in update_fields:
        if value is not None:
            setattr(spot, field, value)

    await db.commit()
    await db.refresh(spot)
    return {"code": 0, "data": _spot_to_dict(spot), "msg": "更新成功"}


@router.delete("/spots/{spot_id}", response_model=dict)
async def delete_spot(
    spot_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """删除标点。"""
    result = await db.execute(delete(FishingSpot).where(FishingSpot.id == spot_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="标点不存在")
    return {"code": 0, "data": {"id": spot_id}, "msg": "删除成功"}


@router.post("/spots/batch-delete", response_model=dict)
async def batch_delete_spots(
    req: BatchDeleteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """批量删除标点。"""
    if not req.spot_ids:
        return {"code": 0, "data": {"deleted": 0}, "msg": ""}
    result = await db.execute(
        delete(FishingSpot).where(FishingSpot.id.in_(req.spot_ids))
    )
    await db.commit()
    return {"code": 0, "data": {"deleted": result.rowcount}, "msg": ""}
