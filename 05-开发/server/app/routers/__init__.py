"""路由模块。"""
from app.routers import spots, categories, forbidden_zones, weather, share

# 注意：users 已在 main.py 中直接使用，若需启用请补充 app/routers/users.py
__all__ = ["spots", "categories", "forbidden_zones", "weather", "share"]
