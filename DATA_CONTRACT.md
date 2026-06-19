# Data Contract

Questo documento definisce quali file appartengono al **sistema** (aggiornabili
in automatico) e quali all'**utente** (mai toccati dagli aggiornamenti).

È il contratto che rende il framework aggiornabile senza distruggere il lavoro
e le personalizzazioni dell'utente. Ogni nuovo file che aggiungi va classificato
in uno dei due strati.

## User Layer (MAI aggiornato in automatico)

Contiene dati personali, personalizzazioni e prodotti del lavoro.

| File | Scopo |
|------|-------|
| `config/profile.yml` | Identità, target, preferenze dell'utente |
| `modes/_profile.md` | Personalizzazioni dei modi (override di `_shared.md`) |
| `data/*` | Stato di lavoro: tracker, code, history |
| `reports/*` | Report/valutazioni generati |
| `output/*` | Artefatti finali (PDF, file esportati...) |

## System Layer (sicuro da aggiornare)

Contiene logica, script, template e istruzioni che migliorano a ogni release.

| File | Scopo |
|------|-------|
| `modes/_shared.md` | Regole comuni, scale di punteggio, formati |
| `modes/_profile.template.md` | Scheletro che l'utente copia in `_profile.md` |
| `modes/<modo>.md` | Istruzioni dei singoli modi |
| `skills/myframe/SKILL.md` | Router |
| `AGENTS.md`, `CLAUDE.md` | Istruzioni per l'agente |
| `scripts/*` | Tool deterministici |
| `templates/*` | Modelli per gli output |
| `config/profile.example.yml` | Esempio di configurazione (NON il file reale dell'utente) |
| `.claude-plugin/*` | Manifest di distribuzione |

## La regola operativa

Quando l'utente chiede di personalizzare **qualsiasi cosa** (preferenze, regole,
narrativa, soglie), scrivi nel **User Layer** — di norma `modes/_profile.md` o
`config/profile.yml`. **Mai** modificare `modes/_shared.md` o gli altri file di
sistema per contenuti specifici dell'utente.

L'agente legge `_shared.md` (sistema) per primo e `_profile.md` (utente) dopo:
le personalizzazioni dell'utente **vincono sempre** sui default di sistema.
