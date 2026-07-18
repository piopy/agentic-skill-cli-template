# `modes/` — Le capacità del framework (il cuore)

## Cosa va qui
Un file Markdown per ogni **capacità** del framework. Ogni modo è un "verbo"
del tuo dominio: `analyze`, `report`, `init`, ecc. Il file contiene le
istruzioni in linguaggio naturale che l'agente segue quando quel modo è attivo.

> Questo è il "codice" del framework: prosa che l'LLM esegue. La precisione la
> ottieni dalla chiarezza delle istruzioni, non dalla sintassi.

## I file speciali

| File | Layer | Ruolo |
|------|-------|-------|
| `_shared.md` | System | Regole, scale, formati comuni a TUTTI i modi. Aggiornabile. |
| `_profile.template.md` | System | Scheletro che l'utente copia in `_profile.md`. |
| `_profile.md` | **User** | Personalizzazioni dell'utente. Override di `_shared.md`. Mai aggiornato. |
| `<verbo>.md` | System | Istruzioni di un singolo modo. |

**Ordine di lettura (importante):** `_shared.md` prima, `_profile.md` dopo.
Le personalizzazioni dell'utente vincono sui default.

## Come scrivere un buon modo
- **Un modo = un verbo.** Se fa troppe cose, spezzalo.
- **Struttura a step o a blocchi.** Step 0 (validazione) → blocchi di lavoro → output.
- **Dichiara input e output attesi.** Dove legge, dove scrive, in che formato.
- **Rimanda a `_shared.md`** per scale e formati invece di duplicarli.
- **Delega ai tool** quando serve precisione (cita gli script di `scripts/`).

## I modi inclusi nel template
- `init.md` — guida interattiva per costruire/estendere il framework.
- `analyze.md` — esempio di modo di valutazione (a blocchi).
- `report.md` — esempio di modo che genera un artefatto da un template.

## Come aggiungere un modo
1. Crea `modes/<verbo>.md`.
2. Se introduce regole condivise, aggiorna `_shared.md` (mai con dati utente).
3. Registralo nel router `skills/travel-planner/SKILL.md`.
4. Classificalo nel `DATA_CONTRACT.md` (di norma System Layer).
