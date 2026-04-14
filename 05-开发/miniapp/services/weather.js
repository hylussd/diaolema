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
    url: '/api/weather/current',
    method: 'GET',
    data: { lat, lng },
  });
}

/**
 * 获取7天天气预报
 */
function getForecast(lat, lng) {
  return request({
    url: '/api/weather/forecast',
    method: 'GET',
    data: { lat, lng },
  });
}

/**
 * 获取历史天气（用于分析）
 */
function getHistorical(lat, lng, days = 7) {
  return request({
    url: '/api/weather/historical',
    method: 'GET',
    data: { lat, lng, days },
  });
}

module.exports = { getCurrentWeather, getForecast, getHistorical };
