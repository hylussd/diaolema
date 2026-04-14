"""钓点评分/点赞路由。"""
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.spot_rating import SpotRating
from app.schemas.spot_rating import SpotRatingUpsert, SpotRatingSummary

router = APIRouter()


@router.post("/spot-ratings", response_model=dict)
async def upsert_spot_rating(
    data: SpotRatingUpsert,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = Query(1, description="用户ID，TODO: 替换为真实认证"),
):
    """评分或更新评分/点赞（upsert）。"""
    stmt = select(SpotRating).where(
        SpotRating.user_id == user_id, SpotRating.spot_id == data.spot_id
    )
    result = await db.execute(stmt)
    record = result.scalar_one_or_none()

    if record:
        if data.rating is not None:
            record.rating = data.rating
        if data.liked is not None:
            record.liked = 1 if data.liked else 0
        record.updated_at = datetime.now(timezone.utc)
    else:
        record = SpotRating(
            user_id=user_id,
            spot_id=data.spot_id,
            rating=data.rating,
            liked=1 if (data.liked if data.liked is not None else True) else 0,
            updated_at=datetime.now(timezone.utc),
        )
        db.add(record)

    await db.commit()
    return {
        "code": 0,
        "data": {
            "spot_id": data.spot_id,
            "rating": record.rating,
            "liked": bool(record.liked),
        },
        "msg": "评分成功" if data.rating else "点赞成功",
    }


@router.get("/spot-ratings", response_model=dict)
async def get_spot_rating_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    spot_id: int = Query(..., gt=0, description="标点ID"),
    user_id: int = Query(None, description="当前用户ID，过滤个人数据"),
):
    """查询某标点的评分汇总。"""
    # 聚合
    agg_stmt = select(
        func.avg(SpotRating.rating).label("avg_rating"),
        func.count(SpotRating.id).label("rating_count"),
        func.sum(SpotRating.liked).label("like_count"),
    ).where(SpotRating.spot_id == spot_id)
    agg_result = await db.execute(agg_stmt)
    agg = agg_result.mappings().first()

    avg_rating = round(float(agg["avg_rating"]), 1) if agg["avg_rating"] else None
    rating_count = agg["rating_count"] or 0
    like_count = agg["like_count"] or 0

    # 用户个人数据
    user_rating = None
    user_liked = None
    if user_id:
        user_stmt = select(SpotRating).where(
            SpotRating.user_id == user_id, SpotRating.spot_id == spot_id
        )
        user_result = await db.execute(user_stmt)
        user_record = user_result.scalar_one_or_none()
        if user_record:
            user_rating = user_record.rating
            user_liked = bool(user_record.liked)

    return {
        "code": 0,
        "data": {
            "spot_id": spot_id,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "like_count": like_count,
            "user_rating": user_rating,
            "user_liked": user_liked,
        },
        "msg": "",
    }
