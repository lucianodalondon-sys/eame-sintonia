#!/usr/bin/env bash
# OVERNIGHT WATCH — registra o estado das branches. NAO faz merge. NAO faz push.
# Uso:  bash scripts/overnight_watch.sh [caminho-do-log]
# Cron: */10 * * * * bash scripts/overnight_watch.sh
#
# A decisao de incorporar QUALQUER coisa continua exigindo os criterios do
# briefing (§8). Este script so mede e anota.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${1:-$REPO/OVERNIGHT-HEADS.log}"
cd "$REPO" || exit 1

git fetch --all --prune --quiet 2>/dev/null

TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "### $TS"
  git for-each-ref \
    --sort=-committerdate \
    --format='%(committerdate:iso8601-strict)  %(objectname:short)  %(refname:short)' \
    refs/remotes/origin \
  | awk '$1 >= "'"$(date -u -d '36 hours ago' +%Y-%m-%dT%H:%M:%S)"'"'
  echo
} >> "$LOG"

# Alerta em stdout se uma branch de integracao paralela aparecer no remoto.
git for-each-ref --format='%(refname:short)' refs/remotes/origin \
  | grep -E 'meeting-portal-(integration-build|final|contradictions)' \
  | while read -r b; do
      echo "AVISO: branch de integracao paralela publicada -> $b"
    done

exit 0
