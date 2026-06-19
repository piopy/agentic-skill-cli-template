#!/usr/bin/env node
/**
 * validate.mjs — esempio di TOOL DETERMINISTICO.
 *
 * Perché esiste: certe operazioni non vanno lasciate all'LLM perché devono
 * essere ESATTE e RIPETIBILI (parsing, validazione di schema, dedup, I/O file).
 * Questo script mostra il pattern minimo: legge un input, lo valida, ed emette
 * un risultato JSON che il modo può leggere.
 *
 * Uso:
 *   node scripts/validate.mjs <percorso-file>
 *
 * Output (stdout, JSON):
 *   {"status":"ok","path":"..."} | {"status":"error","reason":"..."}
 */

import { readFile } from "node:fs/promises";

async function main() {
  const path = process.argv[2];
  if (!path) {
    print({ status: "error", reason: "nessun percorso fornito" });
    return;
  }
  try {
    const content = await readFile(path, "utf8");
    if (content.trim().length === 0) {
      print({ status: "error", reason: "file vuoto" });
      return;
    }
    // TODO: aggiungi qui le tue regole di validazione di dominio.
    print({ status: "ok", path, bytes: content.length });
  } catch (err) {
    print({ status: "error", reason: String(err.message ?? err) });
  }
}

function print(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

main();
