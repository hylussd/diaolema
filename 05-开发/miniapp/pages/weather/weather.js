// pages/weather/weather.js
const { getCurrentWeather, getForecast } = require('../../services/weather');
const { weekday } = require('../../utils/format');

Page({
  data: {
    lat: '',
    lng: '',
    current: null,
    forecast: [],
    loading: true,
  },

  onLoad(query) {
    const lat = query.lat || '';
    const lng = query.lng || '';
    this.setData({ lat, lng });
    this.loadWeather(lat, lng);
  },

  async loadWeather(lat, lng) {
    this.setData({ loading: true });
    try {
      const [cur, fc] = await Promise.all([
        getCurrentWeather(lat, lng),
        getForecast(lat, lng),
      ]);
      // 处理7天预报
      const forecast = (fc.daily || []).map(day => ({
        date: weekday(day.date),
        dateShort: day.date ? day.date.slice(5) : '',
        icon: day.icon || day.textDay,
        textDay: day.textDay || day.icon,
        tempMin: day.tempMin || day.minTemp,
        tempMax: day.tempMax || day.maxTemp,
        windDir: day.windDirDay || day.windDir,
        windScale: day.windScaleDay || day.windScale,
        precip: day.precip || day.precipProb,
        humidity: day.humidity,
        pressure: day.pressure,
        uvIndex: day.uvIndex,
      }));
      this.setData({
        current: cur,
        forecast,
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },
});
