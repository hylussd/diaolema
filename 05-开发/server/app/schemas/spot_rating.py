"""钓点评分/点赞 Schema。"""
from pydantic import BaseModel, Field


class SpotRatingUpsert(BaseModel):
    spot_id: int = Field(..., gt=0)
    rating: int | None = Field(None, ge=1, le=5)
    liked: bool | None = None


class SpotRatingSummary(BaseModel):
    spot_id: int
    avg_rating: float | None = None
    rating_count: int = 0
    like_count: int = 0
    user_rating: int | None = None
    user_liked: bool | None = None
