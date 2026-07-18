#!/usr/bin/env node

/**
 * generate-report.mjs — Genera il report markdown della vacanza
 * da un file JSON strutturato passato come argomento o da stdin.
 *
 * Usage: node scripts/generate-report.mjs < data/vacanza.json > output/vacanza.md
 */

import { readFileSync } from "node:fs";

const input = readFileSync(process.argv[2] || "/dev/stdin", "utf-8");
const data = JSON.parse(input);

const { name, dates, people, budget, transports, accommodations, itinerary, events, notes } = data;

const lines = [];

lines.push(`# 🏖️ ${name} — ${dates}`);
lines.push("");
lines.push("## Info viaggio");
lines.push(`- **Destinazione**: ${data.destination}`);
lines.push(`- **Date**: ${dates}`);
lines.push(`- **Persone**: ${people}`);
lines.push(`- **Budget**: ${budget}`);
lines.push("");

// Trasporti
if (transports?.length) {
  lines.push("## 🚗 Trasporti");
  for (const t of transports) {
    lines.push(`### ${t.type === "outbound" ? "Andata" : t.type === "return" ? "Ritorno" : "Spostamento"}`);
    lines.push(`- **Mezzo**: ${t.mode} — ${t.link}`);
    lines.push(`- **Tratta**: ${t.from} → ${t.to}`);
    lines.push(`- **Orario**: ${t.departure} → ${t.arrival}`);
    if (t.cost) lines.push(`- **Costo**: ${t.cost}`);
    lines.push("");
  }
}

// Alloggi
if (accommodations?.length) {
  lines.push("## 🏨 Alloggi");
  for (const a of accommodations) {
    lines.push(`- **[${a.name}](${a.link})** — ${a.city}, ${a.dates}`);
    lines.push(`  - Indirizzo: ${a.address}`);
    if (a.cost) lines.push(`  - Costo: ${a.cost}`);
    lines.push("");
  }
}

// Itinerario
if (itinerary?.length) {
  lines.push("## 📅 Itinerario");
  for (const day of itinerary) {
    lines.push(`### Giorno ${day.day} — ${day.date}`);
    for (const period of ["morning", "afternoon", "evening"]) {
      const label = { morning: "☀️ Mattina", afternoon: "🌤️ Pomeriggio", evening: "🌙 Sera" }[period];
      const items = day[period];
      if (!items?.length) continue;
      lines.push(`#### ${label}`);
      for (const item of items) {
        const link = item.link ? ` — [Maps](${item.link})` : "";
        lines.push(`- ${item.name}${link}${item.note ? ` — _${item.note}_` : ""}`);
      }
      lines.push("");
    }
  }
}

// Eventi
if (events?.length) {
  lines.push("## 🎟️ Eventi e biglietti");
  for (const e of events) {
    lines.push(`- **[${e.name}](${e.link})** — ${e.date}${e.cost ? ` — ${e.cost}` : ""}`);
  }
  lines.push("");
}

// Budget
if (data.budgetSummary) {
  lines.push("## 💰 Budget riepilogativo");
  lines.push("| Voce | Costo |");
  lines.push("|------|-------|");
  for (const [label, cost] of Object.entries(data.budgetSummary)) {
    lines.push(`| ${label} | ${cost} |`);
  }
  lines.push("");
}

if (notes) {
  lines.push("## 📌 Note");
  lines.push(notes);
}

console.log(lines.join("\n"));
