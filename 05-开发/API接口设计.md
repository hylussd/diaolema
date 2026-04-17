# 钓了吗 P0 MVP API 接口设计

## 1. 概览

- **Base URL：** `https://api.diaolema.com/v1`（开发环境用 `http://127.0.0.1:8000/v1`）
- **认证方式：** Header `X-Openid`，由小程序在请求时注入（简化版无登录态，openid 即用户身份）
- **数据格式：** JSON
- **错误响应：** 统一格式 `{ "detail": "错误描述" }`

---

## 2. 用户接口

### 2.1 获取/创建用户

```
GET /users/me
```

**请求头：**
| 参数 | 必填 | 说明 |
|------|------|------|
| X-Openid | ✅ | 微信用户 openid |

**响应 200：**
```json
{
  "id": 1,
  "openid": "oXXXXXXX",
  "nickname": "钓鱼老王",
  "avatar_url": "https://xxx.com/avatar.png",
  "created_at": "2026-04-01T10:00:00Z"
}
```

> 逻辑：如果 openid 已存在则返回用户信息；首次访问则自动创建用户记录

---

## 3. 标点接口

### 3.1 创建标点

```
POST /spots
```

**请求体：**
```json
{
  "name": "南湖大桥下",
  "latitude": 28.2282,
  "longitude": 112.9388,
  "category_id": 1,
  "terrain": "河流",
  "fish_species": ["鲫鱼", "鲤鱼"],
  "fishing_method": "台钓",
  "water_depth": 2.5,
  "water_clarity": "微浊",
  "price_info": "免费",
  "description": "桥墩附近有回流，适合钓底",
  "photos": ["https://xxx.com/img1.jpg"],
  "is_public": 0,
  "extra": {}
}
```

**响应 201：**
```json
{
  "id": 10,
  "name": "南湖大桥下",
  "latitude": 28.2282,
  "longitude": 112.9388,
  "category_id": 1,
  "terrain": "河流",
  "fish_species": ["鲫鱼", "鲤鱼"],
  "fishing_method": "台钓",
  "water_depth": 2.5,
  "water_clarity": "微浊",
  "price_info": "免费",
  "description": "桥墩附近有回流，适合钓底",
  "photos": ["https://xxx.com/img1.jpg"],
  "is_public": 0,
  "extra": {},
  "created_at": "2026-04-14T15:00:00Z",
  "updated_at": "2026-04-14T15:00:00Z"
}
```

---

### 3.2 查询我的标点

```
GET /spots
```

**Query 参数：**
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| category_id | int | — | 按分类筛选 |
| keyword | string | — | 按名称模糊搜索 |
| offset | int | 0 | 翻页偏移 |
| limit | int | 20 | 每页数量（最大100） |

**响应 200：**
```json
{
  "total": 45,
  "offset": 0,
  "limit": 20,
  "items": [
    {
      "id": 10,
      "name": "南湖大桥下",
      "latitude": 28.2282,
      "longitude": 112.9388,
      "category_id": 1,
      "terrain": "河流",
      "fish_species": ["鲫鱼", "鲤鱼"],
      "fishing_method": "台钓",
      "water_depth": 2.5,
      "water_clarity": "微浊",
      "price_info": "免费",
      "description": "桥墩附近有回流，适合钓底",
      "photos": [],
      "is_public": 0,
      "extra": {},
      "created_at": "2026-04-14T15:00:00Z",
      "updated_at": "2026-04-14T15:00:00Z"
    }
  ]
}
```

---

### 3.3 获取单个标点

```
GET /spots/{spot_id}
```

**响应 200：** 标点详情对象（同 3.2 items 元素）

**响应 404：** `{ "detail": "标点不存在" }`

---

### 3.4 更新标点

```
PUT /spots/{spot_id}
```

**请求体：** 同 3.1，仅传需要更新的字段

**响应 200：** 更新后的标点对象

**响应 403：** `{ "detail": "无权操作此标点" }`

---

### 3.5 删除标点

```
DELETE /spots/{spot_id}
```

**响应 204：** 空 body

**响应 403：** `{ "detail": "无权操作此标点" }`

---

### 3.6 批量删除标点

```
POST /spots/batch-delete
```

**请求体：**
```json
{
  "spot_ids": [1, 2, 3]
}
```

**响应 200：**
```json
{
  "deleted": 3
}
```

---

### 3.7 公开标点列表（地图看别人分享的）

```
GET /spots/public
```

**Query 参数：**
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| lat | float | — | 中心纬度（用于附近排序） |
| lng | float | — | 中心经度 |
| radius_km | float | 50 | 半径（公里） |
| offset | int | 0 | |
| limit | int | 20 | |

**响应 200：** 同 3.2 paginated 格式

---

## 4. 分类接口

### 4.1 获取我的分类

```
GET /categories
```

**响应 200：**
```json
[
  {
    "id": 1,
    "name": "常去",
    "color": "#3B82F6",
    "sort_order": 0,
    "spot_count": 12,
    "created_at": "2026-04-01T10:00:00Z"
  },
  {
    "id": 2,
    "name": "打算去",
    "color": "#F59E0B",
    "sort_order": 1,
    "spot_count": 5,
    "created_at": "2026-04-01T10:00:00Z"
  }
]
```

---

### 4.2 创建分类

```
POST /categories
```

**请求体：**
```json
{
  "name": "常去",
  "color": "#3B82F6",
  "sort_order": 0
}
```

**响应 201：** 创建的分类对象

---

### 4.3 更新分类

```
PUT /categories/{category_id}
```

**请求体：** 同 4.2，仅传需要更新的字段

**响应 200：** 更新后的分类对象

---

### 4.4 删除分类

```
DELETE /categories/{category_id}
```

> 逻辑：删除分类后，该分类下的标点 `category_id` 置为 NULL（不连带删除标点）

**响应 204：** 空 body

---

### 4.5 批量移动标点到分类

```
POST /categories/{category_id}/move-spots
```

**请求体：**
```json
{
  "spot_ids": [1, 2, 3]
}
```

**响应 200：**
```json
{
  "moved": 3
}
```

---

## 5. 禁钓区接口

### 5.1 获取所有禁钓区

```
GET /forbidden-zones
```

**Query 参数：**
| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| lat | float | — | 用户当前纬度（用于计算距离） |
| lng | float | — | 用户当前经度 |
| radius_km | float | 100 | 查询半径 |

**响应 200：**
```json
{
  "items": [
    {
      "id": 1,
      "name": "湘江某河段",
      "polygon": [[112.93, 28.22], [112.95, 28.22], [112.95, 28.24], [112.93, 28.24]],
      "reason": "生态保护",
      "start_time": "2026-01-01T00:00:00Z",
      "end_time": "2026-12-31T23:59:59Z",
      "source": "政府公告",
      "distance_km": 1.2
    }
  ],
  "total": 1
}
```

---

### 5.2 检查坐标是否在禁钓区内

```
POST /forbidden-zones/check
```

**请求体：**
```json
{
  "latitude": 28.2282,
  "longitude": 112.9388
}
```

**响应 200：**
```json
{
  "inside": true,
  "zones": [
    {
      "id": 1,
      "name": "湘江某河段",
      "reason": "生态保护",
      "distance_m": 0
    }
  ]
}
```

> **说明：** 用于进入地图时的实时检测

---

### 5.3 管理员：新增禁钓区

```
POST /forbidden-zones
```

**请求体：**
```json
{
  "name": "湘江某河段",
  "polygon": [[112.93, 28.22], [112.95, 28.22], [112.95, 28.24], [112.93, 28.24]],
  "reason": "生态保护",
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-12-31T23:59:59Z",
  "source": "政府公告"
}
```

> **权限：** 需 X-Openid 对应 user.role='admin'（初期可跳过权限校验直接开放）

---

## 6. 天气接口

### 6.1 获取当前天气

```
GET /weather
```

**Query 参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| lat | float | ✅ | 纬度 |
| lng | float | ✅ | 经度 |

**响应 200：**
```json
{
  "location_key": "28.2282,112.9388",
  "temp": 22,
  "feels_like": 24,
  "pressure": 1013,
  "wind_speed": 3.5,
  "humidity": 65,
  "weather_text": "多云",
  "hourly": [
    {"time": "15:00", "temp": 22, "weather_text": "多云"},
    {"time": "16:00", "temp": 21, "weather_text": "多云"},
    {"time": "17:00", "temp": 20, "weather_text": "阴"}
  ],
  "cached": true,
  "cached_at": "2026-04-14T14:55:00Z"
}
```

> **逻辑：** 先查 weather_cache 缓存（TTL 5分钟），命中则直接返回；未命中则调和风 API

---

## 7. 分享接口

### 7.1 生成小程序码（服务端）

```
POST /share/generate-qrcode
```

**请求体：**
```json
{
  "spot_id": 10,
  "scene": "spot_10"
}
```

**响应 200：**
```json
{
  "qrcode_url": "https://api.diaolema.com/static/qrcode/abc123.png",
  "share_url": "diaolema://spot/10",
  "share_title": "南湖大桥下 - 钓了吗",
  "share_desc": "钓点分享：桥墩附近有回流，适合钓底"
}
```

> **说明：** 微信 `wxacode.getUnlimited` 生成无限制小程序码，scene 携带标点 ID
> **URL Scheme：** `diaolema://spot/{spot_id}`

---

## 8. 错误码汇总

| HTTP Status | detail 示例 | 说明 |
|-------------|-------------|------|
| 400 | 请求参数错误 | 参数格式/必填校验失败 |
| 401 | 未提供 openid | 缺少 X-Openid header |
| 403 | 无权操作此标点 | 标点不属于当前用户 |
| 404 | 标点不存在 | 资源未找到 |
| 422 | 字段验证失败 | Pydantic 校验失败 |
| 500 | 服务器内部错误 | 未知异常 |

---

## 9. P1 新增接口

### 9.1 多参数筛选

```
GET /spots/public/filter
```

**Query 参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pressure_min | float | — | 最低气压（hPa） |
| pressure_max | float | — | 最高气压（hPa） |
| temp_min | float | — | 最低水温（℃） |
| temp_max | float | — | 最高水温（℃） |
| fish_species | string | — | 鱼种（逗号分隔，如"鲫鱼,鲤鱼"） |
| spot_type | string | — | 钓场类型（水库/野河/湖泊等） |
| score_min | int | — | 最低推荐分数（0-100） |
| offset | int | 0 | 翻页偏移 |
| limit | int | 20 | 每页数量 |

**响应 200：**
```json
{
  "total": 8,
  "items": [{ ...标点对象，含 match_score 字段 }]
}
```

---

### 9.2 AI推荐

```
POST /spots/ai-recommend
```

**请求体：**
```json
{
  "fish_species": ["鲫鱼", "鲤鱼"],
  "date": "2026-04-14",
  "time_slot": "morning",
  "lat": 28.2282,
  "lng": 112.9388
}
```

**响应 200：**
```json
{
  "recommendations": [
    {
      "spot_id": 10,
      "name": "南湖大桥下",
      "score": 94,
      "reasons": [
        "气压 1008hPa，适合鲫鱼活性高峰",
        "水温 24℃，鱼群觅食积极",
        "西南风 2.5 级，溶氧充足"
      ]
    }
  ],
  "best_slot": { "time": "06:00-09:00", "reason": "此时段气压稳定，鱼口最佳" }
}
```

---

### 9.3 天文数据

```
GET /astronomy
```

**Query 参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| lat | float | ✅ | 纬度 |
| lng | float | ✅ | 经度 |
| date | string | — | 日期，默认今天（YYYY-MM-DD） |

**响应 200：**
```json
{
  "moon_phase": { "name": "上弦月", "code": "first_quarter", "illumination": 50 },
  "sunrise": "06:12",
  "sunset": "18:45",
  "dawn": "05:48",
  "dusk": "19:09"
}
```

---

### 9.4 打卡记录

```
POST /checkins
```
```json
{ "spot_id": 10, "fish_species": "鲫鱼", "weight": 0.5, "note": "上午口好" }
```

```
GET /checkins?spot_id=10
```
```json
{ "items": [{ "id": 1, "spot_id": 10, "fish_species": "鲫鱼", "weight": 0.5, "weather_data": {...}, "created_at": "..." }] }
```

```
DELETE /checkins/{id}
```
响应 204

---

### 9.5 分享Token

```
POST /share/tokens
```
```json
{ "spot_id": 10, "expires_days": 3 }
```
```json
{ "token": "abc123...", "share_url": "https://diaolema.com/share/abc123...", "expires_at": "2026-04-17T00:00:00Z" }
```

```
GET /share/tokens/{token}
```
Token有效：返回标点详情
Token无效/过期：410 Gone

```
DELETE /share/tokens/{token}
```
响应 204

---

## 10. 接口路径总览

| 方法 | 路径 | 阶段 | 说明 |
|------|------|------|------|
| GET | /users/me | P0 | 获取/创建用户 |
| POST | /spots | P0 | 创建标点 |
| GET | /spots | P0 | 查询我的标点（翻页+筛选） |
| GET | /spots/public | P0 | 公开标点列表 |
| GET | /spots/public/filter | P1 | 多参数筛选 |
| POST | /spots/ai-recommend | P1 | AI推荐 |
| GET | /spots/{spot_id} | P0 | 获取单个标点 |
| PUT | /spots/{spot_id} | P0 | 更新标点 |
| DELETE | /spots/{spot_id} | P0 | 删除标点 |
| POST | /spots/batch-delete | P0 | 批量删除标点 |
| GET | /categories | P0 | 获取我的分类 |
| POST | /categories | P0 | 创建分类 |
| PUT | /categories/{category_id} | P0 | 更新分类 |
| DELETE | /categories/{category_id} | P0 | 删除分类 |
| POST | /categories/{category_id}/move-spots | P0 | 批量移动标点 |
| GET | /forbidden-zones | P0 | 获取禁钓区列表 |
| POST | /forbidden-zones/check | P0 | 检测坐标是否在禁钓区 |
| POST | /forbidden-zones | P0 | 新增禁钓区（管理员） |
| GET | /weather | P0 | 获取天气（含缓存） |
| GET | /astronomy | P1 | 月相/日出日落 |
| POST | /checkins | P1 | 创建打卡 |
| GET | /checkins | P1 | 查询打卡记录 |
| DELETE | /checkins/{id} | P1 | 删除打卡 |
| POST | /share/generate-qrcode | P0 | 生成小程序码 |
| POST | /share/tokens | P1 | 生成加密Token |
| GET | /share/tokens/{token} | P1 | 访问分享Token |
| DELETE | /share/tokens/{token} | P1 | 撤销分享Token |

---

## P2 社区铺垫 — 接口列表

### 水文上报

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/crowd-reports | 创建水文上报（含防垃圾校验） |
| GET | /v1/crowd-reports | 查询标点水文数据 |

### 配方管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/recipes | 创建配方 |
| GET | /v1/recipes/me | 我的所有配方（含公开） |
| GET | /v1/recipes/public | 社区公开配方列表 |
| GET | /v1/recipes/{id} | 配方详情（公开任意访问，私有仅创建者） |
| PUT | /v1/recipes/{id} | 更新配方（仅创建者） |
| DELETE | /v1/recipes/{id} | 删除配方（仅创建者） |

### 标点评分/点赞

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/spot-ratings | 评分/点赞 upsert |
| GET | /v1/spot-ratings | 查询标点评分汇总 |

### 打卡记录扩展

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/checkins | 创建打卡（扩展 fishing_method、is_public） |
| GET | /v1/checkins | 查询打卡（支持 is_public=True 过滤） |

### P2 社区铺垫 — 接口列表

#### 水文上报

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/crowd-reports | 创建水文上报（含防垃圾校验） |
| GET | /v1/crowd-reports | 查询标点水文数据 |

#### 配方管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/recipes | 创建配方 |
| GET | /v1/recipes/me | 我的所有配方（含公开） |
| GET | /v1/recipes/public | 社区公开配方列表 |
| GET | /v1/recipes/{id} | 配方详情（公开任意访问，私有仅创建者） |
| PUT | /v1/recipes/{id} | 更新配方（仅创建者） |
| DELETE | /v1/recipes/{id} | 删除配方（仅创建者） |

#### 标点评分/点赞

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/spot-ratings | 评分/点赞 upsert |
| GET | /v1/spot-ratings | 查询标点评分汇总 |


---

## P3 商城接口

### 商品分类

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /v1/shop/categories | 商品分类列表 |

### 商品

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /v1/shop/products | 商品列表（支持分类/关键词/精选筛选） |
| GET | /v1/shop/products/{id} | 商品详情 |

### 购物车

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /v1/shop/cart | 获取当前用户购物车 |
| POST | /v1/shop/cart | 添加商品到购物车（upsert） |
| PUT | /v1/shop/cart/{item_id} | 更新购物车商品数量 |
| DELETE | /v1/shop/cart/{item_id} | 删除购物车商品 |
| DELETE | /v1/shop/cart | 清空购物车 |

### 订单

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /v1/shop/orders | 创建订单（购物车全量结算） |
| GET | /v1/shop/orders | 订单列表（支持状态筛选） |
| GET | /v1/shop/orders/{order_id} | 订单详情 |
| POST | /v1/shop/orders/{order_id}/pay | 模拟支付 |
| POST | /v1/shop/orders/{order_id}/cancel | 取消订单（退库存） |
