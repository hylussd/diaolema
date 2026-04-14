/**
 * wx.request Promise 封装
 */
const constants = require('./constants');

function request(options) {
  return new Promise((resolve, reject) => {
    const app = getApp();
    wx.request({
      url: `${app.globalData.API_BASE}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'X-Openid': app.globalData.openid || '',
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录', icon: 'none' });
          reject(res);
        } else if (res.statusCode === 403) {
          wx.showToast({ title: '无权限', icon: 'none' });
          reject(res);
        } else {
          reject(res);
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络请求失败', icon: 'none' });
        reject(err);
      },
    });
  });
}

module.exports = { request };
