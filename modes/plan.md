# Mode: plan — Pianificazione vacanza stile AI

Esegue il **flusso completo di pianificazione** intervistando l'utente passo
passo e producendo una guida markdown dettagliata.

## Obiettivo

Alla fine della sessione, l'utente deve avere un file in `output/`
con la guida di viaggio completa: giorno per giorno, mattina/pomeriggio/sera,
con link di Maps per ogni cosa.

## Flusso

### Step 0 — Carica contesto

Leggi `config/profile.yml` e `modes/_profile.md` per conoscere le preferenze.

### Step 1 — Raccolta requisiti (intervista, una domanda alla volta)

**REGOLA — Fai TUTTE le domande prima di proporre mete.**
Non proporre destinazioni finché non hai raccolto TUTTI i requisiti qui sotto.

1. **Città di partenza**: Da dove si parte? (es. città, aeroporto più vicino)
2. **Destinazione**: Dove si va? Una città, più città, una regione? (se non hai idee, chiedi stile prima e proponi dopo aver raccolto tutto)
3. **Date**: Giorni precisi o periodo flessibile? Quante notti/giorni?
4. **Persone**: Quanti siete? (l'utente decide per tutti)
5. **Budget indicativo**: Alto, medio, basso — o range specifico?
6. **Mezzo preferito**: Macchina disponibile? O solo mezzi pubblici?
7. **Stile**: Relax, culturale, natura, misto, cibo?

**REGOLA — Domanda "base fissa vs catena multi-città"**: dopo destinazione e
date, chiedi SEMPRE all'utente (una domanda, non una regola fissa):

> "Vuoi fare **avanti e indietro dalla città base** (un solo perno, gite
> giornaliere e rientro la sera) o **soggiornare anche in altre città**
> (catena multi-tappa con cambio alloggio)?"

In base alla risposta:
- **Base fissa** → applica i vincoli di distanza/tempo per le gite (rientro in
  giornata) e alloggio unico.
- **Catena multi-città** → applica il confronto multimodale (volo/treno/bus) su
  ogni tappa, il cambio alloggio e le 7 regole di arricchimento per ogni città.
- Se l'utente dice "flessibile"/"va bene anche altre città", proponi ENTRAMBE le
  opzioni con costi stimati e chiedi quale preferisce. Non decidere al suo posto.

### Step 2 — Trasporti (via script deterministici)

Prima di tutto, assicurati che Chrome Docker sia attivo (se non lo è):
```
uv run --directory scripts/py chrome_driver.py start
```

**REGOLA — Confronto rotte**: se ci sono più città, confronta SEMPRE la rotta
diretta (arrivo CittàA → partenza CittàB) con la rotta inversa (arrivo CittàB →
partenza CittàA). Usa `search_multi.py`:

```
uv run --directory scripts/py search_multi.py --from <ORIGINE> --cities <CITTA1,CITTA2> --date YYYY-MM-DD --returndate YYYY-MM-DD
```

Esempio: `uv run --directory scripts/py search_multi.py --from BLQ --cities BCN,VLC --date 2026-10-02 --returndate 2026-10-05`

Questo confronta automaticamente:
- **Diretta**: BLQ→BCN + VLC→BLQ
- **Inversa**: BLQ→VLC + BCN→BLQ

**REGOLA — Skiplagging (Hidden City Ticketing)**: verifica sempre se un volo
A→C con scalo a B costa meno del diretto A→B. Se sì, segnalalo all'utente come
"skiplagging candidato". Il fenomeno si chiama **skiplagging** o **hidden city ticketing**
e capita quando prenotare un volo con scalo è più economico del diretto
(es. BLQ→VLC via BCN costa meno di BLQ→BCN diretto — si prende il volo e
si scende a BCN senza imbarcare l'ultima tratta).

Lo script `search_multi.py` elenca già i candidati skiplagging. Per verificare
ciascuno, cerca il volo diretto A→C e controlla se passa per B:

```
uv run --directory scripts/py search_browser.py flights --from <A> --to <C> --date YYYY-MM-DD
```

**REGOLA — Scali**: non cercare solo voli diretti. Se il diretto è caro, cerca
anche voli con scalo (es. BLQ→BCN con scalo a Roma). Google Flights li mostra
automaticamente nei risultati.

**REGOLA — Aeroporti alternativi**: per OGNI città, verifica SEMPRE gli
aeroporti alternativi nelle vicinanze (entro ~150km / 2h via bus/treno).
Esempi:
- Barcellona → GRO (Girona), REU (Reus)
- Roma → CIA (Ciampino)
- Milano → LIN (Linate), BGY (Bergamo)
- Bologna → VRN (Verona), PSA (Pisa)
- Firenze → BLQ (Bologna), PSA (Pisa)

Cerca voli per TUTTI gli aeroporti alternativi e confronta prezzi:
```
uv run --directory scripts/py search_browser.py flights --from {ORIGINE} --to {ALTERNATIVO} --date YYYY-MM-DD
```

**REGOLA — Ritorno da città vicine**: non fermarti all'aeroporto di partenza
previsto. Verifica se volare dal ritorno da un aeroporto vicino (es. GRO→BLQ,
REU→BLQ invece di BCN→BLQ) è più economico, anche se serve un bus/treno
per arrivarci. Includi il costo dello spostamento nel confronto.

**REGOLA — Swap mete per città singola**: anche per una singola città,
confronta:
- Arrivare all'aeroporto principale vs alternativo
- Partire dall'aeroporto principale vs alternativo
- Combinazioni miste (arrivo BCN, partenza GRO)

Se ci sono differenze di prezzo significative (>€20/pers), segnale all'utente.

**REGOLA — Confronto multimodal (volo vs treno vs bus)**: per OGNI tratta
inter-città, e per i trasferimenti dentro/verso città vicine, NON limitarti a
un solo mezzo. Propono SEMPRE e confronta costo+tempi di:
- volo (solo per tratte lunghe),
- treno (regionale/statale),
- **bus a lunga percorrenza (Flixbus, Nettbuss, Vy-ekspress ecc.)**,
- bus/treno locale per l'aeroporto (es. aereo→centro).
Per i bus usa websearch/flixbus.com (manca uno script dedicato: `generate_links.py`
non ha tipo `bus`); per i treni usa `generate_links.py --type trains` o le fonti
di rotta. Includi SEMPRE i prezzi bus nel confronto, non solo treno/volo.

**REGOLA — Trasporto locale**: per ogni città, consiglia il mezzo più
economico e veloce per spostarsi.
- **Metro**: sempre preferibile per città grandi
- **A piedi**: per distanze <2km (<25 min) — indica i minuti
- **Bus/tram/treno**: alternativa se il metro non arriva
- **Taxi/Uber**: solo per necessità
- **Aeroporto→centro**: costo e durata di ogni opzione

Per distanze tra POI usa `route_distance.py --profile foot`.
Per Barcellona: T-casual 10 corse ~€11,35 (condivisibile). Aeroporto:
Aerobús €6,75 35min o metro L9 €5,15 25min.

**REGOLA — Skyscanner è il default per i voli**: genera SEMPRE link Skyscanner
come primo risultato per ogni ricerca voli. Se lo scraping via Selenium non
dà risultati o l'utente dice "non vedo tutti i voli", fornisci il link
Skyscanner diretto come alternativa principale.

**REGOLA — Cross-reference quando Selenium non dà risultati**: Google Flights
a volte non carica o dà "No results returned" per problemi di scraping.
In quel caso:
1. **Rilanciare** il comando `search_browser.py` una seconda volta (a volte funziona)
2. **Fornire subito il link Skyscanner**: l'utente lo apre e vede tutti i voli
3. **Websearch**: cerca su Google "voli {ORIGINE} {DESTINAZIONE} {DATA}" per vedere orari
4. **Chiedere all'utente**: "I dati via browser non sono stati caricati completamente. Ecco il link Skyscanner, vedi tutti i voli lì."
5. **Usare fonti alternative**: Ryanair.com, Skyscanner.it, eoob.it per la schedule
6. Se l'utente conferma un'opzione, salvala comunque

**REGOLA — Skiplagging (Hidden City Ticketing)**: verifica sempre se un volo
A→C con scalo a B costa meno del diretto A→B. Se sì, segnalalo all'utente.
```
uv run --directory scripts/py generate_links.py --type trains --from "<CITTA>" --to "<CITTA>" --date YYYY-MM-DD
```

**Verifica meteo** per le date del viaggio:
```
uv run --directory scripts/py search_weather.py --city "<CITTA>" --days <N>
```

Per ogni opzione: mostra i risultati JSON e i link. L'utente sceglie e conferma.
Salva orari, costi, link.

### Step 3 — Alloggio (via script deterministici)

**REGOLA — Valuta TUTTI i risultati con flusso Google Hotels → Booking (default 2026)**:
   Per ogni città usare SEMPRE `search_browser.py hotels` (Google Hotels, prezzi
   per notte, confronto OTA) con date e adulti esatti, poi **verificare su
   Booking** con `search_hotels.py`/`scrape_prices` per disponibilità REALE,
   prezzo totale per soggiorno e **cancellazione gratuita**. Google Hotels è più
   robusto contro i cambi layout di Booking (che cambia markup spesso). Non usare
   soltanto websearch/siti terzi: possono elencare strutture NON prenotabili.

1. Per ogni città/tappa: scoperta hotel su Google Hotels:
   ```
   uv run --directory scripts/py search_browser.py hotels --city "<CITTA>" --checkin YYYY-MM-DD --checkout YYYY-MM-DD --adults <N>
   ```
   (prezzi per notte; confronta anche su Booking/KAYAK mostrati da Google).

2. Verifica su Booking disponibilità+prezzo totale+cancellazione gratuita:
   ```
   uv run --directory scripts/py search_hotels.py --city "<CITTA>" --checkin YYYY-MM-DD --checkout YYYY-MM-DD --adults <N> --max <N>
   ```
   Se Overpass fallisce, chiama `scrape_prices(city, checkin, checkout, adults)` da `scripts/py/search_hotels.py`.

2. Estrai dall'output JSON completo TUTTI gli hotel con prezzo, nome e rating.
   Se un hotel appare sia nella sezione "sponsored" che in "view prices",
   mostra il prezzo più basso. Segnala sempre la **cancellazione gratuita**
   solo se verificata su Booking (Google Hotels può NON mostrar il dettaglio).

3. Per le distanze tra quartieri e punti d'interesse:
   ```
   uv run --directory scripts/py route_distance.py --from "LAT,LON" --to "LAT,LON" --profile foot
   ```

4. L'utente esplora, sceglie candidati e **incolla i link**.
5. Aiuta a decidere: confronta posizione, prezzo, recensioni (usa geocode.py).
6. Alla conferma: salva nome, indirizzo, link, date, costo.

### Step 4 — Attività e itinerari (via script deterministici)

**REGOLA — applica le 7 Regole di arricchimento itinerario di `_shared.md`**
(sequenza camminabile con orari/chiusure/prezzi/collegamenti/cibo sulla
rotta, non un semplice elenco di attrazioni).

1. **Ricerca POI e attrazioni** via Wikipedia API:
   ```
   uv run --directory scripts/py search_poi.py --city "<CITTA>" --type attractions --lang it
   ```

2. **Eventi**: usa websearch/webfetch per eventi/mostre/concerti.

3. **Cibo tipico locale**:
   ```
   uv run --directory scripts/py search_poi.py --city "<CITTA>" --type food --lang it
   ```

4. **Itinerario giornaliero**: costruisci percorso logico raggruppando POI vicini.
   - Usa `route_distance.py` per calcolare distanze a piedi tra POI
   - Usa `geocode.py` per trovare coordinate di un POI
   - Mattina: primo giro
   - Pomeriggio: proseguimento
   - Sera: cena + zona serale
   - Ogni tappa deve essere ragionevolmente raggiungibile dalla precedente
   - **L'ultima tappa della giornata deve essere l'alloggio**

5. Per ogni POI: fornisci link Google Maps.
6. L'utente approva o chiede modifiche.

### Step 5 — Cibo

1. Ricerca la cucina tipica locale.
2. Su Google Maps: trova locali con recensioni migliori per quei piatti.
3. Proponi 2-3 opzioni per pasto principale con link Maps.
4. Considera costo e posizione (vicino all'itinerario del giorno).
5. L'utente sceglie.

### Step 6 — Generazione report markdown

Esegui lo script per generare il report:
```
node scripts/generate-report.mjs
```
passando i dati raccolti. Il report viene salvato in `output/<vacanza>.md`.

Struttura del report:
```markdown
# 🏖️ <Nome vacanza> — <date>

## Info viaggio
- **Destinazione**: ...
- **Date**: ...
- **Persone**: ...
- **Budget**: ...

## 🚗 Trasporti
### Andata
- [Tipo] [Compagnia] — [link prenotazione]
- Orario: ... → ...
- Costo: ...

### Ritorno
- ...

### Spostamenti interni
- ...

## 🏨 Alloggi
### [Città] — [Date]
- [Nome] — [link Booking/Airbnb]
- Indirizzo: ...
- Costo totale: ...

## 📅 Itinerario

### Giorno 1 — [Data]
#### ☀️ Mattina
- [Attrazione] — [link Maps]
- [Attrazione] — [link Maps]

#### 🌤️ Pomeriggio
- ...

#### 🌙 Sera
- 🍽️ Cena da [Ristorante] — [link Maps]
- 🏠 Rientro all'alloggio ([link Maps])
- ...

### Giorno 2
...

## 🎟️ Eventi e biglietti
- [Evento] — [data] — [link biglietti]

## 💰 Budget riepilogativo
| Voce | Costo |
|------|-------|
| Trasporti | ... |
| Alloggi | ... |
| Cibo (stima) | ... |
| Attività/eventi | ... |
| **Totale** | **...** |

## 📌 Link utili
- [Skyscanner]
- [Booking]
- [Mappe personalizzate]
```

## Step 7 — Revisione

Mostra il report all'utente. Chiedi modifiche o conferma finale. Se modifiche,
itera sugli step interessati e rigenera.

## Step 8 — Cleanup

Se Chrome Docker è stato avviato, fermalo:
```
uv run --directory scripts/py chrome_driver.py stop
```
