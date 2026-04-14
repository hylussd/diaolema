// pages/checkin/checkin.js
const { createCheckin } = require('../../services/checkin');
const { getCurrentWeather } = require('../../services/weather');
const constants = require('../../utils/constants');

Page({
  data: {
    spotId: null,
    spotName: '',
    latitude: constants.MAP.DEFAULT_LAT,
    longitude: constants.MAP.DEFAULT_LNG,
    selectedFish: [],
    fishSpecies: constants.FISH_SPECIES,
    weightKg: '',
    notes: '',
    weather: null,
    weatherLoading: true,
    submitting: false,
    // P2 新增
    fishingMethod: '',
    fishingMethods: constants.FISHING_METHODS,
    isPublic: false,
  },

  onLoad(query) {
    const lat = query.lat ? parseFloat(query.lat) : constants.MAP.DEFAULT_LAT;
    const lng = query.lng ? parseFloat(query.lng) : constants.MAP.DEFAULT_LNG;
    this.setData({
      spotId: parseInt(query.spot_id),
      spotName: query.spot_name || '',
      latitude: lat,
      longitude: lng,
    });
    this.loadWeather();
  },

  async loadWeather() {
    const lat = parseFloat(this.data.lat || constants.MAP.DEFAULT_LAT);
    const lng = parseFloat(this.data.lng || constants.MAP.DEFAULT_LNG);
    try {
      const weather = await getCurrentWeather(lat, lng);
      this.setData({ weather, weatherLoading: false });
    } catch {
      this.setData({ weatherLoading: false });
    }
  },

  // 鱼种切换
  onFishToggle(e) {
    const fish = e.currentTarget.dataset.fish;
    const { selectedFish } = this.data;
    const idx = selectedFish.indexOf(fish);
    if (idx === -1) {
      selectedFish.push(fish);
    } else {
      selectedFish.splice(idx, 1);
    }
    this.setData({ selectedFish });
  },

  // 重量输入
  onWeightInput(e) {
    this.setData({ weightKg: e.detail.value });
  },

  // 备注输入
  onNotesInput(e) {
    this.setData({ notes: e.detail.value });
  },

  // P2: 钓法选择
  onFishingMethodSelect(e) {
    const method = e.currentTarget.dataset.method;
    this.setData({ fishingMethod: method });
  },

  // P2: 公开开关
  onPublicSwitch(e) {
    this.setData({ isPublic: e.detail.value });
  },

  // 提交打卡
  async onSubmit() {
    const { spotId, selectedFish, weightKg, notes, weather, submitting, fishingMethod, isPublic } = this.data;
    if (submitting) return;

    if (selectedFish.length === 0) {
      wx.showToast({ title: '请选择鱼种', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });
    try {
      const body = {
        spot_id: spotId,
        fish_caught: selectedFish,
        weight_kg: weightKg ? parseFloat(weightKg) : undefined,
        notes: notes || undefined,
        fishing_method: fishingMethod || undefined,
        is_public: isPublic,
      };
      if (weather) {
        body.weather_text = weather.condition;
        body.temp = weather.temp;
        body.pressure = weather.pressure;
      }
      const res = await createCheckin(body);
      wx.showToast({ title: '打卡成功', icon: 'success' });
      // 打卡成功后可跳水文上报
      setTimeout(function() {
        wx.navigateBack();
      }, 1500);
    } catch (e) {
      wx.showToast({ title: '打卡失败', icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
