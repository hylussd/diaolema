/**
 * API 基础服务封装
 */
const { request } = require('../utils/request');

function getSpots(params) {
  return request({ url: '/api/spots', method: 'GET', data: params });
}

function getSpot(id) {
  return request({ url: `/api/spots/${id}` });
}

function createSpot(data) {
  return request({ url: '/api/spots', method: 'POST', data });
}

function updateSpot(id, data) {
  return request({ url: `/api/spots/${id}`, method: 'PUT', data });
}

function deleteSpot(id) {
  return request({ url: `/api/spots/${id}`, method: 'DELETE' });
}

module.exports = { getSpots, getSpot, createSpot, updateSpot, deleteSpot };
