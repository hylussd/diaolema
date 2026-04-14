/**
 * 常量配置
 */
module.exports = {
  // API 地址（开发环境，后续可在设置页修改）
  API_BASE: 'http://127.0.0.1:8000',

  // 地图配置
  MAP: {
    DEFAULT_LAT: 30.5728,
    DEFAULT_LNG: 114.2525,
    DEFAULT_SCALE: 14,
    MARKER_WIDTH: 36,
    MARKER_HEIGHT: 44,
  },

  // 地图类型
  MAP_TYPES: [
    { key: 'map', label: '路网' },
    { key: 'satellite', label: '卫星' },
  ],

  // 地形类型
  TERRAIN_TYPES: [
    { value: 'river_bank', label: '河岸' },
    { value: 'lake_shore', label: '湖边' },
    { value: 'pond', label: '池塘' },
    { value: 'reservoir', label: '水库' },
    { value: 'stream', label: '溪流' },
    { value: 'other', label: '其他' },
  ],

  // 鱼种列表
  FISH_SPECIES: [
    '鲫鱼', '鲤鱼', '草鱼', '青鱼', '鲢鳙', '鳊鱼',
    '黑鱼', '鳜鱼', '黄鳝', '泥鳅', '罗非', '翘嘴',
    '鲈鱼', '鲶鱼', '其他'
  ],

  // 禁钓区状态
  FORBIDDEN_STATUS: {
    SAFE: 'safe',
    WARNING: 'warning',
    FORBIDDEN: 'forbidden',
  },

  // P2: 钓法枚举
  FISHING_METHODS: ['台钓', '路亚', '传统钓', '飞蝇钓', '海竿', '手竿'],

  // P2: 钓场类型
  SPOT_TYPES: ['河流', '湖泊', '水库', '池塘', '其他'],
};
