/**
 * 分享服务 - 生成小程序码/链接
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
    url: '/api/share/qrcode',
    method: 'POST',
    data: { path, scene },
  });
}

/**
 * 获取分享链接
 */
function getShareLink(path, query = {}) {
  return request({
    url: '/api/share/link',
    method: 'GET',
    data: { path, ...query },
  });
}

module.exports = { generateQrcode, getShareLink };
