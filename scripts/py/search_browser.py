#!/usr/bin/env python3
"""
search_browser.py — Motore di ricerca universale via browser (Selenium + Chrome).
Cerca voli, alloggi su Google Flights / Google Travel.
Fallback automatico a link generator se Selenium non disponibile.

Usage:
  uv run --directory scripts/py search_browser.py flights --from BLQ --to BCN --date 2026-10-02
  uv run --directory scripts/py search_browser.py hotels --city Barcelona --checkin 2026-10-02 --checkout 2026-10-04
  uv run --directory scripts/py search_browser.py trains --from Barcelona --to Valencia --date 2026-10-04
  uv run --directory scripts/py search_browser.py flights --from BLQ --to BCN --date 2026-10-02 --dry-run
"""

import argparse
import json
import sys
import time
import urllib.parse
import re

SELENIUM_URL = "http://localhost:4444/wd/hub"
COOKIE_BTNS = [
    "//button[.//span[contains(text(),'Accept all')]]",
    "//button[.//span[contains(text(),'Accetta')]]",
    "//button[.//span[contains(text(),'Accept')]]",
    "//div[contains(@aria-label,'Accept')]//button",
    "//button[contains(text(),'Accept all')]",
    "//button[contains(text(),'Accetta tutto')]",
    "//form//button[contains(text(),'Accetta')]",
]


def _accept_cookies(driver):
    from selenium.webdriver.common.by import By
    for xpath in COOKIE_BTNS:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            btn.click()
            time.sleep(2)
            return True
        except Exception:
            continue
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


# ─── Aeroporti vicini per confronto ────────────────────────────────────
# Per ogni città principale, elenca aeroporti alternativi raggiungibili
# via bus/treno (entro ~150km). La skill deve SEMPRE verificarli.
NEARBY_AIRPORTS = {
    "BCN": ["BCN", "GRO", "REU"],       # Barcellona → Girona (1h15 bus), Reus (1h30 bus)
    "MAD": ["MAD"],
    "VLC": ["VLC"],
    "AGP": ["AGP"],
    "PMI": ["PMI"],
    "IBZ": ["IBZ"],
    "FCO": ["FCO", "CIA"],              # Roma → Ciampino
    "MXP": ["MXP", "LIN", "BGY"],       # Milano → Linate, Bergamo
    "BLQ": ["BLQ", "VRN", "PSA"],       # Bologna → Verona (1h30 treno), Pisa (1h30 treno)
    "FLR": ["FLR", "BLQ", "PSA"],       # Firenze → Bologna, Pisa
    "NAP": ["NAP"],
    "VCE": ["VCE", "TSF"],              # Venezia → Treviso
}


def get_airport_alternatives(airport: str) -> list[str]:
    """Restituisce aeroporti alternativi per un dato aeroporto (incluso il primario)."""
    code = airport.upper().strip()
    return NEARBY_AIRPORTS.get(code, [code])


def gen_alt_airport_links(origin: str, dest_primary: str, date: str, adults: int = 2) -> list[dict]:
    """Genera link Skyscanner per tutte le combinazioni di aeroporti alternativi."""
    results = []
    alts = get_airport_alternatives(dest_primary.upper())
    for dest in alts:
        if dest == dest_primary.upper():
            continue
        link = FLIGHT_LINKS["skyscanner"].format(
            origin=origin.lower(), dest=dest.lower(),
            date_c=date, adults=adults,
        )
        results.append({"airport": dest, "type": "alternativo", "link": link})
    return results


# ─── Voli ───────────────────────────────────────────────────────────────

FLIGHT_LINKS = {
    "skyscanner": "https://www.skyscanner.it/trasporto/voli/{origin}/{dest}/{date_c}/?adultsv2={adults}",
    "google_flights": "https://www.google.com/travel/flights?q={origin}+{dest}+{date}",
    "ryanair": "https://www.ryanair.com/it/it/booking/home?originIata={origin_u}&destinationIata={dest_u}&dateOut={date}&adults={adults}",
    "vueling": "https://www.vueling.com/it/voli-da-{origin}-a-{dest}",
}

# Skyscanner ha i risultati più completi, Google Flights come fallback
FLIGHT_SOURCES = ["skyscanner", "google_flights"]


def search_google_with_retry(url: str, max_attempts: int = 2) -> tuple[str | None, bool]:
    """Carica Google Flights/Hotels, gestisce cookie, riprova se vuoto.
    Restituisce (page_text | None, had_error: bool)."""
    for attempt in range(max_attempts):
        driver = _get_driver()
        try:
            driver.get(url)
            time.sleep(5)
            _accept_cookies(driver)
            time.sleep(5)
            body = driver.find_element("tag name", "body").text

            # Se la pagina dice esplicitamente "no results"
            no_results = any(p in body for p in [
                "No results returned", "Nessun risultato", "0 results"
            ])
            if no_results and attempt < max_attempts - 1:
                driver.quit()
                time.sleep(3)
                continue

            driver.quit()
            return body, no_results
        except Exception:
            driver.quit()
            if attempt < max_attempts - 1:
                time.sleep(3)
                continue
            return None, True
    return None, True


def search_flights_selenium(origin: str, dest: str, date: str, adults: int) -> dict:
    url = f"https://www.google.com/travel/flights?q={origin}+{dest}+{date}"
    body, no_results = search_google_with_retry(url)

    result = {
        "flights": [],
        "no_results": no_results,
        "note": None,
    }

    if body is None or no_results:
        if no_results:
            result["note"] = f"Google Flights non ha trovato voli per {origin}→{dest} il {date}. Potrebbe non esserci collegamento diretto in questa data."
        else:
            result["note"] = "Impossibile caricare Google Flights (Selenium non disponibile?)."
        return result

    flights = []
    lines = body.split("\n")
    AIRLINES = ["ryanair", "vueling", "iberia", "easyjet", "wizz", "air europa",
                 "british airways", "lufthansa", "air france", "klm", "swiss",
                 "tap", "itA Airways", "volotea", "norwegian", "transavia"]
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if "€" not in line and "$" not in line:
            continue
        # contesto più ampio (8 righe prima, 4 dopo) per catturare compagnia e orari
        context = lines[max(0, i - 8):i + 4]
        ctx_clean = [c.strip() for c in context if c.strip()]

        airline = None
        time_from = None
        time_to = None
        for ctx_line in ctx_clean:
            cl = ctx_line.lower()
            for a in AIRLINES:
                if a in cl:
                    airline = a.title()
                    break
            # cerca orari tipo "10:35" o "10:35 AM"
            import re as _re
            times = _re.findall(r'\d{1,2}:\d{2}\s*(?:AM|PM)?', ctx_line, _re.IGNORECASE)
            if len(times) >= 2:
                time_from = times[0]
                time_to = times[1]

        flights.append({
            "price": line,
            "airline": airline,
            "time_from": time_from,
            "time_to": time_to,
            "context": ctx_clean[:10],
            "raw": line[:200],
        })

    result["flights"] = flights[:15]
    if not flights:
        result["note"] = "Google Flights ha caricato ma non ho trovato prezzi nel testo. Prova a cercare direttamente sul sito della compagnia aerea."
    return result


def gen_flight_links(origin: str, dest: str, date: str, adults: int) -> dict:
    date_c = date.replace("-", "")
    links = {}
    for name, tmpl in FLIGHT_LINKS.items():
        links[name] = tmpl.format(
            origin=origin.lower(), dest=dest.lower(),
            origin_u=origin.upper(), dest_u=dest.upper(),
            date=date, date_c=date_c, adults=adults,
        )
    return links


# ─── Alloggi ────────────────────────────────────────────────────────────

HOTEL_LINKS = {
    "booking": "https://www.booking.com/searchresults.it.html?ss={city_q}&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms=1&order=price&nflt=review_score%3D80%3Bfc%3D1%3Bpri%3D1",
    "airbnb": "https://www.airbnb.it/s/{city_q}/homes?checkin={checkin}&checkout={checkout}&adults={adults}",
    "google_hotels": "https://www.google.com/travel/search?q=hotels+in+{city_q}&checkIn={checkin}&checkOut={checkout}&adults={adults}",
}


def search_hotels_selenium(city: str, checkin: str, checkout: str, adults: int) -> dict:
    url = f"https://www.google.com/travel/search?q=hotels+in+{urllib.parse.quote(city)}"
    body, no_results = search_google_with_retry(url)

    result = {
        "hotels": [],
        "no_results": no_results,
        "note": None,
    }

    if body is None or no_results:
        if no_results:
            result["note"] = f"Google Hotels non ha trovato alloggi per {city}."
        else:
            result["note"] = "Impossibile caricare Google Hotels (Selenium non disponibile?)."
        return result

    hotels = []
    lines = body.split("\n")
    seen = set()
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if "€" not in line and "$" not in line:
            continue
        # Deduplica per nome + prezzo
        key = line[:50]
        if key in seen:
            continue
        seen.add(key)
        context = lines[max(0, i - 3):i + 2]
        hotels.append({
            "price": line,
            "context": [c.strip() for c in context if c.strip()],
        })

    result["hotels"] = hotels[:20]
    if not hotels:
        result["note"] = "Google Hotels ha caricato ma non ho trovato prezzi. Usa i link Booking/Airbnb qui sotto."
    return result


def gen_hotel_links(city: str, checkin: str, checkout: str, adults: int) -> dict:
    links = {}
    city_q = urllib.parse.quote(city)
    for name, tmpl in HOTEL_LINKS.items():
        links[name] = tmpl.format(
            city_q=city_q, checkin=checkin,
            checkout=checkout, adults=adults,
        )
    return links


# ─── Treni ──────────────────────────────────────────────────────────────

TRAIN_LINKS = {
    "trainline": "https://www.thetrainline.com/it/ricerca?origin={from_c}&destination={to_c}&outwardDate={date}&passengers=2",
    "renfe": "https://www.renfe.com/es/es/viajes/tren/{from_c}/{to_c}/{date}",
    "rome2rio": "https://www.rome2rio.com/s/{from_c}/{to_c}",
}


def gen_train_links(from_city: str, to_city: str, date: str) -> dict:
    links = {}
    fc = urllib.parse.quote(from_city)
    tc = urllib.parse.quote(to_city)
    for name, tmpl in TRAIN_LINKS.items():
        links[name] = tmpl.format(from_c=fc, to_c=tc, date=date)
    return links


# ─── Orchestrator ───────────────────────────────────────────────────────

COMMANDS = {
    "flights": {"selenium": search_flights_selenium, "links": gen_flight_links},
    "hotels": {"selenium": search_hotels_selenium, "links": gen_hotel_links},
    "trains": {"selenium": None, "links": gen_train_links},
}


def main():
    parser = argparse.ArgumentParser(description="Ricerca viaggi via browser")
    parser.add_argument("command", choices=list(COMMANDS.keys()))
    parser.add_argument("--from", dest="from_city", default="")
    parser.add_argument("--to", dest="to_city", default="")
    parser.add_argument("--city", default="")
    parser.add_argument("--date", default="")
    parser.add_argument("--checkin", default="")
    parser.add_argument("--checkout", default="")
    parser.add_argument("--adults", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    result = {"command": args.command, "source": "links", "data": None, "links": {}, "note": None}

    if args.command == "flights" and args.from_city and args.to_city and args.date:
        result["links"] = cmd["links"](args.from_city, args.to_city, args.date, args.adults)
        result["route"] = f"{args.from_city.upper()} → {args.to_city.upper()}"
        result["date"] = args.date
        result["primary_link"] = list(result["links"].values())[0]
        result["search_tip"] = f"Apri Skyscanner: {result['primary_link']}"
        if not args.dry_run:
            resp = cmd["selenium"](args.from_city, args.to_city, args.date, args.adults)
            result["data"] = resp.get("flights", [])
            if resp.get("note"):
                result["note"] = resp["note"]
            if result["data"]:
                result["source"] = "selenium"
            if not result["data"]:
                result["note"] = (result.get("note") or "") + " Dati browser incompleti. Usa il link Skyscanner qui sopra."

    elif args.command == "hotels" and args.city and args.checkin and args.checkout:
        result["links"] = cmd["links"](args.city, args.checkin, args.checkout, args.adults)
        result["city"] = args.city
        result["checkin"] = args.checkin
        result["checkout"] = args.checkout
        if not args.dry_run:
            resp = cmd["selenium"](args.city, args.checkin, args.checkout, args.adults)
            result["data"] = resp.get("hotels", [])
            if resp.get("note"):
                result["note"] = resp["note"]
            if result["data"]:
                result["source"] = "selenium"

    elif args.command == "trains" and args.from_city and args.to_city and args.date:
        result["links"] = cmd["links"](args.from_city, args.to_city, args.date)
        result["route"] = f"{args.from_city} → {args.to_city}"
        result["date"] = args.date
        result["note"] = "Usa i link per verificare orari e prezzi treni."

    else:
        result["error"] = f"Argomenti insufficienti per {args.command}"

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
