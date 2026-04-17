/**
 * 地理多边形判断 - 射线法
 * 判断点是否在多边形内
 */
function isPointInPolygon(point, polygon) {
  if (!polygon || polygon.length < 3) return false;

  var inside = false;
  var n = polygon.length;

  for (var i = 0, j = n - 1; i < n; j = i++) {
    var xi = polygon[i].longitude;
    var yi = polygon[i].latitude;
    var xj = polygon[j].longitude;
    var yj = polygon[j].latitude;

    // 射线法核心判断：yi 和 yj 在 point.latitude 的两侧
    var cond1 = (yi > point.latitude);
    var cond2 = (yj > point.latitude);
    if (cond1 !== cond2) {
      var intersectX = ((xj - xi) * (point.latitude - yi)) / (yj - yi) + xi;
      if (point.longitude < intersectX) {
        inside = !inside;
      }
    }
  }
  return inside;
}

/**
 * 判断坐标是否在任意一个禁钓区内
 * @param {object} point - {latitude, longitude}
 * @param {array} zones - 禁钓区数组，每个元素是 {coordinates: [[lng, lat], ...]}
 */
function isInForbiddenZone(point, zones) {
  if (!zones || !point) return false;
  for (var i = 0; i < zones.length; i++) {
    var zone = zones[i];
    if (!zone || !zone.coordinates || zone.coordinates.length < 3) continue;
    if (isPointInPolygon(point, zone.coordinates)) {
      return true;
    }
  }
  return false;
}

module.exports = {
  isPointInPolygon: isPointInPolygon,
  isInForbiddenZone: isInForbiddenZone,
};
