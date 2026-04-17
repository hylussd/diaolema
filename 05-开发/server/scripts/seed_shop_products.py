"""P3 商城商品 Seed 数据。"""
import sqlite3
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import get_settings

settings = get_settings()
db_url = settings.DATABASE_URL
db_path = db_url.replace("sqlite+aiosqlite:///", "")
if db_path.startswith("./"):
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path[2:]
    )
elif not os.path.isabs(db_path):
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path
    )

print(f"Database path: {db_path}")
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# 查询分类ID
cursor.execute("SELECT id, name FROM product_categories ORDER BY sort_order DESC")
categories = {name: cid for cid, name in cursor.fetchall()}
print(f"Found categories: {categories}")

now = "datetime('now')"

# 6 个商品
products = [
    # 饵料窝料
    {
        "category": "饵料窝料",
        "name": "野战蓝鲫",
        "description": "经典广谱饵料，四季通用，拉丝粉含量适中，适合野钓综合鱼种。",
        "price": 199,
        "stock": 100,
        "images": json.dumps(["https://via.placeholder.com/400x400/2a9d8f/ffffff?text=野战蓝鲫"]),
        "specs": json.dumps([{"name": "规格", "options": ["50g", "100g", "200g"]}]),
        "is_featured": 1,
    },
    # 鱼钩鱼线
    {
        "category": "鱼钩鱼线",
        "name": "伊势尼12号鱼钩",
        "description": "钩条粗壮，强度高，适合钓获大体型鱼类，如鲤鱼、草鱼、青鱼等。",
        "price": 299,
        "stock": 200,
        "images": json.dumps(["https://via.placeholder.com/400x400/264653/ffffff?text=伊势尼12号"]),
        "specs": json.dumps([{"name": "数量", "options": ["10枚", "20枚"]}]),
        "is_featured": 0,
    },
    # 浮漂钓组
    {
        "category": "浮漂钓组",
        "name": "芦苇浮漂15目",
        "description": "天然芦苇材质，灵敏度极高，吃铅量适中，适合春秋季轻口鱼情。",
        "price": 599,
        "stock": 50,
        "images": json.dumps(["https://via.placeholder.com/400x400/e9c46a/264653?text=芦苇浮漂"]),
        "specs": json.dumps([{"name": "吃铅量", "options": ["1.5g", "2.0g", "2.5g"]}]),
        "is_featured": 1,
    },
    # 钓竿钓椅
    {
        "category": "钓竿钓椅",
        "name": "便携折叠钓椅",
        "description": "轻量化铝合金框架，可承重120kg，折叠后体积小巧，携带方便，适合野钓出行。",
        "price": 1999,
        "stock": 30,
        "images": json.dumps(["https://via.placeholder.com/400x400/264653/e9c46a?text=折叠钓椅"]),
        "specs": json.dumps([{"name": "颜色", "options": ["黑色", "军绿色"]}]),
        "is_featured": 0,
    },
    # 配件工具
    {
        "category": "配件工具",
        "name": "多功能子线盒",
        "description": "ABS材质防水盒，内置海绵分隔，可收纳子线、8字环、小配件，分层设计拿取方便。",
        "price": 399,
        "stock": 80,
        "images": json.dumps(["https://via.placeholder.com/400x400/f4a261/264653?text=子线盒"]),
        "specs": json.dumps([{"name": "层数", "options": ["单层", "三层"]}]),
        "is_featured": 0,
    },
    # 服装帽子
    {
        "category": "服装帽子",
        "name": "钓鱼防晒帽",
        "description": "宽檐防晒面料，UPF50+防护，有效遮挡阳光，面料透气速干，后置可调节系带。",
        "price": 499,
        "stock": 60,
        "images": json.dumps(["https://via.placeholder.com/400x400/e76f51/ffffff?text=防晒帽"]),
        "specs": json.dumps([{"name": "颜色", "options": ["卡其色", "深蓝色"]}]),
        "is_featured": 1,
    },
]

for product in products:
    cat_name = product.pop("category")
    cat_id = categories.get(cat_name)
    if not cat_id:
        print(f"⚠️ 分类 '{cat_name}' 未找到，跳过商品 '{product['name']}'")
        continue

    try:
        cursor.execute(
            f"""INSERT INTO products
                (category_id, name, description, price, stock, images, specs, is_featured, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'), datetime('now'))""",
            (
                cat_id,
                product["name"],
                product["description"],
                product["price"],
                product["stock"],
                product["images"],
                product["specs"],
                product["is_featured"],
            ),
        )
        print(f"✓ 商品 '{product['name']}' 插入成功")
    except Exception as e:
        print(f"✗ 商品 '{product['name']}' 插入失败: {e}")

conn.commit()
conn.close()
print("\n✅ Seed 数据写入完成！")
