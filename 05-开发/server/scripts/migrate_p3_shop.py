"""P3 商城数据库迁移脚本。"""
import sqlite3
import os
import sys

# 添加 server 目录到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings

settings = get_settings()

# 从 DATABASE_URL 提取 .db 文件路径
db_url = settings.DATABASE_URL  # e.g. "sqlite+aiosqlite:///./data/diaolema.db"
db_path = db_url.replace("sqlite+aiosqlite:///", "")
if db_path.startswith("./"):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path[2:])
elif not os.path.isabs(db_path):
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_path)

print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# 先查已有表
existing_tables = set(r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print(f"现有表: {existing_tables}")

# --- 0. 确保 users 表存在 ---
if "users" not in existing_tables:
    print("⚠️ users 表不存在，创建基础 users 表")
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openid TEXT UNIQUE,
            nickname TEXT,
            avatar_url TEXT,
            role TEXT DEFAULT 'user',
            address_name TEXT,
            address_phone TEXT,
            address_detail TEXT,
            created_at DATETIME NOT NULL DEFAULT (datetime('now')),
            updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
        );
    """)
    # 创建一个测试用户
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, openid, nickname, role) VALUES (1, 'test_openid_1', '测试用户', 'user')"
    )
    conn.commit()
    print("✓ users 表创建完成并插入测试用户（id=1）")
else:
    # 补充缺失字段
    for col, col_type in [
        ("address_name", "TEXT"),
        ("address_phone", "TEXT"),
        ("address_detail", "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type};")
            print(f"✓ users.{col} 字段添加完成")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"- users.{col} 字段已存在，跳过")
            else:
                raise
    conn.commit()

# --- 1. product_categories ---
if "product_categories" not in existing_tables:
    cursor.execute("""
    CREATE TABLE product_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        icon TEXT,
        sort_order INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT (datetime('now'))
    );
    """)
    print("✓ product_categories 表创建完成")
else:
    print("- product_categories 表已存在，跳过")

# Seed 6 个分类
seed_categories = [
    ("饵料窝料", "🎯", 10),
    ("鱼钩鱼线", "🪝", 9),
    ("浮漂钓组", "🔺", 8),
    ("钓竿钓椅", "🎣", 7),
    ("配件工具", "🧰", 6),
    ("服装帽子", "🧢", 5),
]
for name, icon, sort_order in seed_categories:
    cursor.execute(
        "INSERT OR IGNORE INTO product_categories (name, icon, sort_order) VALUES (?, ?, ?)",
        (name, icon, sort_order),
    )
conn.commit()
print("✓ product_categories 种子数据写入完成")

# --- 2. products ---
if "products" not in existing_tables:
    cursor.execute("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL REFERENCES product_categories(id),
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        stock INTEGER DEFAULT 0,
        images TEXT,
        specs TEXT,
        is_active INTEGER DEFAULT 1,
        is_featured INTEGER DEFAULT 0,
        sales_count INTEGER DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT (datetime('now')),
        updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
    );
    """)
    cursor.execute("CREATE INDEX idx_products_category ON products(category_id);")
    cursor.execute("CREATE INDEX idx_products_active ON products(is_active);")
    print("✓ products 表创建完成")
else:
    print("- products 表已存在，跳过")

# --- 3. carts ---
if "carts" not in existing_tables:
    cursor.execute("""
    CREATE TABLE carts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
        created_at DATETIME NOT NULL DEFAULT (datetime('now')),
        updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
    );
    """)
    print("✓ carts 表创建完成")
else:
    print("- carts 表已存在，跳过")

# --- 4. cart_items ---
if "cart_items" not in existing_tables:
    cursor.execute("""
    CREATE TABLE cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER NOT NULL REFERENCES carts(id),
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity INTEGER NOT NULL DEFAULT 1,
        specs TEXT,
        created_at DATETIME NOT NULL DEFAULT (datetime('now')),
        updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
        UNIQUE(cart_id, product_id, specs)
    );
    """)
    print("✓ cart_items 表创建完成")
else:
    print("- cart_items 表已存在，跳过")

# --- 5. orders ---
if "orders" not in existing_tables:
    cursor.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL REFERENCES users(id),
        total_amount INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        address_name TEXT NOT NULL,
        address_phone TEXT NOT NULL,
        address_detail TEXT NOT NULL,
        remark TEXT,
        pay_status TEXT NOT NULL DEFAULT 'unpaid',
        pay_time DATETIME,
        created_at DATETIME NOT NULL DEFAULT (datetime('now')),
        updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
    );
    """)
    cursor.execute("CREATE INDEX idx_orders_user_id ON orders(user_id);")
    cursor.execute("CREATE INDEX idx_orders_order_no ON orders(order_no);")
    print("✓ orders 表创建完成")
else:
    print("- orders 表已存在，跳过")

# --- 6. order_items ---
if "order_items" not in existing_tables:
    cursor.execute("""
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES orders(id),
        product_id INTEGER NOT NULL REFERENCES products(id),
        product_name TEXT NOT NULL,
        product_price INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        specs TEXT,
        created_at DATETIME NOT NULL DEFAULT (datetime('now'))
    );
    """)
    cursor.execute("CREATE INDEX idx_order_items_order_id ON order_items(order_id);")
    print("✓ order_items 表创建完成")
else:
    print("- order_items 表已存在，跳过")

conn.commit()
conn.close()
print("\n✅ 迁移全部完成！")
