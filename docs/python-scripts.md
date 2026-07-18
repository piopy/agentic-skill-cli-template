# Python Scripts — travel-planner

Tutti gli script si eseguono con `uv run --directory scripts/py <script> <args>` dalla root del progetto.

Prima di usare script che richiedono Selenium (voli, hotel), avviare Chrome:

```
uv run --directory scripts/py chrome_driver.py start
```

---

## chrome_driver.py — Gestione Chrome Docker

Avvia/ferma un container Docker con Chrome standalone per Selenium.

| Comando | Effetto |
|---------|---------|
| `start` | Avvia container `travel-planner-chrome` (se non già attivo) |
| `stop` | Ferma e rimuove il container |
| `status` | Mostra lo stato corrente |

**Esempi:**

```bash
# Avviare Chrome
uv run --directory scripts/py chrome_driver.py start

# Fermare Chrome
uv run --directory scripts/py chrome_driver.py stop

# Controllare stato
uv run --directory scripts/py chrome_driver.py status
```

**Output:** JSON con `status`, `container`, `selenium_url`, `vnc_url`.

---

## search_browser.py — Ricerca voli / hotel / treni via Selenium

Motore universale che carica Google Flights / Google Travel via browser e
restituisce i dati parsati. Fallback automatico a link generator se Selenium
non disponibile.

### Voli (`flights`)

```bash
# Ricerca volo andata
uv run --directory scripts/py search_browser.py flights \
  --from BLQ --to BUD --date 2026-10-02 --adults 2
```

**Output:** `data` array con `price`, `airline`, `time_from`, `time_to`, `context`.

### Hotel (`hotels`)

```bash
# Ricerca hotel per città con date
uv run --directory scripts/py search_browser.py hotels \
  --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04 --adults 2
```

**Output:** `data` array con `name`, `price`.

### Treni (`trains`)

```bash
# Genera link per treni
uv run --directory scripts/py search_browser.py trains \
  --from "Bologna" --to "Firenze" --date 2026-10-02
```

**Output:** solo link (nessuno scraping Selenium per treni).

### Dry-run (solo link, senza browser)

```bash
uv run --directory scripts/py search_browser.py flights \
  --from BLQ --to BUD --date 2026-10-02 --dry-run
```

---

## search_multi.py — Confronto rotte multiple + Skiplagging

Confronta rotta diretta e inversa per viaggi multi-città, e identifica
candidati allo skiplagging (hidden city ticketing).

```bash
# Confronta BLQ→BCN+VLC→BLQ vs BLQ→VLC+BCN→BLQ
uv run --directory scripts/py search_multi.py \
  --from BLQ --cities BCN,VLC --date 2026-10-02 --returndate 2026-10-05 --adults 2
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--from` | sì | Aeroporto partenza |
| `--cities` | sì | Città separate da virgola (es. `BCN,VLC`) |
| `--date` | sì | Data partenza |
| `--returndate` | sì | Data ritorno |
| `--adults` | no (default 2) | Numero adulti |

**Output:** JSON con `direct_routes`, `reverse_routes`, `skiplagging_candidates`,
`recommendation`.

---

## search_poi.py — Punti d'interesse, cibo, eventi (Wikipedia API)

Cerca attrazioni turistiche, informazioni culinarie e sommari via Wikipedia
e Wikivoyage API. Non richiede Selenium.

```bash
# Attrazioni turistiche
uv run --directory scripts/py search_poi.py --city "Budapest" --type attractions --lang it

# Cibo tipico
uv run --directory scripts/py search_poi.py --city "Budapest" --type food --lang it

# Sommario città (descrizione + immagine)
uv run --directory scripts/py search_poi.py --city "Budapest" --type summary --lang it

# Eventi
uv run --directory scripts/py search_poi.py --city "Budapest" --type events --lang it

# Tutto insieme
uv run --directory scripts/py search_poi.py --city "Budapest" --type all --lang it
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--city` | sì | Nome città |
| `--lang` | no (default `it`) | Lingua (`it`, `en`, `es`) |
| `--type` | no (default `all`) | Tipo: `all`, `attractions`, `food`, `summary`, `events` |

**Output:** JSON con `city`, `lang`, `data` (contiene `summary`, `attractions`, `food`).

---

## search_weather.py — Previsioni meteo (Open-Meteo)

Recupera previsioni meteo senza necessità di API key. Usa le coordinate
della città o coordinate esplicite.

```bash
# Per città (geocoding automatico)
uv run --directory scripts/py search_weather.py --city "Budapest" --days 3

# Per coordinate esplicite
uv run --directory scripts/py search_weather.py --lat 47.498 --lon 19.040 --days 5
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--city` | no* | Nome città |
| `--lat` / `--lon` | no* | Coordinate (in alternativa a `--city`) |
| `--days` | no (default 5) | Giorni di previsione (max 16) |

\* Specificare `--city` oppure `--lat` + `--lon`.

**Output:** JSON con `city`, `country`, `latitude`, `longitude`, `forecast[]`.
Ogni giorno: `temp_max_c`, `temp_min_c`, `precip_mm`, `condition`, `wind_max_kmh`.

---

## route_distance.py — Distanze e tempi tra POI (OSRM)

Calcola distanza e tempo di percorrenza tra punti di interesse usando
OpenStreetMap Routing Machine. Supporta profile pedonale, bici e auto.

```bash
# Distanza a piedi tra due punti
uv run --directory scripts/py route_distance.py \
  --from "47.498,19.040" --to "47.512,19.045" --profile foot

# Multi-tappa
uv run --directory scripts/py route_distance.py \
  --from "47.498,19.040" --to "47.512,19.045" --to "47.505,19.070" --profile foot
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--from` | sì | Origine `"lat,lon"` |
| `--to` | sì (ripetibile) | Destinazione/i `"lat,lon"` |
| `--profile` | no (default `foot`) | `foot`, `bike`, `car` |

**Output:** JSON con `profile`, `routes[]`. Ogni route: `total_distance_km`,
`total_duration_min`, `legs[]`.

---

## geocode.py — Geocoding (Nominatim / OpenStreetMap)

Geocoding diretto (da indirizzo/testo a coordinate) e inverso
(da coordinate a indirizzo).

```bash
# Da nome a coordinate
uv run --directory scripts/py geocode.py --q "Parlamento Budapest" --limit 3

# Da coordinate a nome
uv run --directory scripts/py geocode.py --lat 47.507 --lon 19.046
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--q` | no* | Testo da geocodificare |
| `--lat` / `--lon` | no* | Coordinate per reverse geocoding |
| `--limit` | no (default 5) | Max risultati (solo forward) |

\* Specificare `--q` (forward) oppure `--lat` + `--lon` (reverse).

**Output:** Forward: `results[]` con `name`, `lat`, `lon`, `type`, `category`.
Reverse: `result` con indirizzo e coordinate.

---

## generate_links.py — Generatore link di ricerca (nessuna richiesta HTTP)

Genera URL precompilati per voli, treni, alloggi e mappe. Non richiede
browser o API — pura costruzione di URL.

```bash
# Link voli
uv run --directory scripts/py generate_links.py \
  --type flights --from BLQ --to BUD --date 2026-10-02 --adults 2

# Link treni
uv run --directory scripts/py generate_links.py \
  --type trains --from "Bologna" --to "Firenze" --date 2026-10-02

# Link alloggi
uv run --directory scripts/py generate_links.py \
  --type accommodations --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04

# Tutti i link (voli + treni + alloggi)
uv run --directory scripts/py generate_links.py \
  --type all --from BLQ --to BUD --date 2026-10-02 \
  --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04

# Google Maps search
uv run --directory scripts/py generate_links.py \
  --type maps --query "Széchenyi Thermal Bath Budapest"
```

| Argomento | Per `--type` | Descrizione |
|-----------|-------------|-------------|
| `--type` | tutti | `flights`, `trains`, `accommodations`, `all`, `maps` |
| `--from` | flights, trains, all | Origine |
| `--to` | flights, trains, all | Destinazione |
| `--date` | flights, trains, all | Data partenza |
| `--return-date` | flights | Data ritorno (opzionale) |
| `--city` | accommodations, all | Città alloggio |
| `--checkin` / `--checkout` | accommodations, all | Date alloggio |
| `--adults` | flights, accommodations, all | Numero adulti |
| `--max-price` | accommodations | Prezzo max Airbnb |
| `--query` | maps | Testo per Maps search |

**Output:** JSON con `type` e `links` (mappa nome-proveditore → URL).

---

## orchestrator.py — Entry-point unico

Dispatcher che chiama gli altri script (`search_poi`, `search_weather`,
`geocode`, `route_distance`, `generate_links`) tramite subprocess.

```bash
# POI
uv run --directory scripts/py orchestrator.py poi --city "Budapest" --type attractions

# Meteo
uv run --directory scripts/py orchestrator.py weather --city "Budapest" --days 3

# Geocode
uv run --directory scripts/py orchestrator.py geocode --q "Parlamento Budapest"

# Distanza
uv run --directory scripts/py orchestrator.py distance \
  --from "47.498,19.040" --to "47.512,19.045"

# Link
uv run --directory scripts/py orchestrator.py links \
  --type flights --from BLQ --to BUD --date 2026-10-02

# Alloggi (chiama generate_links con --type accommodations)
uv run --directory scripts/py orchestrator.py accommodations \
  --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04
```

| Subcomando | Script chiamato |
|------------|----------------|
| `poi` | `search_poi.py` |
| `weather` | `search_weather.py` |
| `geocode` | `geocode.py` |
| `distance` | `route_distance.py` |
| `links` | `generate_links.py` |
| `accommodations` | `generate_links.py --type accommodations` |

**Output:** JSON dal child script, oppure `{"error": "..."}`.

---

## search_flights_browser.py — Ricerca voli (versione legacy)

Versione più semplice e meno robusta di `search_browser.py flights`.
Cerca solo voli via Google Flights con parsing base.

```bash
uv run --directory scripts/py search_flights_browser.py \
  --from BLQ --to BUD --date 2026-10-02 --adults 2
```

**Output:** JSON con `route`, `date`, `flights[]`, `links`, `source`.

> **Nota:** Preferire `search_browser.py flights` — è più completo, gestisce
> cookie consent e ha parsing migliorato.
