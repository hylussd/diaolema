"""天文计算服务：月相 + 日出日落（Jean Meeus 公式）。"""
from datetime import datetime, date, timezone
import math


# 已知新月基准：2000-01-06 18:14 UTC
KNOWN_NEW_MOON = datetime(2000, 1, 6, 18, 14, 0, tzinfo=timezone.utc)
SYNODIC_MONTH = 29.53058867  # 朔望月天数

MOON_PHASES = [
    (0.00, "新月", "new_moon"),
    (0.125, "蛾眉月", "waxing_crescent"),
    (0.25, "上弦月", "first_quarter"),
    (0.375, "盈凸月", "waxing_gibbous"),
    (0.50, "满月", "full_moon"),
    (0.625, "亏凸月", "waning_gibbous"),
    (0.75, "下弦月", "last_quarter"),
    (0.875, "残月", "waning_crescent"),
]


def calculate_moon_phase(dt: datetime | date) -> tuple[str, str, float]:
    """
    计算指定日期的月相。
    Returns: (月相名称, 月相代码, 月球照明度 0.0-1.0)
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time()).replace(tzinfo=timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    delta = (dt - KNOWN_NEW_MOON).total_seconds() / 86400
    phase = (delta % SYNODIC_MONTH) / SYNODIC_MONTH
    illumination = (1 - math.cos(phase * 2 * math.pi)) / 2

    for threshold, name, code in reversed(MOON_PHASES):
        if phase >= threshold:
            return name, code, round(illumination, 2)
    return MOON_PHASES[0][1], MOON_PHASES[0][2], 0.0


def calculate_sun_times(lat: float, lng: float, dt: datetime | date) -> dict[str, str]:
    """
    计算指定地点和日期的日出日落时刻。
    返回: {sunrise, sunset, dawn, dusk} 格式 "HH:MM"
    太阳在地平线下18度为晨昏影边界。
    """
    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())

    year, month, day = dt.year, dt.month, dt.day

    if month <= 2:
        year -= 1
        month += 12
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    JD = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5

    n = JD - 2451545.0
    L = (280.46 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    eclon = L + 1.915 * math.sin(math.radians(g)) + 0.020 * math.sin(math.radians(2 * g))
    obliquity = 23.439 - 0.0000004 * n

    RA = math.degrees(math.atan2(
        math.cos(math.radians(obliquity)) * math.sin(math.radians(eclon)),
        math.cos(math.radians(eclon))
    ))
    dec = math.degrees(math.asin(
        math.sin(math.radians(obliquity)) * math.sin(math.radians(eclon))
    ))

    lat_rad = math.radians(lat)
    dec_rad = math.radians(dec)

    def hour_angle(alt: float) -> float:
        cos_H = (math.sin(math.radians(alt)) - math.sin(lat_rad) * math.sin(dec_rad)) \
                / (math.cos(lat_rad) * math.cos(dec_rad))
        if cos_H > 1 or cos_H < -1:
            return float('nan')
        return math.degrees(math.acos(cos_H))

    H_sun = hour_angle(0)     # 日出日落
    H_dawn = hour_angle(-18)  # 晨光始/昏影终

    noon = 12 - (lng / 15) - 0.0053 * math.sin(math.radians(g)) \
           + 1.0028 * math.sin(math.radians(2 * (L - lng)))

    def fmt(h: float) -> str:
        if math.isnan(h):
            return "--:--"
        h = max(0, min(24, h))
        return f"{int(h):02d}:{int((h - int(h)) * 60):02d}"

    return {
        "sunrise": fmt(noon - H_sun / 15),
        "sunset":  fmt(noon + H_sun / 15),
        "dawn":    fmt(noon - H_dawn / 15),
        "dusk":    fmt(noon + H_dawn / 15),
    }
