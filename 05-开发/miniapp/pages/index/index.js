// pages/index/index.js
// 地图首页
const app = getApp();
const constants = require('../../utils/constants');
const { getSpots } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const { getForbiddenZones } = require('../../services/forbidden');
const { isInForbiddenZone } = require('../../utils/polygon');
const { distance, formatDistance } = require('../../utils/distance');

Page({
  data: {
    latitude: constants.MAP.DEFAULT_LAT,
    longitude: constants.MAP.DEFAULT_LNG,
    scale: constants.MAP.DEFAULT_SCALE,
    mapType: 'map',          // 'map' | 'satellite'
    satellites: [],          // 标点列表
    polygons: [],            // 禁钓区多边形
    controls: [],
    showForbidden: false,    // 显示禁钓区
    forbiddenZone: null,
    weather: null,
    weatherLoading: true,
    userLocation: null,
    showSpotPanel: false,   // 底部标点面板
    selectedSpot: null,
    locationEnabled: false,
  },

  onLoad() {
    this.initLocation();
    this.loadForbiddenZones();
  },

  onShow() {
    // 每次进入刷新标点
    this.loadSpots();
    this.checkForbidden();
  },

  // 初始化定位
  initLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          userLocation: { lat: res.latitude, lng: res.longitude },
          locationEnabled: true,
        });
        app.globalData.location = {
          latitude: res.latitude,
          longitude: res.longitude,
        };
        this.loadWeather(res.latitude, res.longitude);
        this.checkForbiddenZone(res.latitude, res.longitude);
      },
      fail: () => {
        this.setData({ locationEnabled: false });
        this.loadWeather(constants.MAP.DEFAULT_LAT, constants.MAP.DEFAULT_LNG);
      },
    });
  },

  // 加载天气
  async loadWeather(lat, lng) {
    this.setData({ weatherLoading: true });
    try {
      const weather = await getCurrentWeather(lat, lng);
      this.setData({ weather, weatherLoading: false });
    } catch {
      this.setData({ weatherLoading: false });
    }
  },

  // 加载所有标点
  async loadSpots() {
    try {
      const res = await getSpots();
      const spots = (res.items || res || []).map(spot => {
        // 计算距离
        const userLoc = this.data.userLocation;
        if (userLoc) {
          spot.distance = formatDistance(
            distance(userLoc.lat, userLoc.lng, spot.latitude, spot.longitude)
          );
        }
        // 地形标签映射
        const terrainItem = constants.TERRAIN_TYPES.find(t => t.value === spot.terrain);
        spot.terrainLabel = terrainItem ? terrainItem.label : spot.terrain;
        return spot;
      });
      this.setData({ satellites: spots });
    } catch (err) {
      console.error('加载标点失败', err);
    }
  },

  // 加载禁钓区
  async loadForbiddenZones() {
    try {
      const zones = await getForbiddenZones();
      // 转为地图组件需要的 polygons 格式
      const polygons = (zones || []).map(zone => ({
        id: zone.id,
        name: zone.name,
        description: zone.description,
        points: zone.coordinates.map(coord => ({
          longitude: coord[0],
          latitude: coord[1],
        })),
        strokeColor: '#ef4444',
        strokeWidth: 2,
        fillColor: 'rgba(239,68,68,0.2)',
      }));
      this.setData({ polygons, showForbidden: true });
    } catch (err) {
      console.error('加载禁钓区失败', err);
    }
  },

  // 检查当前坐标是否在禁钓区
  checkForbiddenZone(lat, lng) {
    const { polygons } = this.data;
    if (!polygons || polygons.length === 0) return;

    const zones = polygons.map(p => ({
      id: p.id,
      name: p.name,
      description: p.description,
      coordinates: p.points.map(pt => [pt.longitude, pt.latitude]),
    }));

    const hit = isInForbiddenZone({ latitude: lat, longitude: lng }, zones);
    if (hit) {
      this.setData({ forbiddenZone: hit, showForbiddenModal: true });
    }
  },

  // 地图类型切换
  switchMapType() {
    this.setData({
      mapType: this.data.mapType === 'map' ? 'satellite' : 'map',
    });
  },

  // 定位到我的位置
  relocate() {
    if (!this.data.locationEnabled) {
      wx.showToast({ title: '定位未开启', icon: 'none' });
      return;
    }
    const { latitude, longitude } = this.data;
    this.setData({ latitude, longitude, scale: constants.MAP.DEFAULT_SCALE });
    this.mapCtx && this.mapCtx.moveToLocation && this.mapCtx.moveToLocation();
  },

  // 点击地图标点
  onMarkerTap(e) {
    const { markerId } = e.detail;
    const spot = this.data.satellites.find(s => s.id === markerId);
    if (spot) {
      this.setData({ selectedSpot: spot, showSpotPanel: true });
    }
  },

  // 点击地图空白处
  onMapTap() {
    this.setData({ showSpotPanel: false, selectedSpot: null });
  },

  // 进入标点详情
  goToDetail() {
    const { selectedSpot } = this.data;
    if (!selectedSpot) return;
    wx.navigateTo({
      url: `/pages/spot-detail/spot-detail?id=${selectedSpot.id}`,
    });
  },

  // 新建标点
  goToCreate() {
    const { latitude, longitude } = this.data;
    wx.navigateTo({
      url: `/pages/spot-edit/spot-edit?lat=${latitude}&lng=${longitude}`,
    });
  },

  // 去天气详情
  goToWeather() {
    const { latitude, longitude } = this.data;
    wx.navigateTo({
      url: `/pages/weather/weather?lat=${latitude}&lng=${longitude}`,
    });
  },

  // 禁钓区弹窗关闭
  onForbiddenClose() {
    this.setData({ showForbiddenModal: false });
  },

  // 微信分享
  onShareAppMessage() {
    const { selectedSpot } = this.data;
    if (selectedSpot) {
      return {
        title: `钓了吗 - ${selectedSpot.name}`,
        path: `/pages/spot-detail/spot-detail?id=${selectedSpot.id}`,
        imageUrl: '/assets/images/share-cover.png',
      };
    }
    return {
      title: '钓了吗 - 钓鱼地点管理',
      path: '/pages/index/index',
      imageUrl: '/assets/images/share-cover.png',
    };
  },
});
