// pages/spot-detail/spot-detail.js
// P1+P2改造：天气关联、AI推荐理由、历史打卡、分享Token、打卡入口、评分/点赞、水文数据
const { getSpot, deleteSpot } = require('../../services/spots');
const { getCurrentWeather } = require('../../services/weather');
const { generateQrcode, createToken } = require('../../services/share');
const { getCheckins, deleteCheckin } = require('../../services/checkin');
const { getSpotRatingSummary, upsertSpotRating } = require('../../services/spot-rating');
const { getCrowdReports } = require('../../services/crowd-report');
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
    // P1
    aiRecommendResult: null,
    aiRecommendLoading: false,
    checkins: [],
    checkinsLoading: false,
    checkinsTotal: 0,
    showShareTokenModal: false,
    shareTokenUrl: '',
    shareTokenExpires: '',
    // P2
    ratingSummary: null,
    ratingLoading: false,
    showRatingModal: false,
    tempRating: 0,
    crowdReports: [],
    crowdReportsLoading: false,
    userId: 1,
  },

  onLoad(query) {
    this.loadSpot(query.id);
  },

  async loadSpot(id) {
    try {
      const spot = await getSpot(id);
      const terrainItem = constants.TERRAIN_TYPES.find(function(t) { return t.value === spot.terrain; });
      spot.terrainLabel = terrainItem ? terrainItem.label : spot.terrain;
      spot.createdAt = formatDate(spot.created_at || spot.createdAt);
      this.setData({ spot, loading: false });
      this.loadWeather(spot.latitude, spot.longitude);
      this.loadAiRecommend(spot);
      this.loadCheckins(id);
      this.loadRatingSummary(id);
      this.loadCrowdReports(id);
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

  async loadAiRecommend(spot) {
    this.setData({ aiRecommendLoading: true });
    try {
      const now = new Date();
      const date = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
      const targetFish = (spot.fish_species && spot.fish_species[0]) || '鲫鱼';
      const body = {
        target_fish: targetFish,
        date: date,
        time_slot: this.getCurrentTimeSlot(),
        lat: spot.latitude,
        lng: spot.longitude,
        radius_km: 10,
      };
      const res = await wx.cloud ? Promise.resolve({ spots: [] }) : require('../../services/spots').aiRecommend(body);
      const spotRecommend = (res.spots || []).find(function(s) { return s.id === spot.id; });
      this.setData({ aiRecommendResult: spotRecommend || null, aiRecommendLoading: false });
    } catch {
      this.setData({ aiRecommendLoading: false });
    }
  },

  getCurrentTimeSlot() {
    const h = new Date().getHours();
    if (h < 9) return 'morning';
    if (h < 15) return 'afternoon';
    return 'evening';
  },

  async loadCheckins(spotId) {
    this.setData({ checkinsLoading: true });
    try {
      const res = await getCheckins({ spot_id: spotId, offset: 0, limit: 10 });
      const checkins = (res.items || []).map(function(c) {
        return Object.assign({}, c, {
          checkinDate: formatDate(c.checkin_time),
          fishCaughtText: Array.isArray(c.fish_caught) ? c.fish_caught.join('、') : c.fish_caught,
        });
      });
      this.setData({ checkins, checkinsTotal: res.total || 0, checkinsLoading: false });
    } catch {
      this.setData({ checkinsLoading: false });
    }
  },

  async loadRatingSummary(spotId) {
    this.setData({ ratingLoading: true });
    try {
      const { userId } = this.data;
      const res = await getSpotRatingSummary(spotId, userId);
      this.setData({ ratingSummary: res, ratingLoading: false });
    } catch {
      this.setData({ ratingLoading: false });
    }
  },

  async loadCrowdReports(spotId) {
    this.setData({ crowdReportsLoading: true });
    try {
      const res = await getCrowdReports({ spot_id: spotId, offset: 0, limit: 10 });
      this.setData({ crowdReports: res.items || [], crowdReportsLoading: false });
    } catch {
      this.setData({ crowdReportsLoading: false });
    }
  },

  // P2: 打开评分弹窗
  onOpenRatingModal() {
    const { ratingSummary } = this.data;
    this.setData({
      showRatingModal: true,
      tempRating: ratingSummary && ratingSummary.user_rating || 0,
    });
  },

  closeRatingModal() {
    this.setData({ showRatingModal: false });
  },

  // P2: 选择星级
  onSelectStar(e) {
    const rating = parseInt(e.currentTarget.dataset.rating);
    this.setData({ tempRating: rating });
  },

  // P2: 提交评分
  async onConfirmRating() {
    const { spot, tempRating } = this.data;
    if (!tempRating) {
      wx.showToast({ title: '请先选择星级', icon: 'none' });
      return;
    }
    try {
      await upsertSpotRating({ spot_id: spot.id, rating: tempRating });
      wx.showToast({ title: '评分成功', icon: 'success' });
      this.setData({ showRatingModal: false });
      this.loadRatingSummary(spot.id);
    } catch {
      wx.showToast({ title: '评分失败', icon: 'none' });
    }
  },

  // P2: 点赞/取消点赞
  async onToggleLike() {
    const { spot, ratingSummary } = this.data;
    const liked = !(ratingSummary && ratingSummary.user_liked);
    try {
      await upsertSpotRating({ spot_id: spot.id, liked: liked });
      this.loadRatingSummary(spot.id);
    } catch {
      wx.showToast({ title: '操作失败', icon: 'none' });
    }
  },

  onDeleteCheckin(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该打卡记录吗？',
      confirmColor: '#ef4444',
      success: async function(res) {
        if (!res.confirm) return;
        try {
          await deleteCheckin(id);
          wx.showToast({ title: '已删除' });
          const { spot } = this.data;
          if (spot) this.loadCheckins(spot.id);
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      }.bind(this),
    });
  },

  goToCheckin() {
    const { spot } = this.data;
    if (!spot) return;
    wx.navigateTo({
      url: '/pages/checkin/checkin?spot_id=' + spot.id + '&spot_name=' + encodeURIComponent(spot.name) + '&lat=' + spot.latitude + '&lng=' + spot.longitude,
    });
  },

  // P2: 跳水文上报
  goToCrowdReport() {
    const { spot } = this.data;
    if (!spot) return;
    wx.navigateTo({
      url: '/pages/crowd-report/crowd-report?spot_id=' + spot.id + '&spot_name=' + encodeURIComponent(spot.name),
    });
  },

  async onCreateShareToken() {
    const { spot } = this.data;
    if (!spot) return;
    wx.showLoading({ title: '生成中...' });
    try {
      const res = await createToken(spot.id, 7);
      const base = constants.API_BASE.replace('http://', 'https://');
      const shareUrl = base + '/pages/share-view/share-view?token=' + res.token;
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

  noop() {},

  onCopyShareUrl() {
    wx.setClipboardData({
      data: this.data.shareTokenUrl,
      success: function() { wx.showToast({ title: '已复制', icon: 'success' }); },
    });
  },

  goToEdit() {
    const { spot } = this.data;
    wx.navigateTo({ url: '/pages/spot-edit/spot-edit?id=' + spot.id });
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

  onShareAppMessage() {
    const { spot } = this.data;
    return {
      title: '钓了吗 - ' + spot.name,
      path: '/pages/spot-detail/spot-detail?id=' + spot.id,
      imageUrl: '/assets/images/share-cover.png',
    };
  },

  onShareTimeline() {
    const { spot } = this.data;
    return {
      title: '钓了吗 - ' + spot.name,
      query: 'id=' + spot.id,
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
      const res = await generateQrcode(spot.id, spot.name || '钓了吗');
      this.setData({ shareQrcode: res.qr_data_url });
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
      success: async function(res) {
        if (!res.confirm) return;
        try {
          await deleteSpot(this.data.spot.id);
          wx.showToast({ title: '已删除' });
          wx.navigateBack();
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      }.bind(this),
    });
  },
});
