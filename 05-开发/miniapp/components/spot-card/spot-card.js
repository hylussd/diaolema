// components/spot-card/spot-card.js
Component({
  properties: {
    spot: { type: Object, value: {} },
  },
  methods: {
    onTap() {
      this.triggerEvent('tap', { spot: this.properties.spot });
    },
  },
});
