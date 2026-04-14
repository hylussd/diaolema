"""水文上报 CRUD 路由。"""
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.crowd_report import CrowdReport
from app.models.spot_checkin import SpotCheckin
from app.schemas.crowd_report import CrowdReportCreate, CrowdReportResponse
from app.services.anti_spam_service import anti_spam_service

router = APIRouter()


@router.post("/crowd-reports", response_model=dict)
async def create_crowd_report(
    data: CrowdReportCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """创建水文上报表（含防垃圾校验）。"""
    checkin = await anti_spam_service.validate_report(
        db=db,
        user_id=user_id,
        spot_id=data.spot_id,
        checkin_id=data.checkin_id,
        water_temp=data.water_temp,
        dissolved_oxygen=data.dissolved_oxygen,
        fish_species=data.fish_species,
    )

    report = CrowdReport(
        user_id=user_id,
        spot_id=data.spot_id,
        checkin_id=data.checkin_id,
        water_temp=data.water_temp,
        dissolved_oxygen=data.dissolved_oxygen,
        fish_species=data.fish_species,
        report_time=datetime.now(timezone.utc),
    )
    db.add(report)
    await db.flush()

    # 回填 checkin.crowd_report_id
    checkin.crowd_report_id = report.id
    await db.commit()
    await db.refresh(report)

    return {
        "code": 0,
        "data": {
            "id": report.id,
            "spot_id": report.spot_id,
            "checkin_id": report.checkin_id,
            "report_time": report.report_time.isoformat(),
        },
        "msg": "上报成功",
    }


@router.get("/crowd-reports", response_model=dict)
async def list_crowd_reports(
    db: Annotated[AsyncSession, Depends(get_db)],
    spot_id: int = Query(..., gt=0, description="标点ID"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Query(None, description="用户ID过滤"),
):
    """查询标点的水文数据。"""
    stmt = select(CrowdReport).where(CrowdReport.spot_id == spot_id)
    count_stmt = select(func.count(CrowdReport.id)).where(CrowdReport.spot_id == spot_id)

    if user_id is not None:
        stmt = stmt.where(CrowdReport.user_id == user_id)
        count_stmt = count_stmt.where(CrowdReport.user_id == user_id)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    stmt = stmt.offset(offset).limit(limit).order_by(CrowdReport.report_time.desc())
    result = await db.execute(stmt)
    items = [
        {
            "id": r.id,
            "water_temp": r.water_temp,
            "dissolved_oxygen": r.dissolved_oxygen,
            "fish_species": r.fish_species,
            "report_time": r.report_time.isoformat() if r.report_time else None,
        }
        for r in result.scalars().all()
    ]

    return {
        "code": 0,
        "data": {"total": total, "items": items},
        "msg": "",
    }
