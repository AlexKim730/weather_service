from __future__ import annotations

import base64
import io
import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from weather_hourly import WEATHER_CODES, fetch_today_hourly_weather


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
DEFAULT_LOCATION = "Seoul"


def fetch_location(query: str) -> dict:
    params = {
        "name": query,
        "count": 1,
        "language": "ko",
        "format": "json",
    }
    url = f"{GEOCODING_URL}?{urlencode(params)}"

    with urlopen(url, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Open-Meteo Geocoding API error: HTTP {response.status}")
        data = json.loads(response.read().decode("utf-8"))

    results = data.get("results") or []
    if not results:
        raise ValueError(f"'{query}' 위치를 찾을 수 없습니다.")
    return results[0]


def location_label(location: dict) -> str:
    parts = [
        location.get("name"),
        location.get("admin1"),
        location.get("country"),
    ]
    return ", ".join(part for part in parts if part)


def make_temperature_chart(data: dict) -> str:
    hourly = data["hourly"]
    times = [datetime.fromisoformat(time) for time in hourly["time"]]
    temperatures = hourly["temperature_2m"]
    unit = data.get("hourly_units", {}).get("temperature_2m", "C")

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    ax.plot(
        times,
        temperatures,
        marker="o",
        markersize=5,
        linewidth=2.5,
        color="#2563eb",
    )
    ax.fill_between(times, temperatures, min(temperatures), color="#dbeafe", alpha=0.75)
    ax.set_title("Today's Hourly Temperature", pad=14)
    ax.set_xlabel("Time")
    ax.set_ylabel(f"Temperature ({unit})")
    ax.grid(True, linestyle="--", linewidth=0.8, alpha=0.35)
    ax.set_xticks(times[::2])
    ax.set_xticklabels([time.strftime("%H:%M") for time in times[::2]])
    ax.margins(x=0.02, y=0.18)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def build_weather_payload(query: str) -> dict:
    location = fetch_location(query)
    timezone = location.get("timezone") or "auto"
    weather_data = fetch_today_hourly_weather(
        location["latitude"],
        location["longitude"],
        timezone,
    )
    hourly = weather_data["hourly"]
    temperatures = hourly["temperature_2m"]
    chart = make_temperature_chart(weather_data)

    hours = []
    for index, time in enumerate(hourly["time"]):
        weather_code = hourly["weather_code"][index]
        hours.append(
            {
                "time": datetime.fromisoformat(time).strftime("%H:%M"),
                "weather": WEATHER_CODES.get(weather_code, f"알 수 없음({weather_code})"),
                "temperature": hourly["temperature_2m"][index],
                "humidity": hourly["relative_humidity_2m"][index],
                "precipitation_probability": hourly["precipitation_probability"][index],
                "precipitation": hourly["precipitation"][index],
                "wind_speed": hourly["wind_speed_10m"][index],
            }
        )

    return {
        "location": location_label(location),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": timezone,
        "current_temperature": temperatures[0],
        "min_temperature": min(temperatures),
        "max_temperature": max(temperatures),
        "chart": f"data:image/png;base64,{chart}",
        "hours": hours,
    }
