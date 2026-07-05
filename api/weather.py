from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

from flask import Flask, jsonify, request

from weather_service import DEFAULT_LOCATION, build_weather_payload


app = Flask(__name__)


@app.get("/")
@app.get("/api/weather")
def weather() -> tuple:
    location = request.args.get("location", DEFAULT_LOCATION).strip()
    if not location:
        location = DEFAULT_LOCATION

    try:
        return jsonify(build_weather_payload(location)), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


handler = app
