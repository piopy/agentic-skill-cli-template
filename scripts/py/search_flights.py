#!/usr/bin/env python3
"""
search_flights.py — Ricerca ibrida voli.

Due layer:
  1. Data layer (open): OpenFlights (dataset rotte) per l'ESISTENZA reale
     di una rotta diretta origin→dest. Dataset scaricato e cachato in .cache.
  2. Price layer (scraping): Google Flights via Selenium per il range di
     prezzo realistico. Se Selenium non disponibile, restano le rotte
     (confidence=estimated) + link di ricerca.

Confidence:
  - confirmed → rotta esiste (OpenFlights) + prezzo reale scraped
  - estimated → rotta esiste (OpenFlights), prezzo sconosciuto (forniamo link)
  - link-only → nessun dato, solo link di ricerca manuale

Usage:
  uv run --directory scripts/py search_flights.py --from BLQ --to BCN --date 2026-10-02
  uv run --directory scripts/py search_flights.py --from BLQ --to BCN --date 2026-10-02 --no-browser
  uv run --directory scripts/py search_flights.py --from BLQ --to BCN --date 2026-10-02 --adults 2 --max 10
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OPENFLIGHTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
CACHE_DIR = Path(__file__).parent / ".cache"
ROUTES_FILE = CACHE_DIR / "openflights_routes.dat"
USER_AGENT = "travel-planner/1.0 (AI-travel-agent)"
CACHE_MAX_DAYS = 30


def load_routes() -> set[tuple[str, str]]:
    """Rotta diretta diretta → set di (origin, dest). Scarica+cacha se serve."""
    CACHE_DIR.mkdir(exist_ok=True)
    fresh = False
    if ROUTES_FILE.exists():
        age = datetime.now().timestamp() - ROUTES_FILE.stat().st_mtime
        fresh = age < CACHE_MAX_DAYS * 86400
    if not fresh:
        try:
            req = urllib.request.Request(OPENFLIGHTS_URL, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                ROUTES_FILE.write_bytes(resp.read())
        except Exception as e:
            if not ROUTES_FILE.exists():
                raise RuntimeError(f"Impossibile scaricare OpenFlights: {e}")
    routes = set()
    with ROUTES_FILE.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 8:
                continue
            src, dst, stops = row[2].strip(), row[4].strip(), row[7].strip()
            if len(src) == 3 and len(dst) == 3 and stops == "0":
                routes.add((src.upper(), dst.upper()))
    return routes


def scrape_prices(origin: str, dest: str, date: str, adults: int) -> list[dict]:
    """Scraping Google Flights via Selenium. Ritorna [{price, airline, ...}] o []."""
    try:
        from search_browser import search_flights_selenium
    except ImportError:
        return []
    resp = search_flights_selenium(origin, dest, date, adults)
    flights = resp.get("flights", []) or []
    if resp.get("note"):
        return [{"note": resp["note"]}]
    return flights


def extract_price(s: str) -> int | None:
    m = re.search(r"€\s*(\d{1,6})", s or "")
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,6}(?:[.,]\d{3})?)\s*€", s or "")
    if m:
        return int(m.group(1).replace(".", "").replace(",", ""))
    return None


def fallback_links(origin: str, dest: str, date: str, adults: int) -> dict:
    try:
        from search_browser import gen_flight_links
    except ImportError:
        return {}
    return gen_flight_links(origin, dest, date, adults)


def main():
    parser = argparse.ArgumentParser(description="Ricerca ibrida voli (OpenFlights + prezzo)")
    parser.add_argument("--from", required=True, dest="origin", help="Aeroporto partenza (IATA)")
    parser.add_argument("--to", required=True, dest="dest", help="Aeroporto arrivo (IATA)")
    parser.add_argument("--date", required=True, help="Data (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--max", type=int, default=10)
    parser.add_argument("--no-browser", action="store_true",
                        help="Salta scraping prezzi (solo layer OpenFlights)")
    args = parser.parse_args()

    origin, dest = args.origin.upper(), args.dest.upper()
    fetched_at = datetime.now(timezone.utc)

    route_exists = False
    try:
        routes = load_routes()
        route_exists = (origin, dest) in routes
        routes_note = f"dataset OpenFlights ({len(routes):,} rotte dirette)"
    except RuntimeError as e:
        routes_note = f"OpenFlights non disponibile: {e}"
        route_exists = False

    flights = []
    has_browser = False
    if not args.no_browser:
        flights = scrape_prices(origin, dest, args.date, args.adults)
        has_browser = True

    prices = [extract_price(f.get("price", "")) for f in flights if "price" in f]
    prices = [p for p in prices if p]

    if prices:
        confidence = "confirmed"
    elif route_exists:
        confidence = "estimated"
    else:
        confidence = "link-only"

    links = fallback_links(origin, dest, args.date, args.adults)

    out = {
        "route": f"{origin} → {dest}",
        "date": args.date,
        "adults": args.adults,
        "fetched_at": fetched_at.isoformat(),
        "open_layer": {"route_exists": route_exists, "note": routes_note},
        "price_layer": "browser" if has_browser else "none",
        "confidence": confidence,
        "price_range": {
            "min": min(prices), "max": max(prices),
        } if prices else None,
        "flights": [{
            "price": f.get("price"),
            "airline": f.get("airline"),
            "time_from": f.get("time_from"),
            "time_to": f.get("time_to"),
        } for f in flights if "price" in f][:args.max],
        "note": None,
        "links": links,
    }

    if confidence == "link-only":
        out["note"] = "Nessun dato: rotta non nel dataset OpenFlights e nessun prezzo scraped. Verifica manualmente con i link."
    elif confidence == "estimated" and not prices:
        out["note"] = "Rotta diretta confermata dal dataset OpenFlights, ma prezzo non disponibile. Usa i link."
    elif not route_exists and prices:
        out["note"] = "Prezzi scraped confermati (aggregatore), rotta non nel dataset OpenFlights."

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
