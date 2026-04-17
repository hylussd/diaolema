/**
 * 分享服务 - 生成小程序码/链接 + Token管理
 */
const { request } = require('../utils/request');

/**
 * 生成分享小程序码
 * @param {number} spotId - 标点ID
 * @param {string} title - 标题
 */
function generateQrcode(spotId, title = '钓了吗') {
  return request({
    url: '/v1/share/generate-qr',
    method: 'POST',
    data: { spot_id: spotId, title },
  });
}

/**
 * 获取分享链接
 * @param {number} spotId - 标点ID
 * @param {string} title - 标题
 */
function getShareLink(spotId, title = '钓了吗') {
  return request({
    url: `/v1/share/spots/${spotId}`,
    method: 'GET',
    data: { title },
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
