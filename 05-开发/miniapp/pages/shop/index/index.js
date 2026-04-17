// pages/shop/index/index.js
const { getShopCategories, getShopProducts } = require('../../../services/shop');

Page({
  data: {
    categories: [],
    featuredProducts: [],
    newProducts: [],
    loading: true,
  },

  onLoad() {
    this.loadData();
  },

  onShow() {
    // 每次回来刷新精选
    this.loadFeatured();
  },

  async loadData() {
    this.setData({ loading: true });
    try {
      const [catsRes, featuredRes, newRes] = await Promise.all([
        getShopCategories(),
        getShopProducts({ is_featured: 1, limit: 10 }),
        getShopProducts({ limit: 10 }),
      ]);
      this.setData({
        categories: catsRes.data || [],
        featuredProducts: (featuredRes.data && featuredRes.data.items) || [],
        newProducts: (newRes.data && newRes.data.items) || [],
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
    }
  },

  async loadFeatured() {
    try {
      const res = await getShopProducts({ is_featured: 1, limit: 10 });
      this.setData({ featuredProducts: (res.data && res.data.items) || [] });
    } catch {}
  },

  // 点击搜索栏 → 跳转商品列表
  onSearchTap() {
    wx.navigateTo({ url: '../products/index' });
  },

  // 点击分类 → 跳转商品列表（带分类）
  onCategoryTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `../products/index?category_id=${id}` });
  },

  // 点击商品卡片 → 跳转商品详情
  onProductTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `../product-detail/index?id=${id}` });
  },

  // 跳转购物车
  onCartTap() {
    wx.navigateTo({ url: '../cart/index' });
  },

  // 价格分转元，保留两位小数
  formatPrice(price) {
    return (price / 100).toFixed(2);
  },
});
