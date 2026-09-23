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

### Passo 0 — Rinominare il framework
Questo repo è un template da forkare: il nome `myframe` è un segnaposto.
Se esiste `skills/myframe/`, fai questo passo prima di tutto il resto
(altrimenti saltalo).
1. Chiedi il nome del framework. Deve essere kebab-case (`[a-z0-9-]+`),
   perché diventa il comando `/<nome>`. Proponi un default dal nome della cartella del repo.
2. Mostra l'elenco dei file che contengono `myframe`
   (`grep -rl myframe --exclude-dir=.git --exclude=init.md .`) e fatti confermare.
3. Sostituisci `myframe` con `<nome>` in tutti quei file. Non toccare questo
   file (`modes/init.md`): il Passo 0 deve restare riconoscibile.
4. Rinomina `skills/myframe/` in `skills/<nome>/` e ricrea i symlink:
   `.claude/skills/<nome>` e `.agents/skills/<nome>` → `../../skills/<nome>`
   (rimuovi quelli vecchi `myframe`).
5. Verifica: `grep -rl myframe --exclude-dir=.git --exclude=init.md .` non trova più nulla.
6. Di' all'utente che da ora il comando è `/<nome>` (potrebbe servire
   riavviare il CLI perché lo veda) e prosegui con il Passo 1.

Non committare: è l'utente a decidere quando.

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
Aggiorna `skills/<nome>/SKILL.md`: aggiungi il nuovo comando alla tabella di
routing e al menu di discovery, e indica quali file caricare per quel modo.

### Passo 7 — Prova a secco
Simula l'invocazione `/<nome> <verbo> <input d'esempio>` e mostra all'utente
cosa accadrebbe passo per passo. Raccogli feedback e itera sul modo pilota
finché non è soddisfatto.

### Passo 8 — Prossimi passi
Riepiloga cosa è stato creato e quali verbi restano da implementare. Suggerisci
di tornare con `/<nome> init` per aggiungere il prossimo modo.

### Passo 9 — Installazione globale (opzionale)
Finora la skill è disponibile solo in questo progetto (`.claude/skills/<nome>`).
Se `~/.claude/skills/<nome>` non esiste, chiedi all'utente se vuole renderla
disponibile anche negli altri progetti. Se sì:
1. `mkdir -p ~/.claude/skills`
2. `ln -s "<percorso assoluto del repo>/skills/<nome>" ~/.claude/skills/<nome>`
3. Spiega che:
   - è un symlink, non una copia: le modifiche al repo valgono ovunque, e il
     repo non va spostato né cancellato (altrimenti il link si rompe);
   - negli altri progetti i dati utente (`config/`, `data/`, `reports/`,
     `output/`, `modes/_profile.md`) vengono scritti nella cartella di quel
     progetto (vedi "Percorsi" in `SKILL.md`);
   - per disinstallare: `rm ~/.claude/skills/<nome>`.

Se `~/.claude/skills/<nome>` esiste già, non sovrascriverlo: dillo all'utente.

## Nota per l'agente
Sei tu a scrivere i file (l'utente te lo consente). Usa il tool di domande
interattive quando una scelta è davvero dell'utente; per i default ovvi,
proponi e procedi. Non costruire più di un modo per sessione, salvo richiesta.
