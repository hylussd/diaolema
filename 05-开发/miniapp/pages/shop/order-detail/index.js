// pages/shop/order-detail/index.js
const { getOrderDetail, mockPayOrder, cancelOrder } = require('../../../services/shop');

Page({
  data: {
    order: null,
    loading: true,
    actionLoading: false,
  },

  onLoad(query) {
    const orderId = parseInt(query.order_id);
    this.setData({ orderId });
    this.loadDetail(orderId);
  },

  async loadDetail(orderId) {
    this.setData({ loading: true });
    try {
      const res = await getOrderDetail(orderId);
      this.setData({ order: res.data || {}, loading: false });
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 获取状态说明文字
  getStatusText(status) {
    const map = {
      pending: '等待您完成支付',
      paid: '支付成功，商家正在准备中',
      shipped: '商品已发货，请注意查收',
      delivered: '交易已完成，感谢购买',
      cancelled: '订单已取消',
    };
    return map[status] || '';
  },

  getStatusLabel(status) {
    const map = { pending: '待支付', paid: '已支付', shipped: '已发货', delivered: '已完成', cancelled: '已取消' };
    return map[status] || status;
  },

  getStatusClass(status) {
    const map = { pending: 'warning', paid: 'info', shipped: 'info', delivered: 'success', cancelled: 'muted' };
    return map[status] || '';
  },

  getPayStatusLabel(payStatus) {
    const map = { unpaid: '未支付', paid: '已支付', refunded: '已退款' };
    return map[payStatus] || payStatus;
  },

  // 去支付（mock）
  async onPay() {
    if (this.data.actionLoading) return;
    this.setData({ actionLoading: true });
    try {
      await mockPayOrder(this.data.orderId);
      wx.showToast({ title: '支付成功', icon: 'success' });
      this.loadDetail(this.data.orderId);
    } catch (e) {
      const msg = (e.data && e.data.msg) || '支付失败';
      wx.showToast({ title: msg, icon: 'none' });
    } finally {
      this.setData({ actionLoading: false });
    }
  },

  // 取消订单
  onCancel() {
    wx.showModal({
      title: '确认取消',
      content: '确定要取消该订单吗？',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (!res.confirm) return;
        this.setData({ actionLoading: true });
        try {
          await cancelOrder(this.data.orderId);
          wx.showToast({ title: '订单已取消', icon: 'success' });
          this.loadDetail(this.data.orderId);
        } catch (e) {
          const msg = (e.data && e.data.msg) || '取消失败';
          wx.showToast({ title: msg, icon: 'none' });
        } finally {
          this.setData({ actionLoading: false });
        }
      },
    });
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },

  formatTime(time) {
    if (!time) return '';
    return time.replace('T', ' ').substring(0, 16);
  },
});
