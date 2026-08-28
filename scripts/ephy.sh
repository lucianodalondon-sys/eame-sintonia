#!/usr/bin/env bash
# FR-T4-001 — ANSES E-Phy (catálogo francês de produtos fitofarmacêuticos)
# Dados abertos oficiais, Licence Ouverte, atualização semanal, via data.gouv.fr.
# Camada: NATIONAL PRODUCT AUTHORIZATION (nunca confundir com EU ACTIVE SUBSTANCE).
#
#   ./scripts/ephy.sh download [destino]   -> baixa e descompacta o pacote CSV UTF-8 mais recente
#
# A URL do recurso muda a cada publicação semanal, por isso é resolvida pela API
# do data.gouv.fr em vez de ficar fixa no script.
set -euo pipefail
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
DATASET="575e9fac88ee38072a640390"
DEST="${2:-data/raw/FR-T4-001}"

download() {
  mkdir -p "$DEST"
  local meta url
  meta="$(curl -sS -m 60 -A "$UA" "https://www.data.gouv.fr/api/1/datasets/$DATASET/")"
  url="$(printf '%s' "$meta" | python3 -c '
import json,sys
d=json.load(sys.stdin)
c=[r for r in d["resources"] if r["format"]=="zip" and "utf8" in r["title"]]
if not c: sys.exit("nenhum recurso CSV utf8 encontrado")
print(c[0]["url"])')"
  echo "dataset atualizado em: $(printf '%s' "$meta" | python3 -c 'import json,sys;print(json.load(sys.stdin)["last_update"])')"
  curl -sSL -m 300 -A "$UA" -o "$DEST/ephy.zip" "$url"
  (cd "$DEST" && unzip -oq ephy.zip)
  ls -1 "$DEST"/*.csv
}

case "${1:-download}" in
  download) download ;;
  *) echo "uso: $0 download [destino]" >&2; exit 2 ;;
esac
