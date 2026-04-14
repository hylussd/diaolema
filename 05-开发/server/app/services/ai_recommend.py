"""AI 推荐规则引擎（纯规则，不上模型）。"""
import math
from datetime import datetime, timezone

from app.services.astronomy_service import calculate_moon_phase, calculate_sun_times


# ----------------------------------------------------------------------
# 鱼种气压评分矩阵: (鱼种, 最佳_min, 最佳_max, 良好_min, 良好_max, 勉强_min, 勉强_max)
# 格式: (最佳100区间), (良好80区间), (勉强50区间)
# ----------------------------------------------------------------------
PRESSURE_MATRIX = {
    "鲫鱼":   {"best": (1000, 1015), "good": [(995, 1000), (1015, 1025)], "marginal": [(990, 995), (1025, 1030)]},
    "鲤鱼":   {"best": (1005, 1015), "good": [(1000, 1005), (1015, 1020)], "marginal": [(995, 1000), (1020, 1025)]},
    "草鱼":   {"best": (1005, 1020), "good": [(1000, 1005), (1020, 1025)], "marginal": [(995, 1000), (1025, 1030)]},
    "鲢鳙":   {"best": (1010, 1025), "good": [(1005, 1010), (1025, 1030)], "marginal": [(1000, 1005), (1030, 1035)]},
    "鳜鱼":   {"best": (1005, 1020), "good": [(1000, 1005), (1020, 1025)], "marginal": [(995, 1000), (1025, 1030)]},
    "黑鱼":   {"best": (1000, 1015), "good": [(995, 1000), (1015, 1020)], "marginal": [(990, 995), (1020, 1025)]},
    "罗非":   {"best": (1010, 1025), "good": [(1005, 1010), (1025, 1030)], "marginal": [(1000, 1005), (1030, 1035)]},
    "鳊鱼":   {"best": (1005, 1018), "good": [(1000, 1005), (1018, 1022)], "marginal": [(995, 1000), (1022, 1027)]},
    "青鱼":   {"best": (1005, 1020), "good": [(1000, 1005), (1020, 1025)], "marginal": [(995, 1000), (1025, 1030)]},
    "黄颡鱼": {"best": (1000, 1015), "good": [(995, 1000), (1015, 1020)], "marginal": [(990, 995), (1020, 1025)]},
}

# 水温评分矩阵（水温单位：℃）
TEMP_MATRIX = {
    "鲫鱼":   {"best": (16, 24), "good": [(12, 16), (24, 28)], "marginal": [(8, 12), (28, 32)]},
    "鲤鱼":   {"best": (18, 26), "good": [(14, 18), (26, 30)], "marginal": [(10, 14), (30, 34)]},
    "草鱼":   {"best": (20, 28), "good": [(16, 20), (28, 32)], "marginal": [(12, 16), (32, 35)]},
    "鲢鳙":   {"best": (22, 30), "good": [(18, 22), (30, 34)], "marginal": [(14, 18), (34, 38)]},
    "鳜鱼":   {"best": (22, 28), "good": [(18, 22), (28, 32)], "marginal": [(15, 18), (32, 36)]},
    "黑鱼":   {"best": (24, 30), "good": [(20, 24), (30, 34)], "marginal": [(16, 20), (34, 38)]},
    "罗非":   {"best": (26, 32), "good": [(22, 26), (32, 36)], "marginal": [(18, 22), (36, 40)]},
    "鳊鱼":   {"best": (18, 26), "good": [(14, 18), (26, 30)], "marginal": [(10, 14), (30, 34)]},
    "青鱼":   {"best": (18, 28), "good": [(14, 18), (28, 32)], "marginal": [(10, 14), (32, 36)]},
    "黄颡鱼": {"best": (20, 28), "good": [(16, 20), (28, 32)], "marginal": [(12, 16), (32, 36)]},
}

# 风力评分
WIND_SCORES = [(0, 2, 100), (2, 4, 85), (4, 6, 70), (6, 8, 50), (8, float("inf"), 20)]

# 月相评分
MOON_SCORES = {
    "new_moon": 90,
    "waxing_crescent": 80,
    "first_quarter": 70,
    "waxing_gibbous": 85,
    "full_moon": 60,
    "waning_gibbous": 80,
    "last_quarter": 65,
    "waning_crescent": 75,
}

# 时段评分
TIME_SLOT_SCORES = {
    "morning": 100,   # 5-7点
    "afternoon": 55,  # 14-16点
    "evening": 90,    # 18-19:30
}


def _score_in_range(value: float, matrix: dict) -> int:
    best_min, best_max = matrix["best"]
    if best_min <= value <= best_max:
        return 100
    for m_min, m_max in matrix["good"]:
        if m_min <= value <= m_max:
            return 80
    for m_min, m_max in matrix["marginal"]:
        if m_min <= value <= m_max:
            return 50
    return 20


def _score_wind(wind_speed: float) -> int:
    for lo, hi, score in WIND_SCORES:
        if lo <= wind_speed < hi:
            return score
    return 20


def _score_time_slot(time_slot: str) -> int:
    return TIME_SLOT_SCORES.get(time_slot, 50)


def score_spot(
    target_fish: str,
    pressure: float | None,
    temp: float | None,
    wind_speed: float | None,
    moon_phase_code: str,
    time_slot: str,
) -> tuple[int, list[str]]:
    """
    计算单个标点的推荐评分及理由。
    Returns: (总分, [推荐理由列表])
    """
    reasons = []

    p_score = 0
    t_score = 0
    w_score = 0
    m_score = MOON_SCORES.get(moon_phase_code, 50)
    ts_score = _score_time_slot(time_slot)

    if pressure is not None and target_fish in PRESSURE_MATRIX:
        p_score = _score_in_range(pressure, PRESSURE_MATRIX[target_fish])
    if temp is not None and target_fish in TEMP_MATRIX:
        t_score = _score_in_range(temp, TEMP_MATRIX[target_fish])
    if wind_speed is not None:
        w_score = _score_wind(wind_speed)

    total = round(p_score * 0.35 + t_score * 0.25 + w_score * 0.20 + m_score * 0.10 + ts_score * 0.10)

    # 生成推荐理由
    if p_score >= 90 and pressure is not None and target_fish in PRESSURE_MATRIX:
        mat = PRESSURE_MATRIX[target_fish]
        reasons.append(f"气压{pressure}hPa，处于{target_fish}活跃区间")
    elif p_score >= 80 and pressure is not None:
        reasons.append(f"气压{pressure}hPa，适合{target_fish}出没")

    if t_score >= 90 and temp is not None:
        reasons.append(f"水温{temp}℃，适合{target_fish}出没")
    elif t_score >= 80 and temp is not None:
        reasons.append(f"水温{temp}℃尚可，{target_fish}活性较好")

    if w_score >= 85 and wind_speed is not None:
        reasons.append(f"风力{wind_speed}级，{target_fish}觅食积极")
    elif w_score <= 50 and wind_speed is not None:
        reasons.append(f"风力{wind_speed}级偏大，出钓效果可能受影响")

    if m_score >= 85:
        phase_names = {
            "new_moon": "新月",
            "waxing_gibbous": "盈凸月",
            "waning_gibbous": "亏凸月",
            "waxing_crescent": "蛾眉月",
        }
        phase_name = phase_names.get(moon_phase_code, "")
        if phase_name:
            reasons.append(f"{phase_name}，{target_fish}活性增强")

    if ts_score >= 90:
        slot_names = {"morning": "清晨", "evening": "黄昏"}
        reasons.append(f"当前处于{slot_names.get(time_slot, '')}{target_fish}黄金出钓时段")
    elif ts_score >= 80:
        slot_names = {"morning": "早晨", "evening": "傍晚"}
        reasons.append(f"{slot_names.get(time_slot, '')}时段，{target_fish}出钓较合适")

    return total, reasons


def build_general_advice(
    target_fish: str,
    date_str: str,
    time_slot: str,
    moon_phase_text: str,
) -> str:
    """生成综合建议。"""
    slot_hints = {
        "morning": "建议5-7点出钓，选择回流区或水草边",
        "afternoon": "建议14-16点出钓，注意避暑防晒",
        "evening": "建议17-19点出钓，傍晚是黄金窗口",
    }
    hint = slot_hints.get(time_slot, "")
    return f"今日{date_str}，{moon_phase_text}，是钓{target_fish}的好时机。{hint}"
