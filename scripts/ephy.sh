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

# O cold start da MISSAO 08 pegou um "connection reset by peer" na primeira tentativa
# e sucesso na segunda. Com `set -e` isso derrubava a cadeia inteira. Falhar fechado
# esta certo; falhar fechado por um reset transitorio custa uma execucao a toa.
retry() {
  local n=0
  until "$@"; do
    n=$((n+1))
    [ "$n" -ge 4 ] && { echo "falhou apos $n tentativas: $*" >&2; return 1; }
    sleep $((2 ** n))
  done
}

download() {
  mkdir -p "$DEST"
  local meta url
  meta="$(retry curl -sS -m 60 -A "$UA" "https://www.data.gouv.fr/api/1/datasets/$DATASET/")"
  url="$(printf '%s' "$meta" | python3 -c '
import json,sys
d=json.load(sys.stdin)
c=[r for r in d["resources"] if r["format"]=="zip" and "utf8" in r["title"]]
if not c: sys.exit("nenhum recurso CSV utf8 encontrado")
print(c[0]["url"])')"
  echo "dataset atualizado em: $(printf '%s' "$meta" | python3 -c 'import json,sys;print(json.load(sys.stdin)["last_update"])')"
  retry curl -sSL -m 300 -A "$UA" -o "$DEST/ephy.zip" "$url"
  (cd "$DEST" && unzip -oq ephy.zip)
  ls -1 "$DEST"/*.csv
}

case "${1:-download}" in
  download) download ;;
  *) echo "uso: $0 download [destino]" >&2; exit 2 ;;
esac
