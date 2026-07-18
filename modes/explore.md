# Mode: explore — Scopri cosa fare e mangiare

Modo dedicato alla scoperta di POI, eventi e cibo di una città/zona,
indipendentemente dal resto della pianificazione.

## Obiettivo

Costruire una lista ragionata di cose da vedere, eventi in corso e posti dove
mangiare per una destinazione, con link Maps e informazioni utili.

## Flusso

### Step 1 — Parametri

1. **Città/zona**: dove
2. **Date**: giorni specifici (per eventi) o generico
3. **Interessi**: culturale, natura, relax, shopping, misto
4. **Budget**: alto, medio, basso

### Step 2 — POI principali

Elenca le attrazioni principali della città, raggruppate per zona. Per ognuna:
- Nome
- Link Google Maps
- Breve descrizione
- Costo (gratuito/a pagamento)
- Tempo indicativo di visita

### Step 3 — Eventi

Usa websearch/webfetch per trovare eventi, mostre, concerti, festival nelle
date indicate. Per ognuno:
- Nome
- Link per info/biglietti
- Data e orario
- Costo
- Posizione (link Maps)

### Step 4 — Itinerario suggerito (opzionale)

Se l'utente lo chiede, organizza POI ed eventi in un itinerario di 1-3 giorni
con mezzi pubblici.

### Step 5 — Cibo

1. Ricerca piatti tipici locali
2. Su Maps: locali con recensioni migliori per quei piatti
3. Per ogni locale: nome, link Maps, costo indicativo, tipo di cucina

## Output

Elenco strutturato (non report completo) con link Maps, eventi e opzioni cibo.
L'utente può prendere appunti e usare le info in una sessione `plan` successiva.
