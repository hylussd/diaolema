// pages/shop/cart/index.js
const { getCart, updateCartItem, deleteCartItem } = require('../../../services/shop');

Page({
  data: {
    cart: null,
    items: [],
    totalAmount: 0,
    totalCount: 0,
    selectedIds: [],
    loading: true,
  },

  onShow() {
    this.loadCart();
  },

  async loadCart() {
    this.setData({ loading: true });
    try {
      const res = await getCart();
      const cart = res || {};
      const items = cart.items || [];
      // 默认全选
      const selectedIds = items.map((i) => i.id);
      const totalAmount = cart.total_amount || 0;
      const totalCount = cart.total_count || 0;
      this.setData({ cart, items, selectedIds, totalAmount, totalCount, loading: false });
    } catch {
      this.setData({ loading: false });
    }
  },

  // 勾选/取消勾选
  onCheckTap(e) {
    const { id } = e.currentTarget.dataset;
    const { selectedIds } = this.data;
    const idx = selectedIds.indexOf(id);
    if (idx === -1) {
      selectedIds.push(id);
    } else {
      selectedIds.splice(idx, 1);
    }
    this.setData({ selectedIds });
  },

  // 全选/取消全选
  onSelectAll() {
    const { selectedIds, items } = this.data;
    if (selectedIds.length === items.length) {
      this.setData({ selectedIds: [] });
    } else {
      this.setData({ selectedIds: items.map((i) => i.id) });
    }
  },

  // 数量减少
  async onDecrement(e) {
    const { id } = e.currentTarget.dataset;
    const item = this.data.items.find((i) => i.id === id);
    if (!item || item.quantity <= 1) return;
    try {
      await updateCartItem(id, { quantity: item.quantity - 1 });
      this.loadCart();
    } catch {}
  },

  // 数量增加
  async onIncrement(e) {
    const { id } = e.currentTarget.dataset;
    const item = this.data.items.find((i) => i.id === id);
    if (!item) return;
    try {
      await updateCartItem(id, { quantity: item.quantity + 1 });
      this.loadCart();
    } catch {}
  },

  // 删除商品
  async onDelete(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该商品吗？',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await deleteCartItem(id);
          wx.showToast({ title: '已删除', icon: 'success' });
          this.loadCart();
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      },
    });
  },

  // 结算
  onCheckout() {
    const { selectedIds } = this.data;
    if (selectedIds.length === 0) {
      wx.showToast({ title: '请先选择商品', icon: 'none' });
      return;
    }
    wx.navigateTo({ url: '../checkout/index?from=cart' });
  },

  // 去逛逛
  onGoShopping() {
    wx.navigateTo({ url: '../index/index' });
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },
});
