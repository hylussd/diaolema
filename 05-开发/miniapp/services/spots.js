/**
 * 标点服务 - CRUD + 筛选 + AI推荐
 */
const { request } = require('../utils/request');

// ---------- 基础 CRUD ----------

function getSpots(params) {
  return request({ url: '/v1/spots', method: 'GET', data: params });
}

function getSpot(id) {
  return request({ url: `/v1/spots/${id}` });
}

function createSpot(data) {
  return request({ url: '/v1/spots', method: 'POST', data });
}

function updateSpot(id, data) {
  return request({ url: `/v1/spots/${id}`, method: 'PUT', data });
}

function deleteSpot(id) {
  return request({ url: `/v1/spots/${id}`, method: 'DELETE' });
}

// ---------- P1: 多参数筛选 ----------

/**
 * 多条件筛选钓点
 * @param {object} params - { lat, lng, radius_km, pressure_min, pressure_max,
 *                            temp_min, temp_max, fish_species, category_type, offset, limit }
 */
function filterSpots(params) {
  return request({ url: '/v1/spots/public/filter', method: 'GET', data: params });
}

// ---------- P1: AI推荐 ----------

/**
 * AI推荐钓点
 * @param {object} body - { target_fish, date, time_slot, lat, lng, radius_km }
 */
function aiRecommend(body) {
  return request({ url: '/v1/spots/ai-recommend', method: 'POST', data: body });
}

module.exports = {
  getSpots,
  getSpot,
  createSpot,
  updateSpot,
  deleteSpot,
  filterSpots,
  aiRecommend,
};
