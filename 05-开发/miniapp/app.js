/**
 * 钓了吗 - 应用入口
 */
App({
  globalData: {
    userInfo: null,
    openid: '',
    location: null,         // {latitude, longitude}
    currentSpot: null,      // 当前选中标点
    mapCtx: null,           // map 组件上下文
    // 服务端地址（后续可通过设置页修改）
    API_BASE: 'http://127.0.0.1:8000',
  },

  onLaunch() {
    // 检查登录态
    this.checkSession();
    // 获取 openid
    this.getOpenid();
  },

  onShow() {
    // 每次进入前台检查定位权限
    this.checkLocationAuth();
  },

  // 检查 session
  checkSession() {
    wx.checkSession({
      success: () => {
        // session 有效，尝试读取本地 openid
        const openid = wx.getStorageSync('openid');
        if (openid) {
          this.globalData.openid = openid;
        }
      },
      fail: () => {
        // session 失效，清除
        wx.removeStorageSync('openid');
        this.globalData.openid = '';
      }
    });
  },

  // 获取 openid
  getOpenid() {
    const openid = wx.getStorageSync('openid');
    if (openid) {
      this.globalData.openid = openid;
      return;
    }
    wx.login({
      success: (res) => {
        if (!res.code) return;
        wx.request({
          url: `${this.globalData.API_BASE}/api/auth/openid`,
          method: 'POST',
          data: { code: res.code },
          success: (r) => {
            if (r.data.openid) {
              this.globalData.openid = r.data.openid;
              wx.setStorageSync('openid', r.data.openid);
            }
          }
        });
      }
    });
  },

  // 检查定位权限
  checkLocationAuth() {
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.userLocation']) {
          wx.authorize({
            scope: 'scope.userLocation',
            fail: () => {
              wx.showToast({ title: '需要定位权限', icon: 'none' });
            }
          });
        }
      }
    });
  },

  // 获取当前位置
  getLocation() {
    return new Promise((resolve, reject) => {
      wx.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.globalData.location = {
            latitude: res.latitude,
            longitude: res.longitude
          };
          resolve(res);
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  },
});
