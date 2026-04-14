// pages/recipe/recipe.js
const { getMyRecipes, createRecipe, deleteRecipe, updateRecipe } = require('../../services/recipe');
const constants = require('../../utils/constants');

Page({
  data: {
    recipes: [],
    loading: false,
    showForm: false,
    // 表单字段
    formName: '',
    formPressureMin: '',
    formPressureMax: '',
    formWaterTempMin: '',
    formWaterTempMax: '',
    formFishSpecies: '',
    formSpotType: '',
    formIsPublic: false,
    editingId: null,
    fishSpeciesList: constants.FISH_SPECIES,
    spotTypes: constants.SPOT_TYPES,
  },

  onShow() {
    this.loadRecipes();
  },

  async loadRecipes() {
    this.setData({ loading: true });
    try {
      const res = await getMyRecipes({ offset: 0, limit: 100 });
      const recipes = (res.items || []).map(function(r) {
        return r;
      });
      this.setData({ recipes, loading: false });
    } catch {
      this.setData({ loading: false });
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },

  // 打开创建表单
  onAddRecipe() {
    this.setData({
      showForm: true,
      editingId: null,
      formName: '',
      formPressureMin: '',
      formPressureMax: '',
      formWaterTempMin: '',
      formWaterTempMax: '',
      formFishSpecies: '',
      formSpotType: '',
      formIsPublic: false,
    });
  },

  // 关闭表单
  onCloseForm() {
    this.setData({ showForm: false });
  },

  // 鱼种选择
  onFishSpeciesChange(e) {
    const val = e.detail.value;
    this.setData({ formFishSpecies: val });
  },

  // 钓场类型选择
  onSpotTypeChange(e) {
    const val = e.detail.value;
    this.setData({ formSpotType: val });
  },

  // 公开切换
  onPublicSwitch(e) {
    this.setData({ formIsPublic: e.detail.value });
  },

  // 输入监听
  onFormInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ [field]: e.detail.value });
  },

  // 提交配方
  async onSubmitForm() {
    const { formName, formPressureMin, formPressureMax, formWaterTempMin, formWaterTempMax, formFishSpecies, formSpotType, formIsPublic, editingId } = this.data;
    if (!formName) {
      wx.showToast({ title: '请输入配方名称', icon: 'none' });
      return;
    }
    if (!formFishSpecies) {
      wx.showToast({ title: '请选择目标鱼种', icon: 'none' });
      return;
    }
    const body = {
      name: formName,
      pressure_min: parseInt(formPressureMin) || 1000,
      pressure_max: parseInt(formPressureMax) || 1013,
      water_temp_min: parseFloat(formWaterTempMin) || 15,
      water_temp_max: parseFloat(formWaterTempMax) || 25,
      fish_species: formFishSpecies,
      spot_type: formSpotType || undefined,
      is_public: formIsPublic,
    };
    try {
      if (editingId) {
        await updateRecipe(editingId, body);
        wx.showToast({ title: '更新成功', icon: 'success' });
      } else {
        await createRecipe(body);
        wx.showToast({ title: '创建成功', icon: 'success' });
      }
      this.setData({ showForm: false });
      this.loadRecipes();
    } catch (e) {
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },

  // 编辑配方
  onEditRecipe(e) {
    const recipe = e.currentTarget.dataset.recipe;
    this.setData({
      showForm: true,
      editingId: recipe.id,
      formName: recipe.name,
      formPressureMin: String(recipe.pressure_min),
      formPressureMax: String(recipe.pressure_max),
      formWaterTempMin: String(recipe.water_temp_min),
      formWaterTempMax: String(recipe.water_temp_max),
      formFishSpecies: recipe.fish_species,
      formSpotType: recipe.spot_type || '',
      formIsPublic: !!recipe.is_public,
    });
  },

  // 删除配方
  onDeleteRecipe(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该配方吗？',
      confirmColor: '#ef4444',
      success: async function(res) {
        if (!res.confirm) return;
        try {
          await deleteRecipe(id);
          wx.showToast({ title: '已删除', icon: 'success' });
          this.loadRecipes();
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      }.bind(this),
    });
  },

  // 切换公开状态
  async onTogglePublic(e) {
    const recipe = e.currentTarget.dataset.recipe;
    try {
      await updateRecipe(recipe.id, { is_public: !recipe.is_public });
      wx.showToast({ title: '已更新', icon: 'success' });
      this.loadRecipes();
    } catch {
      wx.showToast({ title: '更新失败', icon: 'none' });
    }
  },
});
