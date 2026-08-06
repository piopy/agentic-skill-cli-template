#!/usr/bin/env python3
"""
search_poi.py — Cerca POI, attrazioni, eventi e info di viaggio
per una città usando Wikipedia/Wikivoyage API.

Usage:
  uv run scripts/py/search_poi.py --city "Barcelona"
  uv run scripts/py/search_poi.py --city "Valencia" --lang it
  uv run scripts/py/search_poi.py --city "Barcelona" --type attractions
  uv run scripts/py/search_poi.py --city "Barcelona" --type food
"""

import argparse
import json
import random
import sys
import time
import urllib.request
import urllib.parse


WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKIVOYAGE_API = "https://en.wikivoyage.org/w/api.php"
USER_AGENT = "travel-planner/1.0 (AI-travel-agent)"


def wiki_request(api_url: str, params: dict) -> dict:
    params["format"] = "json"
    url = f"{api_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def get_city_wikipedia_summary(city: str, lang: str = "it") -> dict:
    lang_map = {"it": "it", "en": "en", "es": "es"}
    api = f"https://{lang_map.get(lang, 'it')}.wikipedia.org/w/api.php"
    data = wiki_request(api, {
        "action": "query",
        "titles": city,
        "prop": "extracts|pageimages",
        "exintro": 1,
        "explaintext": 1,
        "pithumbsize": 400,
    })
    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id != "-1":
            return {
                "title": page.get("title"),
                "description": page.get("extract", "").strip()[:2000],
                "image": page.get("thumbnail", {}).get("source"),
                "page_url": f"https://{lang_map.get(lang, 'it')}.wikipedia.org/wiki/{urllib.parse.quote(page.get('title', '').replace(' ', '_'))}",
            }
    return {"title": city, "description": "", "image": None}


def get_attractions(city: str, lang: str = "en") -> list[dict]:
    category = f"Category:Tourist_attractions_in_{city}"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": 30,
    }
    data = wiki_request(WIKI_API, params)
    members = data.get("query", {}).get("categorymembers", [])
    results = []
    for m in members:
        results.append({
            "title": m["title"].replace("_", " "),
            "page_url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(m['title'].replace(' ', '_'))}",
        })
    return results


def get_wikivoyage_listing(city: str, section: str = "See") -> list[dict]:
    params = {
        "action": "parse",
        "page": city,
        "prop": "sections|text",
        "section": section,
    }
    data = wiki_request(WIKIVOYAGE_API, params)
    sections = data.get("parse", {}).get("sections", [])
    results = []
    for s in sections:
        if section.lower() in s.get("line", "").lower():
            sec_data = wiki_request(WIKIVOYAGE_API, {
                "action": "parse",
                "page": city,
                "prop": "text",
                "section": s["index"],
            })
            text = sec_data.get("parse", {}).get("text", {}).get("*", "")
            results.append({"section": s["line"], "content": text[:2000]})
    return results


def get_food_info(city: str, lang: str = "it") -> dict:
    terms = [f"cucina {city}", f"gastronomia {city}", f"{city} typical food"]
    results = {}
    for term in terms:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": term,
            "srlimit": 3,
        }
        data = wiki_request(
            f"https://{lang}.wikipedia.org/w/api.php" if lang != "en" else WIKI_API,
            params,
        )
        time.sleep(random.uniform(0.5, 1.5))
        items = []
        for r in data.get("query", {}).get("search", []):
            items.append({
                "title": r["title"],
                "snippet": r.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", ""),
            })
        if items:
            results[term] = items
    return results


def main():
    parser = argparse.ArgumentParser(description="Cerca POI e info città")
    parser.add_argument("--city", required=True, help="Nome città")
    parser.add_argument("--lang", default="it", help="Lingua (it/en/es)")
    parser.add_argument("--type", default="all",
                        choices=["all", "attractions", "food", "summary", "events"])
    args = parser.parse_args()

    time.sleep(random.uniform(1.5, 3.5))

    result = {"city": args.city, "lang": args.lang, "data": {}}

    if args.type in ("all", "summary"):
        result["data"]["summary"] = get_city_wikipedia_summary(args.city, args.lang)

    if args.type in ("all", "attractions"):
        attractions = get_attractions(args.city)
        result["data"]["attractions"] = attractions[:20]

    if args.type in ("all", "food"):
        result["data"]["food"] = get_food_info(args.city, args.lang)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
