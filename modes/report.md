# Mode: report — genera un artefatto finale

<!-- Modo di ESEMPIO. Mostra come un modo produce un output usando un template
     e uno script deterministico. -->

Genera un artefatto finale (es. documento, PDF, export) a partire dai dati
dell'utente e da un modello in `templates/`.

## Step 1 — Raccogli i dati
Leggi le fonti rilevanti (`config/profile.yml`, eventuali `reports/`, `data/`).

## Step 2 — Compila il template
Prendi il modello da `templates/` e riempilo con i dati. La parte di
sostituzione/generazione deterministica può essere delegata a uno script in
`scripts/` (vedi `modes/_shared.md` per i tool disponibili).

## Step 3 — Salva ed esponi
Salva l'artefatto in `output/` con naming coerente. Mostra all'utente il
percorso del file generato e un riepilogo.
