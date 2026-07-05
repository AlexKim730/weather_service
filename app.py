from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".matplotlib-cache").resolve()))

from flask import Flask, jsonify, request, send_from_directory

from weather_service import DEFAULT_LOCATION, build_weather_payload


app = Flask(__name__, static_folder="public", static_url_path="")


@app.get("/")
def index():
    return send_from_directory("public", "index.html")


@app.get("/api/weather")
def weather():
    location = request.args.get("location", DEFAULT_LOCATION).strip()
    if not location:
        location = DEFAULT_LOCATION

    try:
        return jsonify(build_weather_payload(location)), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
