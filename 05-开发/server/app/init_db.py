"""数据库初始化脚本：建表 + 预置数据。
用法：uv run python -m app.init_db
"""
import asyncio
import json
import sys
from datetime import datetime, timezone

# 确保 app 模块可导入
sys.path.insert(0, ".")

from sqlalchemy import text
from app.database import engine, async_session_maker, Base
from app.models.user import User
from app.models.category import Category
from app.models.fishing_spot import FishingSpot
from app.models.forbidden_zone import ForbiddenZone
from app.models.weather_cache import WeatherCache


# 预置禁钓区数据（polygon 存为 JSON 字符串，格式 [[lng, lat], ...]）
PRESET_FORBIDDEN_ZONES = [
    {
        "name": "武汉长江段（白沙洲-鹦鹉洲）",
        "polygon": json.dumps([
            [114.250, 30.450],
            [114.280, 30.445],
            [114.290, 30.470],
            [114.260, 30.480],
            [114.240, 30.465],
        ]),
        "reason": "长江通航水域，禁止锚鱼",
        "start_time": None,
        "end_time": None,
        "source": "武汉市渔政执法公告",
    },
    {
        "name": "北京密云水库一级保护区",
        "polygon": json.dumps([
            [116.780, 40.480],
            [116.850, 40.475],
            [116.860, 40.520],
            [116.790, 40.530],
            [116.770, 40.500],
        ]),
        "reason": "密云水库一级水源保护区，禁止一切渔业活动",
        "start_time": None,
        "end_time": None,
        "source": "北京市密云区人民政府公告",
    },
    {
        "name": "北京官厅水库（延庆段）",
        "polygon": json.dumps([
            [115.720, 40.380],
            [115.780, 40.370],
            [115.800, 40.410],
            [115.750, 40.420],
            [115.710, 40.400],
        ]),
        "reason": "饮用水源保护区，禁止钓鱼、游泳",
        "start_time": None,
        "end_time": None,
        "source": "北京市水务局公告",
    },
    {
        "name": "南京长江段（南京长江大桥上下游）",
        "polygon": json.dumps([
            [118.720, 32.050],
            [118.780, 32.040],
            [118.800, 32.070],
            [118.740, 32.080],
            [118.710, 32.060],
        ]),
        "reason": "长江主航道，禁止锚鱼和夜间垂钓",
        "start_time": None,
        "end_time": None,
        "source": "南京市农业农村局公告",
    },
]

# 预置分类
PRESET_CATEGORIES = [
    {"name": "野塘", "color": "#4CAF50", "sort_order": 1},
    {"name": "黑坑", "color": "#FF9800", "sort_order": 2},
    {"name": "江河", "color": "#2196F3", "sort_order": 3},
    {"name": "湖库", "color": "#9C27B0", "sort_order": 4},
    {"name": "海钓", "color": "#00BCD4", "sort_order": 5},
]


async def init_db():
    """建表 + 写入预置数据。"""
    print("🔧 开始初始化数据库...")

    async with engine.begin() as conn:
        # 建表（全部模型）
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据表创建完成")

    async with async_session_maker() as session:
        # 检查是否已有数据
        result = await session.execute(text("SELECT COUNT(*) FROM forbidden_zones"))
        fz_count = result.scalar()
        if fz_count > 0:
            print(f"⚠️  禁钓区已有 {fz_count} 条，跳过预置")
        else:
            for fz_data in PRESET_FORBIDDEN_ZONES:
                fz = ForbiddenZone(**fz_data)
                session.add(fz)
            print(f"✅ 预置 {len(PRESET_FORBIDDEN_ZONES)} 条禁钓区数据")

        # 检查分类
        result = await session.execute(text("SELECT COUNT(*) FROM categories"))
        cat_count = result.scalar()
        if cat_count > 0:
            print(f"⚠️  分类已有 {cat_count} 条，跳过预置")
        else:
            # 创建系统默认用户（ID=1）
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            if user_count == 0:
                default_user = User(openid="system", nickname="系统", role="admin")
                session.add(default_user)
                await session.flush()
                print("✅ 创建系统默认用户 (ID=1)")

            for i, cat_data in enumerate(PRESET_CATEGORIES):
                cat = Category(user_id=1, **cat_data)
                session.add(cat)
            print(f"✅ 预置 {len(PRESET_CATEGORIES)} 条分类数据")

        await session.commit()

    print("🎉 数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_db())
