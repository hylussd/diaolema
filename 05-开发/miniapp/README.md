# 钓了吗 - 微信小程序前端

> P0 MVP 版本 | 微信小程序原生开发（WXML/WXSS/JS）

---

## 项目结构

```
miniapp/
├── app.js / app.json / app.wxss   # 应用入口
├── project.config.json             # 微信小程序项目配置
├── sitemap.json                    # SEO 配置
├── assets/                         # 静态资源
│   ├── images/                     # 位图（logo/空状态图/分享封面）
│   └── icons/                      # TabBar 图标（map/spot/category/me）
├── components/                     # 通用组件
│   ├── spot-card/                  # 标点卡片
│   ├── weather-card/               # 天气悬浮卡片
│   ├── category-picker/            # 分类多选器
│   ├── forbidden-modal/            # 禁钓区警告弹窗
│   └── loading/                    # 统一加载态
├── pages/                          # 页面
│   ├── index/                      # 地图首页 ⭐（TabBar 地图）
│   ├── spot-list/                  # 标点列表   （TabBar 标点）
│   ├── spot-detail/                # 标点详情
│   ├── spot-edit/                  # 新建/编辑标点
│   ├── category/                   # 分类管理   （TabBar 分类）
│   ├── weather/                    # 天气详情
│   └── settings/                   # 设置页     （TabBar 我的）
├── services/                       # API 业务层
│   ├── api.js                      # 基础请求封装
│   ├── spots.js                    # 标点 CRUD
│   ├── categories.js               # 分类管理
│   ├── weather.js                  # 天气（当前+7天预报）
│   ├── forbidden.js                # 禁钓区
│   └── share.js                   # 微信分享码
├── utils/                          # 工具函数
│   ├── request.js                  # wx.request Promise 封装
│   ├── constants.js                # 常量配置
│   ├── polygon.js                  # 地理多边形判断（射线法）
│   ├── distance.js                 # 两点距离（Haversine）
│   └── format.js                  # 日期/相对时间格式化
├── behaviors/                       # Behavior 逻辑复用
│   └── location-auth.js            # 定位权限校验
└── doc/
    └── api-contract.md             # API 契约文档
```

---

## 页面说明

| 页面 | 路径 | 说明 |
|------|------|------|
| 地图首页 | `pages/index/index` | 地图主界面，GPS定位，标点展示，禁钓区多边形，天气悬浮卡片 |
| 标点列表 | `pages/spot-list/spot-list` | 所有标点列表，支持分类筛选/关键词搜索 |
| 标点详情 | `pages/spot-detail/spot-detail` | 标点详情+关联天气+微信分享+导航 |
| 标点编辑 | `pages/spot-edit/spot-edit` | 新建/编辑标点（名称/坐标/地形/鱼种/备注/分类） |
| 分类管理 | `pages/category/category` | 新建/编辑/删除分类 |
| 天气详情 | `pages/weather/weather` | 当前天气+7天预报+钓鱼建议 |
| 设置页 | `pages/settings/settings` | 服务端地址/账号信息/隐私说明 |

---

## 地图页交互

- **首次进入**：请求定位权限，获取 GPS 后移动地图中心并加载天气
- **地图类型切换**：顶部工具栏「卫星/路网」按钮
- **标点点击**：底部弹出悬浮面板，点击进入详情
- **FAB按钮**（右下角加号）：新建标点，当前地图中心作为默认坐标
- **禁钓区**：红色半透明多边形标注，进入时弹出警告弹窗

---

## API 对接说明

### 服务端地址
- 开发环境：`http://127.0.0.1:8000`
- 可在「我的 → 设置 → 服务端地址」中修改（持久化到 Storage）

### API 契约（与后端对赌文档）

```
GET    /api/spots                    → 标点列表
GET    /api/spots/:id                → 标点详情
POST   /api/spots                    → 新建标点
PUT    /api/spots/:id                → 更新标点
DELETE /api/spots/:id                → 删除标点

GET    /api/categories               → 分类列表
POST   /api/categories               → 新建分类
PUT    /api/categories/:id           → 更新分类
DELETE /api/categories/:id          → 删除分类

GET    /api/weather/current?lat=&lng=     → 当前天气（服务端中转和风API）
GET    /api/weather/forecast?lat=&lng=    → 7天预报

GET    /api/forbidden-zones           → 禁钓区多边形数据
GET    /api/forbidden-zones/check?lat=&lng= → 坐标是否在禁钓区

POST   /api/auth/openid               → 微信 code 换 openid
POST   /api/share/qrcode             → 生成小程序码
```

详细字段请参考 `doc/api-contract.md`。

### 请求头
- `X-Openid`: 用户唯一标识（用于服务端鉴权）

---

## 本地开发

### 1. 安装微信开发者工具
下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)

### 2. 导入项目
打开微信开发者工具 → 导入项目 → 选择 `miniapp/` 目录

### 3. 配置 appid
在 `project.config.json` 中填入真实小程序 appid

### 4. 启动后端
```bash
cd server
uv pip install -r requirements.txt
uv run python -m app.main
# 服务运行在 http://127.0.0.1:8000
```

### 5. 开启调试
微信开发者工具 → 详情 → 本地设置 → 勾选「不校验合法域名...」（开发阶段）

---

## 设计原则

- **面向老钓手**：无新手引导，无花哨动画，功能直给
- **地图优先**：首页即地图，标点操作不超过 2 次点击
- **实用天气**：气压/风力/湿度直接展示，钓鱼建议一目了然
- **禁钓预警**：进入禁区立即弹窗警告，不存侥幸
