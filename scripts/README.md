# `scripts/` — Tool deterministici

## Cosa va qui
Codice eseguibile (`.mjs`, `.py`) per operazioni che **non vanno lasciate all'LLM**
perché devono essere esatte e ripetibili.

## Quando scrivere uno script invece di prosa
- **Deterministico** — stesso input, stesso output, sempre (API calls, parsing).
- **Strutturale** — manipolazione di file, dati, formati (JSON, CSV, PDF).
- **Ripetuto** — dedup, normalizzazione, sincronizzazione di uno stato.

## Tool disponibili

### Python (`scripts/py/`)
Tutti gli script Python vanno eseguiti con `uv run --directory scripts/py/ <script>`.

| Script | Cosa fa | Esempio |
|--------|---------|---------|
| `search_poi.py` | POI, attrazioni, cibo via Wikipedia API | `--city "Barcelona" --type attractions` |
| `search_weather.py` | Previsioni meteo via Open-Meteo (free) | `--city "Barcelona" --days 5` |
| `geocode.py` | Geocoding via OpenStreetMap Nominatim | `--q "Sagrada Familia"` |
| `route_distance.py` | Distanze e tempi tra POI via OSRM | `--from "41.38,2.16" --to "41.40,2.17" --profile foot` |
| `generate_links.py` | Link di ricerca voli/treni/alloggi | `--type flights --from BLQ --to BCN --date 2026-10-02` |
| **`search_browser.py`** | **Ricerca reale via Selenium + Chrome** (voli, hotel) | `flights --from BLQ --to BCN --date 2026-10-02` |
| **`search_multi.py`** | **Confronto rotte (diretta/inversa) + skiplagging** | `--from BLQ --cities BCN,VLC --date 2026-10-02 --returndate 2026-10-05` |
| `chrome_driver.py` | Avvia/ferma Chrome in Docker | `start` / `stop` / `status` |

### Uso combinato consigliato
```bash
# 1. Avvia Chrome
uv run --directory scripts/py chrome_driver.py start

# 2. Cerca voli reali
uv run --directory scripts/py search_browser.py flights --from BLQ --to BCN --date 2026-10-02

# 3. Cerca hotel reali
uv run --directory scripts/py search_browser.py hotels --city Barcelona --checkin 2026-10-02 --checkout 2026-10-04

# 4. Cerca POI
uv run --directory scripts/py search_poi.py --city Barcelona --type all

# 5. Ferma Chrome
uv run --directory scripts/py chrome_driver.py stop
```

### Node.js (`scripts/`)
| Comando | Script | Cosa fa |
|---------|--------|---------|
| `node scripts/validate.mjs` | `scripts/validate.mjs` | Valida dati di input |
| `node scripts/generate-report.mjs` | `scripts/generate-report.mjs` | Genera report markdown da JSON |

## Convenzioni
- Output **JSON su stdout** per essere parsabile dall'agente.
- Errori chiari e codici di uscita sensati.
- Un compito per script; niente effetti collaterali nascosti.
