/**
 * 标点评分/点赞服务
 */
const { request } = require('../utils/request');

/**
 * 评分或点赞（upsert）
 * @param {object} body - { spot_id, rating, liked }
 */
function upsertSpotRating(body) {
  return request({
    url: '/api/spot-ratings',
    method: 'POST',
    data: body,
  });
}

/**
 * 查询标点评分汇总
 * @param {number} spotId
 * @param {number} userId - 当前用户ID（可选）
 */
function getSpotRatingSummary(spotId, userId) {
  const params = { spot_id: spotId };
  if (userId) params.user_id = userId;
  return request({
    url: '/api/spot-ratings',
    method: 'GET',
    data: params,
  });
}

module.exports = {
  upsertSpotRating,
  getSpotRatingSummary,
};
