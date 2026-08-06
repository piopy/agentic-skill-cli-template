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

## search_hotels.py — Ricerca ibrida hotel (Overpass OSM + prezzo browser)

Due layer: **OpenStreetMap (Overpass)** per l'esistenza reale degli hotel
(nome, coordinate, stelle, sito), incrociato con **Booking.com (Selenium)**
per il range di prezzo reale. Dedup per coordinate (<60m) e match fuzzy dei nomi.

**Disponibilità garantita**: lo scraping delle card Booking conserva l'URL
completo con `matching_block_id`/`sr_pri_blocks` — il blocco tariffa che Booking
genera SOLO per le date/adulti richiesti. Le card senza prezzo o senza blocco
tariffa (sold-out per quelle date) vengono escluse automaticamente. Le card
mostrano prezzi simbolici "€1" per strutture non disponibili → escluse
(filtro <€10).

```bash
# Layer completo (OSM + prezzi)
uv run --directory scripts/py search_hotels.py \
  --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04 --adults 2

# Solo layer OSM (nessun browser)
uv run --directory scripts/py search_hotels.py --city "Budapest" --no-browser
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--city` | sì | Città da geocodificare |
| `--checkin` / `--checkout` | sì* | Date (serve per i prezzi) |
| `--adults` | no (default 2) | Numero adulti |
| `--max` | no (default 25) | Max hotel in output |
| `--no-browser` | no | Salta scraping prezzi |
| `--cluster-dist` | no (default 60) | Distanza dedup in metri |
| `--match-threshold` | no (default 0.5) | Soglia match fuzzy nomi |

\* Se mancano, si esegue solo il layer OSM.

**Output:** `stats` (osm_raw, osm_after_dedup, confirmed, estimated), `hotels[]`
con `confidence` (`confirmed`=prezzo Booking verificato per le date,
`estimated`=solo OSM), `price_range` (totale soggiorno, non per notte),
`url` (link Booking con blocco tariffa, o sito OSM).

---

## search_flights.py — Ricerca ibrida voli (OpenFlights + prezzo browser)

Due layer: **OpenFlights** (dataset rotte, cachato in `.cache/`) per l'esistenza
della rotta diretta, incrociato con **Google Flights (Selenium)** per il range
di prezzo. Fallback a link se il browser non è disponibile.

```bash
# Layer completo (rotta + prezzi)
uv run --directory scripts/py search_flights.py \
  --from BLQ --to BUD --date 2026-10-02 --adults 2

# Solo rotta (nessun browser)
uv run --directory scripts/py search_flights.py --from BLQ --to BUD --date 2026-10-02 --no-browser
```

| Argomento | Obbligatorio | Descrizione |
|-----------|-------------|-------------|
| `--from` | sì | Aeroporto partenza (IATA) |
| `--to` | sì | Aeroporto arrivo (IATA) |
| `--date` | sì | Data (YYYY-MM-DD) |
| `--adults` | no (default 2) | Numero adulti |
| `--max` | no (default 10) | Max voli in output |
| `--no-browser` | no | Salta scraping prezzi |

**Output:** `open_layer.route_exists` (rotta diretta nel dataset OpenFlights),
`confidence` (`confirmed`=rotta+prezzo, `estimated`=solo rotta, `link-only`=niente),
`price_range` (min/max), `flights[]`, `links`.

> Il dataset OpenFlights viene scaricato al primo uso e cachato in
> `scripts/py/.cache/` (30 giorni). La presenza nel dataset indica che la rotta
> è storicamente operata: non garantisce l'operatività in quella data.

---

## orchestrator.py — Entry-point unico

Dispatcher che chiama gli altri script (`search_poi`, `search_weather`,
`geocode`, `route_distance`, `search_hotels`, `search_flights`,
`generate_links`) tramite subprocess.

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

# Hotel ibridi
uv run --directory scripts/py orchestrator.py hotels \
  --city "Budapest" --checkin 2026-10-02 --checkout 2026-10-04

# Voli ibridi
uv run --directory scripts/py orchestrator.py flights \
  --from BLQ --to BUD --date 2026-10-02

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
| `hotels` | `search_hotels.py` |
| `flights` | `search_flights.py` |
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
