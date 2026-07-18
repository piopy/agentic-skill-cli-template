# Mode: report — Genera la guida di viaggio finale

Modo per generare il report markdown della vacanza a partire da dati già
decisi, senza rifare l'intera pianificazione.

## Obiettivo

Partendo da decisioni già prese (in una sessione `plan` precedente o
manualmente fornite), produrre la guida markdown dettagliata pronta da
condividere.

## Flusso

### Step 1 — Raccogli dati

Se esiste già una pianificazione in `data/state.md`, leggila. Altrimenti
intervista l'utente per raccogliere TUTTI i dati necessari:

1. **Destinazione e date**
2. **Trasporti** (andata, ritorno, spostamenti interni) — orari, costi, link prenotazione
3. **Alloggi** — nome, link, indirizzo, costo, date
4. **Itinerario** — giorno per giorno, mattina/pomeriggio/sera, con link Maps
5. **Eventi** — nome, link biglietti, data, costo
6. **Ristoranti** — nome, link Maps, costo
7. **Budget** riepilogativo

### Step 2 — Genera report

Usa lo script `scripts/generate-report.mjs` passando i dati in formato JSON,
oppure scrivi direttamente il markdown se i dati non sono strutturati.

### Step 3 — Salva

Il file viene salvato in `output/<nome-vacanza>.md`.

### Step 4 — Mostra e approva

Mostra l'anteprima all'utente. Chiedi approvazione o modifiche. Se modifiche,
itera e rigenera.

## Struttura del report

Vedi `modes/plan.md` per la struttura completa del markdown. Il formato è
identico: giorno per giorno, link Maps per tutto, orari trasporti, budget.
