// components/category-picker/category-picker.js
Component({
  properties: {
    categories: { type: Array, value: [] },
    value: { type: String, value: '' },
  },
  methods: {
    onSelect(e) {
      const id = e.currentTarget.dataset.id;
      this.triggerEvent('change', { id });
    },
  },
});
