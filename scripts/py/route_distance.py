#!/usr/bin/env python3
"""
route_distance.py — Calcola distanze e tempi di percorrenza
tra punti di interesse via OSRM (Open Source Routing Machine).
Utile per costruire itinerari giornalieri coerenti.

Usage:
  uv run scripts/py/route_distance.py --from "41.3874,2.1686" --to "41.4036,2.1744"
  uv run scripts/py/route_distance.py --from "41.3874,2.1686" --to "41.4036,2.1744" --profile foot
  uv run scripts/py/route_distance.py --from "41.3874,2.1686" --to "41.4036,2.1744" --to "41.4145,2.1527"
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse


OSRM = "https://routing.openstreetmap.de"
USER_AGENT = "travel-planner/1.0 (AI-travel-agent)"
PROFILES = {"foot": "routed-foot", "bike": "routed-bike", "car": "routed-car"}


def osrm_route(coords: list[str], profile: str = "foot") -> dict:
    base = f"{OSRM}/{PROFILES.get(profile, 'routed-foot')}/route/v1/driving"
    coord_str = ";".join(c for c in coords)
    url = f"{base}/{coord_str}?overview=false&steps=true&alternatives=true"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="Calcolo distanze via OSRM")
    parser.add_argument("--from", required=True, dest="origin", help="Origine (lat,lon)")
    parser.add_argument("--to", required=True, action="append", dest="destinations",
                        help="Destinazione (lat,lon). Multipla per waypoints.")
    parser.add_argument("--profile", default="foot",
                        choices=["foot", "bike", "car"],
                        help="Profilo di percorrenza")
    args = parser.parse_args()

    # Converti lat,lon → lon,lat per OSRM
    def swap(coord: str) -> str:
        lat, lon = coord.strip().split(",")
        return f"{lon},{lat}"

    coords = [swap(args.origin)] + [swap(d) for d in args.destinations]
    coords_str = ";".join(coords)

    data = osrm_route(coords, args.profile)
    routes = data.get("routes", [])
    if not routes:
        print(json.dumps({"error": "Nessuna route trovata"}, indent=2))
        sys.exit(1)

    results = []
    for route in routes:
        legs = route.get("legs", [])
        leg_details = []
        for leg in legs:
            leg_details.append({
                "distance_m": leg.get("distance", 0),
                "distance_km": round(leg.get("distance", 0) / 1000, 2),
                "duration_s": leg.get("duration", 0),
                "duration_min": round(leg.get("duration", 0) / 60, 1),
                "summary": leg.get("summary", ""),
            })
        total_dist = sum(l["distance_m"] for l in leg_details)
        total_time = sum(l["duration_s"] for l in leg_details)
        results.append({
            "total_distance_km": round(total_dist / 1000, 2),
            "total_duration_min": round(total_time / 60, 1),
            "legs": leg_details,
            "waypoints": [args.origin] + args.destinations,
        })

    print(json.dumps({
        "profile": args.profile,
        "routes": results,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
