# `templates/` — Modelli per gli output

## Cosa va qui
I modelli riutilizzabili che danno **forma** agli artefatti prodotti dai modi:
documenti Markdown, HTML, LaTeX, email, ecc. Contengono la struttura con
segnaposto (es. `{{title}}`), non i dati dell'utente.

## Perché separarli dai modi
Separare la *forma* (template) dalla *logica* (modo) ti permette di cambiare
l'aspetto di un output senza toccare le istruzioni, e di riusare lo stesso
modello in più modi.

## Come si usano
Un modo (o uno script in `scripts/`) carica il template, sostituisce i
segnaposto con i dati reali, e salva il risultato in `output/`.

## Layer
System Layer: i template sono aggiornabili. I dati che li riempiono vengono dal
User Layer (`config/`, `data/`); il file finale prodotto va in `output/`.

## Incluso nel template
- `report-template.md` — esempio con segnaposto `{{...}}`.
- `vacanza-html.html` — pagina HTML autonoma e condivisibile (CSS inline, nessuna risorsa esterna), popolata da `render_vacanza_html.py` a partire da un `vacanza.json`. Segnaposto `{{section_*}}` riempiti dal rendering dello script; link di prenotazione in evidenza in testa.
- `vacanza.json` — skeleton di partenza per creare il `vacanza.json` di un nuovo viaggio (tutti i campi con placeholder `<...>`).
- `vacanza.schema.json` — JSON Schema (draft-07) che descrive e valida la struttura di un `vacanza.json`.
