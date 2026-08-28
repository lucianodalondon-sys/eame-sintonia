#!/usr/bin/env bash
# EU-T4-001 — EU Publications Office / CELLAR
# Coleta repetível de atos regulatórios da UE (camada EU ACTIVE SUBSTANCE) e do texto
# integral de um ato em qualquer língua oficial.
#
#   ./scripts/cellar.sh sparql "<query SPARQL>"        -> resultados JSON
#   ./scripts/cellar.sh act <CELEX> <iso3>             -> texto integral XHTML
#   ./scripts/cellar.sh substances <ano>               -> atos do ano sobre active substance
#
# Sem chave de API. Endpoint público do Publications Office.
set -euo pipefail
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
SPARQL_EP="https://publications.europa.eu/webapi/rdf/sparql"
CELLAR="https://publications.europa.eu/resource/celex"

sparql() {
  curl -sS -m 180 -A "$UA" -G "$SPARQL_EP" \
    --data-urlencode "query=$1" \
    --data-urlencode "format=application/sparql-results+json"
}

act() { # $1=CELEX  $2=iso3 (eng|fra|spa|ita|...)
  curl -sSL -m 120 -A "$UA" \
    -H "Accept: application/xhtml+xml" -H "Accept-Language: ${2:-eng}" \
    "$CELLAR/$1"
}

substances() { # $1 = ano (ex.: 2026)
  local year="${1:?ano obrigatorio}"
  sparql "PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?celex ?date ?title WHERE {
  ?w cdm:resource_legal_id_celex ?celex .
  FILTER(STRSTARTS(STR(?celex),\"3${year}R\"))
  ?w cdm:work_date_document ?date .
  ?e cdm:expression_belongs_to_work ?w ;
     cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ;
     cdm:expression_title ?title .
  FILTER(CONTAINS(LCASE(STR(?title)),\"active substance\"))
} ORDER BY DESC(?date) LIMIT 200"
}

case "${1:-}" in
  sparql)     sparql "$2" ;;
  act)        act "$2" "${3:-eng}" ;;
  substances) substances "${2:-2026}" ;;
  *) echo "uso: $0 {sparql <query>|act <CELEX> [iso3]|substances <ano>}" >&2; exit 2 ;;
esac
