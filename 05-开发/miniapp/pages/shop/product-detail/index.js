// pages/shop/product-detail/index.js
const { getShopProductDetail, addToCart } = require('../../../services/shop');

Page({
  data: {
    product: null,
    images: [],
    selectedSpecs: {},
    specsOptions: [],
    loading: true,
    submitting: false,
    currentSwiper: 0,
  },

  onLoad(query) {
    const id = parseInt(query.id);
    this.setData({ productId: id });
    this.loadDetail(id);
  },

  async loadDetail(id) {
    this.setData({ loading: true });
    try {
      const res = await getShopProductDetail(id);
      const product = res.data || {};
      const images = product.images || [];
      // 初始化规格选中项（默认选每个规格第一个选项）
      const specs = product.specs || [];
      const selectedSpecs = {};
      (specs || []).forEach((spec) => {
        if (spec.options && spec.options.length > 0) {
          selectedSpecs[spec.name] = spec.options[0];
        }
      });
      this.setData({
        product,
        images,
        specsOptions: specs,
        selectedSpecs,
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 轮播切换
  onSwiperChange(e) {
    this.setData({ currentSwiper: e.detail.current });
  },

  // 规格选项点击
  onSpecTap(e) {
    const { name, value } = e.currentTarget.dataset;
    const selectedSpecs = { ...this.data.selectedSpecs };
    selectedSpecs[name] = value;
    this.setData({ selectedSpecs });
  },

  // 加入购物车
  async onAddToCart() {
    if (this.data.submitting) return;
    this.setData({ submitting: true });
    try {
      await addToCart({
        product_id: this.data.productId,
        quantity: 1,
        specs: this.data.selectedSpecs,
      });
      wx.showToast({ title: '已加入购物车', icon: 'success' });
    } catch (e) {
      const msg = (e.data && e.data.msg) || '加入失败';
      wx.showToast({ title: msg, icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  // 立即购买
  async onBuyNow() {
    if (this.data.submitting) return;
    this.setData({ submitting: true });
    try {
      await addToCart({
        product_id: this.data.productId,
        quantity: 1,
        specs: this.data.selectedSpecs,
      });
      wx.navigateTo({ url: `../checkout/index?from=cart` });
    } catch (e) {
      const msg = (e.data && e.data.msg) || '加入失败';
      wx.showToast({ title: msg, icon: 'none' });
    } finally {
      this.setData({ submitting: false });
    }
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },
});
