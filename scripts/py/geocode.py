#!/usr/bin/env python3
"""
geocode.py — Geocoding e ricerca luoghi via Nominatim (OpenStreetMap).
Output JSON su stdout.

Usage:
  uv run scripts/py/geocode.py --q "Barcelona Sants station"
  uv run scripts/py/geocode.py --q "Sagrada Familia, Barcelona" --limit 5
  uv run scripts/py/geocode.py --lat 41.3874 --lon 2.1686  # reverse geocode
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse


NOMINATIM = "https://nominatim.openstreetmap.org"
USER_AGENT = "travel-planner/1.0 (AIravel-agent)"


def nominatim_request(params: dict) -> dict:
    params["format"] = "json"
    url = f"{NOMINATIM}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def reverse_geocode(lat: float, lon: float) -> dict:
    params = {"lat": lat, "lon": lon, "format": "json"}
    url = f"{NOMINATIM}/reverse?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Geocoding via OpenStreetMap")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--q", help="Testo da geocodificare")
    group.add_argument("--lat", type=float, help="Latitudine (reverse geocode)")
    parser.add_argument("--lon", type=float, help="Longitudine (reverse geocode)")
    parser.add_argument("--limit", type=int, default=5, help="Max risultati")
    args = parser.parse_args()

    if args.lat is not None and args.lon is not None:
        result = reverse_geocode(args.lat, args.lon)
        print(json.dumps({
            "query": f"{args.lat},{args.lon}",
            "result": result,
        }, ensure_ascii=False, indent=2))
    elif args.q:
        data = nominatim_request({"q": args.q, "limit": args.limit})
        results = []
        for item in data:
            results.append({
                "name": item.get("display_name", ""),
                "lat": item.get("lat"),
                "lon": item.get("lon"),
                "type": item.get("type"),
                "category": item.get("class"),
                "osm_id": item.get("osm_id"),
            })
        print(json.dumps({
            "query": args.q,
            "results": results,
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "Specifica --q o --lat/--lon"}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
