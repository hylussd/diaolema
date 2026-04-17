/**
 * 天文数据服务 - 月相/日出日落
 */
const { request } = require('../utils/request');

/**
 * 获取指定位置和日期的天文数据（月相/日出日落）
 * @param {number} lat
 * @param {number} lng
 * @param {string} date - YYYY-MM-DD
 */
function getAstronomy(lat, lng, date) {
  return request({
    url: '/v1/astronomy',
    method: 'GET',
    data: { lat, lng, date },
  });
}

module.exports = {
  getAstronomy,
};
