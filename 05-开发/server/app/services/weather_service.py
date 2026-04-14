"""和风天气 API 服务，含 SQLite 缓存（TTL=300s）。"""
import json
from datetime import datetime, timezone
from typing import Annotated
import httpx

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.weather_cache import WeatherCache
from app.schemas.weather import WeatherResponse, HourlyForecast

# TTL = 300 秒
CACHE_TTL_SECONDS = 300


class WeatherService:
    def __init__(self, db: AsyncSession | None = None):
        self.db = db
        self.settings = get_settings()

    async def get_weather(self, latitude: float, longitude: float) -> WeatherResponse:
        """查询天气：优先读缓存，未过期直接返回；过期则调和风 API 并更新缓存。"""
        location_key = self._make_location_key(latitude, longitude)

        if self.db:
            cached = await self._get_cached(location_key)
            if cached and not self._is_expired(cached):
                return self._cache_to_response(cached, cached=True)

        # 未命中缓存，调和风 API
        fresh = await self._fetch_from_qweather(latitude, longitude)
        fresh.location_key = location_key

        if self.db:
            await self._save_cache(location_key, fresh)

        fresh.cached = False
        fresh.cached_at = None
        return fresh

    def _make_location_key(self, lat: float, lon: float) -> str:
        # 保留 2 位小数，约 1km 精度
        return f"{round(lat, 2)},{round(lon, 2)}"

    async def _get_cached(self, location_key: str) -> WeatherCache | None:
        stmt = select(WeatherCache).where(WeatherCache.location_key == location_key)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _is_expired(self, cache: WeatherCache) -> bool:
        return datetime.now(timezone.utc) > cache.expires_at.replace(tzinfo=timezone.utc)

    def _cache_to_response(self, cache: WeatherCache, cached: bool) -> WeatherResponse:
        hourly = None
        if cache.hourly_forecast:
            try:
                raw = json.loads(cache.hourly_forecast)
                hourly = [HourlyForecast(**h) for h in raw]
            except Exception:
                pass

        return WeatherResponse(
            location_key=cache.location_key,
            temp=cache.now_temp,
            feels_like=cache.now_feels_like,
            pressure=cache.now_pressure,
            wind_speed=cache.now_wind_speed,
            humidity=cache.now_humidity,
            weather_text=cache.now_weather_text,
            hourly=hourly,
            cached=cached,
            cached_at=cache.cached_at,
        )

    async def _fetch_from_qweather(
        self, latitude: float, longitude: float
    ) -> WeatherResponse:
        """调用和风天气 API v7。"""
        api_key = self.settings.QWEATHER_API_KEY
        if not api_key:
            # 无 API Key 时返回空数据
            return WeatherResponse(
                location_key=self._make_location_key(latitude, longitude),
                temp=None, feels_like=None, pressure=None,
                wind_speed=None, humidity=None,
                weather_text="未配置和风 API Key", hourly=None,
                cached=False, cached_at=None,
            )

        params = {
            "key": api_key,
            "location": f"{longitude},{latitude}",
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 实时天气
                r_now = await client.get(
                    "https://devapi.qweather.com/v7/weather/now", params=params
                )
                now_data = r_now.json().get("now", {})

                # 24小时预报
                r_hourly = await client.get(
                    "https://devapi.qweather.com/v7/weather/24h", params=params
                )
                hourly_raw = r_hourly.json().get("hourly", [])[:12]

                hourly = [
                    HourlyForecast(
                        time=h.get("fxTime", "")[-8:-3] if h.get("fxTime") else "",
                        temp=float(h.get("temp", 0)),
                        weather_text=h.get("text", ""),
                    )
                    for h in hourly_raw
                ]

                return WeatherResponse(
                    location_key=self._make_location_key(latitude, longitude),
                    temp=float(now_data.get("temp", 0)),
                    feels_like=float(now_data.get("feelsLike", 0)),
                    pressure=float(now_data.get("pressure", 0)),
                    wind_speed=float(now_data.get("windSpeed", 0)),
                    humidity=int(now_data.get("humidity", 0)),
                    weather_text=now_data.get("text", ""),
                    hourly=hourly,
                    cached=False,
                    cached_at=None,
                )
        except Exception as e:
            return WeatherResponse(
                location_key=self._make_location_key(latitude, longitude),
                temp=None, feels_like=None, pressure=None,
                wind_speed=None, humidity=None,
                weather_text=f"获取失败: {e}",
                hourly=None,
                cached=False,
                cached_at=None,
            )

    async def _save_cache(self, location_key: str, data: WeatherResponse):
        now = datetime.now(timezone.utc)
        expires = datetime.fromtimestamp(
            now.timestamp() + CACHE_TTL_SECONDS, tz=timezone.utc
        )

        hourly_json = None
        if data.hourly:
            hourly_json = json.dumps(
                [h.model_dump() for h in data.hourly], ensure_ascii=False
            )

        stmt = select(WeatherCache).where(WeatherCache.location_key == location_key)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.raw_response = None
            existing.now_temp = data.temp
            existing.now_pressure = data.pressure
            existing.now_wind_speed = data.wind_speed
            existing.now_humidity = data.humidity
            existing.now_weather_text = data.weather_text
            existing.now_feels_like = data.feels_like
            existing.hourly_forecast = hourly_json
            existing.cached_at = now
            existing.expires_at = expires
        else:
            cache = WeatherCache(
                location_key=location_key,
                now_temp=data.temp,
                now_pressure=data.pressure,
                now_wind_speed=data.wind_speed,
                now_humidity=data.humidity,
                now_weather_text=data.weather_text,
                now_feels_like=data.feels_like,
                hourly_forecast=hourly_json,
                cached_at=now,
                expires_at=expires,
            )
            self.db.add(cache)

        await self.db.commit()
