// pages/spot-edit/spot-edit.js
const app = getApp();
const { getSpot, createSpot, updateSpot } = require('../../services/spots');
const { getCategories } = require('../../services/categories');
const constants = require('../../utils/constants');

Page({
  data: {
    isEdit: false,
    spotId: null,
    name: '',
    latitude: '',
    longitude: '',
    terrain: '',
    terrainIndex: 0,
    terrainLabel: '请选择地形',
    fishSpecies: [],
    note: '',
    categoryId: '',
    categories: [],
    loading: false,
    submitting: false,
    terrainOptions: constants.TERRAIN_TYPES,
    fishOptions: constants.FISH_SPECIES,
    selectedFish: [],
  },

  onLoad(query) {
    // 新建模式
    if (query.id) {
      this.setData({ isEdit: true, spotId: query.id });
      wx.setNavigationBarTitle({ title: '编辑标点' });
      this.loadSpot(query.id);
    } else {
      // 新建：使用传入坐标或当前定位
      const lat = query.lat || (app.globalData.location ? app.globalData.location.latitude : '');
      const lng = query.lng || (app.globalData.location ? app.globalData.location.longitude : '');
      this.setData({ latitude: lat, longitude: lng });
      wx.setNavigationBarTitle({ title: '新建标点' });
    }
    this.loadCategories();
  },

  // 地形选项翻译
  getTerrainLabel(terrain) {
    const found = constants.TERRAIN_TYPES.find(t => t.value === terrain);
    return found ? found.label : '请选择地形';
  },

  async loadSpot(id) {
    this.setData({ loading: true });
    try {
      const spot = await getSpot(id);
      const selectedFish = spot.fish_species || spot.fishSpecies || [];
      const terrain = spot.terrain || '';
      const terrainIndex = constants.TERRAIN_TYPES.findIndex(t => t.value === terrain);
      this.setData({
        name: spot.name || '',
        latitude: spot.latitude || '',
        longitude: spot.longitude || '',
        terrain,
        terrainIndex: terrainIndex >= 0 ? terrainIndex : 0,
        terrainLabel: terrain ? this.getTerrainLabel(terrain) : '请选择地形',
        note: spot.note || '',
        categoryId: spot.category_id || '',
        selectedFish,
        loading: false,
      });
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  async loadCategories() {
    try {
      const cats = await getCategories();
      this.setData({ categories: cats });
    } catch {}
  },

  // 名称输入
  onNameInput(e) {
    this.setData({ name: e.detail.value });
  },

  // 备注输入
  onNoteInput(e) {
    this.setData({ note: e.detail.value });
  },

  // 分类选择
  onCategoryChange(e) {
    this.setData({ categoryId: e.detail.id });
  },

  // 地形选择
  onTerrainChange(e) {
    const idx = parseInt(e.detail.value, 10);
    const terrain = constants.TERRAIN_TYPES[idx] ? constants.TERRAIN_TYPES[idx].value : '';
    this.setData({
      terrainIndex: idx,
      terrain: terrain,
      terrainLabel: terrain ? this.getTerrainLabel(terrain) : '请选择地形',
    });
  },

  // 鱼种多选
  onFishToggle(e) {
    const species = e.currentTarget.dataset.species;
    const { selectedFish } = this.data;
    const idx = selectedFish.indexOf(species);
    if (idx >= 0) {
      selectedFish.splice(idx, 1);
    } else {
      selectedFish.push(species);
    }
    this.setData({ selectedFish });
  },

  // 选择地图位置
  chooseLocation() {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          latitude: res.latitude,
          longitude: res.longitude,
        });
      },
    });
  },

  // 提交
  async submit() {
    const { name, latitude, longitude, terrain, selectedFish, note, categoryId, isEdit, spotId } = this.data;
    if (!name.trim()) {
      wx.showToast({ title: '请输入标点名称', icon: 'none' }); return;
    }
    if (!latitude || !longitude) {
      wx.showToast({ title: '请选择位置', icon: 'none' }); return;
    }

    const data = {
      name: name.trim(),
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      terrain: terrain,
      fish_species: selectedFish,
      note: note.trim(),
      category_id: categoryId,
    };

    this.setData({ submitting: true });
    try {
      if (isEdit) {
        await updateSpot(spotId, data);
        wx.showToast({ title: '已更新' });
      } else {
        await createSpot(data);
        wx.showToast({ title: '已创建' });
      }
      this.setData({ submitting: false });
      wx.navigateBack();
    } catch (err) {
      this.setData({ submitting: false });
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },
});
