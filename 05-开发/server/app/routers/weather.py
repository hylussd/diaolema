"""天气查询路由。"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.weather_service import WeatherService
from app.schemas.weather import WeatherResponse

router = APIRouter()


@router.get("/weather", response_model=dict)
async def get_weather(
    latitude: float = Query(...),
    longitude: float = Query(...),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """查询指定坐标的天气，使用缓存（TTL=300s）。"""
    service = WeatherService(db)
    result = await service.get_weather(latitude, longitude)
    return {"code": 0, "data": result.model_dump(), "msg": ""}
