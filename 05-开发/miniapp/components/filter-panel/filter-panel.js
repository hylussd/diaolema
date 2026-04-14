// components/filter-panel/filter-panel.js
const constants = require('../../utils/constants');

Component({
  properties: {
    visible: {
      type: Boolean,
      value: false,
    },
  },

  data: {
    // 气压区间（hPa）
    pressureRange: [980, 1040],
    pressureMin: 980,
    pressureMax: 1040,
    // 水温区间（℃，用气温代替）
    tempRange: [0, 40],
    tempMin: 0,
    tempMax: 40,
    // 鱼种多选
    selectedFish: [],
    fishSpecies: constants.FISH_SPECIES,
    // 钓场类型
    terrainTypes: constants.TERRAIN_TYPES,
    selectedTerrain: '',
  },

  methods: {
    // 空操作，阻止事件穿透
    noop() {},

    // 关闭面板
    onClose() {
      this.triggerEvent('close');
    },

    // 重置筛选
    onReset() {
      this.setData({
        pressureMin: 980,
        pressureMax: 1040,
        tempMin: 0,
        tempMax: 40,
        selectedFish: [],
        selectedTerrain: '',
      });
    },

    // 气压滑块变化
    onPressureChange(e) {
      const values = e.detail.value;
      this.setData({
        pressureMin: values[0],
        pressureMax: values[1],
      });
    },

    // 水温滑块变化
    onTempChange(e) {
      const values = e.detail.value;
      this.setData({
        tempMin: values[0],
        tempMax: values[1],
      });
    },

    // 鱼种切换
    onFishToggle(e) {
      const fish = e.currentTarget.dataset.fish;
      const { selectedFish } = this.data;
      const idx = selectedFish.indexOf(fish);
      if (idx === -1) {
        selectedFish.push(fish);
      } else {
        selectedFish.splice(idx, 1);
      }
      this.setData({ selectedFish });
    },

    // 钓场类型切换
    onTerrainChange(e) {
      this.setData({ selectedTerrain: e.detail.value });
    },

    // 确认筛选
    onConfirm() {
      const { pressureMin, pressureMax, tempMin, tempMax, selectedFish, selectedTerrain } = this.data;
      this.triggerEvent('confirm', {
        pressure_min: pressureMin,
        pressure_max: pressureMax,
        temp_min: tempMin,
        temp_max: tempMax,
        fish_species: selectedFish.join(','),
        category_type: selectedTerrain,
      });
    },
  },
});
