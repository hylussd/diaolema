// pages/shop/orders/index.js
const { getOrders } = require('../../../services/shop');

const TABS = [
  { label: '全部', value: '' },
  { label: '待支付', value: 'pending' },
  { label: '已支付', value: 'paid' },
  { label: '已发货', value: 'shipped' },
  { label: '已完成', value: 'delivered' },
];

Page({
  data: {
    tabs: TABS,
    currentTab: '',
    orders: [],
    loading: false,
    hasMore: true,
    offset: 0,
    limit: 20,
  },

  onLoad() {
    this.loadOrders(true);
  },

  onShow() {
    this.loadOrders(true);
  },

  async loadOrders(reset = false) {
    const { currentTab, offset, limit, loading, hasMore } = this.data;
    if (loading || (!reset && !hasMore)) return;

    this.setData({ loading: true });
    const params = { offset: reset ? 0 : offset, limit };
    if (currentTab) params.status = currentTab;

    try {
      const res = await getOrders(params);
      const items = (res.data && res.data.items) || [];
      const total = (res.data && res.data.total) || 0;
      this.setData({
        orders: reset ? items : this.data.orders.concat(items),
        offset: (reset ? 0 : offset) + items.length,
        hasMore: this.data.orders.length + items.length < total,
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
    }
  },

  onTabTap(e) {
    const { value } = e.currentTarget.dataset;
    if (value === this.data.currentTab) return;
    this.setData({ currentTab: value, orders: [], offset: 0, hasMore: true });
    this.loadOrders(true);
  },

  onOrderTap(e) {
    const { orderId } = e.currentTarget.dataset;
    wx.navigateTo({ url: `../order-detail/index?order_id=${orderId}` });
  },

  onReachBottom() {
    this.loadOrders(false);
  },

  getStatusLabel(status) {
    const map = { pending: '待支付', paid: '已支付', shipped: '已发货', delivered: '已完成', cancelled: '已取消' };
    return map[status] || status;
  },

  getStatusClass(status) {
    const map = { pending: 'warning', paid: 'info', shipped: 'info', delivered: 'success', cancelled: 'muted' };
    return map[status] || '';
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },

  formatTime(time) {
    if (!time) return '';
    return time.replace('T', ' ').substring(0, 16);
  },
});
