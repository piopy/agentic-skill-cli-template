# Agentic Framework Template

Un template generico e didattico per costruire il **tuo** framework agentico sopra un AI coding CLI (Claude Code, OpenCode, Gemini, Codex, Qwen...).

> Framework per il AI Travel Planner.

---

## 1. Cos'è un "framework agentico"

Non è un programma che gira da solo. È un **insieme di istruzioni, dati e tool** che un agente AI (l'LLM dentro il tuo CLI) legge ed esegue per portare a termine compiti ripetibili nel tuo dominio.

L'agente è il "motore". Il framework è la "macchina" che gli costruisci intorno: gli dici *cosa* fare (istruzioni), *con cosa* (tool deterministici), *su quali dati* (file di stato) e *come restare nei binari* (regole e contratti).

Tre principi guida:

1. **Funziona out-of-the-box, ma è fatto per essere reso tuo.** L'agente stesso può modificare i file del framework su richiesta dell'utente.
2. **Separa la logica di sistema dai dati dell'utente** (vedi `DATA_CONTRACT.md`). Così gli aggiornamenti non cancellano le personalizzazioni.
3. **Markdown per il ragionamento, codice per il determinismo.** Le decisioni "morbide" (valutare, scrivere, classificare) stanno nei file `modes/*.md`; le operazioni esatte e ripetibili (parsing, validazione, generazione file) stanno negli script in `scripts/`.

---

## 2. I 5 mattoni del framework

| Mattone | Dove vive | A cosa serve |
|---------|-----------|--------------|
| **Router / Skill** | `skills/travel-planner/SKILL.md` | Punto d'ingresso. L'utente scrive `/travel-planner <comando>` e il router decide quale "modo" eseguire. |
| **Modi (Modes)** | `modes/*.md` | Un file per ogni capacità (un "verbo" del tuo dominio). Contiene le istruzioni in linguaggio naturale che l'agente segue. |
| **Istruzioni agente** | `AGENTS.md` (+ wrapper `CLAUDE.md`) | Regole globali sempre valide, indipendenti dal modo. |
| **Tool deterministici** | `scripts/*.mjs` | Codice eseguibile per ciò che non va lasciato all'LLM (I/O file, validazione, parsing). |
| **Stato e configurazione** | `config/`, `data/`, `output/`, `reports/` | Dati dell'utente: identità, input, file di lavoro, output prodotti. |

---

## 3. Come l'agente "esegue" il framework (il ciclo)

```
Utente:  /travel-planner analyze <input>
            │
            ▼
SKILL.md (router) ── individua il modo "analyze"
            │
            ▼
Carica:  AGENTS.md  +  modes/_shared.md  +  modes/_profile.md  +  modes/analyze.md
            │
            ▼
L'agente segue le istruzioni del modo, eventualmente chiamando scripts/*.mjs
            │
            ▼
Scrive output in  output/  o  reports/ ,  aggiorna stato in  data/
```

Punto chiave: **il "codice" che l'agente esegue è prosa in Markdown.** Il CLI inietta il contenuto di questi file nel contesto e l'LLM li segue come fossero istruzioni. Gli script `.mjs` sono i punti in cui scendi a codice vero perché ti serve precisione.

---

## 4. La separazione System Layer / User Layer (la regola d'oro)

Questo è il pattern più importante da copiare. Divide i file in due strati:

- **System Layer** — logica, script, modi, regole. *Aggiornabile.* Quando rilasci una nuova versione del framework, questi file possono essere sovrascritti.
- **User Layer** — identità, preferenze, dati di lavoro, output. *Mai toccato dagli aggiornamenti.*

La regola operativa: **quando l'utente personalizza qualcosa, scrivi SEMPRE nel User Layer** (es. `modes/_profile.md` o `config/profile.yml`), **mai nei file di sistema** (es. `modes/_shared.md`). Così un futuro aggiornamento non cancella il lavoro dell'utente.

Dettagli completi in `DATA_CONTRACT.md`.

---

## 5. Costruisci il tuo: ricetta in 7 passi

1. **Definisci il dominio e i "verbi".** Cosa deve saper fare il framework? Ogni verbo (es. `analyze`, `report`, `scan`) diventa un file in `modes/`.
2. **Scrivi `config/profile.example.yml`.** Quali dati dell'utente servono sempre? (identità, target, preferenze). Questo è il cuore del User Layer.
3. **Scrivi `modes/_shared.md`.** Le regole comuni a tutti i modi: definizioni, scale di punteggio, formati di output, tool disponibili.
4. **Scrivi `modes/_profile.template.md`.** Lo scheletro che l'utente copierà in `_profile.md` per personalizzare senza toccare il sistema.
5. **Scrivi un file per modo.** Comincia con UNO solo (il più importante), fallo funzionare end-to-end, poi aggiungi gli altri.
6. **Scrivi gli script deterministici** in `scripts/` solo quando un compito è troppo delicato per lasciarlo all'LLM (parsing, validazione, dedup, generazione PDF...).
7. **Collega tutto nel router** `skills/travel-planner/SKILL.md` e nelle istruzioni globali `AGENTS.md`.

> Inizia minuscolo: 1 modo + 1 file di config + il router. Espandi solo quando il primo flusso gira pulito.

---

## 6. Mappa delle cartelle

Ogni cartella ha il suo `README.md` con spiegazioni dettagliate. Panoramica:

| Percorso | Contenuto | Layer |
|----------|-----------|-------|
| `skills/travel-planner/SKILL.md` | Router: smista i comandi verso i modi | System |
| `modes/` | Un `.md` per capacità + `_shared.md` + `_profile.md` | System (`_profile.md` è User) |
| `config/` | `profile.yml` e configurazioni utente | User |
| `scripts/` | Tool deterministici `.mjs` | System |
| `templates/` | Modelli per gli output (HTML, MD, ecc.) | System |
| `data/` | Stato di lavoro: tracker, code, history | User |
| `output/` | Artefatti finali generati | User |
| `reports/` | Report/valutazioni prodotti | User |
| `.claude-plugin/` | Manifest per distribuire come plugin | System |
| `AGENTS.md` / `CLAUDE.md` | Istruzioni globali per l'agente | System |
| `DATA_CONTRACT.md` | Definizione System vs User Layer | System |

---

## 7. Errori comuni da evitare

- **Mettere dati utente nei file di sistema.** Gli aggiornamenti li cancelleranno. Rispetta il Data Contract.
- **Scrivere codice quando basta la prosa (e viceversa).** Valutazioni e testo → Markdown. Parsing e validazione → script.
- **Modi giganti.** Un modo = un verbo. Se un file fa troppe cose, spezzalo.
- **Hardcodare valori dell'utente nelle regole.** Le metriche e le preferenze si leggono a runtime dal User Layer, non si incollano in `_shared.md`.
- **Partire da 15 modi.** Parti da uno che funziona davvero.

---

## 8. Prossimi passi

1. Leggi i README di ogni cartella (sono pensati come una lezione).
2. Il framework si chiama `travel-planner`.
3. Compila `config/profile.example.yml` e crea il tuo `modes/_shared.md`.
4. Implementa il primo modo end-to-end.
5. Testa il giro completo dal router.
