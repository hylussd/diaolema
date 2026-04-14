"""防垃圾服务：水文上报的数据校验和频率限制。"""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.spot_checkin import SpotCheckin
from app.models.crowd_report import CrowdReport
from app.services.constants import FISH_SPECIES_LIST, FISHING_METHODS, SPOT_TYPES

# 配置
WATER_TEMP_MIN = -5.0
WATER_TEMP_MAX = 40.0
DO_MIN = 0.0
DO_MAX = 20.0
MAX_REPORTS_PER_DAY = 3
CHECKIN_WINDOW_HOURS = 24


class AntiSpamService:
    """水文上报防垃圾校验。"""

    async def validate_report(
        self,
        db: AsyncSession,
        user_id: int,
        spot_id: int,
        checkin_id: int,
        water_temp: float,
        dissolved_oxygen: float,
        fish_species: str,
    ) -> SpotCheckin:
        """校验水文上报请求，返回关联的打卡记录。
        失败抛出 HTTPException。
        """
        # Step 1: 关联打卡校验
        latest = await self._get_latest_checkin(db, user_id, spot_id)
        if not latest:
            raise HTTPException(status_code=403, detail="您尚未在此标点打卡，无法上报水文数据")
        if latest.id != checkin_id:
            raise HTTPException(status_code=403, detail="上报需关联最近一次打卡记录")
        now = datetime.now(timezone.utc)
        if (now - latest.checkin_time.replace(tzinfo=timezone.utc)) > timedelta(hours=CHECKIN_WINDOW_HOURS):
            raise HTTPException(status_code=403, detail="打卡已超过24小时，无法上报水文数据")

        # Step 2: 数据范围校验
        if not (WATER_TEMP_MIN <= water_temp <= WATER_TEMP_MAX):
            raise HTTPException(status_code=400, detail=f"水温需在{WATER_TEMP_MIN}~{WATER_TEMP_MAX}°C之间")
        if not (DO_MIN <= dissolved_oxygen <= DO_MAX):
            raise HTTPException(status_code=400, detail=f"溶氧量需在{DO_MIN}~{DO_MAX}mg/L之间")
        if fish_species not in FISH_SPECIES_LIST:
            raise HTTPException(status_code=400, detail="鱼种不在标准列表中")

        # Step 3: 频率限制
        today_count = await self._get_today_report_count(db, user_id, spot_id)
        if today_count >= MAX_REPORTS_PER_DAY:
            raise HTTPException(
                status_code=429,
                detail=f"今日上报次数已达上限{MAX_REPORTS_PER_DAY}次，请明天再试",
            )
        return latest

    async def _get_latest_checkin(
        self, db: AsyncSession, user_id: int, spot_id: int
    ) -> SpotCheckin | None:
        stmt = (
            select(SpotCheckin)
            .where(SpotCheckin.user_id == user_id, SpotCheckin.spot_id == spot_id)
            .order_by(SpotCheckin.checkin_time.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_today_report_count(
        self, db: AsyncSession, user_id: int, spot_id: int
    ) -> int:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        stmt = select(func.count(CrowdReport.id)).where(
            CrowdReport.user_id == user_id,
            CrowdReport.spot_id == spot_id,
            CrowdReport.report_time >= today_start,
        )
        result = await db.execute(stmt)
        return result.scalar() or 0

    def validate_fishing_method(self, method: str | None) -> None:
        """校验钓法枚举。"""
        if method is not None and method not in FISHING_METHODS:
            raise HTTPException(
                status_code=400,
                detail=f"无效的钓法，可选：{', '.join(FISHING_METHODS)}",
            )

    def validate_spot_type(self, spot_type: str | None) -> None:
        """校验钓场类型枚举。"""
        if spot_type is not None and spot_type not in SPOT_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"无效的钓场类型，可选：{', '.join(SPOT_TYPES)}",
            )


anti_spam_service = AntiSpamService()
