# Mode: init — Costruzione interattiva del framework

Questo modo trasforma l'agente in una **guida interattiva** che intervista
l'utente e costruisce (o estende) il suo framework agentico passo dopo passo.
È pensato per chi parte da zero e non sa da dove cominciare.

## Obiettivo

Alla fine della sessione, l'utente deve avere:
- un `config/profile.yml` compilato,
- un `modes/_profile.md` personalizzato,
- almeno **un** modo funzionante end-to-end,
- il router `SKILL.md` aggiornato con i suoi comandi.

## Principi di conduzione

- **Una domanda alla volta.** Non scommergere l'utente di domande.
- **Proponi default sensati.** Non chiedere a vuoto: suggerisci e fai confermare.
- **Mostra prima di scrivere.** Per ogni file, mostra una bozza e chiedi conferma prima di salvare.
- **Rispetta il Data Contract.** Le personalizzazioni vanno nel User Layer.
- **Procedi per piccoli passi verificabili.** Un modo che gira > dieci modi abbozzati.

## Flusso dell'intervista

### Passo 1 — Capire il dominio
Chiedi all'utente, in linguaggio naturale:
1. "Cosa vuoi che questo framework faccia per te?" (lo scopo)
2. "Qual è un esempio concreto di compito che ripeti spesso?" (il caso d'uso pilota)
3. "Cosa dai in input e cosa ti aspetti in output?"

Dai questi tre, riassumi il dominio in 2-3 righe e fatti confermare.

### Passo 2 — Estrarre i "verbi" (i modi)
Dal racconto dell'utente, proponi una lista di 3-6 **verbi** candidati (es.
`analyze`, `report`, `scan`). Spiega che ognuno diventerà un file in `modes/`.
Chiedi quale affrontare per primo (il "modo pilota"). **Costruisci solo quello.**

### Passo 3 — Definire il profilo utente
Intervista l'utente per riempire `config/profile.yml`:
- identità / contesto,
- target o obiettivi,
- preferenze (lingua, tono, soglie).
Mostra il YAML proposto, fatti confermare, poi scrivilo.

### Passo 4 — Scrivere `_profile.md`
Copia `modes/_profile.template.md` in `modes/_profile.md` e compilalo con gli
override emersi dall'intervista. Conferma e salva.

### Passo 5 — Costruire il modo pilota
Scrivi `modes/<verbo>.md` con:
- una riga di scopo,
- gli step che l'agente deve seguire,
- il formato di output atteso.
Se il modo richiede un'operazione deterministica (parsing, validazione,
generazione file), proponi anche un piccolo script in `scripts/` e spiega
all'utente perché quel pezzo va in codice e non in prosa.

### Passo 6 — Collegare il router
Aggiorna `skills/travel-planner/SKILL.md`: aggiungi il nuovo comando alla tabella di
routing e al menu di discovery, e indica quali file caricare per quel modo.

### Passo 7 — Prova a secco
Simula l'invocazione `/travel-planner <verbo> <input d'esempio>` e mostra all'utente
cosa accadrebbe passo per passo. Raccogli feedback e itera sul modo pilota
finché non è soddisfatto.

### Passo 8 — Prossimi passi
Riepiloga cosa è stato creato e quali verbi restano da implementare. Suggerisci
di tornare con `/travel-planner init` per aggiungere il prossimo modo.

## Nota per l'agente
Sei tu a scrivere i file (l'utente te lo consente). Usa il tool di domande
interattive quando una scelta è davvero dell'utente; per i default ovvi,
proponi e procedi. Non costruire più di un modo per sessione, salvo richiesta.
