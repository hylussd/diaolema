"""禁钓区查询与坐标检查路由。"""
import json
import math
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.forbidden_zone import ForbiddenZone
from app.schemas.forbidden_zone import (
    ForbiddenZoneResponse,
    ForbiddenZoneListResponse,
    ForbiddenZoneCheckRequest,
    ForbiddenZoneCheckResponse,
)

router = APIRouter()


def _parse_polygon(raw: str | None) -> list[list[float]]:
    """解析 polygon 字段，返回 [[lng, lat], ...]。"""
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []


def _point_in_polygon(lat: float, lng: float, polygon: list[list[float]]) -> bool:
    """射线法判断点是否在多边形内。"""
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i][1], polygon[i][0]
        yj, xj = polygon[j][1], polygon[j][0]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间球面距离（km）。"""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.get("/forbidden-zones", response_model=dict)
async def list_forbidden_zones(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """查询所有禁钓区列表。"""
    result = await db.execute(select(ForbiddenZone).order_by(ForbiddenZone.id))
    zones = result.scalars().all()
    items = []
    for z in zones:
        items.append({
            "id": z.id,
            "name": z.name,
            "polygon": _parse_polygon(z.polygon),
            "reason": z.reason,
            "start_time": z.start_time.isoformat() if z.start_time else None,
            "end_time": z.end_time.isoformat() if z.end_time else None,
            "source": z.source,
            "distance_km": None,
        })
    return {"code": 0, "data": {"items": items, "total": len(items)}, "msg": ""}


@router.get("/forbidden-zones/check", response_model=dict)
async def check_forbidden_zone(
    db: Annotated[AsyncSession, Depends(get_db)],
    latitude: float = Query(...),
    longitude: float = Query(...),
):
    """检查给定坐标是否在禁钓区内，并计算距离最近的禁钓区。"""
    result = await db.execute(select(ForbiddenZone))
    zones = result.scalars().all()

    inside_zones = []
    for z in zones:
        polygon = _parse_polygon(z.polygon)
        is_inside = _point_in_polygon(latitude, longitude, polygon)

        # 计算到多边形最近点的距离（简化为到多边形中心的球面距离）
        if polygon:
            center_lat = sum(p[1] for p in polygon) / len(polygon)
            center_lng = sum(p[0] for p in polygon) / len(polygon)
        else:
            center_lat, center_lng = latitude, longitude
        dist = _haversine_km(latitude, longitude, center_lat, center_lng)

        zone_data = {
            "id": z.id,
            "name": z.name,
            "polygon": polygon,
            "reason": z.reason,
            "start_time": z.start_time.isoformat() if z.start_time else None,
            "end_time": z.end_time.isoformat() if z.end_time else None,
            "source": z.source,
            "distance_km": round(dist, 3),
        }

        if is_inside:
            inside_zones.append(zone_data)

    return {
        "code": 0,
        "data": {
            "inside": len(inside_zones) > 0,
            "zones": inside_zones,
        },
        "msg": "",
    }
