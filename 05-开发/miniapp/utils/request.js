/**
 * wx.request Promise 封装
 * 自动拆包：code===0 时 resolve(data)，否则 reject(res)
 */
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
          const body = res.data;
          // 如果是 {code, data, msg} 包装格式，自动拆包
          if (body && body.code === 0) {
            resolve(body.data);
          } else if (body && body.code !== undefined) {
            // 有 code 但非 0，当作错误处理
            reject(body);
          } else {
            // 非包装格式，直接返回
            resolve(body);
          }
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
