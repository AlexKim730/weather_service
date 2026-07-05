from __future__ import annotations

import argparse
import os
from datetime import datetime
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib-cache").resolve()))

import matplotlib.pyplot as plt

from weather_hourly import fetch_today_hourly_weather


def parse_hourly_times(times: list[str]) -> list[datetime]:
    return [datetime.fromisoformat(time) for time in times]


def save_temperature_plot(data: dict, output_path: Path) -> None:
    hourly = data["hourly"]
    times = parse_hourly_times(hourly["time"])
    temperatures = hourly["temperature_2m"]
    unit = data.get("hourly_units", {}).get("temperature_2m", "C")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        times,
        temperatures,
        marker="o",
        linewidth=2,
        color="#2563eb",
    )

    ax.set_title("Today's Hourly Temperature")
    ax.set_xlabel("Time")
    ax.set_ylabel(f"Temperature ({unit})")
    ax.grid(True, linestyle="--", alpha=0.35)

    ax.set_xticks(times[::2])
    ax.set_xticklabels([time.strftime("%H:%M") for time in times[::2]], rotation=45)

    min_temp = min(temperatures)
    max_temp = max(temperatures)
    ax.annotate(
        f"Min {min_temp:.1f}{unit}",
        xy=(times[temperatures.index(min_temp)], min_temp),
        xytext=(0, -28),
        textcoords="offset points",
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#0f172a"},
    )
    ax.annotate(
        f"Max {max_temp:.1f}{unit}",
        xy=(times[temperatures.index(max_temp)], max_temp),
        xytext=(0, 24),
        textcoords="offset points",
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#0f172a"},
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch today's Open-Meteo forecast and save a temperature chart."
    )
    parser.add_argument("--lat", type=float, default=37.5665, help="Latitude")
    parser.add_argument("--lon", type=float, default=126.9780, help="Longitude")
    parser.add_argument("--timezone", default="Asia/Seoul", help="Timezone")
    parser.add_argument(
        "--output",
        default="today_temperature.png",
        help="Output PNG path",
    )
    args = parser.parse_args()

    data = fetch_today_hourly_weather(args.lat, args.lon, args.timezone)
    output_path = Path(args.output)
    save_temperature_plot(data, output_path)
    print(f"Saved temperature chart to {output_path.resolve()}")


if __name__ == "__main__":
    main()
