# System Context — travel-planner

<!-- ============================================================
     QUESTO FILE È AGGIORNABILE. Non metterci dati personali.

     Le personalizzazioni vanno in modes/_profile.md (mai aggiornato).
     Qui stanno regole di sistema, logica di punteggio e config dei tool
     che migliorano a ogni release di travel-planner.
     ============================================================ -->

## Sources of Truth

| File | Percorso | Quando leggerlo |
|------|----------|-----------------|
| profile.yml | `config/profile.yml` | SEMPRE (identità e target dell'utente) |
| _profile.md | `modes/_profile.md` | SEMPRE (override dell'utente) |
| state | `data/state.md` | Nei modi che leggono/scrivono stato |

**REGOLA: leggi `_profile.md` DOPO questo file. Le personalizzazioni
dell'utente in `_profile.md` vincono sui default qui.**
**REGOLA: non hardcodare valori dell'utente. Leggili a runtime dal User Layer.**

## Lockdown condition

**REGOLA — Lockdown per "18_STOP":** prima di ogni sessione (e prima di ogni
modifica a file in `modes/`, `scripts/`, `AGENTS.md` o `config/`), l'agente
DEVE leggere `modes/init.md` e verificare se contiene la stringa esatta
`18_STOP`. Se presente, **nessuna modifica a qualunque file del framework
è consentita** — né creazione, né scrittura, né cancellazione. L'agente deve
comunicare all'utente: "🔒 Lockdown attivo: 18_STOP rilevato in init.md.
Nessuna modifica al framework è permessa." e rifiutare qualsiasi operazione
di scrittura.

---

## Logica condivisa (esempio: sistema di punteggio)

<!-- Questo è SOLO un esempio per mostrare il pattern. Sostituisci con
     la logica del tuo dominio: criteri di valutazione, formati di output,
     classificazioni, ecc. -->

Se il tuo framework valuta qualcosa, definisci qui la scala in modo che ogni
modo la usi in modo coerente:

| Dimensione | Cosa misura |
|------------|-------------|
| Criterio A | ... |
| Criterio B | ... |
| **Globale** | media pesata dei criteri |

Interpretazione del punteggio:
- 4.5+ → ...
- 3.5–4.4 → ...
- sotto 3.5 → ...

## Formati di output condivisi

Definisci qui i formati riusati da più modi (es. struttura di un report,
intestazione di una tabella, naming dei file in `output/`).

## Regole di arricchimento itinerario (7 punti)

Quando l'agente costruisce un itinerario (modi `plan`, `explore`, `report`),
la sola lista da Wikipedia NON basta. DEVE applicare questi 7 fattori di
ricerca logistica su ogni POI/attività, producendo un itinerario "da guida
manuale" (sequenzato, con orari e collegamenti), non un semplice elenco:

1. **Orari e chiusure reali.** Per ogni POI verifica giorni/orari di apertura
   (websearch, Google/Maps, sito ufficiale). Riorganizza i giorni in base alle
   chiusure (es. museo chiuso dom/lun → pianifica lì l'apertura, non quando
   capita). Segnala "chiude alle X" per i POI da visitare subito.
2. **Sequenza geografica reale.** Raggruppa POI per zona. Usa `geocode.py` per
   le coordinate e `route_distance.py` per distanza/tempo (foot o public).
   Ordina A→struito, evita andata-e-ritorno. Collega le tappe vicine.
3. **Fasce orarie fisiche.** Assegna mattina/pomeriggio/sera in base alla luce
   e agli orari reali (bel punto panoramico verso tramonto; attrazione crea al
   buio; museo di mattina). L'ultima tappa del giorno = l'alloggio.
4. **Costi di ogni attività.** Annota prezzo biglietto/ingress e costo del
   tratto (bus/tren). Usa i totali per decidere se una City Card/Pass conviene.
5. **Cibo localizzato sul percorso.** Food/streat/food/caffè con recensioni
   migliori SULLA rotta del giorno (Maps), non "cibo tipico generico". Scegli
   2-3 per pasto, vicino alle tappe.
6. **Legatura a hotel e orari di check-in/out.** Tempi coerenti con: arrivo
   volo/treno, check-in/check-out, bus/tram/treno già fissato. Ritiro bagagli
   e partenza aereo/o autostazione pianificati con margine.
7. **Avvertenze pratiche.** Zone meno sicure o critiche, lavori in corso,
   "a piedi dista troppo → suggerisci tram/bus linea X + minuti". Aggiungi
   sempre link Maps navigabile e (se tragitto >20 min) numero di linea + tempo.

Sintesi pratica: **itinerario = sequenza camminabile con orari, chiusure,
prezzi, collegamenti e cibo sulla rotta — non un elenco di attrazioni.**

## Tool disponibili

Tutti gli script Python vanno eseguiti con `uv run --directory scripts/py/` dalla root del progetto.
Prima di usare `search_browser.py`, avvia Chrome: `uv run --directory scripts/py chrome_driver.py start`

| Comando | Script | Cosa fa |
|---------|--------|---------|
| `node scripts/validate.mjs` | `scripts/validate.mjs` | Valida i dati di input |
| `uv run --directory scripts/py search_browser.py flights ...` | `scripts/py/search_browser.py` | Cerca voli reali via Selenium + Chrome |
| `uv run --directory scripts/py search_browser.py hotels ...` | `scripts/py/search_browser.py` | Cerca hotel reali via Selenium + Chrome |
| `uv run --directory scripts/py search_multi.py ...` | `scripts/py/search_multi.py` | Confronto rotte diretta/inversa + skiplagging |
| `uv run --directory scripts/py search_poi.py ...` | `scripts/py/search_poi.py` | POI, attrazioni, cibo via Wikipedia API |
| `uv run --directory scripts/py search_weather.py ...` | `scripts/py/search_weather.py` | Previsioni meteo via Open-Meteo |
| `uv run --directory scripts/py geocode.py ...` | `scripts/py/geocode.py` | Geocoding via OpenStreetMap |
| `uv run --directory scripts/py route_distance.py ...` | `scripts/py/route_distance.py` | Distanze e tempi tra POI via OSRM |
| `uv run --directory scripts/py generate_links.py ...` | `scripts/py/generate_links.py` | Genera link di ricerca (fallback) |
| `uv run --directory scripts/py chrome_driver.py start\|stop` | `scripts/py/chrome_driver.py` | Gestisce Chrome in Docker per Selenium |

**Nota bus intercity**: non esiste uno script dedicato agli autobus a lunga
percorrenza (es. Flixbus). Per proporre prezzi bus usa websearch (es.
"Flixbus CittàX CittàY") o flixbus.com, e confronta SEMPRE costo+tempi
rispetto a treno e volo (vedi regola multimodale in `plan.md`).
