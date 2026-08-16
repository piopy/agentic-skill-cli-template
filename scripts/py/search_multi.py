#!/usr/bin/env python3
"""
search_multi.py — Confronta rotte multiple e cerca skiplagging.
Valuta routing diretto vs inverso, e verifica se esistono
voli con scalo più economici dello scalo stesso (skiplagging).

Usage:
  uv run --directory scripts/py search_multi.py --from BLQ --cities BCN,VLC --date 2026-10-02 --returndate 2026-10-05

Esempio skiplagging: se BLQ→BCN costa €91 ma BLQ→VLC con scalo a BCN costa €49,
conviene prendere il volo per VLC e scendere a BCN (skiplagging).
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
SELENIUM_URL = "http://localhost:4444/wd/hub"


def search_google_flights(origin: str, dest: str, date: str, return_date: str = "") -> list[dict]:
    """Cerca voli via Selenium e restituisce prezzi strutturati."""
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

        url = f"https://www.google.com/travel/flights?q={origin}+{dest}+{date}" + (f"+{return_date}" if return_date else "")
        driver.get(url)
        time.sleep(8)

        # Accept cookies
        for xpath in [
            "//button[.//span[contains(text(),'Accept all')]]",
            "//button[contains(text(),'Accetta tutto')]",
            "//button[.//span[contains(text(),'Accetta')]]",
        ]:
            try:
                driver.find_element(By.XPATH, xpath).click()
                time.sleep(2)
                break
            except Exception:
                pass

        time.sleep(4)
        body = driver.find_element(By.TAG_NAME, "body").text

        prices = []
        lines = body.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or "€" not in line or "from" in line.lower():
                continue
            # Cerca pattern "€XX" e contesto
            context = lines[max(0, i - 4):i + 2]
            prices.append({
                "price": line,
                "context": [c.strip() for c in context if c.strip()],
            })

        driver.quit()
        return prices[:10]
    except Exception as e:
        return [{"error": str(e)}]


def search_one_way(origin: str, dest: str, date: str, return_date: str = "") -> list[dict]:
    return search_google_flights(origin, dest, date, return_date)


def main():
    parser = argparse.ArgumentParser(description="Confronto rotte e skiplagging")
    parser.add_argument("--from", required=True, dest="origin", help="Aeroporto partenza")
    parser.add_argument("--cities", required=True, help="Città separate da virgola (es. BCN,VLC)")
    parser.add_argument("--date", required=True, help="Data partenza (YYYY-MM-DD)")
    parser.add_argument("--returndate", required=True, help="Data ritorno (YYYY-MM-DD)")
    parser.add_argument("--adults", type=int, default=2)
    args = parser.parse_args()

    cities = [c.strip().upper() for c in args.cities.split(",")]
    origin = args.origin.upper()
    result = {
        "origin": origin,
        "cities": cities,
        "date": args.date,
        "return_date": args.returndate,
        "adults": args.adults,
        "direct_routes": {},
        "reverse_routes": {},
        "skiplagging_candidates": [],
        "recommendation": None,
    }

    # 1. Rotta diretta: origin → City1, City2 → origin
    result["direct_routes"]["outbound"] = {
        "route": f"{origin} → {cities[0]}",
        "flights": search_one_way(origin, cities[0], args.date, args.returndate),
    }
    result["direct_routes"]["return"] = {
        "route": f"{cities[-1]} → {origin}",
        "flights": search_one_way(cities[-1], origin, args.returndate, args.date),
    }

    # 2. Rotta inversa: origin → City2, City1 → origin
    if len(cities) >= 2:
        result["reverse_routes"]["outbound"] = {
            "route": f"{origin} → {cities[-1]}",
            "flights": search_one_way(origin, cities[-1], args.date, args.returndate),
        }
        result["reverse_routes"]["return"] = {
            "route": f"{cities[0]} → {origin}",
            "flights": search_one_way(cities[0], origin, args.returndate, args.date),
        }

    # 3. Skiplagging: cercare A→C via B costa meno di A→B diretto
    # Se volo A→VLC con scalo a BCN costa < A→BCN, è skiplagging
    for city in cities[1:]:
        result["skiplagging_candidates"].append({
            "route": f"{origin} → {city} (via {cities[0]})",
            "note": f"Se BLQ→{city} via {cities[0]} costa meno di BLQ→{cities[0]}, si può skiplaggare a {cities[0]}",
        })

    # 4. Stima minima per confronto
    def extract_min_price(flights: list) -> int | None:
        for f in flights:
            if "price" not in f:
                continue
            p = f["price"]
            try:
                val = int(p.replace("€", "").replace(",", "").strip().split()[0])
                return val
            except (ValueError, AttributeError):
                continue
        return None

    direct_out = extract_min_price(result["direct_routes"]["outbound"]["flights"])
    direct_ret = extract_min_price(result["direct_routes"]["return"]["flights"])
    reverse_out = extract_min_price(result["reverse_routes"].get("outbound", {}).get("flights", []))
    reverse_ret = extract_min_price(result["reverse_routes"].get("return", {}).get("flights", []))

    if direct_out is not None and reverse_out is not None:
        if direct_out + reverse_ret < reverse_out + direct_ret:
            result["recommendation"] = f"Rotta diretta (arrivo {cities[0]}, partenza {cities[-1]})"
        elif reverse_ret is not None:
            result["recommendation"] = f"Rotta inversa (arrivo {cities[-1]}, partenza {cities[0]})"
        else:
            result["recommendation"] = "Confronta prezzi manualmente per decidere"

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
