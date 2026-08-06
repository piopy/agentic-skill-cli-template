#!/usr/bin/env python3
"""
orchestrator.py — Punto d'ingresso unico per gli script Python.
In base al comando, richiama lo script corrispondente e restituisce JSON.

Usage:
  uv run scripts/py/orchestrator.py poi --city Barcelona
  uv run scripts/py/orchestrator.py weather --city Barcelona
  uv run scripts/py/orchestrator.py geocode --q "Sagrada Familia"
  uv run scripts/py/orchestrator.py links flights --from BLQ --to BCN --date 2026-10-02
  uv run scripts/py/orchestrator.py distance --from "41.3874,2.1686" --to "41.4036,2.1744"
  uv run scripts/py/orchestrator.py accommodations --city Barcelona --checkin 2026-10-02 --checkout 2026-10-04
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).parent


def run(script: str, *args: str, timeout: int = 60) -> dict:
    cmd = ["uv", "run", str(SCRIPTS_DIR / script)] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "command": " ".join(cmd)}
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}", "raw": result.stdout}
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout ({timeout}s)"}
    except Exception as e:
        return {"error": str(e)}


COMMANDS = {
    "poi": ("search_poi.py", ["--city", "--lang", "--type"]),
    "weather": ("search_weather.py", ["--city", "--lat", "--lon", "--days"]),
    "geocode": ("geocode.py", ["--q", "--lat", "--lon", "--limit"]),
    "distance": ("route_distance.py", ["--from", "--to", "--profile"]),
    "hotels": ("search_hotels.py", ["--city", "--checkin", "--checkout", "--adults", "--max", "--no-browser", "--cluster-dist", "--match-threshold"]),
    "flights": ("search_flights.py", ["--from", "--to", "--date", "--adults", "--max", "--no-browser"]),
    "links": ("generate_links.py", ["--type", "--from", "--to", "--date",
                                     "--return-date", "--city", "--checkin",
                                     "--checkout", "--adults", "--max-price", "--query"]),
}


def main():
    parser = argparse.ArgumentParser(description="Orchestrator script Python")
    parser.add_argument("command", choices=list(COMMANDS.keys()) + ["accommodations"],
                        help="Comando da eseguire")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Argomenti del comando")
    args = parser.parse_args()

    if args.command == "accommodations":
        result = run("generate_links.py", "--type", "accommodations", *args.args)
    else:
        script, _ = COMMANDS[args.command]
        result = run(script, *args.args)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
