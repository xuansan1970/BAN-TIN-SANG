#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weather_fetch.py — Lấy dự báo thời tiết từ Open-Meteo (miễn phí, không cần API key)
Mặc định: TP. Hồ Chí Minh. Thay LAT/LON nếu anh ở thành phố khác.
"""

import requests

# ─── Cấu hình vị trí ─────────────────────────────────────────────────────────
CITY    = "TP. Hồ Chí Minh"
LAT     = 10.8231
LON     = 106.6297
TZ      = "Asia/Ho_Chi_Minh"

# ─── Mã thời tiết WMO → (emoji, mô tả tiếng Việt) ───────────────────────────
WMO = {
    0:  ("☀️",  "Trời quang"),
    1:  ("🌤️", "Ít mây"),
    2:  ("⛅",  "Có mây"),
    3:  ("☁️",  "Nhiều mây"),
    45: ("🌫️", "Sương mù"),
    48: ("🌫️", "Sương mù giá"),
    51: ("🌦️", "Mưa phùn nhẹ"),
    53: ("🌦️", "Mưa phùn"),
    55: ("🌧️", "Mưa phùn dày"),
    61: ("🌧️", "Mưa nhẹ"),
    63: ("🌧️", "Mưa vừa"),
    65: ("🌧️", "Mưa to"),
    71: ("🌨️", "Tuyết nhẹ"),
    73: ("🌨️", "Tuyết vừa"),
    75: ("❄️",  "Tuyết dày"),
    80: ("🌦️", "Mưa rào nhẹ"),
    81: ("🌧️", "Mưa rào"),
    82: ("⛈️",  "Mưa rào rất to"),
    95: ("⛈️",  "Giông bão"),
    96: ("⛈️",  "Giông có mưa đá"),
    99: ("⛈️",  "Giông mưa đá lớn"),
}


def _weather_info(code: int):
    for k in sorted(WMO.keys(), reverse=True):
        if code >= k:
            return WMO[k]
    return ("🌡️", "Không xác định")


def _advice(temp: int, feels: int, rain_prob: int, humidity: int, wind: float) -> list:
    tips = []

    # Mưa
    if rain_prob >= 70:
        tips.append(("🌂", f"Mang ô — xác suất mưa {rain_prob}%"))
    elif rain_prob >= 40:
        tips.append(("☂️", f"Nên mang theo ô ({rain_prob}% khả năng mưa)"))

    # Nhiệt độ
    if feels >= 39:
        tips.append(("🥵", "Rất nóng, hạn chế ra ngoài lúc 11h–15h"))
    elif feels >= 35:
        tips.append(("🌡️", "Nóng, uống nhiều nước & đội nón khi ra ngoài"))
    elif feels >= 28:
        tips.append(("🌞", "Thời tiết ấm, mặc thoáng mát"))
    elif feels < 22:
        tips.append(("🧥", "Hơi lạnh, mặc thêm áo khoác"))

    # Gió mạnh
    if wind >= 35:
        tips.append(("💨", f"Gió mạnh {wind} km/h — cẩn thận khi đi xe"))
    elif wind >= 25:
        tips.append(("🌬️", f"Gió khá mạnh {wind} km/h"))

    # Độ ẩm
    if humidity >= 88:
        tips.append(("💧", f"Độ ẩm {humidity}% — cảm giác ngột ngạt"))

    if not tips:
        tips.append(("✅", "Thời tiết đẹp — thích hợp ra ngoài!"))

    return tips[:3]  # Tối đa 3 lời khuyên


def fetch_weather() -> dict:
    """Gọi Open-Meteo API và trả về dict thời tiết."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":  LAT,
        "longitude": LON,
        "current": [
            "temperature_2m", "apparent_temperature",
            "precipitation", "weather_code",
            "wind_speed_10m", "relative_humidity_2m",
        ],
        "daily": [
            "weather_code",
            "temperature_2m_max", "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum",
        ],
        "timezone":       TZ,
        "forecast_days":  1,
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        d = r.json()

        cur   = d["current"]
        daily = d["daily"]

        code     = cur["weather_code"]
        temp     = round(cur["temperature_2m"])
        feels    = round(cur["apparent_temperature"])
        humidity = round(cur["relative_humidity_2m"])
        wind     = round(cur["wind_speed_10m"])

        temp_max  = round(daily["temperature_2m_max"][0])
        temp_min  = round(daily["temperature_2m_min"][0])
        rain_prob = int(daily["precipitation_probability_max"][0] or 0)
        rain_mm   = round(daily["precipitation_sum"][0] or 0, 1)

        emoji, desc = _weather_info(code)
        tips = _advice(temp, feels, rain_prob, humidity, wind)

        return {
            "ok":       True,
            "city":     CITY,
            "temp":     temp,
            "feels":    feels,
            "temp_max": temp_max,
            "temp_min": temp_min,
            "humidity": humidity,
            "wind":     wind,
            "desc":     desc,
            "emoji":    emoji,
            "rain_prob": rain_prob,
            "rain_mm":  rain_mm,
            "will_rain": rain_prob >= 50,
            "tips":     tips,
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}


if __name__ == "__main__":
    w = fetch_weather()
    if w["ok"]:
        print(f"{w['emoji']} {w['city']}: {w['temp']}°C (cảm giác {w['feels']}°C)")
        print(f"Cao: {w['temp_max']}°C / Thấp: {w['temp_min']}°C")
        print(f"Mưa: {w['rain_prob']}% | Độ ẩm: {w['humidity']}% | Gió: {w['wind']} km/h")
        print("Lời khuyên:")
        for icon, tip in w["tips"]:
            print(f"  {icon} {tip}")
    else:
        print(f"❌ Lỗi: {w['error']}")
