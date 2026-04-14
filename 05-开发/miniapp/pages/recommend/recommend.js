// pages/recommend/recommend.js
const { aiRecommend } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const constants = require('../../utils/constants');
const { formatDistance, distance } = require('../../utils/distance');

Page({
  data: {
    // 定位
    hasLocation: false,
    latitude: constants.MAP.DEFAULT_LAT,
    longitude: constants.MAP.DEFAULT_LNG,
    // 筛选条件
    selectedFish: '',
    fishSpecies: constants.FISH_SPECIES.slice(0, 10),   // 常用鱼种
    date: '',   // YYYY-MM-DD 默认今天
    timeSlots: [
      { value: 'morning', label: '清晨', range: '5:00-9:00' },
      { value: 'afternoon', label: '中午', range: '11:00-14:00' },
      { value: 'evening', label: '傍晚', range: '16:00-19:00' },
    ],
    selectedSlot: 'morning',
    selectedSlotIndex: 0,
    // 结果
    loading: false,
    result: null,
    generalAdvice: '',
    spots: [],
    // 地图标注
    mapHeight: 0,
  },

  onLoad() {
    const now = new Date();
    const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    this.setData({ date });
    this.initLocation();
    this.updateMapHeight();
  },

  updateMapHeight() {
    const sys = wx.getSystemInfoSync();
    this.setData({ mapHeight: sys.windowHeight * 0.45 });
  },

  // 获取定位
  initLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
          hasLocation: true,
        });
      },
      fail: () => {
        this.setData({ hasLocation: false });
      },
    });
  },

  relocate() {
    this.initLocation();
  },

  // 选择鱼种
  onFishSelect(e) {
    const fish = e.currentTarget.dataset.fish;
    this.setData({ selectedFish: fish });
  },

  // 选择日期
  onDateChange(e) {
    this.setData({ date: e.detail.value });
  },

  // 选择时段
  onSlotChange(e) {
    const idx = parseInt(e.detail.value);
    const slots = this.data.timeSlots;
    this.setData({
      selectedSlotIndex: idx,
      selectedSlot: slots[idx].value,
    });
  },

  // 执行AI推荐
  async onRecommend() {
    const { selectedFish, date, selectedSlot, latitude, longitude, loading } = this.data;
    if (!selectedFish) {
      wx.showToast({ title: '请选择目标鱼种', icon: 'none' });
      return;
    }
    if (loading) return;

    this.setData({ loading: true, result: null });
    try {
      const weather = await getCurrentWeather(latitude, longitude);
      const body = {
        target_fish: selectedFish,
        date,
        time_slot: selectedSlot,
        lat: latitude,
        lng: longitude,
        radius_km: 10,
      };
      const res = await aiRecommend(body);
      const spots = (res.spots || []).map(s => {
        if (this.data.hasLocation) {
          s.distance = formatDistance(
            distance(latitude, longitude, s.latitude, s.longitude)
          );
        }
        return s;
      });
      this.setData({
        result: res,
        generalAdvice: res.general_advice || '',
        spots,
        weather,
      });
    } catch (err) {
      console.error('AI推荐失败', err);
      wx.showToast({ title: '推荐失败，请重试', icon: 'none' });
    } finally {
      this.setData({ loading: false });
    }
  },

  // 前往标点详情
  goToDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/spot-detail/spot-detail?id=${id}` });
  },

  // 地图导航
  goToMap(e) {
    const spot = e.currentTarget.dataset.spot;
    wx.openLocation({
      latitude: spot.latitude,
      longitude: spot.longitude,
      name: spot.name,
      scale: 16,
    });
  },
});
