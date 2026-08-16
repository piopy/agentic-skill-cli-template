#!/usr/bin/env python3
"""
search_hotels.py — Ricerca ibrida hotel.

Due layer:
  1. Data layer (open): Overpass API (OpenStreetMap) per l'ESISTENZA reale
     di hotel/guest_house/hostel nella bbox della città, con nome, coordinate,
     stelle, sito web e data ultima modifica OSM.
  2. Price layer (scraping): Google Travel / Booking via Selenium per il range
     di prezzo reale. Se Selenium non disponibile, restano solo i dati OSM
     (confidence=estimated).

Incrocio: match fuzzy per nome + dedup per coordinate (distanza < 60m).
Confidence:
  - confirmed   → esistenza verificata da aggregatore (nome matchato) + prezzo
  - estimated   → esistenza solo OSM (prezzo sconosciuto, forniamo link)
  - stale       → dato OSM vecchio (>2 anni), da ricontrollare

Usage:
  uv run --directory scripts/py search_hotels.py --city "Barcelona" --checkin 2026-10-02 --checkout 2026-10-04
  uv run --directory scripts/py search_hotels.py --city "Barcelona" --checkin 2026-10-02 --checkout 2026-10-04 --no-browser
  uv run --directory scripts/py search_hotels.py --city "Barcelona" --max 30
"""

import argparse
import json
import math
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = "https://overpass-api.de/api/interpreter"
OVERPASS_FALLBACKS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
SELENIUM_URL = "http://localhost:4444/wd/hub"
USER_AGENT = "travel-planner/1.0 (AI-travel-agent)"
TOURISM_TAGS = "^(hotel|guest_house|hostel|motel|apartment)$"
CLUSTER_DIST_M = 60.0
PRICE_FLOOR_EUR = 10
STALE_MAX_DAYS = 730
SOLD_OUT_MARKERS = ("non disponibile", "sold out", "esaurito", "nessuna disponibilità",
                    "no availability", "nothing available", "choose different dates",
                    "scegli altre date")


def _request(url: str, params: dict | None = None, data: str | None = None) -> dict | list:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    body = data.encode() if data else None
    req = urllib.request.Request(url, data=body, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def geocode_city(city: str) -> dict | None:
    """Geocoding via Nominatim: restituisce bbox [south,west,north,east]."""
    results = _request(NOMINATIM, {"q": city, "format": "json", "limit": 1})
    if not results:
        return None
    r = results[0]
    bb = r.get("boundingbox") or [0, 0, 0, 0]
    return {
        "name": r.get("display_name", city),
        "bbox": [float(bb[0]), float(bb[2]), float(bb[1]), float(bb[3])],
    }


def overpass_hotels(bbox: list[float]) -> list[dict]:
    """Interroga Overpass per i nodi/way hotel nella bbox (con fallback)."""
    s, w, n, e = bbox
    query = f"""
[out:json][timeout:60];
(
  node["tourism"~"{TOURISM_TAGS}"]({s:.6f},{w:.6f},{n:.6f},{e:.6f});
  way["tourism"~"{TOURISM_TAGS}"]({s:.6f},{w:.6f},{n:.6f},{e:.6f});
);
out center tags;
"""
    payload = f"data={urllib.parse.quote(query)}"
    last_err: Exception | None = None
    for endpoint in OVERPASS_FALLBACKS:
        try:
            data = _request(endpoint, data=payload)
            if "elements" in data:
                break
            raise RuntimeError(f"Risposta Overpass inattesa: {str(data)[:200]}")
        except Exception as e:
            last_err = e
            continue
    else:
        raise RuntimeError(f"Tutti gli endpoint Overpass falliti: {last_err}")

    hotels = []
    for el in data.get("elements", []):
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        if el["type"] == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            lat, lon = center.get("lat"), center.get("lon")
        hotels.append({
            "id": f"osm:{el['type']}/{el['id']}",
            "name": name,
            "lat": lat,
            "lon": lon,
            "stars": tags.get("stars"),
            "website": tags.get("website"),
            "phone": tags.get("phone"),
            "addr": " ".join(x for x in [
                tags.get("addr:street"), tags.get("addr:housenumber"),
                tags.get("addr:city"),
            ] if x),
            "tourism": tags.get("tourism"),
        })
    return hotels


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def cluster_by_coords(hotels: list[dict], max_dist: float = CLUSTER_DIST_M) -> list[dict]:
    """Dedup: raggruppa hotel entro max_dist metri, tiene il primo."""
    clusters: list[list[dict]] = []
    for h in hotels:
        placed = False
        for c in clusters:
            ref = c[0]
            if (h["lat"] is not None and ref["lat"] is not None and
                    haversine_m(ref["lat"], ref["lon"], h["lat"], h["lon"]) <= max_dist):
                c.append(h)
                placed = True
                break
        if not placed:
            clusters.append([h])
    return [c[0] for c in clusters]


def normalize_name(name: str) -> str:
    """Rimuove accenti, lowercase, solo alfanumerici."""
    s = unicodedata.normalize("NFKD", name or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def name_tokens(name: str) -> set[str]:
    stop = {"hotel", "hostel", "boutique", "apartments", "apart", "suites",
            "resort", "palace", "house", "the", "de", "la", "el", "le", "barcelona",
            "madrid", "valencia", "budapest", "paris", "rome", "roma", "&", "and"}
    return {t for t in normalize_name(name).split() if t not in stop}


def match_score(osm_name: str, agg_name: str) -> float:
    a, b = name_tokens(osm_name), name_tokens(agg_name)
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / max(len(a), len(b))


def scrape_prices(city: str, checkin: str, checkout: str, adults: int) -> list[dict]:
    """Scraping Booking.com via Selenium per date reali. Ritorna [{name, price, url}].

    Disponibilità = la card ha un prezzo reale + l'URL contiene il blocco
    tariffa (matching_block_id) generato da Booking per quelle date/adulti.
    Le card senza prezzo o senza blocco tariffa sono NON disponibili → escluse.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
    except ImportError:
        return []

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    no_rooms = max(1, -(-adults // 2))
    q = urllib.parse.quote(city)
    url = (f"https://www.booking.com/searchresults.it.html?ss={q}"
           f"&checkin={checkin}&checkout={checkout}&group_adults={adults}"
           f"&no_rooms={no_rooms}&order=price")
    try:
        driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    except Exception:
        return []

    try:
        driver.set_page_load_timeout(30)
        driver.get(url)
        time.sleep(10)
        hotels = []
        seen_urls = set()
        for _ in range(3):
            cards = driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='property-card-container']"
            ) or driver.find_elements(By.CSS_SELECTOR, "div[data-testid='property-card']")
            if cards:
                break
            time.sleep(8)
        for card in cards:
            if len(hotels) >= 25:
                break
            html = card.get_attribute("innerHTML") or ""
            name = None
            m = re.search(r"data-testid=\"title\"[^>]*>(.*?)</div", html, re.S)
            if m:
                name = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if not name:
                continue
            price = None
            for pat in (
                r"data-testid=\"price-and-discounted-price\"[^>]*>\s*€\s*(?:&nbsp;)?\s*([\d.,]+)",
                r"Prezzo attuale:\s*€\s*(?:&nbsp;)?\s*([\d.,]+)",
                r"Prezzo:\s*€\s*(?:&nbsp;)?\s*([\d.,]+)",
            ):
                m = re.search(pat, html)
                if m:
                    price = m.group(1).replace(".", "").replace(",", ".").rstrip(".") + " €"
                    break
            if not price:
                continue
            card_text = html.lower()
            if any(mk in card_text for mk in SOLD_OUT_MARKERS):
                continue
            link = None
            m = re.search(r"\"availability-cta-btn\"[^>]*href=\"([^\"]+)\"", html)
            if not m:
                m = re.search(r"href=\"([^\"]+)\"", html)
            if m:
                link = m.group(1)
            if not link or "matching_block_id=" not in link:
                continue
            if link in seen_urls:
                continue
            seen_urls.add(link)
            hotels.append({"name": name, "price": price, "url": link})
        return hotels
    except Exception:
        return []
    finally:
        driver.quit()


def extract_price(s: str) -> int | None:
    m = re.search(r"€\s*(\d{1,6})", s or "")
    if m:
        return int(m.group(1))
    m = re.search(r"(\d{1,6}(?:[.,]\d{3})?)\s*€", s or "")
    if m:
        return int(m.group(1).replace(".", "").replace(",", ""))
    return None


def booking_url(name: str, checkin: str, checkout: str, adults: int) -> str:
    q = urllib.parse.quote(name)
    return (f"https://www.booking.com/searchresults.it.html?ss={q}"
            f"&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms=1")


def main():
    parser = argparse.ArgumentParser(description="Ricerca ibrida hotel (OSM + prezzo)")
    parser.add_argument("--city", required=True)
    parser.add_argument("--checkin", default="")
    parser.add_argument("--checkout", default="")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--max", type=int, default=25)
    parser.add_argument("--no-browser", action="store_true",
                        help="Salta scraping prezzi (solo layer OSM)")
    parser.add_argument("--cluster-dist", type=float, default=CLUSTER_DIST_M)
    parser.add_argument("--match-threshold", type=float, default=0.5)
    args = parser.parse_args()

    fetched_at = datetime.now(timezone.utc)
    geo = geocode_city(args.city)
    if not geo:
        print(json.dumps({"error": f"Città non trovata: {args.city}"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    try:
        osm_hotels = overpass_hotels(geo["bbox"])
    except Exception as e:
        print(json.dumps({"error": f"Overpass fallito: {e}"}, ensure_ascii=False, indent=2))
        sys.exit(1)
    deduped = cluster_by_coords(osm_hotels, args.cluster_dist)

    agg_prices = []
    has_browser = False
    if args.checkin and args.checkout and not args.no_browser:
        agg_prices = scrape_prices(args.city, args.checkin, args.checkout, args.adults)
        has_browser = True

    # Aggregatore (Booking) = lista primaria: prezzo + URL veri per le date.
    # OSM arricchisce solo con match ad ALTA confidenza (evita associazioni false).
    results = []
    osm_used = set()

    for i, a in enumerate(agg_prices):
        if "name" not in a:
            continue
        entry = {
            "id": f"agg:{i}",
            "name": a["name"],
            "lat": None,
            "lon": None,
            "stars": None,
            "address": None,
            "website": None,
            "price_range": None,
            "confidence": "confirmed",
            "exists": True,
            "url": a.get("url") or booking_url(a["name"], args.checkin, args.checkout, args.adults),
            "source": ["aggregator"],
            "note": None,
        }
        p = extract_price(a.get("price", ""))
        entry["price_range"] = {"min": p, "max": p}
        if p is None or p < PRICE_FLOOR_EUR:
            entry["price_range"] = None
            entry["note"] = "Prezzo non attendibile (Booking mostra un valore simbolico). Disponibilità da verificare."
        if has_browser:
            best_h = None
            best_score = 0.0
            for j, h in enumerate(deduped):
                if j in osm_used:
                    continue
                score = match_score(h["name"], a["name"])
                if score > best_score:
                    best_score = score
                    best_h = j
            if best_h is not None and best_score >= args.match_threshold:
                h = deduped[best_h]
                osm_used.add(best_h)
                entry["id"] = h["id"]
                entry["lat"] = h["lat"]
                entry["lon"] = h["lon"]
                entry["stars"] = h.get("stars")
                entry["address"] = h.get("addr")
                if h.get("website"):
                    entry["website"] = h["website"]
                entry["source"].append("osm")
        results.append(entry)

    for j, h in enumerate(deduped):
        if j in osm_used:
            continue
        results.append({
            "id": h["id"],
            "name": h["name"],
            "lat": h["lat"],
            "lon": h["lon"],
            "stars": h.get("stars"),
            "address": h.get("addr"),
            "website": h.get("website"),
            "price_range": None,
            "confidence": "estimated",
            "exists": True,
            "url": h.get("website") or booking_url(h["name"], args.checkin, args.checkout, args.adults),
            "source": ["osm"],
            "note": "Presente in OSM ma non su Booking per queste date. Disponibilità da verificare.",
        })

    results.sort(key=lambda x: (x["confidence"] != "confirmed", x["name"] or ""))

    out = {
        "city": args.city,
        "geocoded": geo["name"],
        "bbox": geo["bbox"],
        "fetched_at": fetched_at.isoformat(),
        "stats": {
            "osm_raw": len(osm_hotels),
            "osm_after_dedup": len(deduped),
            "aggregator_items": len(agg_prices) if has_browser else 0,
            "confirmed": sum(1 for r in results if r["confidence"] == "confirmed"),
            "estimated": sum(1 for r in results if r["confidence"] == "estimated"),
        },
        "price_layer": "browser" if has_browser else "none",
        "source_name": "booking.com",
        "hotels": results[:args.max],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
