"""标点 CRUD 路由 + 多参数筛选。"""
import json
import math
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.fishing_spot import FishingSpot
from app.models.weather_cache import WeatherCache
from app.schemas.fishing_spot import (
    SpotCreate,
    SpotUpdate,
    SpotResponse,
    SpotListResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)
from app.services.ai_recommend import score_spot
from app.services.astronomy_service import calculate_moon_phase

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


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离（km）。"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


@router.get("/spots/public/filter", response_model=dict)
async def filter_spots(
    db: Annotated[AsyncSession, Depends(get_db)],
    lat: float | None = Query(None, description="中心纬度"),
    lng: float | None = Query(None, description="中心经度"),
    radius_km: float = Query(50.0, ge=0.1, le=200, description="半径km"),
    pressure_min: int | None = Query(None, description="气压最小值 hPa"),
    pressure_max: int | None = Query(None, description="气压最大值 hPa"),
    temp_min: int | None = Query(None, description="气温最小值 ℃"),
    temp_max: int | None = Query(None, description="气温最大值 ℃"),
    fish_species: str | None = Query(None, description="鱼种，多个用逗号分隔"),
    category_type: str | None = Query(None, description="钓场类型 terrain"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """多参数筛选公开标点，返回带天气和 AI 推荐分数。"""
    # 查询所有公开标点
    stmt = select(FishingSpot).where(FishingSpot.is_public == 1)
    result = await db.execute(stmt)
    all_spots = result.scalars().all()

    target_fish = fish_species.split(",")[0].strip() if fish_species else ""
    moon_name, moon_code, _ = calculate_moon_phase(datetime.now(timezone.utc))
    time_slot = "morning"  # 默认时段，筛选接口不指定

    matched = []
    for spot in all_spots:
        # 距离过滤
        if lat is not None and lng is not None:
            dist = _haversine(lat, lng, spot.latitude, spot.longitude)
            if dist > radius_km:
                continue
        else:
            dist = None

        # 天气过滤
        location_key = f"{round(spot.latitude, 2)},{round(spot.longitude, 2)}"
        w_result = await db.execute(select(WeatherCache).where(WeatherCache.location_key == location_key))
        w = w_result.scalar_one_or_none()

        pressure = w.now_pressure if w else None
        temp = w.now_temp if w else None

        # 气压过滤
        if pressure_min is not None and (pressure is None or pressure < pressure_min):
            continue
        if pressure_max is not None and (pressure is None or pressure > pressure_max):
            continue

        # 水温过滤
        if temp_min is not None and (temp is None or temp < temp_min):
            continue
        if temp_max is not None and (temp is None or temp > temp_max):
            continue

        # 鱼种过滤
        spot_fish = []
        if spot.fish_species:
            try:
                spot_fish = json.loads(spot.fish_species)
            except Exception:
                pass
        if fish_species:
            wanted = [f.strip() for f in fish_species.split(",")]
            if not any(f in spot_fish for f in wanted):
                continue

        # 类型过滤
        if category_type and spot.terrain and category_type not in spot.terrain:
            continue

        # 评分
        score, reasons = score_spot(
            target_fish=target_fish,
            pressure=pressure,
            temp=temp,
            wind_speed=w.now_wind_speed if w else None,
            moon_phase_code=moon_code,
            time_slot=time_slot,
        )

        item = {
            "id": spot.id,
            "name": spot.name,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "terrain": spot.terrain,
            "fish_species": spot_fish,
            "is_public": spot.is_public,
            "weather": {
                "temp": temp,
                "pressure": pressure,
                "wind_speed": w.now_wind_speed if w else None,
                "weather_text": w.now_weather_text if w else None,
            },
            "match_score": score,
            "match_reasons": reasons,
        }
        if dist is not None:
            item["distance_km"] = dist

        matched.append(item)

    # 按 match_score 降序
    matched.sort(key=lambda x: x["match_score"], reverse=True)

    total = len(matched)
    items = matched[offset:offset + limit]

    return {
        "code": 0,
        "data": {"total": total, "offset": offset, "limit": limit, "items": items},
        "msg": "",
    }
