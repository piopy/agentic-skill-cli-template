# Mode: analyze — <cosa analizza>

<!-- Modo di ESEMPIO. Mostra la struttura tipica di un modo "di valutazione".
     Sostituisci i blocchi con la logica del tuo dominio. -->

Quando l'utente fornisce un input (testo o file), produci un'analisi strutturata
seguendo questi blocchi. Usa la scala e i formati definiti in `modes/_shared.md`
e applica gli override presenti in `modes/_profile.md`.

## Step 0 — Validazione input
Se l'input è un file/URL, verifica che sia valido e leggibile prima di procedere.
Se non lo è, fermati e spiega all'utente cosa manca. (Eventualmente usa
`node scripts/validate.mjs`.)

## Blocco A — Sintesi
Riassumi l'input in una tabella: cosa è, contesto, TL;DR in una frase.

## Blocco B — Valutazione sui criteri
Per ogni criterio definito in `_shared.md`, assegna un punteggio e motivalo
citando parti specifiche dell'input.

## Blocco C — Raccomandazione
Verdetto finale basato sul punteggio globale, con il razionale.

## Output
Salva il risultato in `reports/` con naming coerente (vedi `_shared.md`) e
mostra all'utente un riassunto. Se previsto, aggiorna lo stato in `data/state.md`.
