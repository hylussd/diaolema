// pages/category/category.js
const { getCategories, createCategory, updateCategory, deleteCategory } = require('../../services/categories');

Page({
  data: {
    categories: [],
    loading: true,
    showAddModal: false,
    editCategory: null,
    newName: '',
  },

  onLoad() {
    this.loadCategories();
  },

  onShow() {
    this.loadCategories();
  },

  async loadCategories() {
    this.setData({ loading: true });
    try {
      const cats = await getCategories();
      this.setData({ categories: cats, loading: false });
    } catch {
      this.setData({ loading: false });
    }
  },

  // 显示新建弹窗
  showAdd() {
    this.setData({ showAddModal: true, editCategory: null, newName: '' });
  },

  // 显示编辑弹窗
  showEdit(e) {
    const cat = e.currentTarget.dataset.cat;
    this.setData({ showAddModal: true, editCategory: cat, newName: cat.name });
  },

  // 关闭弹窗
  closeModal() {
    this.setData({ showAddModal: false, editCategory: null, newName: '' });
  },

  onNameInput(e) {
    this.setData({ newName: e.detail.value });
  },

  // 保存（新建/编辑）
  async save() {
    const { newName, editCategory } = this.data;
    if (!newName.trim()) {
      wx.showToast({ title: '请输入分类名称', icon: 'none' }); return;
    }
    try {
      if (editCategory) {
        await updateCategory(editCategory.id, { name: newName.trim() });
        wx.showToast({ title: '已更新' });
      } else {
        await createCategory({ name: newName.trim() });
        wx.showToast({ title: '已创建' });
      }
      this.closeModal();
      this.loadCategories();
    } catch {
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },

  // 删除分类
  async deleteCat(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: '删除后该分类下的标点将变为无分类状态',
      confirmColor: '#ef4444',
      success: async (res) => {
        if (!res.confirm) return;
        try {
          await deleteCategory(id);
          wx.showToast({ title: '已删除' });
          this.loadCategories();
        } catch {
          wx.showToast({ title: '删除失败', icon: 'none' });
        }
      },
    });
  },
});
