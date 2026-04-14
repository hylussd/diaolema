/**
 * 禁钓区服务
 */
const { request } = require('../utils/request');

/**
 * 获取所有禁钓区（多边形数据）
 */
function getForbiddenZones() {
  return request({ url: '/api/forbidden-zones' });
}

/**
 * 检查某个坐标是否在禁钓区内
 */
function checkForbidden(lat, lng) {
  return request({ url: '/api/forbidden-zones/check', method: 'GET', data: { lat, lng } });
}

module.exports = { getForbiddenZones, checkForbidden };
