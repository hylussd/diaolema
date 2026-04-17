// pages/shop/products/index.js
const { getShopCategories, getShopProducts } = require('../../../services/shop');

Page({
  data: {
    categories: [],
    selectedCategoryId: null,
    keyword: '',
    products: [],
    loading: false,
    hasMore: true,
    offset: 0,
    limit: 20,
  },

  onLoad(query) {
    if (query.category_id) {
      this.setData({ selectedCategoryId: parseInt(query.category_id) });
    }
    if (query.keyword) {
      this.setData({ keyword: query.keyword });
    }
    this.loadCategories();
    this.loadProducts(true);
  },

  async loadCategories() {
    try {
      const res = await getShopCategories();
      this.setData({ categories: res || [] });
    } catch {}
  },

  async loadProducts(reset = false) {
    const { selectedCategoryId, keyword, offset, limit, loading, hasMore } = this.data;
    if (loading || (!reset && !hasMore)) return;

    this.setData({ loading: true });
    const params = { offset: reset ? 0 : offset, limit };
    if (selectedCategoryId) params.category_id = selectedCategoryId;
    if (keyword) params.keyword = keyword;

    try {
      const res = await getShopProducts(params);
      const items = (res && res.items) || [];
      const total = (res && res.total) || 0;
      this.setData({
        products: reset ? items : this.data.products.concat(items),
        offset: (reset ? 0 : offset) + items.length,
        hasMore: this.data.products.length + items.length < total,
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  // 搜索确认
  onSearchConfirm(e) {
    this.setData({ keyword: e.detail.value, offset: 0, hasMore: true });
    this.loadProducts(true);
  },

  // 选择分类
  onCategoryTap(e) {
    const { id } = e.currentTarget.dataset;
    const current = this.data.selectedCategoryId;
    this.setData({
      selectedCategoryId: current === id ? null : id,
      offset: 0,
      hasMore: true,
      products: [],
    });
    this.loadProducts(true);
  },

  // 商品卡片点击
  onProductTap(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `../product-detail/index?id=${id}` });
  },

  // 触底加载更多
  onReachBottom() {
    this.loadProducts(false);
  },

  formatPrice(price) {
    return (price / 100).toFixed(2);
  },
});
