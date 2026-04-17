/**
 * 分享服务 - 生成小程序码/链接 + Token管理
 */
const { request } = require('../utils/request');

/**
 * 生成分享小程序码
 * @param {string} path - 小程序页面路径
 * @param {object} query - 页面参数
 */
function generateQrcode(path, query = {}) {
  const scene = Object.entries(query)
    .map(([k, v]) => `${k}=${v}`)
    .join('&');
  return request({
    url: '/v1/share/qrcode',
    method: 'POST',
    data: { path, scene },
  });
}

/**
 * 获取分享链接
 */
function getShareLink(path, query = {}) {
  return request({
    url: '/v1/share/link',
    method: 'GET',
    data: { path, ...query },
  });
}

// ---------- P1: Token管理 ----------

/**
 * 生成分享Token（创建加密分享链接）
 * @param {number} spotId
 * @param {number} validDays - 有效期天数，默认7
 */
function createToken(spotId, validDays = 7) {
  return request({
    url: '/v1/share/tokens',
    method: 'POST',
    data: { spot_id: spotId, valid_days: validDays },
  });
}

/**
 * 通过Token获取标点信息
 * @param {string} token
 */
function getToken(token) {
  return request({
    url: `/v1/share/tokens/${token}`,
    method: 'GET',
  });
}

/**
 * 撤销分享Token
 * @param {string} token
 */
function revokeToken(token) {
  return request({
    url: `/v1/share/tokens/${token}`,
    method: 'DELETE',
  });
}

module.exports = {
  generateQrcode,
  getShareLink,
  createToken,
  getToken,
  revokeToken,
};
