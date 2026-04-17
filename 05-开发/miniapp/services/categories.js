/**
 * 分类服务
 */
const { request } = require('../utils/request');

function getCategories() {
  return request({ url: '/v1/categories' });
}

function createCategory(data) {
  return request({ url: '/v1/categories', method: 'POST', data });
}

function updateCategory(id, data) {
  return request({ url: `/v1/categories/${id}`, method: 'PUT', data });
}

function deleteCategory(id) {
  return request({ url: `/v1/categories/${id}`, method: 'DELETE' });
}

function reorderCategories(orders) {
  return request({ url: '/v1/categories/reorder', method: 'PUT', data: { orders } });
}

module.exports = { getCategories, createCategory, updateCategory, deleteCategory, reorderCategories };
