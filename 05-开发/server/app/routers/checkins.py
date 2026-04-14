"""打卡记录 CRUD 路由。"""
import json
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.spot_checkin import SpotCheckin
from app.models.weather_cache import WeatherCache
from app.schemas.spot_checkin import CheckinCreate, CheckinResponse

router = APIRouter()


def _checkin_to_dict(c: SpotCheckin) -> dict:
    fish_caught = c.fish_caught
    if fish_caught:
        try:
            fish_caught = json.loads(fish_caught)
        except Exception:
            pass
    return {
        "id": c.id,
        "user_id": c.user_id,
        "spot_id": c.spot_id,
        "fish_caught": fish_caught,
        "weight_kg": c.weight_kg,
        "weather_text": c.weather_text,
        "temp": c.temp,
        "pressure": c.pressure,
        "notes": c.notes,
        "checkin_time": c.checkin_time.isoformat() if c.checkin_time else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


async def _fetch_current_weather(db: AsyncSession, spot_id: int) -> dict:
    """从 weather_cache 读取最新天气数据。"""
    from app.models.fishing_spot import FishingSpot
    result = await db.execute(select(FishingSpot).where(FishingSpot.id == spot_id))
    spot = result.scalar_one_or_none()
    if not spot:
        return {}
    location_key = f"{round(spot.latitude, 2)},{round(spot.longitude, 2)}"
    cached = await db.execute(select(WeatherCache).where(WeatherCache.location_key == location_key))
    cache = cached.scalar_one_or_none()
    if not cache:
        return {}
    return {
        "weather_text": cache.now_weather_text,
        "temp": cache.now_temp,
        "pressure": cache.now_pressure,
    }


@router.post("/checkins", response_model=dict)
async def create_checkin(
    data: CheckinCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """新增打卡记录，自动关联当日天气。"""
    # 写入天气
    weather = await _fetch_current_weather(db, data.spot_id)
    fish_caught_json = json.dumps(data.fish_caught, ensure_ascii=False) if data.fish_caught else None

    checkin = SpotCheckin(
        user_id=user_id,
        spot_id=data.spot_id,
        fish_caught=fish_caught_json,
        weight_kg=data.weight_kg,
        weather_text=weather.get("weather_text"),
        temp=weather.get("temp"),
        pressure=weather.get("pressure"),
        notes=data.notes,
        checkin_time=datetime.now(timezone.utc),
    )
    db.add(checkin)
    await db.commit()
    await db.refresh(checkin)
    return {
        "code": 0,
        "data": {"id": checkin.id, "spot_id": checkin.spot_id, "checkin_time": checkin.checkin_time.isoformat()},
        "msg": "打卡成功",
    }


@router.get("/checkins", response_model=dict)
async def list_checkins(
    db: Annotated[AsyncSession, Depends(get_db)],
    spot_id: int | None = Query(None),
    user_id: int | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """查询打卡记录。"""
    stmt = select(SpotCheckin)
    count_stmt = select(func.count(SpotCheckin.id))

    if spot_id is not None:
        stmt = stmt.where(SpotCheckin.spot_id == spot_id)
        count_stmt = count_stmt.where(SpotCheckin.spot_id == spot_id)
    if user_id is not None:
        stmt = stmt.where(SpotCheckin.user_id == user_id)
        count_stmt = count_stmt.where(SpotCheckin.user_id == user_id)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit).order_by(SpotCheckin.checkin_time.desc())
    result = await db.execute(stmt)
    items = [_checkin_to_dict(c) for c in result.scalars().all()]

    return {
        "code": 0,
        "data": {"total": total, "items": items},
        "msg": "",
    }


@router.delete("/checkins/{checkin_id}", response_model=dict)
async def delete_checkin(
    checkin_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """删除打卡记录（仅创建者可删除，TODO: 替换为真实认证）。"""
    result = await db.execute(delete(SpotCheckin).where(SpotCheckin.id == checkin_id))
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="打卡记录不存在")
    return {"code": 0, "data": {"id": checkin_id}, "msg": "删除成功"}
