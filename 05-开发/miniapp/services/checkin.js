/**
 * 打卡记录服务 - CRUD
 */
const { request } = require('../utils/request');

/**
 * 新建打卡记录
 * @param {object} body - { spot_id, fish_caught, weight_kg, notes }
 */
function createCheckin(body) {
  return request({
    url: '/v1/checkins',
    method: 'POST',
    data: body,
  });
}

/**
 * 查询打卡记录
 * @param {object} params - { spot_id, offset, limit }
 */
function getCheckins(params) {
  return request({
    url: '/v1/checkins',
    method: 'GET',
    data: params,
  });
}

/**
 * 删除打卡记录
 * @param {number} id
 */
function deleteCheckin(id) {
  return request({
    url: `/v1/checkins/${id}`,
    method: 'DELETE',
  });
}

module.exports = {
  createCheckin,
  getCheckins,
  deleteCheckin,
};
