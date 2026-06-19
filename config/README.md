# `config/` — Configurazione dell'utente

## Cosa va qui
La configurazione che definisce **chi è l'utente** e **cosa vuole**: identità,
obiettivi/target, preferenze (lingua, tono, soglie).

## I file
| File | Layer | Note |
|------|-------|------|
| `profile.example.yml` | System | Esempio documentato. Aggiornabile. |
| `profile.yml` | **User** | Il file reale dell'utente. Mai aggiornato. |

L'utente **copia** `profile.example.yml` in `profile.yml` e lo compila.
`profile.yml` non è versionato nel template (è dato personale).

## Perché è centrale
È la principale fonte di verità del User Layer. Tutti i modi lo leggono
("SEMPRE", vedi `_shared.md`) per adattare il comportamento all'utente, invece
di avere valori hardcoded nelle regole di sistema.

## Buone pratiche
- Tieni `profile.example.yml` allineato a ciò che i modi si aspettano di leggere.
- Documenta ogni campo con un commento.
- Non mettere segreti/API key qui in chiaro: usa variabili d'ambiente.
