# `scripts/` — Tool deterministici

## Cosa va qui
Codice eseguibile (qui `.mjs`, ma può essere qualsiasi linguaggio) per le
operazioni che **non vanno lasciate all'LLM** perché devono essere esatte e
ripetibili.

## Quando scrivere uno script invece di prosa
Usa uno script quando il compito è:
- **Deterministico** — stesso input, stesso output, sempre (parsing, validazione).
- **Strutturale** — manipolazione di file, dati, formati (JSON, CSV, PDF).
- **Ripetuto** — dedup, normalizzazione, sincronizzazione di uno stato.
- **Verificabile** — vuoi testarlo con un test, non "fidarti" dell'LLM.

Lascia invece all'LLM (cioè ai `modes/*.md`) i compiti "morbidi": valutare,
scrivere testo, classificare, decidere con giudizio.

## Come i modi li usano
Un modo invoca uno script via Bash e ne legge l'output (idealmente JSON):

```
node scripts/validate.mjs <input>   →   {"status":"ok", ...}
```

Registra ogni script nella tabella "Tool disponibili" di `modes/_shared.md`
così i modi sanno che esiste.

## Convenzioni
- Output **JSON su stdout** per essere parsabile dall'agente.
- Errori chiari e codici di uscita sensati.
- Un compito per script; niente effetti collaterali nascosti.

## Incluso nel template
- `validate.mjs` — scheletro minimo di validazione input che emette JSON.
