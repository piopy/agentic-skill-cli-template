---
name: travel-planner
description: "AI Travel Planner — pianifica vacanze con dati reali via Selenium + API (confronta rotte, skiplagging, valuta TUTTI gli alloggi)"
arguments: mode
user_invocable: true
argument-hint: "[init | plan | transport | explore | analyze | report ]"
license: MIT
---

# travel-planner — Router

Questo file è il **punto d'ingresso** del framework. L'utente scrive
`/travel-planner <comando>` e qui decidi quale modo eseguire e quali file caricare.

## Comportamenti della skill

1. **Valuta TUTTI gli alloggi** — mostra ogni risultato dagli script, non filtrarli a priori.
2. **Confronto rotte** — su viaggi multi-città, confronta SEMPRE routing diretto vs inverso.
3. **Skiplagging check** — verifica sempre se voli con scalo sono più economici dei diretti (hidden city ticketing).
4. **Voli con scalo** — non limitarti ai diretti; cerca anche voli con scalo se il diretto è caro.
5. **Cross-reference su dati mancanti** — se Selenium dà "nessun risultato", rilancia, cerca su web, e chiedi all'utente. Non assumere che la rotta non esista. Usa fonti alternative (eoob.it, Ryanair.com, Skyscanner).
6. **Skyscanner è il default per i voli** — genera SEMPRE link Skyscanner come primo risultato. Se l'utente dice "non vedo tutti i voli", dagli il link Skyscanner diretto.
7. **Aeroporti alternativi** — per OGNI città, controlla aeroporti vicini (GRO/REU per BCN, CIA per FCO, LIN/BGY per MXP, VRN/PSA per BLQ). Cerca voli per TUTTI e confronta.
8. **Ritorno da città vicine** — verifica se volare dal ritorno da un aeroporto vicino è più economico. Includi costo spostamento via bus/treno.
9. **Swap mete per città singola** — confronta combinazioni miste arrivo/partenza tra aeroporto principale e alternativi.
10. **Trasporto locale** — per ogni città, consiglia il mezzo più economico e veloce (metro preferibile, a piedi se <2km). Calcola distanze con route_distance.py. Per Barcellona: T-casual 10 corse o Aerobús dall'aeroporto.

## Routing dei modi

Determina il modo da `$mode`:

| Input | Modo |
|-------|------|
| (vuoto / nessun argomento) | `plan` — pianificazione vacanza completa stile AI (DEFAULT) |
| `init` | `init` — costruzione interattiva del framework |
| `plan` | `plan` — pianificazione vacanza completa stile AI |
| `transport` | `transport` — ricerca e confronto trasporti (volo/treno/bus) |
| `explore` | `explore` — scoperta POI, eventi e cibo di una città |
| `analyze` | `analyze` — analisi e confronto link (alloggi, ristoranti, attività) |
| `report` | `report` — genera guida markdown da dati già decisi |

Se `$mode` è vuoto → esegui `plan` (default). Se `$mode` non è un comando noto,
mostra la **Discovery Mode**.

---

## Discovery Mode (solo per comando non riconosciuto)

Mostra questo menu:

```
travel-planner — Command Center

Comandi disponibili:
  /travel-planner (vuoto) → Pianificazione vacanza completa (DEFAULT)
  /travel-planner init     → Costruzione interattiva: ti guido a creare/estendere il framework
  /travel-planner plan     → Pianificazione vacanza completa stile AI
  /travel-planner transport→ Ricerca e confronto trasporti (volo/treno/bus)
  /travel-planner explore  → Scoperta POI, eventi e cibo di una città
  /travel-planner analyze  → Analisi e confronto link (alloggi, ristoranti, attività)
  /travel-planner report   → Genera guida markdown da dati già decisi

Suggerimento: di default (senza argomento) esegue /travel-planner plan.
```

---

## Caricamento del contesto per modo

Dopo aver individuato il modo, carica i file necessari PRIMA di eseguire.

### Modi che richiedono `_shared.md` + il file del modo:
Leggi `modes/_shared.md` + `modes/_profile.md` + `modes/<modo>.md`.
Applica a: `plan`, `transport`, `explore`, `analyze`, `report`.

### Modi standalone (solo il loro file):
Leggi solo `modes/<modo>.md`.
Applica a: `init`, <modi indipendenti dalle regole di scoring>.

### Modi delegati a un subagent:
Per modi pesanti (molti tool, lavoro parallelo), lancia un Agent iniettando
nel prompt il contenuto di `modes/_shared.md` + `modes/<modo>.md` + i dati
specifici dell'invocazione.

```
Agent(
  subagent_type="general-purpose",
  prompt="[contenuto di modes/_shared.md]\n\n[contenuto di modes/<modo>.md]\n\n[dati]",
  description="travel-planner <modo>"
)
```

Esegui le istruzioni del file del modo caricato.
