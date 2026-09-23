# `skills/` — Il punto d'ingresso del framework

## Cosa va qui
Una sottocartella per ogni skill invocabile dall'utente. Nel template c'è
`myframe/` con dentro `SKILL.md`, il **router**.

## Cos'è il router (`SKILL.md`)
È il file che il CLI esegue quando l'utente scrive `/myframe <comando>`.
L'intestazione YAML (`name`, `description`, `argument-hint`, `user_invocable`)
dice al CLI come esporre la skill. Il corpo fa tre cose:

1. **Routing** — mappa l'argomento dell'utente al modo giusto (tabella input→modo).
2. **Discovery** — se non c'è argomento, mostra il menu dei comandi.
3. **Caricamento del contesto** — per ogni modo, dice *quali file leggere prima*
   di eseguire (di solito `_shared.md` + `_profile.md` + il file del modo).

## Perché è separato dai modi
Il router è "sottile": decide *cosa* eseguire, non *come*. La logica vera sta
nei `modes/`. Così aggiungere una capacità = aggiungere un file in `modes/` +
una riga nel router.

## Come si estende
1. Aggiungi una riga alla tabella di routing.
2. Aggiungi la voce al menu di discovery.
3. Indica quali file caricare per quel modo.

## Nota multi-CLI
`.claude/skills/myframe` (Claude Code) e `.agents/skills/myframe` (Codex, OpenCode)
sono symlink a questa cartella: c'è una sola copia da modificare.
