from __future__ import annotations

import base64
import html
import io
import json
import os
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import urlopen

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib-cache").resolve()))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from weather_hourly import WEATHER_CODES, fetch_today_hourly_weather


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
DEFAULT_LOCATION = "Seoul"
HOST = "127.0.0.1"
PORT = 8000


def configure_matplotlib_font() -> None:
    font_path = Path("C:/Windows/Fonts/malgun.ttf")
    if font_path.exists():
        font_manager.fontManager.addfont(font_path)
        plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False


configure_matplotlib_font()


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


def parse_hourly_times(times: list[str]) -> list[datetime]:
    return [datetime.fromisoformat(time) for time in times]


def make_temperature_chart(data: dict, title: str) -> str:
    hourly = data["hourly"]
    times = parse_hourly_times(hourly["time"])
    temperatures = hourly["temperature_2m"]
    unit = data.get("hourly_units", {}).get("temperature_2m", "°C")

    fig, ax = plt.subplots(figsize=(11, 4.8))
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

    ax.set_title(title, pad=16)
    ax.set_xlabel("시간")
    ax.set_ylabel(f"기온 ({unit})")
    ax.grid(True, linestyle="--", linewidth=0.8, alpha=0.35)
    ax.set_xticks(times[::2])
    ax.set_xticklabels([time.strftime("%H:%M") for time in times[::2]], rotation=0)

    min_temp = min(temperatures)
    max_temp = max(temperatures)
    ax.scatter(
        [times[temperatures.index(min_temp)], times[temperatures.index(max_temp)]],
        [min_temp, max_temp],
        color="#dc2626",
        zorder=5,
    )
    ax.margins(x=0.02, y=0.18)
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def build_hourly_rows(data: dict) -> str:
    hourly = data["hourly"]
    rows = []

    for index, time in enumerate(hourly["time"]):
        weather_code = hourly["weather_code"][index]
        weather = WEATHER_CODES.get(weather_code, f"알 수 없음({weather_code})")
        display_time = datetime.fromisoformat(time).strftime("%H:%M")
        rows.append(
            "<tr>"
            f"<td>{display_time}</td>"
            f"<td>{html.escape(weather)}</td>"
            f"<td>{hourly['temperature_2m'][index]:.1f}°C</td>"
            f"<td>{hourly['relative_humidity_2m'][index]}%</td>"
            f"<td>{hourly['precipitation_probability'][index]}%</td>"
            f"<td>{hourly['precipitation'][index]:.1f}mm</td>"
            f"<td>{hourly['wind_speed_10m'][index]:.1f}km/h</td>"
            "</tr>"
        )

    return "\n".join(rows)


def render_page(query: str = DEFAULT_LOCATION, error: str | None = None) -> str:
    location = None
    weather_data = None
    chart_base64 = ""

    if error is None:
        try:
            location = fetch_location(query)
            timezone = location.get("timezone") or "auto"
            weather_data = fetch_today_hourly_weather(
                location["latitude"],
                location["longitude"],
                timezone,
            )
            chart_base64 = make_temperature_chart(
                weather_data,
                f"{location_label(location)} 오늘 시간별 기온",
            )
        except Exception as exc:
            error = str(exc)

    escaped_query = html.escape(query)
    location_name = html.escape(location_label(location)) if location else ""
    rows = build_hourly_rows(weather_data) if weather_data else ""
    current = weather_data["hourly"] if weather_data else {}
    first_weather = WEATHER_CODES.get(current.get("weather_code", [None])[0], "-") if weather_data else "-"
    first_temp = f"{current['temperature_2m'][0]:.1f}°C" if weather_data else "-"
    min_temp = f"{min(current['temperature_2m']):.1f}°C" if weather_data else "-"
    max_temp = f"{max(current['temperature_2m']):.1f}°C" if weather_data else "-"
    chart_html = (
        f'<img class="chart" src="data:image/png;base64,{chart_base64}" alt="오늘 시간별 기온 그래프">'
        if chart_base64
        else ""
    )
    error_html = f'<div class="notice">{html.escape(error)}</div>' if error else ""

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>오늘 날씨 검색</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Arial, "Malgun Gothic", sans-serif;
      --text: #172033;
      --muted: #667085;
      --line: #d9e2ec;
      --brand: #2563eb;
      --brand-dark: #1d4ed8;
      --surface: #ffffff;
      --bg: #f5f7fb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
    }}
    .topbar {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
    }}
    .wrap {{
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }}
    .topbar .wrap {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 72px;
      gap: 20px;
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
    }}
    form {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      max-width: 520px;
    }}
    input {{
      width: 100%;
      min-width: 0;
      height: 42px;
      border: 1px solid #c9d4e5;
      border-radius: 6px;
      padding: 0 12px;
      font-size: 15px;
      background: #ffffff;
    }}
    button {{
      height: 42px;
      border: 0;
      border-radius: 6px;
      padding: 0 16px;
      background: var(--brand);
      color: #ffffff;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }}
    button:hover {{ background: var(--brand-dark); }}
    main {{
      padding: 28px 0 40px;
    }}
    .notice {{
      margin-bottom: 18px;
      padding: 14px 16px;
      border: 1px solid #fecaca;
      border-radius: 6px;
      background: #fff1f2;
      color: #9f1239;
    }}
    .summary {{
      display: grid;
      grid-template-columns: minmax(220px, 1.5fr) repeat(3, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      line-height: 1.2;
    }}
    .metric.location strong {{
      font-size: 20px;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 18px;
    }}
    .panel-header {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      font-weight: 700;
    }}
    .chart {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .table-wrap {{
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 760px;
      font-size: 14px;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #edf1f7;
      text-align: left;
      white-space: nowrap;
    }}
    th {{
      background: #f8fafc;
      color: #475467;
      font-weight: 700;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    @media (max-width: 760px) {{
      .topbar .wrap {{
        align-items: stretch;
        flex-direction: column;
        padding: 16px 0;
      }}
      form {{
        max-width: none;
      }}
      .summary {{
        grid-template-columns: 1fr 1fr;
      }}
      .metric.location {{
        grid-column: 1 / -1;
      }}
    }}
    @media (max-width: 480px) {{
      .wrap {{
        width: min(100% - 20px, 1120px);
      }}
      form {{
        flex-direction: column;
      }}
      button {{
        width: 100%;
      }}
      .summary {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="wrap">
      <h1>오늘 날씨 검색</h1>
      <form method="get" action="/">
        <input name="location" value="{escaped_query}" placeholder="예: 서울, Busan, Tokyo" autocomplete="off">
        <button type="submit">검색</button>
      </form>
    </div>
  </header>
  <main class="wrap">
    {error_html}
    <section class="summary" aria-label="날씨 요약">
      <div class="metric location"><span>검색 위치</span><strong>{location_name or "-"}</strong></div>
      <div class="metric"><span>현재 기온</span><strong>{first_temp}</strong></div>
      <div class="metric"><span>오늘 최저</span><strong>{min_temp}</strong></div>
      <div class="metric"><span>오늘 최고</span><strong>{max_temp}</strong></div>
    </section>
    <section class="panel">
      <div class="panel-header">시간별 기온 그래프</div>
      {chart_html}
    </section>
    <section class="panel">
      <div class="panel-header">시간별 날씨</div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>시간</th>
              <th>날씨</th>
              <th>기온</th>
              <th>습도</th>
              <th>강수확률</th>
              <th>강수량</th>
              <th>풍속</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>"""


class WeatherHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return

        if parsed.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        query_params = parse_qs(parsed.query)
        location = query_params.get("location", [DEFAULT_LOCATION])[0].strip()
        if not location:
            location = DEFAULT_LOCATION

        body = render_page(location).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), WeatherHandler)
    print(f"Weather web app running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
