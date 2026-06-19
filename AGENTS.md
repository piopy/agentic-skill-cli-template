# myframe — <una frase che descrive cosa fa il framework>

<!-- Questo file contiene le istruzioni GLOBALI per l'agente AI, valide
     in ogni modo. È il file canonico: CLAUDE.md e gli altri wrapper di CLI
     specifici lo importano o lo replicano. Fa parte del System Layer. -->

## Origin

Una o due frasi su chi ha costruito questo framework e per quale scopo reale.
Serve a dare contesto all'agente sul "perché" delle scelte di default.

**Funziona out-of-the-box, ma è fatto per essere reso tuo.** Tu (agente AI)
puoi modificare i file dell'utente. Se l'utente dice "cambia X", lo fai.
È esattamente il punto del framework.

## Data Contract (CRITICO)

Ci sono due strati. Leggi `DATA_CONTRACT.md` per la lista completa.

**User Layer (MAI aggiornato in automatico — le personalizzazioni vanno QUI):**
- `config/profile.yml`, `modes/_profile.md`
- `data/*`, `reports/*`, `output/*`

**System Layer (aggiornabile — NON metterci dati utente):**
- `modes/_shared.md` e tutti gli altri modi
- `AGENTS.md`, `CLAUDE.md`, gli script `scripts/*`, `templates/*`

**LA REGOLA: quando l'utente chiede di personalizzare qualcosa, scrivi SEMPRE
in `modes/_profile.md` o `config/profile.yml`. MAI in `modes/_shared.md`.**
Così gli aggiornamenti di sistema non sovrascrivono le personalizzazioni.

## Caricamento del contesto

All'inizio di ogni sessione, prima di eseguire un modo, carica nell'ordine:
1. Questo file (`AGENTS.md`) — regole globali
2. `modes/_shared.md` — logica di sistema condivisa
3. `modes/_profile.md` — personalizzazioni utente (vincono sui default)
4. `modes/<modo>.md` — istruzioni del modo richiesto

## Regole globali

- Conferma prima di azioni distruttive o irreversibili.
- Riporta gli esiti fedelmente: se qualcosa fallisce, dillo con l'output.
- Non hardcodare valori dell'utente nelle regole; leggili a runtime dal User Layer.
- <aggiungi qui le regole etiche / di sicurezza specifiche del tuo dominio>

## Cosa è myframe

<Descrizione di 2-3 righe: input, output, capacità principali.>

### File principali

| File | Funzione |
|------|----------|
| `config/profile.yml` | Identità e preferenze dell'utente |
| `data/state.md` | Stato di lavoro / tracker |
| `templates/...` | Modelli per gli output |
| `scripts/...` | Tool deterministici |
