#!/usr/bin/env python3
"""
search_weather.py — Previsioni meteo per una città via Open-Meteo API
(free, no API key needed).

Usage:
  uv run scripts/py/search_weather.py --city "Barcelona"
  uv run scripts/py/search_weather.py --lat 41.3874 --lon 2.1686 --days 7
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse


GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "travel-planner/1.0 (AI-travel-agent)"


def geocode_city(city: str) -> dict | None:
    params = {"name": city, "count": 3, "language": "it"}
    url = f"{GEO_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    results = data.get("results", [])
    if results:
        r = results[0]
        return {"name": r.get("name"), "lat": r["latitude"], "lon": r["longitude"],
                "country": r.get("country")}
    return None


def get_weather(lat: float, lon: float, days: int = 7) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,wind_speed_10m_max",
        "timezone": "Europe/Madrid",
        "forecast_days": min(days, 16),
    }
    url = f"{WEATHER_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


WEATHER_CODES = {
    0: "Sereno", 1: "Prevalentemente sereno", 2: "Parzialmente nuvoloso",
    3: "Coperto", 45: "Nebbia", 48: "Nebbia con ghiaccio",
    51: "Pioggia leggera", 53: "Pioggia moderata", 55: "Pioggia intensa",
    61: "Pioggia leggera", 63: "Pioggia moderata", 65: "Pioggia intensa",
    71: "Neve leggera", 73: "Neve moderata", 75: "Neve intensa",
    80: "Rovesci leggeri", 81: "Rovesci moderati", 82: "Rovesci intensi",
    95: "Temporale", 96: "Temporale con grandine", 99: "Temporale con grandine intensa",
}


def main():
    parser = argparse.ArgumentParser(description="Previsioni meteo")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--city", help="Nome città")
    group.add_argument("--lat", type=float, help="Latitudine")
    parser.add_argument("--lon", type=float, help="Longitudine")
    parser.add_argument("--days", type=int, default=5, help="Giorni di previsione")
    args = parser.parse_args()

    if args.city:
        geo = geocode_city(args.city)
        if not geo:
            print(json.dumps({"error": f"Città '{args.city}' non trovata"}, indent=2))
            sys.exit(1)
        lat, lon = geo["lat"], geo["lon"]
        city_name = geo["name"]
        country = geo.get("country", "")
    elif args.lat is not None and args.lon is not None:
        lat, lon = args.lat, args.lon
        city_name = f"{lat},{lon}"
        country = ""
    else:
        print(json.dumps({"error": "Specifica --city o --lat/--lon"}, indent=2))
        sys.exit(1)

    data = get_weather(lat, lon, args.days)
    daily = data.get("daily", {})

    forecast = []
    for i in range(len(daily.get("time", []))):
        code = daily.get("weather_code", [0])[i]
        forecast.append({
            "date": daily["time"][i],
            "temp_max_c": daily["temperature_2m_max"][i],
            "temp_min_c": daily["temperature_2m_min"][i],
            "precip_mm": daily["precipitation_sum"][i],
            "condition": WEATHER_CODES.get(code, f"Codice {code}"),
            "wind_max_kmh": round(daily.get("wind_speed_10m_max", [0])[i], 1),
        })

    print(json.dumps({
        "city": city_name,
        "country": country,
        "latitude": lat,
        "longitude": lon,
        "forecast": forecast,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
