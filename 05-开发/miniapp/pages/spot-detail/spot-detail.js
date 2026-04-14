// pages/spot-detail/spot-detail.js
const { getSpot, deleteSpot } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const { generateQrcode } = require('../../services/share');
const constants = require('../../utils/constants');
const { formatDate } = require('../../utils/format');

Page({
  data: {
    spot: null,
    weather: null,
    weatherLoading: true,
    loading: true,
    showShareMenu: false,
    shareQrcode: null,
  },

  onLoad(query) {
    this.loadSpot(query.id);
  },

  async loadSpot(id) {
    try {
      const spot = await getSpot(id);
      const terrainItem = constants.TERRAIN_TYPES.find(t => t.value === spot.terrain);
      spot.terrainLabel = terrainItem ? terrainItem.label : spot.terrain;
      spot.createdAt = formatDate(spot.created_at || spot.createdAt);
      this.setData({ spot, loading: false });
      // 加载关联天气
      this.loadWeather(spot.latitude, spot.longitude);
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async loadWeather(lat, lng) {
    try {
      const weather = await getCurrentWeather(lat, lng);
      this.setData({ weather, weatherLoading: false });
    } catch {
      this.setData({ weatherLoading: false });
    }
  },

  goToEdit() {
    const { spot } = this.data;
    wx.navigateTo({
      url: `/pages/spot-edit/spot-edit?id=${spot.id}`,
    });
  },

  goToMap() {
    const { spot } = this.data;
    wx.openLocation({
      latitude: spot.latitude,
      longitude: spot.longitude,
      name: spot.name,
      address: spot.note || '',
      scale: 16,
    });
  },

  // 微信分享
  onShareAppMessage() {
    const { spot } = this.data;
    return {
      title: `钓了吗 - ${spot.name}`,
      path: `/pages/spot-detail/spot-detail?id=${spot.id}`,
      imageUrl: '/assets/images/share-cover.png',
    };
  },

  onShareTimeline() {
    const { spot } = this.data;
    return {
      title: `钓了吗 - ${spot.name}`,
      query: `id=${spot.id}`,
    };
  },

  // 显示分享菜单
  showShare() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline'],
    });
    this.setData({ showShareMenu: true });
  },

  async generatePoster() {
    wx.showLoading({ title: '生成中...' });
    try {
      const { spot } = this.data;
      const res = await generateQrcode('/pages/spot-detail/spot-detail', { id: spot.id });
      this.setData({ shareQrcode: res.image_url });
      wx.hideLoading();
    } catch {
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    }
  },

  // 删除标点
  deleteSpot() {
    wx.showModal({
      title: '确认删除',
      content: '删除后不可恢复，确定要删除该标点吗？',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await deleteSpot(this.data.spot.id);
          wx.showToast({ title: '已删除' });
          wx.navigateBack();
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      },
    });
  },
});
