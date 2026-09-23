---
name: myframe
description: <una frase sul tuo framework> — router che smista i comandi verso i modi
arguments: mode
user-invocable: true
argument-hint: "[init | analyze | report | <i tuoi modi> ]"
license: MIT
---

# myframe — Router

Questo file è il **punto d'ingresso** del framework. L'utente scrive
`/myframe <comando>` e qui decidi quale modo eseguire e quali file caricare.

## Percorsi (leggi prima di tutto)

Tutti i percorsi del framework sono relativi a due radici:

- **SYSTEM** — dove stanno `AGENTS.md`, `modes/`, `scripts/`, `templates/`.
  Se la cartella di lavoro contiene `AGENTS.md` e `modes/_shared.md`, è quella
  (repo forkato e aperto direttamente). Altrimenti (installato come plugin) è
  due livelli sopra il percorso *reale* di questo `SKILL.md` (risolvi i symlink).
- **USER** — sempre la cartella di lavoro. Qui stanno `config/profile.yml`,
  `modes/_profile.md`, `data/`, `reports/`, `output/`. Mai scrivere dati utente
  in SYSTEM se è diversa da USER: gli aggiornamenti del plugin la sovrascrivono.

---

## Routing dei modi

Determina il modo da `$mode`:

| Input | Modo |
|-------|------|
| (vuoto / nessun argomento) | `discovery` — mostra il menu comandi |
| `init` | `init` — costruzione interattiva del framework |
| `analyze` | `analyze` |
| `report` | `report` |
| `<altri tuoi comandi>` | `<modo corrispondente>` |

Se `$mode` non è un comando noto, mostra la **Discovery Mode**.

---

## Discovery Mode (nessun argomento)

Mostra questo menu:

```
myframe — Command Center

Comandi disponibili:
  /myframe init      → Costruzione interattiva: ti guido a creare/estendere il framework
  /myframe analyze   → <cosa fa>
  /myframe report    → <cosa fa>
  ...

Suggerimento: parti da /myframe init se è la prima volta.
```

---

## Caricamento del contesto per modo

Dopo aver individuato il modo, carica i file necessari PRIMA di eseguire.

### Modi che richiedono `_shared.md` + il file del modo:
Leggi `modes/_shared.md` + `modes/_profile.md` + `modes/<modo>.md`.
Applica a: `analyze`, `report`, <i modi che usano le regole condivise>.

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
  description="myframe <modo>"
)
```

Esegui le istruzioni del file del modo caricato.
