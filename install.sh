#!/usr/bin/env bash
# install.sh — Installa o aggiorna la skill travel-planner in opencode.
#
# Copia skills/travel-planner/ (il router del framework) in
# ~/.config/opencode/skills/travel-planner/, così `/travel-planner` è
# disponibile in ogni progetto.
#
# Uso:
#   ./install.sh          # installa/aggiorna
#   ./install.sh --force  # aggiorna anche se identico
#   ./install.sh --dry    # mostra cosa farebbe senza farlo
set -euo pipefail

SKILL_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/travel-planner"
SKILL_NAME="travel-planner"

case "$(uname -s)" in
  Darwin) CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/Library/Application Support/opencode}" ;;
  *)      CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode" ;;
esac

SKILL_DST="$CONFIG_DIR/skills/$SKILL_NAME"
FORCE=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --dry)   DRY=1 ;;
    -h|--help)
      sed -n '1,12p' "${BASH_SOURCE[0]}"
      exit 0
      ;;
    *) echo "Argomento sconosciuto: $arg (usa --force, --dry, -h)" >&2; exit 1 ;;
  esac
done

if [ ! -f "$SKILL_SRC/SKILL.md" ]; then
  echo "ERRORE: $SKILL_SRC/SKILL.md non trovato. Esegui dalla root del progetto." >&2
  exit 1
fi

mkdir -p "$CONFIG_DIR/skills"
if [ ! -d "$CONFIG_DIR/skills" ]; then
  echo "ERRORE: impossibile creare $CONFIG_DIR/skills" >&2
  exit 1
fi

if [ "$DRY" = 1 ]; then
  echo "[dry] Sorgente: $SKILL_SRC"
  echo "[dry] Destinazione: $SKILL_DST"
  if [ -f "$SKILL_DST/SKILL.md" ] && diff -q "$SKILL_SRC/SKILL.md" "$SKILL_DST/SKILL.md" >/dev/null 2>&1; then
    echo "[dry] Skill gia' aggiornata (nessuna modifica)."
  else
    echo "[dry] Verrebbe installata/aggiornata."
  fi
  exit 0
fi

if [ -f "$SKILL_DST/SKILL.md" ] && [ "$FORCE" != 1 ] \
   && diff -q "$SKILL_SRC/SKILL.md" "$SKILL_DST/SKILL.md" >/dev/null 2>&1; then
  echo "Skill '$SKILL_NAME' gia' aggiornata. Nulla da fare (usa --force per reinstallare)."
  exit 0
fi

rm -rf "$SKILL_DST"
cp -R "$SKILL_SRC" "$SKILL_DST"
echo "OK: skill '$SKILL_NAME' installata/aggiornata in $SKILL_DST"
echo "Nota: riavvia la sessione opencode (o /skills) per ricaricarla."
