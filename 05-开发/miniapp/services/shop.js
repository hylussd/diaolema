/**
 * 商城服务 API（v1/shop/*）
 * 所有接口默认携带 user_id（当前模拟为 1）
 */
const { request } = require('../utils/request');

const USER_ID = 1; // 模拟用户 ID，后续接真实登录后替换

function getShopCategories() {
  return request({
    url: '/v1/shop/categories',
    method: 'GET',
    data: {},
  });
}

function getShopProducts(params = {}) {
  return request({
    url: '/v1/shop/products',
    method: 'GET',
    data: { user_id: USER_ID, ...params },
  });
}

function getShopProductDetail(id) {
  return request({
    url: `/v1/shop/products/${id}`,
    method: 'GET',
    data: { user_id: USER_ID },
  });
}

function getCart() {
  return request({
    url: '/v1/shop/cart',
    method: 'GET',
    data: { user_id: USER_ID },
  });
}

function addToCart(data) {
  return request({
    url: '/v1/shop/cart',
    method: 'POST',
    data: { user_id: USER_ID, ...data },
  });
}

function updateCartItem(itemId, data) {
  return request({
    url: `/v1/shop/cart/${itemId}`,
    method: 'PUT',
    data: { user_id: USER_ID, ...data },
  });
}

function deleteCartItem(itemId) {
  return request({
    url: `/v1/shop/cart/${itemId}`,
    method: 'DELETE',
    data: { user_id: USER_ID },
  });
}

function clearCart() {
  return request({
    url: '/v1/shop/cart',
    method: 'DELETE',
    data: { user_id: USER_ID },
  });
}

function createOrder(data) {
  return request({
    url: '/v1/shop/orders',
    method: 'POST',
    data: { user_id: USER_ID, ...data },
  });
}

function getOrders(params = {}) {
  return request({
    url: '/v1/shop/orders',
    method: 'GET',
    data: { user_id: USER_ID, ...params },
  });
}

function getOrderDetail(orderId) {
  return request({
    url: `/v1/shop/orders/${orderId}`,
    method: 'GET',
    data: { user_id: USER_ID },
  });
}

function mockPayOrder(orderId) {
  return request({
    url: `/v1/shop/orders/${orderId}/pay`,
    method: 'POST',
    data: { user_id: USER_ID, pay_status: 'paid' },
  });
}

function cancelOrder(orderId) {
  return request({
    url: `/v1/shop/orders/${orderId}/cancel`,
    method: 'POST',
    data: { user_id: USER_ID },
  });
}

module.exports = {
  getShopCategories,
  getShopProducts,
  getShopProductDetail,
  getCart,
  addToCart,
  updateCartItem,
  deleteCartItem,
  clearCart,
  createOrder,
  getOrders,
  getOrderDetail,
  mockPayOrder,
  cancelOrder,
};
