/**
 * 水文上报服务
 */
const { request } = require('../utils/request');

/**
 * 创建水文上报
 * @param {object} body - { spot_id, checkin_id, water_temp, dissolved_oxygen, fish_species }
 */
function createCrowdReport(body) {
  return request({
    url: '/v1/crowd-reports',
    method: 'POST',
    data: body,
  });
}

/**
 * 查询标点的水文数据
 * @param {object} params - { spot_id, offset, limit, user_id }
 */
function getCrowdReports(params) {
  return request({
    url: '/v1/crowd-reports',
    method: 'GET',
    data: params,
  });
}

module.exports = {
  createCrowdReport,
  getCrowdReports,
};
