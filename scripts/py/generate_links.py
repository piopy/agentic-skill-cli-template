#!/usr/bin/env python3
"""
generate_links.py — Genera link di ricerca per voli, treni, alloggi
con tutti i parametri pre-compilati. Output JSON.

Usage:
  uv run scripts/py/generate_links.py --type flights --from BLQ --to BCN --date 2026-10-02
  uv run scripts/py/generate_links.py --type trains --from "Barcelona" --to "Valencia" --date 2026-10-04
  uv run scripts/py/generate_links.py --type accommodations --city "Barcelona" --checkin 2026-10-02 --checkout 2026-10-04
  uv run scripts/py/generate_links.py --type all --from BLQ --to BCN --date 2026-10-02 --adults 2
"""

import argparse
import json
import urllib.parse


def build_skyscanner(origin: str, dest: str, date: str, adults: int = 2) -> str:
    date_compact = date.replace("-", "")
    return (f"https://www.skyscanner.it/trasporti/voli/{origin.lower()}/{dest.lower()}/"
            f"{date_compact}/?adultsv2={adults}")


def build_google_flights(origin: str, dest: str, date: str, return_date: str = "") -> str:
    q = f"{origin}+{dest}+{date}" + (f"+{return_date}" if return_date else "")
    return f"https://www.google.com/travel/flights?q={q}"


def build_ryanair(origin: str, dest: str, date: str, adults: int = 2) -> str:
    params = urllib.parse.urlencode({
        "originIata": origin.upper(),
        "destinationIata": dest.upper(),
        "dateOut": date,
        "adults": adults,
        "teens": 0, "children": 0, "infants": 0,
    })
    return f"https://www.ryanair.com/it/it/booking/home?{params}"


def build_vueling(origin: str, dest: str) -> str:
    return f"https://www.vueling.com/it/voli-da-{origin.lower()}-a-{dest.lower()}"


def build_trainline(origin: str, dest: str, date: str, passengers: int = 2) -> str:
    o = urllib.parse.quote(origin)
    d = urllib.parse.quote(dest)
    params = urllib.parse.urlencode({
        "origin": origin,
        "destination": dest,
        "outwardDate": date,
        "passengers": passengers,
    })
    return f"https://www.thetrainline.com/it/ricerca?{params}"


def build_renfe(origin: str, dest: str, date: str) -> str:
    o = urllib.parse.quote(origin)
    d = urllib.parse.quote(dest)
    return f"https://www.renfe.com/es/es/viajes/tren/{o}/{d}/{date}"


def build_booking(city: str, checkin: str, checkout: str, adults: int = 2,
                  min_rating: float = 4.0, free_cancel: bool = True) -> str:
    params = {
        "ss": f"{city}, Spagna",
        "checkin": checkin,
        "checkout": checkout,
        "group_adults": adults,
        "no_rooms": 1,
    }
    filters = []
    if min_rating:
        score_map = {4.0: "80", 4.5: "90"}
        filters.append(f"review_score%3D{score_map.get(min_rating, '80')}")
    if free_cancel:
        filters.append("fc%3D1")
    filters.append("pri%3D1")
    if filters:
        params["nflt"] = "%3B".join(filters)
    params["order"] = "price"
    return f"https://www.booking.com/searchresults.it.html?{urllib.parse.urlencode(params)}"


def build_airbnb(city: str, checkin: str, checkout: str, adults: int = 2,
                 max_price: int = 0) -> str:
    params = {
        "checkin": checkin,
        "checkout": checkout,
        "adults": adults,
    }
    if max_price:
        params["price_max"] = max_price
        params["price_min"] = 50
    c = urllib.parse.quote(f"{city}, Spagna")
    return f"https://www.airbnb.it/s/{c}/homes?{urllib.parse.urlencode(params)}"


def build_google_maps_search(query: str) -> str:
    return f"https://www.google.com/maps/search/{urllib.parse.quote(query)}"


def build_rome2rio(origin: str, dest: str) -> str:
    return f"https://www.rome2rio.com/s/{urllib.parse.quote(origin)}/{urllib.parse.quote(dest)}"


FLIGHT_PROVIDERS = {
    "skyscanner": build_skyscanner,
    "google_flights": build_google_flights,
    "ryanair": build_ryanair,
    "vueling": build_vueling,
}

TRAIN_PROVIDERS = {
    "trainline": build_trainline,
    "renfe": build_renfe,
}

ACCOMMODATION_PROVIDERS = {
    "booking": build_booking,
    "airbnb": build_airbnb,
}


def main():
    parser = argparse.ArgumentParser(description="Generatore link di viaggio")
    parser.add_argument("--type", required=True,
                        choices=["flights", "trains", "accommodations", "all", "maps"])
    parser.add_argument("--from", dest="origin", help="Origine (codice aeroporto o città)")
    parser.add_argument("--to", dest="dest", help="Destinazione")
    parser.add_argument("--date", help="Data partenza (YYYY-MM-DD)")
    parser.add_argument("--return-date", help="Data ritorno (YYYY-MM-DD)")
    parser.add_argument("--city", help="Città per alloggi")
    parser.add_argument("--checkin", help="Check-in (YYYY-MM-DD)")
    parser.add_argument("--checkout", help="Check-out (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2, help="Numero adulti")
    parser.add_argument("--max-price", type=int, default=0, help="Prezzo max alloggio")
    parser.add_argument("--query", help="Query per Maps search")
    args = parser.parse_args()

    result = {"type": args.type, "links": {}}

    if args.type in ("flights", "all") and args.origin and args.dest and args.date:
        for name, builder in FLIGHT_PROVIDERS.items():
            try:
                result["links"][name] = builder(args.origin, args.dest, args.date, args.adults)
            except Exception:
                pass
        if args.return_date:
            result["links"]["google_flights_roundtrip"] = build_google_flights(
                args.origin, args.dest, args.date, args.return_date)

    if args.type in ("trains", "all") and args.origin and args.dest and args.date:
        for name, builder in TRAIN_PROVIDERS.items():
            try:
                result["links"][name] = builder(args.origin, args.dest, args.date)
            except Exception:
                pass
        result["links"]["rome2rio"] = build_rome2rio(args.origin, args.dest)

    if args.type in ("accommodations", "all") and args.city and args.checkin and args.checkout:
        result["links"]["booking"] = build_booking(
            args.city, args.checkin, args.checkout, args.adults)
        result["links"]["airbnb"] = build_airbnb(
            args.city, args.checkin, args.checkout, args.adults, args.max_price)

    if args.type == "maps" and args.query:
        result["links"]["google_maps"] = build_google_maps_search(args.query)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
