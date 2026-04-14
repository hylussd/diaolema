// pages/crowd-report/crowd-report.js
const { createCrowdReport } = require('../../services/crowd-report');
const { getCheckins } = require('../../services/checkin');
const constants = require('../../utils/constants');

Page({
  data: {
    spotId: null,
    spotName: '',
    checkinId: null,
    recentCheckin: null,
    waterTemp: '',
    dissolvedOxygen: '',
    selectedFish: '',
    fishSpecies: constants.FISH_SPECIES,
    submitting: false,
    loaded: false,
  },

  onLoad(query) {
    const spotId = parseInt(query.spot_id);
    const spotName = query.spot_name || '';
    this.setData({ spotId, spotName });
    this.loadRecentCheckin(spotId);
  },

  async loadRecentCheckin(spotId) {
    try {
      const res = await getCheckins({ spot_id: spotId, offset: 0, limit: 5 });
      const items = res.items || [];
      if (items.length > 0) {
        this.setData({ recentCheckin: items[0], checkinId: items[0].id });
      } else {
        wx.showModal({
          title: '提示',
          content: '您尚未在此标点打卡，无法上报水文数据',
          showCancel: false,
          success: function() {
            wx.navigateBack();
          },
        });
        return;
      }
      this.setData({ loaded: true });
    } catch {
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 水温输入
  onWaterTempInput(e) {
    this.setData({ waterTemp: e.detail.value });
  },

  // 溶氧量输入
  onDoInput(e) {
    this.setData({ dissolvedOxygen: e.detail.value });
  },

  // 鱼种选择
  onFishChange(e) {
    const val = e.detail.value;
    this.setData({ selectedFish: val });
  },

  // 提交
  async onSubmit() {
    const { spotId, checkinId, waterTemp, dissolvedOxygen, selectedFish, submitting } = this.data;
    if (submitting) return;

    if (!waterTemp) {
      wx.showToast({ title: '请输入水温', icon: 'none' });
      return;
    }
    if (!dissolvedOxygen) {
      wx.showToast({ title: '请输入溶氧量', icon: 'none' });
      return;
    }
    if (!selectedFish) {
      wx.showToast({ title: '请选择鱼种', icon: 'none' });
      return;
    }

    const wt = parseFloat(waterTemp);
    const doVal = parseFloat(dissolvedOxygen);
    if (wt < -5 || wt > 40) {
      wx.showToast({ title: '水温需在-5~40°C之间', icon: 'none' });
      return;
    }
    if (doVal < 0 || doVal > 20) {
      wx.showToast({ title: '溶氧量需在0~20mg/L之间', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });
    try {
      await createCrowdReport({
        spot_id: spotId,
        checkin_id: checkinId,
        water_temp: wt,
        dissolved_oxygen: doVal,
        fish_species: selectedFish,
      });
      wx.showToast({ title: '上报成功', icon: 'success' });
      setTimeout(function() {
        wx.navigateBack();
      }, 1500);
    } catch (e) {
      const msg = (e && e.msg) || '上报失败，请稍后重试';
      wx.showToast({ title: msg, icon: 'none', duration: 3000 });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
