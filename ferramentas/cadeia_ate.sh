#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# A CADEIA CANÓNICA, MAS SÓ ATÉ À MIGRATION N — DA-19 (26/09): «migrações
# SEPARADAS e na ordem: 034 -> 035 -> 036, uma por vez».
#
#   uso:  ferramentas/cadeia_ate.sh <NNN> <PSQL_URL>
#
# `motor/cadeia_canonica.sh migrations` aplica TODAS as pendentes de uma vez.
# Isto NÃO a reescreve nem lhe acrescenta um modo: monta uma pasta de etapa com
# uma CÓPIA do mesmo `cadeia_canonica.sh` e só os ficheiros `supabase/migrations/`
# com número <= NNN, COPIADOS BYTE A BYTE (o sha256 que vai para o livro-razão é
# o mesmo que a cadeia inteira gravaria), e corre-a lá. A pasta apaga-se no fim.
#
#     UMA ORDEM SÓ: a da cadeia. Isto só decide ATÉ ONDE.
#
# Nunca ecoa a URL.
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ATE="${1:?uso: cadeia_ate.sh <NNN> <PSQL_URL>}"
URL="${2:?falta a URL do banco}"
case "$ATE" in [0-9][0-9][0-9]) ;; *) echo "ATE_INVALIDO=$ATE (tres digitos)"; exit 2;; esac

ETAPA="$(mktemp -d)"
trap 'rm -rf "$ETAPA"' EXIT
mkdir -p "$ETAPA/motor" "$ETAPA/supabase/migrations"
cp -p "$RAIZ/motor/cadeia_canonica.sh" "$ETAPA/motor/"
n=0
for f in "$RAIZ"/supabase/migrations/*.sql; do
  num=$(basename "$f" | cut -c1-3)
  if [ "$num" \< "$ATE" ] || [ "$num" = "$ATE" ]; then
    cp -p "$f" "$ETAPA/supabase/migrations/"; n=$((n+1))
  fi
done
ls "$ETAPA/supabase/migrations/${ATE}_"*.sql >/dev/null 2>&1 || { echo "ATE_SEM_FICHEIRO=$ATE"; exit 2; }
echo "CADEIA_ATE=$ATE FICHEIROS=$n"
bash "$ETAPA/motor/cadeia_canonica.sh" migrations "$URL"
