"""所有 SQLAlchemy 模型的统一导出。"""
from app.models.user import User
from app.models.category import Category
from app.models.fishing_spot import FishingSpot
from app.models.forbidden_zone import ForbiddenZone
from app.models.weather_cache import WeatherCache

__all__ = ["User", "Category", "FishingSpot", "ForbiddenZone", "WeatherCache"]
