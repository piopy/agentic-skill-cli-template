# Mode: analyze — Analisi e confronto opzioni

Modo per analizzare e confrontare link che l'utente incolla (alloggi, attività,
ristoranti) e aiutarlo a decidere.

## Obiettivo

Dati 2+ link a opzioni (es. due annunci Booking, due ristoranti), produrre un
confronto strutturato che aiuti l'utente a scegliere.

## Flusso

### Step 1 — Raccolta input

L'utente incolla i link (Booking, Airbnb, Google Maps, ristoranti, eventi, ecc.)
specificando cosa sta confrontando:
- "Questi due B&B a Vienna, quale mi consigli?"
- "Questi tre ristoranti a Copenaghen"

### Step 2 — Analisi

Per ogni link, cerca di estrarre:
- **Posizione**: quartiere, vicinanza a metro/centro (max 20 min a piedi da metro)
- **Prezzo**: costo totale/notte/persona
- **Rating**: voto utenti
- **Servizi**: bagno privato, cancellaz. gratuita, WiFi, colazione
- **Vicinanza a POI**: confronto con attrazioni principali

### Step 3 — Tabella comparativa

| Criterio | Opzione A | Opzione B | Opzione C |
|----------|-----------|-----------|-----------|
| Prezzo | €120 | €100 | €140 |
| Posizione | Centro, 5 min metro | Periferia, 15 min bus | Centro, 2 min metro |
| Rating | 4.5 | 4.2 | 4.7 |
| Bagno privato | ✅ | ❌ | ✅ |
| Cancellaz. grat. | ✅ | ✅ | ❌ |
| **Verdetto** | ✅ Buon compromesso | ❌ | ⭐ Migliore qualità |

### Step 4 — Raccomandazione

Spiega quale opzione è migliore e perché, in base alle preferenze del profilo.

## Output

Tabella comparativa + raccomandazione motivata. Non salva nulla permanentemente
a meno che l'utente non chieda espressamente di aggiungere la scelta a una
pianificazione in corso.
