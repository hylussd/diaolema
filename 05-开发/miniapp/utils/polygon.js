/**
 * 地理多边形判断 - 射线法
 * 判断点是否在多边形内
 */
function isPointInPolygon(point, polygon) {
  if (!polygon || polygon.length < 3) return false;

  let inside = false;
  const n = polygon.length;

  for (let i = 0, j = n - 1; i < n; j = i++) {
    const xi = polygon[i].longitude;
    const yi = polygon[i].latitude;
    const xj = polygon[j].longitude;
    const yj = polygon[j].latitude;

    if (
      yi > point.latitude !== yj > point.latitude &&
      point.longitude < ((xj - xi) * (point.latitude - yi)) / (yj - yi) + xi)
    ) {
      inside = !inside;
    }
  }
  return inside;
}

/**
 * 判断坐标是否在任意一个禁钓区内
 * @param {object} point - {latitude, longitude}
 * @param {array} zones - 禁钓区数组，每个元素是 {coordinates: [[lng, lat], ...]}
 * @returns {boolean}
 */
function isInForbiddenZone(point, zones) {
  for (const zone of zones) {
    if (!zone.coordinates || zone.coordinates.length < 3) continue;
    const polygon = zone.coordinates.map(coord => ({
      longitude: coord[0],
      latitude: coord[1],
    }));
    if (isPointInPolygon(point, polygon)) {
      return zone;
    }
  }
  return null;
}

module.exports = { isPointInPolygon, isInForbiddenZone };
