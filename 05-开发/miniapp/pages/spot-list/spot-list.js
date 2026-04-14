// pages/spot-list/spot-list.js
const app = getApp();
const { getSpots } = require('../../services/spots');
const { getCategories } = require('../../services/categories');
const constants = require('../../utils/constants');
const { distance, formatDistance } = require('../../utils/distance');

Page({
  data: {
    spots: [],
    filteredSpots: [],
    categories: [],
    currentCategoryId: '',
    loading: true,
    keyword: '',
  },

  onLoad() {
    this.loadCategories();
    this.loadSpots();
  },

  onShow() {
    this.loadSpots();
  },

  async loadCategories() {
    try {
      const cats = await getCategories();
      this.setData({ categories: cats });
    } catch {}
  },

  async loadSpots() {
    this.setData({ loading: true });
    try {
      const res = await getSpots();
      const spots = (res.items || res || []).map(spot => {
        const terrainItem = constants.TERRAIN_TYPES.find(t => t.value === spot.terrain);
        spot.terrainLabel = terrainItem ? terrainItem.label : spot.terrain;
        // 计算距离
        const loc = app.globalData.location;
        if (loc) {
          spot.distance = formatDistance(distance(loc.latitude, loc.longitude, spot.latitude, spot.longitude));
        }
        return spot;
      });
      this.setData({ spots, loading: false });
      this.filterSpots();
    } catch {
      this.setData({ loading: false });
    }
  },

  filterSpots() {
    const { spots, currentCategoryId, keyword } = this.data;
    let filtered = spots;
    if (currentCategoryId) {
      filtered = filtered.filter(s => s.category_id === currentCategoryId);
    }
    if (keyword) {
      const kw = keyword.toLowerCase();
      filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(kw) ||
        (s.note && s.note.toLowerCase().includes(kw))
      );
    }
    this.setData({ filteredSpots: filtered });
  },

  onCategoryChange(e) {
    this.setData({ currentCategoryId: e.detail.id || '' });
    this.filterSpots();
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
    this.filterSpots();
  },

  goToDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({ url: `/pages/spot-detail/spot-detail?id=${id}` });
  },

  goToCreate() {
    wx.navigateTo({ url: '/pages/spot-edit/spot-edit' });
  },
});
