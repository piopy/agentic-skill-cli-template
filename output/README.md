# `output/` — Artefatti finali generati

## Cosa va qui
I prodotti finali "consegnabili" del framework: PDF, documenti esportati, file
generati a partire dai `templates/`. È ciò che l'utente porta fuori dal sistema.

## Layer
**User Layer.** Mai aggiornato in automatico.

## Differenza con `reports/`
- `output/` → artefatti **finali/consegnabili** (spesso binari: PDF, export).
- `reports/` → **valutazioni/analisi** prodotte dai modi (di solito Markdown).
La distinzione è una convenzione utile, non un obbligo: adattala al tuo dominio.

## Buone pratiche
- Naming coerente dei file (definiscilo in `modes/_shared.md`).
- Non committare gli artefatti generati: aggiungi `output/` al `.gitignore`.

> Nel template questa cartella contiene solo `.gitkeep`: si popola all'uso.
