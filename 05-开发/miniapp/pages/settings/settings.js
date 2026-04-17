// pages/settings/settings.js
const app = getApp();

Page({
  data: {
    apiBase: '',
    openid: '',
  },

  onLoad() {
    this.setData({
      apiBase: app.globalData.API_BASE,
      openid: app.globalData.openid || '未登录',
    });
  },

  onShow() {
    this.setData({ openid: app.globalData.openid || '未登录' });
  },

  // 修改服务端地址
  changeApiBase() {
    wx.showModal({
      title: '修改服务端地址',
      editable: true,
      placeholderText: 'http://127.0.0.1:8000',
      content: this.data.apiBase,
      success: (res) => {
        if (res.confirm && res.content) {
          const base = res.content.trim();
          app.globalData.API_BASE = base;
          wx.setStorageSync('api_base', base);
          this.setData({ apiBase: base });
          wx.showToast({ title: '已保存' });
        }
      },
    });
  },

  // 跳转商城
  goShop() {
    wx.navigateTo({ url: '/pages/shop/index/index' });
  },

  // 关于页面
  showAbout() {
    wx.showModal({
      title: '关于「钓了吗」',
      content: '版本：1.0.0 (P0 MVP)\n面向老钓手，简洁高效的钓鱼地点管理工具。\n\n数据存储在本地服务端，定位权限用于地图和禁钓区判断。',
      showCancel: false,
    });
  },

  // 隐私政策
  showPrivacy() {
    wx.showModal({
      title: '隐私说明',
      content: '本小程序获取您的位置信息仅用于：\n1. 在地图上显示您的位置\n2. 判断是否进入禁钓区\n3. 加载钓点天气数据\n\n您的位置数据不会上传至任何第三方服务器。',
      showCancel: false,
    });
  },

  // 清空本地缓存
  clearCache() {
    wx.showModal({
      title: '清空缓存',
      content: '确定清空本地缓存数据？',
      confirmColor: '#ef4444',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorageSync();
          wx.showToast({ title: '已清空' });
        }
      },
    });
  },
});
