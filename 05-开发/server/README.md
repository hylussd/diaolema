# 钓了吗 API 服务

FastAPI 后端，提供钓点标点、分类、禁钓区查询、天气、微信分享等功能。

## 快速启动

```bash
# 1. 安装依赖
uv sync

# 2. 初始化数据库（建表 + 预置数据）
uv run python -m app.init_db

# 3. 启动服务
uv run python -m app.main
# 或
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 环境变量

复制 `.env.example` 为 `.env`，填入以下配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | SQLite 数据库路径 | `sqlite+aiosqlite:///./data/diaolema.db` |
| `QWEATHER_API_KEY` | 和风天气 API Key | 空 |
| `WECHAT_APPID` | 微信小程序 AppID | 空 |
| `WECHAT_SECRET` | 微信小程序 Secret | 空 |
| `WECHAT_MASTER_KEY` | 微信消息校验密钥 | 空 |
| `DEBUG` | 调试模式 | `true` |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔） | 见 `.env.example` |

## API 接口清单

> Base URL: `/v1`，所有接口返回格式：`{"code": 0, "data": ..., "msg": ""}`
> `code != 0` 表示错误。

### 标点（Spots）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `POST` | `/spots` | 创建标点 | body: `SpotCreate` |
| `GET` | `/spots` | 列表查询 | `offset`, `limit`, `category_id`, `keyword` |
| `GET` | `/spots/{spot_id}` | 详情 | `spot_id` |
| `PUT` | `/spots/{spot_id}` | 更新 | `spot_id`, body: `SpotUpdate` |
| `DELETE` | `/spots/{spot_id}` | 删除 | `spot_id` |
| `POST` | `/spots/batch-delete` | 批量删除 | body: `{"spot_ids": []}` |

### 分类（Categories）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `POST` | `/categories` | 创建分类 | body: `CategoryCreate` |
| `GET` | `/categories` | 列表（含标点数量） | - |
| `GET` | `/categories/{category_id}` | 详情 | `category_id` |
| `PUT` | `/categories/{category_id}` | 更新 | `category_id`, body: `CategoryUpdate` |
| `DELETE` | `/categories/{category_id}` | 删除 | `category_id` |

### 禁钓区（Forbidden Zones）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `GET` | `/forbidden-zones` | 列表 | - |
| `GET` | `/forbidden-zones/check` | 坐标是否在禁钓区内 | `latitude`, `longitude` |

### 天气（Weather）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `GET` | `/weather` | 查询天气（含缓存，TTL=300s） | `latitude`, `longitude` |

### 分享（Share）

| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| `GET` | `/share/spots/{spot_id}` | 生成分享链接 | `spot_id`, `title`, `description` |
| `POST` | `/share/generate-qr` | 生成二维码（Base64） | `spot_id`, `title` |

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 服务信息 |
| `GET` | `/health` | 健康检查 |

## 数据库初始化

```bash
uv run python -m app.init_db
```

预置数据：
- **分类**：野塘、黑坑、江河、湖库、海钓
- **禁钓区**：
  - 武汉长江段（白沙洲-鹦鹉洲）
  - 北京密云水库一级保护区
  - 北京官厅水库（延庆段）
  - 南京长江段（南京长江大桥上下游）

## 微信分享 URL Scheme

```
diaolema://spot/{spot_id}
```

唤起 App 后直接跳转对应标点详情页。

## 技术栈

- **框架**：FastAPI + Pydantic v2
- **ORM**：SQLAlchemy 2.0（async）
- **数据库**：SQLite（aiosqlite）
- **天气**：和风天气 API v7
- **二维码**：qrcode（Python）
