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

## 9. 接口路径总览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /users/me | 获取/创建用户 |
| POST | /spots | 创建标点 |
| GET | /spots | 查询我的标点（翻页+筛选） |
| GET | /spots/public | 公开标点列表 |
| GET | /spots/{spot_id} | 获取单个标点 |
| PUT | /spots/{spot_id} | 更新标点 |
| DELETE | /spots/{spot_id} | 删除标点 |
| POST | /spots/batch-delete | 批量删除标点 |
| GET | /categories | 获取我的分类 |
| POST | /categories | 创建分类 |
| PUT | /categories/{category_id} | 更新分类 |
| DELETE | /categories/{category_id} | 删除分类 |
| POST | /categories/{category_id}/move-spots | 批量移动标点 |
| GET | /forbidden-zones | 获取禁钓区列表 |
| POST | /forbidden-zones/check | 检测坐标是否在禁钓区 |
| POST | /forbidden-zones | 新增禁钓区（管理员） |
| GET | /weather | 获取天气（含缓存） |
| POST | /share/generate-qrcode | 生成小程序码 |
