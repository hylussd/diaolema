"""天文计算路由。"""
from datetime import datetime, date
from fastapi import APIRouter, Query

from app.schemas.astronomy import AstronomyResponse, BestFishingSlot
from app.services.astronomy_service import calculate_moon_phase, calculate_sun_times

router = APIRouter()


def _best_fishing_slots(sun_times: dict, moon_phase: str) -> list[BestFishingSlot]:
    """根据日出日落和月相生成最佳钓鱼时段。"""
    slots = []
    sunrise = sun_times.get("sunrise", "06:00")
    sunset = sun_times.get("sunset", "18:00")

    # 清晨窗口：日出前1h ~ 日出后2h
    if sunrise != "--:--":
        try:
            h, m = int(sunrise[:2]), int(sunrise[3:])
            total_min = h * 60 + m - 60
            end_min = h * 60 + m + 120
            slots.append(BestFishingSlot(
                start=f"{max(0, total_min)//60:02d}:{(max(0,total_min)%60):02d}",
                end=f"{end_min//60:02d}:{(end_min%60):02d}",
                label="清晨窗口",
            ))
        except Exception:
            pass

    # 傍晚窗口：日落前2h ~ 日落后1h
    if sunset != "--:--":
        try:
            h, m = int(sunset[:2]), int(sunset[3:])
            start_min = h * 60 + m - 120
            end_min = h * 60 + m + 60
            slots.append(BestFishingSlot(
                start=f"{start_min//60:02d}:{(start_min%60):02d}",
                end=f"{min(24*60-1, end_min)//60:02d}:{(min(24*60-1,end_min)%60):02d}",
                label="傍晚窗口",
            ))
        except Exception:
            pass

    # 夜钓窗口（满月/盈凸月/亏凸月时增加）
    bright_moons = {"full_moon", "waxing_gibbous", "waning_gibbous"}
    if moon_phase in bright_moons and sunset != "--:--":
        try:
            h, m = int(sunset[:2]), int(sunset[3:])
            start_min = h * 60 + m + 60
            end_min = start_min + 180
            slots.append(BestFishingSlot(
                start=f"{start_min//60:02d}:{(start_min%60):02d}",
                end=f"{end_min//60:02d}:{(end_min%60):02d}",
                label="夜钓窗口",
            ))
        except Exception:
            pass

    return slots


@router.get("/astronomy", response_model=dict)
async def get_astronomy(
    lat: float = Query(..., description="纬度"),
    lng: float = Query(..., description="经度"),
    date_str: str = Query(..., alias="date", description="日期 YYYY-MM-DD"),
):
    """获取月相、日出日落及最佳钓鱼时段。"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        dt = datetime.now()

    moon_name, moon_code, illumination = calculate_moon_phase(dt)
    sun_times = calculate_sun_times(lat, lng, dt)
    fishing_slots = _best_fishing_slots(sun_times, moon_code)

    data = AstronomyResponse(
        date=date_str,
        moon_phase=moon_code,
        moon_phase_text=moon_name,
        moon_illumination=illumination,
        sunrise=sun_times["sunrise"],
        sunset=sun_times["sunset"],
        dawn=sun_times["dawn"],
        dusk=sun_times["dusk"],
        best_fishing_slots=fishing_slots,
    )
    return {"code": 0, "data": data.model_dump(), "msg": ""}
