# Mode: transport — Ricerca trasporti

Modo dedicato alla ricerca e confronto di opzioni di trasporto tra città,
indipendentemente dal resto della pianificazione.

## Obiettivo

Trovare la soluzione di trasporto più conveniente (tempo + costo) per andare
da A a B, considerando tutte le modalità.

## Flusso

### Step 1 — Raccolta parametri

1. **Partenza**: città/aeroporto di partenza
2. **Destinazione**: città di arrivo (o "zona")
3. **Date flessibili?** Sì/No. Se sì: periodo
4. **Persone**: quante
5. **Preferenza**: volo, treno, bus, qualsiasi

### Step 2 — Ricerca opzioni

Per ogni modalità pertinente:

- **Volo**: cerca su Skyscanner (link con parametri). Verifica aeroporti alternativi nelle vicinanze (sia partenza che arrivo)
- **Treno**: verifica operatori (Trenitalia, Interrail, ÖBB, DB, SNCF, ecc.). Link alla ricerca
- **Bus**: Flixbus e altri operatori locali. Link alla ricerca
- **Multi-città**: valuta arrivo in città X e rientro da città Y

### Step 3 — Confronto

| Opzione | Mezzo | Durata | Costo | Link |
|---------|-------|--------|-------|------|
| 1 | Volo AZ123 | 2h | €120 | ... |
| 2 | Treno FR123 | 4h | €80 | ... |
| 3 | Flixbus 456 | 6h | €35 | ... |

### Step 4 — Scelta

L'utente sceglie. Salva la decisione con link, orari, costo.

## Output

Riepilogo della scelta + link di prenotazione. Niente report completo: questo
modo si occupa solo di trasporti.
