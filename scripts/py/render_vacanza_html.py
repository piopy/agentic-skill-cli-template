#!/usr/bin/env python3
"""render_vacanza_html.py — rende una pagina HTML autonoma da un vacanza.json.

Template: templates/vacanza-html.html (segnaposto {{...}}).
Output: file HTML self-contained (CSS inline, nessuna risorsa esterna).

Usage:
  uv run --directory scripts/py render_vacanza_html.py [vacanza.json] [--out output.html]
  Se il percorso JSON termina con output/<viaggio>/vacanza.json, il default
  dell'output è output/<viaggio>/<slug-nome>.html (stessa cartella).

Output su stdout: percorso del file HTML prodotto (manca anche il definito
percorso dei quartieri? no: schema libero).
"""

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "vacanza-html.html"

PALETTES = [
    ("#2563eb", "#4f46e5"),   # blu → indaco
    ("#0ea5e9", "#2563eb"),   # azzurro → blu
    ("#10b981", "#0d9488"),   # verde → teal
    ("#f59e0b", "#ea580c"),   # ambra → arancio
    ("#ec4899", "#c026d3"),   # rosa → fucsia
    ("#8b5cf6", "#6d28d9"),   # viola
    ("#ef4444", "#dc2626"),   # rosso
    ("#14b8a6", "#0891b2"),   # teal → cyan
]

TRANS_LABEL = {"outbound": "Germania ✈️", "return": "Ritorno ↘", "local": "In città 🚇"}


def esc(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "vacanza"


def accent_for(name: str) -> tuple[str, str]:
    h = hashlib.md5(name.encode()).digest()[0]
    return PALETTES[h % len(PALETTES)]


def link_or_text(item: dict, cls: str = "") -> str:
    """Rende un oggetto item: accetta {'name','link','note'} o una stringa."""
    if isinstance(item, str):
        return f"<div class=\"item\"><b>{esc(item)}</b></div>"
    name = item.get("name", "")
    note = item.get("note", "")
    link = item.get("link")
    out = "<div class=\"item\">"
    if link:
        out += f"<b>{esc(name)}</b> <a href=\"{esc(link)}\" target=\"_blank\" rel=\"noopener\">🔗 {esc(link)}</a>"
    else:
        out += f"<b>{esc(name)}</b>"
    if note:
        out += f"<div class=\"note\">{esc(note)}</div>"
    out += "</div>"
    return out


def section_transports(d: dict) -> str:
    ts = d.get("transports") or []
    if not ts:
        return ""
    blocks = []
    for t in ts:
        label = TRANS_LABEL.get(t.get("type"), "Trasporto 🚌")
        link = t.get("link")
        body = []
        if t.get("from") or t.get("to"):
            body.append(f"<b>🛫 {esc(t.get('from', '—'))} → {esc(t.get('to', '—'))}</b>")
        if t.get("departure"):
            body.append(f"<span class=\"muted\">🕒 {esc(t.get('departure'))}" +
                        (f" → {esc(t.get('arrival'))}" if t.get("arrival") else "") + "</span>")
        if t.get("cost"):
            body.append(f"<span class=\"muted\">💶 {esc(t.get('cost'))}</span>")
        if link:
            body.append(f"<a href=\"{esc(link)}\" target=\"_blank\" rel=\"noopener\">🔗 {esc(link)}</a>")
        blocks.append(
            f"<div class=\"card\"><span class=\"tag\">🚗 {esc(label)}</span><div class=\"row\">{''.join(body)}</div></div>"
        )
    return "<section><h2>🚗 Trasporti</h2>" + "".join(blocks) + "</section>"


def _travel_tail_generic(generic: str) -> str:
    """Riusa hl/ts/qs/ap dal link Google Travel generico (fissano date e zona)."""
    tail = ""
    for p in ("hl", "ts", "qs", "ap"):
        m = re.search(r"[?&]" + p + r"=[^&]+", generic)
        if m:
            tail += "&" + m.group(0).lstrip("?&")
    return tail


def acc_specific_link(a: dict) -> str:
    """Link di ricerca Google Travel per l'albergo SPECIFICO (nome in q=)
    così compare come primo risultato, con date/parametri dal link generico.
    Overridabile con 'search_link'."""
    if a.get("search_link"):
        return a["search_link"]
    name = a.get("name", "")
    if not name:
        return a.get("link", "")
    name_clean = re.sub(r"\s*\([^)]*(scelt|candidato|selected)[^)]*\)\s*$", "", name, flags=re.I).strip()
    city = re.sub(r"\s*\(.*?\)\s*$", "", a.get("city", "")).strip()
    q = quote_plus(f"{name_clean} hotels in {city}".replace("  ", " "))
    url = f"https://www.google.com/travel/search?q={q}"
    tail = _travel_tail_generic(a.get("link", ""))
    return url + tail


def section_accommodations(d: dict) -> str:
    accs = d.get("accommodations") or []
    if not accs:
        return ""
    blocks = []
    for a in accs:
        spec = acc_specific_link(a)
        head = esc(a.get("name", "Alloggio"))
        if spec:
            head = f"<a href=\"{esc(spec)}\" target=\"_blank\" rel=\"noopener\">{head}</a>"
        rows = []
        for k, lab in (("city", "📍"), ("dates", "📅"), ("address", "🏠"), ("cost", "💶"), ("note", "📝")):
            if a.get(k):
                rows.append(f"<div class=\"muted\">{lab} {esc(a.get(k))}</div>")
        if a.get("link") and a["link"] != spec:
            rows.append(f"<div class=\"muted\">🏨 Tutte le opzioni in zona: "
                        f"<a href=\"{esc(a['link'])}\" target=\"_blank\" rel=\"noopener\">🔗 {esc(a['link'])}</a></div>")
        blocks.append(f"<div class=\"card\"><b>{head}</b>{''.join(rows)}</div>")
    return "<section><h2>🏨 Alloggio</h2>" + "".join(blocks) + "</section>"


def score_badge(score: str) -> str:
    try:
        v = float(str(score).replace(",", "."))
    except Exception:
        return f"<span class=\"score\" style=\"background:#98a2b3\">{esc(score)}</span>"
    if v >= 4.7:
        return f"<span class=\"score s-49\">{esc(score)}</span>"
    if v >= 4.5:
        return f"<span class=\"score s-47\">{esc(score)}</span>"
    return f"<span class=\"score s-42\">{esc(score)}</span>"


def verdict_cls(v: str) -> str:
    v = (v or "").lower()
    if "eccellente" in v:
        return " sv-ot"
    if "ottimo" in v:
        return " sv-ot"
    return " sv-bu"


def section_neighborhoods(d: dict) -> str:
    nbs = d.get("neighborhoods") or []
    if not nbs:
        return ""
    rows = []
    for n in nbs:
        rows.append(
            f"<tr><td><b>{esc(n.get('name', ''))}</b></td>"
            f"<td>{score_badge(n.get('score', ''))}</td>"
            f"<td class=\"{verdict_cls(n.get('verdict', ''))}\">{esc(n.get('verdict', ''))}</td>"
            f"<td>{esc(n.get('avg_price_night', ''))}</td>"
            f"<td>{esc(n.get('known_for', ''))}</td></tr>"
        )
    return ("<section><h2>📍 Quartieri — info da Google Hotels</h2>"
            "<table><thead><tr><th>Quartiere</th><th>Punteggio pos.</th><th>Giudizio</th>"
            "<th>Prezzo medio/notte</th><th>Noto per</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></section>")


def section_itinerary(d: dict) -> str:
    days = d.get("itinerary") or []
    if not days:
        return ""
    parts = []
    for day in days:
        daynum = day.get("day", "")
        head = esc(day.get("date") or (f"Giorno {daynum}" if daynum else ""))
        slots = []
        for key, emoji in (("morning", "☀️ Mattina"), ("afternoon", "🌤️ Pomeriggio"), ("evening", "🌙 Sera")):
            items = day.get(key) or []
            if not items:
                continue
            body = "".join(link_or_text(i) for i in items)
            slots.append(f"<div class=\"slot\"><h4>{emoji}</h4>{body}</div>")
        parts.append(f"<div class=\"day\"><div class=\"dayhead\">📅 {head}</div>{''.join(slots)}</div>")
    return "<section><h2>📅 Itinerario</h2>" + "".join(parts) + "</section>"


def section_events(d: dict) -> str:
    evs = d.get("events") or []
    evs = [e for e in evs if e.get("name")]
    if not evs:
        return ""
    rows = []
    for e in evs:
        name = esc(e.get("name", ""))
        if e.get("link"):
            name = f"<a href=\"{esc(e['link'])}\" target=\"_blank\" rel=\"noopener\">{name}</a>"
        rows.append(f"<div class=\"card\"><b>🎟️ {name}</b>"
                    f"<div class=\"muted\">📅 {esc(e.get('date', ''))} · 💶 {esc(e.get('cost', ''))}</div></div>")
    return "<section><h2>🎟️ Eventi</h2>" + "".join(rows) + "</section>"


def section_budget(d: dict) -> str:
    b = d.get("budgetSummary")
    if not b or not isinstance(b, dict):
        return ""
    rows = []
    for k, v in b.items():
        tag = "TOTALE" if k.strip().upper().startswith("TOTALE") else ""
        cls = " style=\"color:var(--accent);font-weight:800\"" if tag else ""
        rows.append(f"<tr><td>{esc(k)}</td><td{cls}>{esc(v)}</td></tr>")
    return "<section><h2>💰 Budget</h2><table class=\"budget\"><tbody>" + "".join(rows) + "</tbody></table></section>"


def section_notes(d: dict) -> str:
    if not d.get("notes"):
        return ""
    return f"<section><h2>📌 Note</h2><p class=\"muted\">{esc(d.get('notes'))}</p></section>"


def section_booking(d: dict) -> str:
    outbound = next((t for t in (d.get("transports") or []) if t.get("type") == "outbound" and t.get("link")), None)
    acc = (d.get("accommodations") or [None])[0]
    btns = []
    if outbound:
        btns.append(f"<a class=\"btn primary\" href=\"{esc(outbound['link'])}\" target=\"_blank\" rel=\"noopener\">✈️ Prenota il volo</a>")
    if acc and acc.get("link"):
        btns.append(f"<a class=\"btn ghost\" href=\"{esc(acc['link'])}\" target=\"_blank\" rel=\"noopener\">🏨 Prenota l'hotel</a>")
    return "".join(btns) if btns else ""


def render(d: dict) -> str:
    name = d.get("name", "Vacanza")
    accent, accent2 = accent_for(name)
    tpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    repl = {
        "{{hero_name}}": esc(name),
        "{{hero_dates}}": esc(d.get("dates", "")),
        "{{hero_people}}": esc(d.get("people", "")),
        "{{hero_budget}}": esc(d.get("budget", "")),
        "{{hero_destination}}": esc(d.get("destination", "")),
        "{{hero_kicker}}": esc(d.get("kicker", "Piano di viaggio per te e chi viaggia con te")),
        "{{accent}}": accent,
        "{{accent2}}": accent2,
        "{{section_booking}}": section_booking(d),
        "{{section_transports}}": section_transports(d),
        "{{section_accommodations}}": section_accommodations(d),
        "{{section_neighborhoods}}": section_neighborhoods(d),
        "{{section_itinerary}}": section_itinerary(d),
        "{{section_events}}": section_events(d),
        "{{section_budget}}": section_budget(d),
        "{{section_notes}}": section_notes(d),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)
    left = re.findall(r"\{\{[^}]+\}\}", tpl)
    if left:
        sys.stderr.write(f"WARN: placeholder non sostituiti: {sorted(set(left))}\n")
    return tpl


def main() -> int:
    ap = argparse.ArgumentParser(description="Rende HTML autonomo da vacanza.json.")
    ap.add_argument("json", nargs="?", help="Percorso al vacanza.json")
    ap.add_argument("--out", default=None, help="Percorso HTML output (default: stessa cartella del JSON)")
    args = ap.parse_args()

    if args.json:
        inp = Path(args.json)
    else:
        candidates = sorted(PROJECT_ROOT.glob("output/*/vacanza.json"))
        if not candidates:
            sys.stderr.write("Nessun vacanza.json trovato. Passa un percorso.\n")
            return 1
        inp = candidates[-1]
        sys.stderr.write(f"Usato: {inp}\n")

    data = json.loads(Path(inp).read_text(encoding="utf-8"))
    html_out = render(data)

    if args.out:
        out = Path(args.out)
    else:
        # default: stessa cartella del JSON, file <slug-nome>.html
        out = inp.parent / f"{slugify(data.get('name', 'vacanza'))}.html"

    out.write_text(html_out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())