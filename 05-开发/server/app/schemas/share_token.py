"""分享 Token Schema。"""
from datetime import datetime
from pydantic import BaseModel, Field


class ShareTokenCreate(BaseModel):
    spot_id: int = Field(..., gt=0)
    valid_days: int = Field(default=7, ge=1, le=30)


class ShareTokenResponse(BaseModel):
    token: str
    share_url: str
    expires_at: datetime
    valid_days: int


class ShareTokenVisitResponse(BaseModel):
    spot: dict
    weather: dict
    expires_at: datetime
    remaining_days: int
