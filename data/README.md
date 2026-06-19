# `data/` — Stato di lavoro dell'utente

## Cosa va qui
Lo **stato** che il framework legge e aggiorna nel tempo: tracker, code di
input da processare, history, file di lavoro. È memoria persistente tra sessioni.

## Esempi tipici
- `state.md` / `tracker.md` — fonte di verità di ciò che è stato fatto.
- `pipeline.md` — inbox di input ancora da processare.
- `history.tsv` — log per deduplicazione.

## Layer
**User Layer.** Mai aggiornato in automatico: è il lavoro dell'utente.

## Buone pratiche
- Scegli **una** fonte di verità (di solito un file Markdown leggibile).
- Indici/DB derivati (es. SQLite) devono essere rigenerabili da uno script:
  così sono "sicuri da cancellare".
- Mantieni i file leggibili dall'uomo dove possibile: facilitano debug e fiducia.

> Nel template questa cartella contiene solo `.gitkeep`: si popola all'uso.
