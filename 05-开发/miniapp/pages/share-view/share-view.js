// pages/share-view/share-view.js
const { getToken } = require('../../services/share');
const { getCurrentWeather } = require('../../services/weather');

Page({
  data: {
    token: '',
    loading: true,
    error: null,          // null | 'expired' | 'notfound'
    spot: null,
    weather: null,
    expiresAt: '',
    remainingDays: 0,
  },

  onLoad(query) {
    const token = query.token || '';
    if (!token) {
      this.setData({ loading: false, error: 'notfound' });
      return;
    }
    this.setData({ token });
    this.loadShareData(token);
  },

  async loadShareData(token) {
    this.setData({ loading: true, error: null });
    try {
      const res = await getToken(token);
      const spot = res.spot;
      const expiresAt = res.expires_at;
      // 计算剩余天数
      const remaining = Math.ceil((new Date(expiresAt) - new Date()) / 86400000);
      this.setData({
        spot,
        expiresAt,
        remainingDays: remaining,
        loading: false,
      });
      // 加载天气
      if (spot.latitude && spot.longitude) {
        this.loadWeather(spot.latitude, spot.longitude);
      }
    } catch (err) {
      const status = err.status || err.errno;
      if (status === 410 || (err.msg && err.msg.includes('过期'))) {
        this.setData({ loading: false, error: 'expired' });
      } else {
        this.setData({ loading: false, error: 'notfound' });
      }
    }
  },

  async loadWeather(lat, lng) {
    try {
      const weather = await getCurrentWeather(lat, lng);
      this.setData({ weather });
    } catch {}
  },

  // 打开地图导航
  goToMap() {
    const { spot } = this.data;
    if (!spot) return;
    wx.openLocation({
      latitude: spot.latitude,
      longitude: spot.longitude,
      name: spot.name,
      address: spot.description || '',
      scale: 16,
    });
  },

  // 复制坐标
  copyCoords() {
    const { spot } = this.data;
    if (!spot) return;
    const text = `${spot.latitude.toFixed(6)}, ${spot.longitude.toFixed(6)}`;
    wx.setClipboardData({
      data: text,
      success: () => wx.showToast({ title: '坐标已复制', icon: 'success' }),
    });
  },

  // 前往详情
  goToDetail() {
    const { spot } = this.data;
    if (!spot) return;
    wx.navigateTo({ url: `/pages/spot-detail/spot-detail?id=${spot.id}` });
  },
});
