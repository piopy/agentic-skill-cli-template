# myframe — istruzioni per Claude Code

<!-- Wrapper specifico per Claude Code. Il file canonico è AGENTS.md.
     Tieni qui solo ciò che è specifico di Claude Code; per il resto,
     replica o rimanda ad AGENTS.md per non duplicare la logica. -->

> Le istruzioni canoniche sono in `AGENTS.md`. Leggi quel file: contiene il
> Data Contract, le regole globali e l'ordine di caricamento del contesto.

## Specifico di Claude Code

- Il framework si invoca come skill: `/myframe <comando>` (vedi `skills/myframe/SKILL.md`).
- Per modi pesanti (molte chiamate a tool, lavoro parallelo), valuta di delegare
  a un subagent tramite il tool Agent, iniettando nel prompt il contenuto di
  `modes/_shared.md` + `modes/<modo>.md`.
- Permessi suggeriti per il plugin: vedi `.claude-plugin/plugin.json`.
