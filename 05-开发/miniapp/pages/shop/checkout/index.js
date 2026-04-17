// pages/shop/checkout/index.js
const { getCart, createOrder, mockPayOrder } = require('../../../services/shop');

Page({
  data: {
    items: [],
    totalAmount: 0,
    addressName: '',
    addressPhone: '',
    addressDetail: '',
    remark: '',
    submitting: false,
    loading: true,
  },

  onLoad(query) {
    this.fromCart = query.from === 'cart';
    this.loadCartData();
  },

  async loadCartData() {
    this.setData({ loading: true });
    try {
      if (this.fromCart) {
        const res = await getCart();
        const cart = res.data || {};
        const items = cart.items || [];
        const totalAmount = cart.total_amount || 0;
        this.setData({ items, totalAmount, loading: false });
      } else {
        this.setData({ loading: false });
      }
    } catch {
      this.setData({ loading: false });
    }
  },

  onAddressNameInput(e) {
    this.setData({ addressName: e.detail.value });
  },

  onAddressPhoneInput(e) {
    this.setData({ addressPhone: e.detail.value });
  },

  onAddressDetailInput(e) {
    this.setData({ addressDetail: e.detail.value });
  },

  onRemarkInput(e) {
    this.setData({ remark: e.detail.value });
  },

  async onSubmit() {
    const { addressName, addressPhone, addressDetail, submitting, items } = this.data;
    if (submitting) return;

    if (!addressName.trim()) {
      wx.showToast({ title: '请填写收货人姓名', icon: 'none' }); return;
    }
    if (!addressPhone.trim()) {
      wx.showToast({ title: '请填写联系电话', icon: 'none' }); return;
    }
    if (!addressDetail.trim()) {
      wx.showToast({ title: '请填写收货地址', icon: 'none' }); return;
    }
    if (items.length === 0) {
      wx.showToast({ title: '购物车为空', icon: 'none' }); return;
    }

    this.setData({ submitting: true });
    try {
      const orderRes = await createOrder({
        address_name: addressName.trim(),
        address_phone: addressPhone.trim(),
        address_detail: addressDetail.trim(),
        remark: this.data.remark.trim(),
        pay_status: 'paid',
      });
      const orderData = orderRes.data || {};
      const orderId = orderData.order_id;

      // Mock 支付
      await mockPayOrder(orderId);

      wx.showToast({ title: '支付成功', icon: 'success' });
      setTimeout(() => {
        wx.redirectTo({ url: `../order-detail/index?order_id=${orderId}` });
      }, 1500);
    } catch (e) {
      const msg = (e.data && e.data.msg) || '提交失败';
      wx.showToast({ title: msg, icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },
});
