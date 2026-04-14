"""AI 推荐路由（POST /spots/ai-recommend）。"""
import json
import math
from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.fishing_spot import FishingSpot
from app.models.weather_cache import WeatherCache
from app.services.astronomy_service import calculate_moon_phase, calculate_sun_times
from app.services.ai_recommend import score_spot, build_general_advice

router = APIRouter()


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离（km）。"""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 2)


def _get_location_key(lat: float, lon: float) -> str:
    return f"{round(lat, 2)},{round(lon, 2)}"


async def _get_weather(db: AsyncSession, lat: float, lon: float) -> dict:
    """从 weather_cache 读取当前天气。"""
    key = _get_location_key(lat, lon)
    cached = await db.execute(select(WeatherCache).where(WeatherCache.location_key == key))
    w = cached.scalar_one_or_none()
    if not w:
        return {"temp": None, "pressure": None, "wind_speed": None, "weather_text": "未知"}
    return {
        "temp": w.now_temp,
        "pressure": w.now_pressure,
        "wind_speed": w.now_wind_speed,
        "weather_text": w.now_weather_text or "未知",
    }


@router.post("/spots/ai-recommend", response_model=dict)
async def ai_recommend(
    body: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    AI 推荐接口。
    body: { target_fish, date, time_slot, lat, lng, radius_km }
    """
    target_fish: str = body.get("target_fish", "")
    date_str: str = body.get("date", datetime.now().strftime("%Y-%m-%d"))
    time_slot: str = body.get("time_slot", "morning")
    lat: float = body.get("lat", 0)
    lng: float = body.get("lng", 0)
    radius_km: float = body.get("radius_km", 10)

    # 天文计算
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        dt = datetime.now()
    moon_name, moon_code, illumination = calculate_moon_phase(dt)
    sun_times = calculate_sun_times(lat, lng, dt)

    # 天气
    weather = await _get_weather(db, lat, lng)
    moon_phase_text_map = {
        "new_moon": "新月", "waxing_crescent": "蛾眉月",
        "first_quarter": "上弦月", "waxing_gibbous": "盈凸月",
        "full_moon": "满月", "waning_gibbous": "亏凸月",
        "last_quarter": "下弦月", "waning_crescent": "残月",
    }

    # 查询附近公开标点
    stmt = select(FishingSpot).where(FishingSpot.is_public == 1)
    result = await db.execute(stmt)
    all_spots = result.scalars().all()

    scored = []
    for spot in all_spots:
        dist = _haversine(lat, lng, spot.latitude, spot.longitude)
        if dist > radius_km:
            continue

        # 获取标点附近天气（简化：使用用户位置天气）
        score, reasons = score_spot(
            target_fish=target_fish,
            pressure=weather.get("pressure"),
            temp=weather.get("temp"),
            wind_speed=weather.get("wind_speed"),
            moon_phase_code=moon_code,
            time_slot=time_slot,
        )

        fish_species = []
        if spot.fish_species:
            try:
                fish_species = json.loads(spot.fish_species)
            except Exception:
                pass

        scored.append({
            "id": spot.id,
            "name": spot.name,
            "latitude": spot.latitude,
            "longitude": spot.longitude,
            "terrain": spot.terrain,
            "fish_species": fish_species,
            "distance_km": dist,
            "score": score,
            "reasons": reasons,
        })

    # 按分数降序
    scored.sort(key=lambda x: x["score"], reverse=True)

    general_advice = build_general_advice(target_fish, date_str, time_slot, moon_name)

    return {
        "code": 0,
        "data": {
            "target_fish": target_fish,
            "date": date_str,
            "time_slot": time_slot,
            "weather": {
                "temp": weather.get("temp"),
                "pressure": weather.get("pressure"),
                "wind_speed": weather.get("wind_speed"),
                "moon_phase": moon_code,
                "moon_phase_text": moon_name,
                "sunrise": sun_times["sunrise"],
                "sunset": sun_times["sunset"],
            },
            "spots": scored[:20],
            "general_advice": general_advice,
        },
        "msg": "",
    }
