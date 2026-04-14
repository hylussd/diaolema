// pages/spot-detail/spot-detail.js
// P1改造：增加天气关联、AI推荐理由、历史打卡、分享Token、打卡入口
const { getSpot, deleteSpot, aiRecommend } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const { generateQrcode, createToken } = require('../../services/share');
const { getCheckins, deleteCheckin } = require('../../services/checkin');
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
    // P1 新增
    aiRecommendResult: null,      // AI推荐结果
    aiRecommendLoading: false,
    checkins: [],                 // 历史打卡记录
    checkinsLoading: false,
    checkinsTotal: 0,
    showShareTokenModal: false,  // 分享Token弹窗
    shareTokenUrl: '',
    shareTokenExpires: '',
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
      // 关联天气
      this.loadWeather(spot.latitude, spot.longitude);
      // P1: AI推荐理由
      this.loadAiRecommend(spot);
      // P1: 历史打卡
      this.loadCheckins(id);
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

  // P1: AI推荐理由
  async loadAiRecommend(spot) {
    this.setData({ aiRecommendLoading: true });
    try {
      const now = new Date();
      const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
      // 取第一个鱼种作为目标
      const targetFish = (spot.fish_species && spot.fish_species[0]) || '鲫鱼';
      const body = {
        target_fish: targetFish,
        date,
        time_slot: this.getCurrentTimeSlot(),
        lat: spot.latitude,
        lng: spot.longitude,
        radius_km: 10,
      };
      const res = await aiRecommend(body);
      // 找当前标点的推荐数据
      const spotRecommend = (res.spots || []).find(s => s.id === spot.id);
      this.setData({
        aiRecommendResult: spotRecommend || null,
        aiRecommendLoading: false,
      });
    } catch {
      this.setData({ aiRecommendLoading: false });
    }
  },

  // 判断当前时段
  getCurrentTimeSlot() {
    const h = new Date().getHours();
    if (h < 9) return 'morning';
    if (h < 15) return 'afternoon';
    return 'evening';
  },

  // P1: 历史打卡
  async loadCheckins(spotId) {
    this.setData({ checkinsLoading: true });
    try {
      const res = await getCheckins({ spot_id: spotId, offset: 0, limit: 10 });
      const checkins = ((res.items || []) || []).map(c => ({
        ...c,
        checkinDate: formatDate(c.checkin_time),
        fishCaughtText: Array.isArray(c.fish_caught) ? c.fish_caught.join('、') : c.fish_caught,
      }));
      this.setData({ checkins, checkinsTotal: res.total || 0, checkinsLoading: false });
    } catch {
      this.setData({ checkinsLoading: false });
    }
  },

  // P1: 删除打卡
  onDeleteCheckin(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该打卡记录吗？',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await deleteCheckin(id);
          wx.showToast({ title: '已删除' });
          // 刷新列表
          const { spot } = this.data;
          if (spot) this.loadCheckins(spot.id);
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      },
    });
  },

  // P1: 前往打卡页
  goToCheckin() {
    const { spot } = this.data;
    if (!spot) return;
    wx.navigateTo({
      url: `/pages/checkin/checkin?spot_id=${spot.id}&spot_name=${encodeURIComponent(spot.name)}&lat=${spot.latitude}&lng=${spot.longitude}`,
    });
  },

  // P1: 生成分享Token
  async onCreateShareToken() {
    const { spot } = this.data;
    if (!spot) return;
    wx.showLoading({ title: '生成中...' });
    try {
      const res = await createToken(spot.id, 7);
      const base = constants.API_BASE.replace('http://', 'https://');
      const shareUrl = `${base}/pages/share-view/share-view?token=${res.token}`;
      this.setData({
        shareTokenUrl: shareUrl,
        shareTokenExpires: res.expires_at,
        showShareTokenModal: true,
      });
      wx.hideLoading();
    } catch {
      wx.hideLoading();
      wx.showToast({ title: '生成失败', icon: 'none' });
    }
  },

  closeShareTokenModal() {
    this.setData({ showShareTokenModal: false });
  },

  // 空操作，阻止事件穿透
  noop() {},

  // P1: 复制分享链接
  onCopyShareUrl() {
    wx.setClipboardData({
      data: this.data.shareTokenUrl,
      success: () => wx.showToast({ title: '已复制', icon: 'success' }),
    });
  },

  goToEdit() {
    const { spot } = this.data;
    wx.navigateTo({ url: `/pages/spot-edit/spot-edit?id=${spot.id}` });
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
