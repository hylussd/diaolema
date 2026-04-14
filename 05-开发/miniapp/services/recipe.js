/**
 * 配方服务
 */
const { request } = require('../utils/request');

/**
 * 创建配方
 * @param {object} body - { name, pressure_min, pressure_max, water_temp_min, water_temp_max, fish_species, spot_type, is_public }
 */
function createRecipe(body) {
  return request({
    url: '/api/recipes',
    method: 'POST',
    data: body,
  });
}

/**
 * 我的所有配方
 * @param {object} params - { offset, limit }
 */
function getMyRecipes(params) {
  return request({
    url: '/api/recipes/me',
    method: 'GET',
    data: params,
  });
}

/**
 * 社区公开配方
 * @param {object} params - { fish_species, spot_type, offset, limit }
 */
function getPublicRecipes(params) {
  return request({
    url: '/api/recipes/public',
    method: 'GET',
    data: params,
  });
}

/**
 * 配方详情
 * @param {number} id
 */
function getRecipe(id) {
  return request({
    url: `/api/recipes/${id}`,
    method: 'GET',
  });
}

/**
 * 更新配方
 * @param {number} id
 * @param {object} body
 */
function updateRecipe(id, body) {
  return request({
    url: `/api/recipes/${id}`,
    method: 'PUT',
    data: body,
  });
}

/**
 * 删除配方
 * @param {number} id
 */
function deleteRecipe(id) {
  return request({
    url: `/api/recipes/${id}`,
    method: 'DELETE',
  });
}

module.exports = {
  createRecipe,
  getMyRecipes,
  getPublicRecipes,
  getRecipe,
  updateRecipe,
  deleteRecipe,
};
