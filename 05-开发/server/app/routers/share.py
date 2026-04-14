"""微信分享码生成路由 + 分享 Token 管理。"""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.share_token import ShareToken
from app.models.fishing_spot import FishingSpot
from app.models.weather_cache import WeatherCache
from app.schemas.share_token import ShareTokenCreate, ShareTokenResponse, ShareTokenVisitResponse

router = APIRouter()


class ShareLinkResponse(BaseModel):
    spot_id: int
    title: str
    description: str
    url_scheme: str
    webpage_url: str


@router.get("/share/spots/{spot_id}", response_model=dict)
async def get_share_link(
    spot_id: int,
    title: str = "钓了吗",
    description: str = "一起来钓鱼吧！",
):
    """生成分享链接。
    URL Scheme: diaolema://spot/{spot_id}
    """
    url_scheme = f"diaolema://spot/{spot_id}"
    webpage_url = f"https://diaolema.com/share/spot?id={spot_id}"
    return {
        "code": 0,
        "data": {
            "spot_id": spot_id,
            "title": title,
            "description": description,
            "url_scheme": url_scheme,
            "webpage_url": webpage_url,
        },
        "msg": "",
    }


@router.post("/share/generate-qr", response_model=dict)
async def generate_qr(
    spot_id: int,
    title: str = "钓了吗",
):
    """生成分享二维码（返回 data URL）。
    实际项目建议调用微信 OCR 接口或第三方二维码服务。
    """
    import qrcode
    import io
    import base64

    url_scheme = f"diaolema://spot/{spot_id}"
    img = qrcode.make(url_scheme)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    data_url = f"data:image/png;base64,{b64}"

    return {
        "code": 0,
        "data": {
            "spot_id": spot_id,
            "title": title,
            "qr_data_url": data_url,
        },
        "msg": "",
    }


# ----------------------------------------------------------------------
# 分享 Token 管理（/share/tokens）
# ----------------------------------------------------------------------

@router.post("/share/tokens", response_model=dict)
async def create_share_token(
    data: ShareTokenCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """生成加密分享 Token。"""
    # 校验标点存在
    result = await db.execute(select(FishingSpot).where(FishingSpot.id == data.spot_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="标点不存在")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=data.valid_days)

    db_token = ShareToken(
        token=token,
        spot_id=data.spot_id,
        creator_user_id=user_id,
        expires_at=expires_at,
        max_valid_days=data.valid_days,
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)

    share_url = f"https://diaolema.com/share?token={token}"
    return {
        "code": 0,
        "data": {
            "token": token,
            "share_url": share_url,
            "expires_at": expires_at.isoformat(),
            "valid_days": data.valid_days,
        },
        "msg": "分享链接已生成",
    }


@router.get("/share/tokens/{token}", response_model=dict)
async def get_share_token(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """访问分享 Token，返回标点信息。过期返回 410 并删除。"""
    result = await db.execute(select(ShareToken).where(ShareToken.token == token))
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    if datetime.now(timezone.utc) > db_token.expires_at.replace(tzinfo=timezone.utc):
        # 惰性删除
        await db.execute(delete(ShareToken).where(ShareToken.token == token))
        await db.commit()
        raise HTTPException(status_code=410, detail="分享链接已过期")

    # 更新访问次数
    db_token.visit_count += 1
    await db.commit()

    # 查标点
    spot_result = await db.execute(select(FishingSpot).where(FishingSpot.id == db_token.spot_id))
    spot = spot_result.scalar_one_or_none()
    if not spot:
        raise HTTPException(status_code=404, detail="标点不存在")

    import json
    fish_species = []
    if spot.fish_species:
        try:
            fish_species = json.loads(spot.fish_species)
        except Exception:
            pass

    # 查天气
    location_key = f"{round(spot.latitude, 2)},{round(spot.longitude, 2)}"
    w_result = await db.execute(select(WeatherCache).where(WeatherCache.location_key == location_key))
    w = w_result.scalar_one_or_none()

    remaining = (db_token.expires_at.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).days

    return {
        "code": 0,
        "data": {
            "spot": {
                "id": spot.id,
                "name": spot.name,
                "latitude": spot.latitude,
                "longitude": spot.longitude,
                "terrain": spot.terrain,
                "fish_species": fish_species,
                "description": spot.description,
                "price_info": spot.price_info,
            },
            "weather": {
                "temp": w.now_temp if w else None,
                "pressure": w.now_pressure if w else None,
                "weather_text": w.now_weather_text if w else None,
            },
            "expires_at": db_token.expires_at.isoformat(),
            "remaining_days": max(0, remaining),
        },
        "msg": "",
    }


@router.delete("/share/tokens/{token}", response_model=dict)
async def delete_share_token(
    token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """撤销分享 Token（仅创建者可删除，TODO: 替换为真实认证）。"""
    result = await db.execute(select(ShareToken).where(ShareToken.token == token))
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=404, detail="分享链接不存在")

    await db.execute(delete(ShareToken).where(ShareToken.token == token))
    await db.commit()
    return {"code": 0, "data": {}, "msg": ""}
