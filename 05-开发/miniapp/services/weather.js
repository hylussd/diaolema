/**
 * 天气服务
 */
const { request } = require('../utils/request');

/**
 * 获取当前位置天气（服务端中转和风API）
 * @param {number} lat
 * @param {number} lng
 */
function getCurrentWeather(lat, lng) {
  return request({
    url: '/v1/weather',
    method: 'GET',
    data: { latitude: lat, longitude: lng },
  });
}

/**
 * 获取7天天气预报
 */
function getForecast(lat, lng) {
  return request({
    url: '/v1/weather',
    method: 'GET',
    data: { latitude: lat, longitude: lng },
  });
}

module.exports = { getCurrentWeather, getForecast };
