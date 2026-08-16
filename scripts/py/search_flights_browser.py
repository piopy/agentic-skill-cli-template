#!/usr/bin/env python3
"""
search_flights_browser.py — Cerca voli reali via browser (Selenium + Chrome in Docker).
Usa Skyscanner e Google Flights come fonti.

Usage:
  uv run scripts/py/search_flights_browser.py --from BLQ --to BCN --date 2026-10-02
  uv run scripts/py/search_flights_browser.py --from BLQ --to VLC --date 2026-10-05 --adults 2
  uv run scripts/py/search_flights_browser.py --from BLQ --to BCN --date 2026-10-02 --dry-run
"""

import argparse
import json
import sys
import os
import time
import urllib.parse
from datetime import datetime

SELENIUM_URL = "http://localhost:4444/wd/hub"


def try_selenium_search(origin: str, dest: str, date: str, adults: int) -> list[dict] | None:
    """Prova a ottenere dati volo via Selenium + Chrome."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, WebDriverException
    except ImportError:
        return None

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:
        driver = webdriver.Remote(
            command_executor=SELENIUM_URL,
            options=options,
        )
    except Exception:
        return None

    try:
        # Prova Google Flights
        date_fmt = date.replace("-", "")
        url = f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{dest}+on+{date_fmt}"
        driver.get(url)
        time.sleep(5)

        flights = []
        cards = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
        for card in cards[:10]:
            try:
                text = card.text.strip()
                if not text or "Prezzo" not in text:
                    continue
                flights.append({"raw": text[:500]})
            except Exception:
                continue

        driver.quit()
        return flights if flights else None

    except Exception:
        driver.quit()
        return None


def build_links(origin: str, dest: str, date: str, adults: int) -> dict:
    """Genera link di ricerca come fallback."""
    date_compact = date.replace("-", "")
    return {
        "skyscanner": (
            f"https://www.skyscanner.it/trasporto/voli/{origin.lower()}/{dest.lower()}/"
            f"{date_compact}/?adultsv2={adults}"
        ),
        "google_flights": (
            f"https://www.google.com/travel/flights?q={origin}+{dest}+{date}+{adults}+adults"
        ),
        "ryanair": (
            f"https://www.ryanair.com/it/it/booking/home?"
            f"originIata={origin.upper()}&destinationIata={dest.upper()}"
            f"&dateOut={date}&adults={adults}"
        ),
        "vueling": f"https://www.vueling.com/it/voli-da-{origin.lower()}-a-{dest.lower()}",
    }


def main():
    parser = argparse.ArgumentParser(description="Ricerca voli via browser")
    parser.add_argument("--from", required=True, dest="origin", help="Codice aeroporto partenza")
    parser.add_argument("--to", required=True, dest="dest", help="Codice aeroporto arrivo")
    parser.add_argument("--date", required=True, help="Data (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2, help="Numero adulti")
    parser.add_argument("--dry-run", action="store_true", help="Solo link, niente browser")
    args = parser.parse_args()

    result = {
        "route": f"{args.origin.upper()} → {args.dest.upper()}",
        "date": args.date,
        "adults": args.adults,
        "links": build_links(args.origin, args.dest, args.date, args.adults),
        "flights": None,
        "source": "links",
    }

    if not args.dry_run:
        flights = try_selenium_search(args.origin, args.dest, args.date, args.adults)
        if flights:
            result["flights"] = flights
            result["source"] = "selenium"
        else:
            result["note"] = "Browser non disponibile o timeout. Usa i link per cercare."

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
