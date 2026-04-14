# 钓了吗 API 契约

> 前后端对赌文档 - v1.0

---

## 认证

所有需要用户身份的接口，在请求头中携带：
```
X-Openid: <用户openid>
```

获取 openid：
```
POST /api/auth/openid
Body: { "code": "<wx.login返回的code>" }
Response: { "openid": "xxx" }
```

---

## 标点（Spots）

### GET /api/spots
查询标点列表

Query 参数：
- `category_id` (optional) - 按分类筛选
- `keyword` (optional) - 关键词搜索（名称/备注）

Response：
```json
{
  "items": [
    {
      "id": 1,
      "name": "东湖鱼塘",
      "latitude": 30.5728,
      "longitude": 114.2525,
      "terrain": "lake_shore",
      "terrain_label": "湖边",
      "fish_species": ["鲫鱼", "鲤鱼"],
      "note": "水深2米，收费20/天",
      "category_id": 1,
      "created_at": "2026-04-10T10:00:00Z"
    }
  ],
  "total": 100
}
```

### GET /api/spots/:id
标点详情

Response：
```json
{
  "id": 1,
  "name": "东湖鱼塘",
  "latitude": 30.5728,
  "longitude": 114.2525,
  "terrain": "lake_shore",
  "terrain_label": "湖边",
  "fish_species": ["鲫鱼", "鲤鱼"],
  "note": "水深2米，收费20/天",
  "category_id": 1,
  "created_at": "2026-04-10T10:00:00Z",
  "updated_at": "2026-04-10T10:00:00Z"
}
```

### POST /api/spots
新建标点

Body：
```json
{
  "name": "东湖鱼塘",
  "latitude": 30.5728,
  "longitude": 114.2525,
  "terrain": "lake_shore",
  "fish_species": ["鲫鱼", "鲤鱼"],
  "note": "水深2米，收费20/天",
  "category_id": 1
}
```

### PUT /api/spots/:id
更新标点（同 POST Body）

### DELETE /api/spots/:id
删除标点

Response：`204 No Content`

---

## 分类（Categories）

### GET /api/categories
Response：
```json
[
  { "id": 1, "name": "野钓", "count": 10 },
  { "id": 2, "name": "收费塘", "count": 5 }
]
```

### POST /api/categories
Body：`{ "name": "新分类" }`

### PUT /api/categories/:id
Body：`{ "name": "新名称" }`

### DELETE /api/categories/:id

---

## 天气（Weather）

> 服务端中转和风天气 API Key，不暴露给前端

### GET /api/weather/current
Query：`lat`, `lng`

Response：
```json
{
  "temp": 22,
  "condition": "多云",
  "pressure": 1013,
  "windSpeed": 12,
  "windScale": "3级",
  "windDir": "东南风",
  "humidity": 65,
  "precip": 0,
  "fishingIndex": "较适宜",
  "fishingTip": "气压稳定，适合出钓"
}
```

### GET /api/weather/forecast
Query：`lat`, `lng`

Response：
```json
{
  "daily": [
    {
      "date": "2026-04-15",
      "textDay": "多云",
      "tempMin": 18,
      "tempMax": 26,
      "windDirDay": "东南风",
      "windScaleDay": "3级",
      "precip": 0.1,
      "humidity": 65,
      "pressure": 1013,
      "uvIndex": 6
    }
  ]
}
```

---

## 禁钓区（Forbidden Zones）

### GET /api/forbidden-zones
Response：
```json
[
  {
    "id": 1,
    "name": "长江武汉段",
    "description": "全年禁钓",
    "coordinates": [[114.25, 30.57], [114.30, 30.58], ...]
  }
]
```

### GET /api/forbidden-zones/check
Query：`lat`, `lng`

Response：
```json
{ "in_zone": true, "zone": { "id": 1, "name": "长江武汉段", "description": "全年禁钓" } }
```

---

## 分享（Share）

### POST /api/share/qrcode
Body：`{ "path": "/pages/spot-detail/spot-detail", "scene": "id=1" }`

Response：
```json
{ "image_url": "/static/qrcode/xxx.png" }
```

---

## 错误响应格式

```json
{
  "detail": "错误描述",
  "code": "ERROR_CODE"
}
```

| HTTP 状态码 | 含义 |
|------------|------|
| 400 | 参数错误 |
| 401 | 未登录/openid无效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
