"""Pydantic schemas 统一导出。"""
from app.schemas.user import UserCreate, UserResponse
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithCount,
)
from app.schemas.fishing_spot import (
    SpotCreate,
    SpotUpdate,
    SpotResponse,
    SpotListResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
)
from app.schemas.forbidden_zone import (
    ForbiddenZoneCreate,
    ForbiddenZoneResponse,
    ForbiddenZoneListResponse,
    ForbiddenZoneCheckRequest,
    ForbiddenZoneCheckResponse,
)
from app.schemas.weather import WeatherResponse
from app.schemas.common import ApiResponse, PageMeta
