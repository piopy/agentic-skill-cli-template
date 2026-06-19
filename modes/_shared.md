# System Context — myframe

<!-- ============================================================
     QUESTO FILE È AGGIORNABILE. Non metterci dati personali.

     Le personalizzazioni vanno in modes/_profile.md (mai aggiornato).
     Qui stanno regole di sistema, logica di punteggio e config dei tool
     che migliorano a ogni release di myframe.
     ============================================================ -->

## Sources of Truth

| File | Percorso | Quando leggerlo |
|------|----------|-----------------|
| profile.yml | `config/profile.yml` | SEMPRE (identità e target dell'utente) |
| _profile.md | `modes/_profile.md` | SEMPRE (override dell'utente) |
| state | `data/state.md` | Nei modi che leggono/scrivono stato |

**REGOLA: leggi `_profile.md` DOPO questo file. Le personalizzazioni
dell'utente in `_profile.md` vincono sui default qui.**
**REGOLA: non hardcodare valori dell'utente. Leggili a runtime dal User Layer.**

---

## Logica condivisa (esempio: sistema di punteggio)

<!-- Questo è SOLO un esempio per mostrare il pattern. Sostituisci con
     la logica del tuo dominio: criteri di valutazione, formati di output,
     classificazioni, ecc. -->

Se il tuo framework valuta qualcosa, definisci qui la scala in modo che ogni
modo la usi in modo coerente:

| Dimensione | Cosa misura |
|------------|-------------|
| Criterio A | ... |
| Criterio B | ... |
| **Globale** | media pesata dei criteri |

Interpretazione del punteggio:
- 4.5+ → ...
- 3.5–4.4 → ...
- sotto 3.5 → ...

## Formati di output condivisi

Definisci qui i formati riusati da più modi (es. struttura di un report,
intestazione di una tabella, naming dei file in `output/`).

## Tool disponibili

Elenca gli script in `scripts/` che i modi possono invocare e cosa fanno:

| Comando | Script | Cosa fa |
|---------|--------|---------|
| `node scripts/validate.mjs` | `scripts/validate.mjs` | Valida i dati di input |
