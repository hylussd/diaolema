// behaviors/location-auth.js
// 定位权限校验 Behavior
module.exports = Behavior({
  data: {
    locationAuth: false,
  },
  attached() {
    wx.getSetting({
      success: (res) => {
        this.setData({ locationAuth: !!res.authSetting['scope.userLocation'] });
      },
    });
  },
  methods: {
    checkLocation() {
      if (!this.data.locationAuth) {
        wx.showModal({
          title: '需要定位权限',
          content: '请在设置中开启定位权限',
          success: (res) => {
            if (res.confirm) wx.openSetting();
          },
        });
        return false;
      }
      return true;
    },
  },
});
