"""所有 SQLAlchemy 模型的统一导出。"""
from app.models.user import User
from app.models.category import Category
from app.models.fishing_spot import FishingSpot
from app.models.forbidden_zone import ForbiddenZone
from app.models.weather_cache import WeatherCache
from app.models.spot_checkin import SpotCheckin
from app.models.share_token import ShareToken
from app.models.crowd_report import CrowdReport
from app.models.recipe import Recipe
from app.models.spot_rating import SpotRating

__all__ = [
    "User",
    "Category",
    "FishingSpot",
    "ForbiddenZone",
    "WeatherCache",
    "SpotCheckin",
    "ShareToken",
    "CrowdReport",
    "Recipe",
    "SpotRating",
]
