# 钓了吗 — 钓鱼标点地图

科学找标点，快乐钓鱼。

微信小程序 + Python FastAPI，数据融合型钓鱼工具，支持标点管理、天气查询、禁钓区预警。

---

## 功能预览

| 功能 | 说明 |
|---|---|
| 🗺️ 地图 | 卫星/路网双图层，GPS精准定位 |
| 📍 标点管理 | 创建/编辑/删除标点，补充地形、鱼种、备注 |
| 📂 分类管理 | 自定义分类文件夹，批量管理标点 |
| 🌤️ 天气查询 | 温度、气压、风力、湿度实时数据 |
| 🚫 禁钓区预警 | 进入禁钓区弹窗警告，避免违规 |
| 🔗 微信分享 | 生成小程序码/链接，一键分享给钓友 |

---

## 项目结构

```
钓了吗/
├── 05-开发/
│   ├── miniapp/          # 微信小程序前端
│   │   ├── pages/        # 页面（地图/标点/分类/天气/设置）
│   │   ├── components/    # 组件（天气卡片/标点卡片/禁钓弹窗）
│   │   ├── services/      # API请求封装
│   │   └── utils/         # 工具函数
│   └── server/           # Python FastAPI 后端
│       └── app/
│           ├── models/    # 数据库模型
│           ├── schemas/   # Pydantic schemas
│           ├── routers/   # API路由
│           └── services/  # 业务逻辑（天气服务等）
├── 01-方案/              # 产品方案文档
└── 06-汇报/             # 项目汇报文件
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:hylussd/diaolema.git
cd diaolema
```

### 2. 配置后端

```bash
cd 05-开发/server

# 复制环境变量配置
cp .env.example .env

# 编辑 .env，填入你的 Key
# - QWEATHER_API_KEY: 和风天气 API Key
# - WECHAT_APPID: 微信小程序 AppID
# - WECHAT_SECRET: 微信小程序 Secret
```

> 和风天气申请地址：https://dev.qweather.com/（有免费额度）

### 3. 安装依赖 & 启动后端

```bash
cd 05-开发/server

# 安装 Python 依赖（推荐使用 uv）
uv pip install -r requirements.txt

# 初始化数据库（建表 + 预置数据）
uv run python -m app.init_db

# 启动服务（默认 http://127.0.0.1:8000）
uv run python -m app.main
```

### 4. 启动小程序

1. 打开 **微信开发者工具**
2. 导入项目：`05-开发/miniapp/`
3. 在 `project.config.json` 中填入你的小程序 AppID
4. 勾选「不校验合法域名」（开发阶段）
5. 服务端地址默认 `http://127.0.0.1:8000`，可在「设置页」修改

---

## API 接口一览

后端启动后访问 `http://127.0.0.1:8000/docs` 查看完整 Swagger 文档。

| 模块 | 路径 | 说明 |
|---|---|---|
| 标点 | `GET/POST /api/spots` | 获取列表 / 创建标点 |
| 标点 | `GET/PUT/DELETE /api/spots/{id}` | 详情 / 更新 / 删除 |
| 分类 | `GET/POST /api/categories` | 获取 / 创建分类 |
| 分类 | `PUT/DELETE /api/categories/{id}` | 更新 / 删除分类 |
| 禁钓区 | `GET /api/forbidden-zones` | 获取所有禁钓区 |
| 禁钓区 | `POST /api/forbidden-zones/check` | 检查坐标是否在禁钓区 |
| 天气 | `GET /api/weather` | 获取当前位置天气 |
| 分享 | `GET /api/share/spot/{id}` | 生成标点分享码 |

---

## 环境要求

- **后端**：Python 3.10+，Node.js（可选）
- **前端**：微信开发者工具（最新版）
- **第三方API**：和风天气（必选）、微信小程序（必选）

---

## 更新日志

### 2026-04-14 — P0 MVP
- 地图 + 标点 CRUD + 分类管理
- 天气查询（和风API接入，5分钟缓存）
- 禁钓区标注 + 进入预警
- 微信分享码生成
- 完整 FastAPI 后端 + 微信小程序前端

---

## 注意事项

1. **天气API**：和风天气有免费额度，内陆淡水数据全覆盖，够早期使用
2. **水文数据**：当前版本水温/溶氧量依赖用户众包上报，后续版本支持
3. **禁钓区**：预置了长江/密云水库等典型区域，生产环境需对接官方数据源
4. **微信分享**：需填入真实的微信小程序 AppID 和 Secret

---

## 许可证

MIT License
