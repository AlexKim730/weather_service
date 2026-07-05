from __future__ import annotations

import argparse
import json
from urllib.parse import urlencode
from urllib.request import urlopen


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    56: "약한 어는 이슬비",
    57: "강한 어는 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    66: "약한 어는 비",
    67: "강한 어는 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    77: "싸락눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    85: "약한 눈 소나기",
    86: "강한 눈 소나기",
    95: "뇌우",
    96: "약한 우박 동반 뇌우",
    99: "강한 우박 동반 뇌우",
}


def fetch_today_hourly_weather(
    latitude: float,
    longitude: float,
    timezone: str,
) -> dict:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": 1,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
    }
    url = f"{OPEN_METEO_URL}?{urlencode(params)}"

    with urlopen(url, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Open-Meteo API error: HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def print_hourly_weather(data: dict) -> None:
    hourly = data["hourly"]
    units = data.get("hourly_units", {})

    for i, time in enumerate(hourly["time"]):
        formatted_time = time.replace("T", " ")
        weather_code = hourly["weather_code"][i]
        weather = WEATHER_CODES.get(weather_code, f"알 수 없음({weather_code})")

        print(
            f"{formatted_time} | "
            f"{weather:<10} | "
            f"{hourly['temperature_2m'][i]:>5.1f}{units.get('temperature_2m', '')} | "
            f"습도 {hourly['relative_humidity_2m'][i]:>3}{units.get('relative_humidity_2m', '')} | "
            f"강수확률 {hourly['precipitation_probability'][i]:>3}{units.get('precipitation_probability', '')} | "
            f"강수량 {hourly['precipitation'][i]:>3.1f}{units.get('precipitation', '')} | "
            f"풍속 {hourly['wind_speed_10m'][i]:>4.1f}{units.get('wind_speed_10m', '')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch today's hourly weather forecast from Open-Meteo."
    )
    parser.add_argument("--lat", type=float, default=37.5665, help="Latitude")
    parser.add_argument("--lon", type=float, default=126.9780, help="Longitude")
    parser.add_argument(
        "--timezone",
        default="Asia/Seoul",
        help='Timezone, for example "Asia/Seoul" or "America/New_York"',
    )
    args = parser.parse_args()

    data = fetch_today_hourly_weather(args.lat, args.lon, args.timezone)
    print_hourly_weather(data)


if __name__ == "__main__":
    main()
