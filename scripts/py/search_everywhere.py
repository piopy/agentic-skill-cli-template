#!/usr/bin/env python3
"""
search_everywhere.py — Scansiona destinazioni economiche SENZA destinazione né
data precisa. Fonte: Google Flights Explore (viaggi 1 settimana, prossimi 6 mesi).

Usage:
  uv run --directory scripts/py search_everywhere.py --from BLQ
  uv run --directory scripts/py search_everywhere.py --from BLQ --month 2026-09 --max 15 --adults 2
"""

import argparse
import json
import re
import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SELENIUM_URL = "http://localhost:4444/wd/hub"
COOKIE_BTNS = [
    "//button[contains(., 'Accept all')]",
    "//button[contains(., 'Accetta tutto')]",
    "//button[contains(., 'I agree')]",
    "//button[contains(., 'Accetto')]",
    "//button[.//span[contains(text(),'Accept all')]]",
    "//button[.//span[contains(text(),'Accetta')]]",
    "//div[contains(@role,'dialog')]//a[contains(.,'Rifiuta')]",
]

MONTHS_IT = {
    "gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
    "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12,
}


def _accept_cookies(driver):
    for xpath in COOKIE_BTNS:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            btn.click()
            time.sleep(2)
            return True
        except Exception:
            continue
    return False


def _handle_consent_page(driver):
    try:
        current = driver.current_url
    except Exception:
        return False
    if "consent.google.com" not in current:
        return False
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
        )
        btn.click()
        time.sleep(3)
        return True
    except Exception:
        pass
    return False


def _get_driver():
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Remote(command_executor=SELENIUM_URL, options=options)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": (
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
                "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});"
            )
        })
    except Exception:
        pass
    return driver


def _parse_explore(body: str, month: str | None) -> list[dict]:
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    rows = []
    for i, line in enumerate(lines):
        m = re.match(r"^(?:da\s*)?([€]\s?\d+|\d+\s?€)$", line, re.IGNORECASE)
        if not m:
            continue
        ctx = lines[max(0, i - 5):i]
        ctx = [l for l in ctx if l]
        dest = next((l for l in reversed(ctx) if not _is_metadata(l)), None)
        when = next((l for l in reversed(ctx) if re.search(r'\b(gen|feb|mar|apr|mag|giu|lug|ago|set|ott|nov|dic)\b', l, re.I) and "–" in l), None)
        stop = next((l for l in reversed(ctx) if re.search(r'(dirett\w*|scal\w*)', l, re.I)), None)
        durations = [l for l in ctx if re.match(r'^\d+\s?h\s?\d+\s?min$', l)]
        duration = durations[0] if durations else None

        if month:
            y, mm = month.split("-")
            mm_int = int(mm)
            when_ok = any(MONTHS_IT.get(k) == mm_int for k in MONTHS_IT if when and k in when.lower())
            if not when_ok:
                continue

        price = re.sub(r"\s", "", m.group(1))
        rows.append({
            "dest": dest or "?",
            "price": price,
            "when": when or "",
            "stop": stop or "",
            "duration": duration or "",
            "to": price.replace("€", "").replace(" ", ""),
        })
    return rows


def _is_metadata(line: str) -> bool:
    if line.startswith("Da ") or line.startswith("Dettagli"):
        return True
    if re.match(r"^\d+", line):
        return True
    return False


def last_stops(rows: list[dict]) -> list[dict]:
    seen = []
    for r in rows:
        if r["dest"] not in [s["dest"] for s in seen]:
            seen.append(r)
    return seen


def search_explore(origin: str, month: str | None, max_items: int) -> dict:
    url = (f"https://www.google.com/travel/explore?q=flights+from+{origin.lower()}"
           f"+to+anywhere&hl=it&curr=EUR")
    result = {"destinations": [], "note": None, "scraped_url": url}

    driver = None
    try:
        driver = _get_driver()
        wait = WebDriverWait(driver, 20)
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        if _handle_consent_page(driver):
            time.sleep(5)
        _accept_cookies(driver)
        time.sleep(10)
        body = driver.find_element(By.TAG_NAME, "body").text
    except Exception as e:
        result["note"] = f"Selenium fallito: {e}"
        return result
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

    rows = _parse_explore(body, month)
    rows = last_stops(rows)
    rows.sort(key=lambda r: r["to"])
    result["destinations"] = rows[:max_items]
    if not rows:
        result["note"] = ("Google Flights Explore ha caricato ma parsing vuoto. "
                          "Apri il link e usa il filtro 'Esplora destinazioni'.")
    return result


def main():
    parser = argparse.ArgumentParser(description="Scansione voli senza destinazione/data (Google Flights Explore)")
    parser.add_argument("--from", dest="origin", required=True, help="Aeroporto o città partenza (es. BLQ)")
    parser.add_argument("--month", default="", help="Filtra mese (YYYY-MM)")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--max", type=int, default=15)
    args = parser.parse_args()

    month = args.month or None
    oym = ""
    if month:
        oym = month.replace("-", "")
    link = f"https://www.skyscanner.it/trasporti/voli-da/{args.origin.lower()}/?oym={oym}"
    explore_url = (f"https://www.google.com/travel/explore?q=flights+from+{args.origin.lower()}"
                   f"+to+anywhere&hl=it&curr=EUR")

    print(f"Carico Google Flights Explore: voli da {args.origin.upper()} → ovunque...", file=sys.stderr)
    resp = search_explore(args.origin, month, args.max)
    dests = resp["destinations"]

    result = {
        "command": "everywhere",
        "origin": args.origin.upper(),
        "month": args.month or "prossimi 6 mesi",
        "adults": args.adults,
        "source": "links",
        "data": dests,
        "primary_link": link,
        "links": {
            "skyscanner": link,
            "skyscanner_all": "https://www.skyscanner.it/trasporti/voli-da/" + args.origin.lower() + "/",
            "google_flights_explore": explore_url,
            "google_flights": "https://www.google.com/travel/flights?q=" + args.origin.lower() + "+anywhere",
        },
        "note": None,
    }
    if resp.get("note"):
        result["note"] = resp["note"]
    elif dests:
        result["source"] = "selenium"
        result["search_tip"] = (f"Destinazioni più economiche da {args.origin.upper()}. "
                                f"Dettagli volo: apri Skyscanner: {link}")
    else:
        result["note"] = "Nessun prezzo estratto. Websearch cross-reference consigliata."

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()