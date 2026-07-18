#!/usr/bin/env python3
"""
chrome_driver.py — Avvia/ferma Chrome in Docker per Selenium.
Fornisce un WebDriver remoto condiviso.

Usage:
  uv run scripts/py/chrome_driver.py start    # avvia container
  uv run scripts/py/chrome_driver.py status   # check se attivo
  uv run scripts/py/chrome_driver.py stop     # ferma container
"""

import json
import os
import subprocess
import sys
import time
import urllib.request

CONTAINER_NAME = "travel-planner-chrome"
SELENIUM_URL = "http://localhost:4444/wd/hub"


def docker_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args],
        capture_output=True, text=True, timeout=30000
    )


def start():
    r = docker_cmd("ps", "-q", "-f", f"name={CONTAINER_NAME}")
    if r.stdout.strip():
        print(json.dumps({"status": "already_running", "container": CONTAINER_NAME}))
        return

    r = docker_cmd("run", "-d",
                   "--name", CONTAINER_NAME,
                   "-p", "4444:4444",
                   "-p", "7900:7900",
                   "--shm-size", "2g",
                   "selenium/standalone-chrome:latest")
    if r.returncode != 0:
        print(json.dumps({"error": r.stderr.strip()}))
        sys.exit(1)

    # Attendi che Selenium sia pronto
    for i in range(30):
        try:
            resp = urllib.request.urlopen(f"{SELENIUM_URL}/status", timeout=5)
            if json.loads(resp.read()).get("value", {}).get("ready"):
                print(json.dumps({
                    "status": "started",
                    "container": CONTAINER_NAME,
                    "selenium_url": SELENIUM_URL,
                    "vnc_url": "http://localhost:7900",
                }))
                return
        except Exception:
            pass
        time.sleep(1)

    print(json.dumps({"error": "Timeout waiting for Selenium"}))
    sys.exit(1)


def status():
    r = docker_cmd("ps", "-f", f"name={CONTAINER_NAME}", "--format", "{{.Status}}")
    is_running = bool(r.stdout.strip())
    print(json.dumps({
        "running": is_running,
        "container": CONTAINER_NAME if is_running else None,
        "selenium_url": SELENIUM_URL if is_running else None,
    }))


def stop():
    docker_cmd("kill", CONTAINER_NAME)
    docker_cmd("rm", "-f", CONTAINER_NAME)
    print(json.dumps({"status": "stopped", "container": CONTAINER_NAME}))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: chrome_driver.py [start|stop|status]"}))
        sys.exit(1)

    cmd = sys.argv[1]
    {"start": start, "status": status, "stop": stop}.get(cmd, lambda: (
        print(json.dumps({"error": f"Comando sconosciuto: {cmd}"}))
    ))()


if __name__ == "__main__":
    main()
