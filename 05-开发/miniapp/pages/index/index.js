// pages/index/index.js
// 地图首页 - P1改造：增加筛选入口
const app = getApp();
const constants = require('../../utils/constants');
const { getSpots, filterSpots } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const { getForbiddenZones } = require('../../services/forbidden');
const { isInForbiddenZone } = require('../../utils/polygon');
const { distance, formatDistance } = require('../../utils/distance');

Page({
  data: {
    latitude: constants.MAP.DEFAULT_LAT,
    longitude: constants.MAP.DEFAULT_LNG,
    scale: constants.MAP.DEFAULT_SCALE,
    mapType: 'map',
    satellites: [],
    polygons: [],
    showForbidden: false,
    forbiddenZone: null,
    weather: null,
    weatherLoading: true,
    userLocation: null,
    showSpotPanel: false,
    selectedSpot: null,
    locationEnabled: false,
    // P1: 筛选相关
    showFilter: false,           // 筛选面板显示
    filteredSpots: null,          // 筛选结果
    filterActive: false,          // 是否有筛选条件
    filterParams: {},            // 当前筛选参数
    // P1: 推荐页入口
    showRecommendBtn: false,
  },

  onLoad() {
    this.initLocation();
    this.loadForbiddenZones();
  },

  onShow() {
    this.loadSpots();
    this.checkForbidden();
  },

  // ---------- 定位 ----------
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

  // ---------- 天气 ----------
  async loadWeather(lat, lng) {
    this.setData({ weatherLoading: true });
    try {
      const weather = await getCurrentWeather(lat, lng);
      this.setData({ weather, weatherLoading: false });
    } catch {
      this.setData({ weatherLoading: false });
    }
  },

  // ---------- 标点加载 ----------
  async loadSpots(params) {
    try {
      const queryParams = params || {};
      const res = await filterSpots(queryParams);
      const spots = ((res.items || []) || []).map(spot => {
        const userLoc = this.data.userLocation;
        if (userLoc) {
          spot.distance = formatDistance(
            distance(userLoc.lat, userLoc.lng, spot.latitude, spot.longitude)
          );
        }
        const terrainItem = constants.TERRAIN_TYPES.find(t => t.value === spot.terrain);
        spot.terrainLabel = terrainItem ? terrainItem.label : spot.terrain;
        return spot;
      });
      this.setData({ satellites: spots });
    } catch (err) {
      console.error('加载标点失败', err);
    }
  },

  // ---------- 禁钓区 ----------
  async loadForbiddenZones() {
    try {
      const zones = await getForbiddenZones();
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

  // ---------- P1: 筛选 ----------
  openFilter() {
    this.setData({ showFilter: true });
  },

  closeFilter() {
    this.setData({ showFilter: false });
  },

  onFilterConfirm(e) {
    const params = e.detail;
    const { userLocation } = this.data;
    const queryParams = {
      ...params,
      lat: userLocation ? userLocation.lat : constants.MAP.DEFAULT_LAT,
      lng: userLocation ? userLocation.lng : constants.MAP.DEFAULT_LNG,
      radius_km: 50,
    };
    this.setData({ showFilter: false, filterActive: true, filterParams: queryParams });
    wx.showLoading({ title: '筛选中...' });
    filterSpots(queryParams).then(res => {
      wx.hideLoading();
      const spots = ((res.items || []) || []).map(spot => {
        if (userLocation) {
          spot.distance = formatDistance(
            distance(userLocation.lat, userLocation.lng, spot.latitude, spot.longitude)
          );
        }
        return spot;
      });
      this.setData({ satellites: spots, filteredSpots: spots });
      wx.showToast({ title: `找到${spots.length}个钓点`, icon: 'none' });
    }).catch(() => {
      wx.hideLoading();
      wx.showToast({ title: '筛选失败', icon: 'none' });
    });
  },

  clearFilter() {
    this.setData({ filterActive: false, filterParams: {}, filteredSpots: null });
    this.loadSpots();
  },

  // ---------- 地图操作 ----------
  switchMapType() {
    this.setData({ mapType: this.data.mapType === 'map' ? 'satellite' : 'map' });
  },

  relocate() {
    if (!this.data.locationEnabled) {
      wx.showToast({ title: '定位未开启', icon: 'none' });
      return;
    }
    const { latitude, longitude } = this.data;
    this.setData({ latitude, longitude, scale: constants.MAP.DEFAULT_SCALE });
    this.mapCtx && this.mapCtx.moveToLocation && this.mapCtx.moveToLocation();
  },

  onMarkerTap(e) {
    const { markerId } = e.detail;
    const spot = this.data.satellites.find(s => s.id === markerId);
    if (spot) {
      this.setData({ selectedSpot: spot, showSpotPanel: true });
    }
  },

  onMapTap() {
    this.setData({ showSpotPanel: false, selectedSpot: null });
  },

  // ---------- 导航 ----------
  goToDetail() {
    const { selectedSpot } = this.data;
    if (!selectedSpot) return;
    wx.navigateTo({
      url: `/pages/spot-detail/spot-detail?id=${selectedSpot.id}`,
    });
  },

  goToCreate() {
    const { latitude, longitude } = this.data;
    wx.navigateTo({
      url: `/pages/spot-edit/spot-edit?lat=${latitude}&lng=${longitude}`,
    });
  },

  goToWeather() {
    const { latitude, longitude } = this.data;
    wx.navigateTo({
      url: `/pages/weather/weather?lat=${latitude}&lng=${longitude}`,
    });
  },

  // ---------- P1: AI推荐入口 ----------
  goToRecommend() {
    wx.navigateTo({ url: '/pages/recommend/recommend' });
  },

  // ---------- 禁钓区 ----------
  onForbiddenClose() {
    this.setData({ showForbiddenModal: false });
  },

  // ---------- 分享 ----------
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
