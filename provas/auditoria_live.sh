#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# AUDITORIA DA PRODUÇÃO — SÓ SELECT, E É ESSE O PONTO
#
# Substitui o `canario-022`, que era uma porta de MISSÃO ÚNICA e ficou com
# capacidade de escrever produção depois de a missão ter terminado.
#
#     MISSÃO ONE-SHOT TERMINOU → PORTA ONE-SHOT É FECHADA.
#     Não vira daemon. Não vira coletor. Não vira caminho permanente.
#
# O que sobrou tem valor operacional e nenhum poder: ler o livro-razão das
# migrations, comparar cada SHA com o ficheiro do repositório, e conferir que o
# canário continua a ser UM.
#
# Ele recebe `SUPABASE_DB_URL` e mais nada. Sem `SUPABASE_SECRET_KEY`, sem
# `SUPABASE_URL` — aquilo só existia para escrever no Storage, e já não há o
# que escrever.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${SUPABASE_DB_URL:?falta SUPABASE_DB_URL}"
falhou=0

sanitiza() { sed -E 's#postgres(ql)?://[^ ]*#<URL_OMITIDA>#g'; }
q() { psql "$URL" -X -q -A -t -F '|' -v ON_ERROR_STOP=1 -c "$1" 2>/tmp/e \
        || { echo "ERRO"; sanitiza </tmp/e | head -2; }; }

ok()  { printf '  PASS  %-46s %s\n' "$1" "${2:-}"; }
mal() { printf '  FAIL  %-46s %s\n' "$1" "${2:-}"; falhou=1; }

echo "=== AUDITORIA LIVE · SOMENTE SELECT ==="
echo "medida_em=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── A · CADA MIGRATION APLICADA CONTINUA A SER O MESMO FICHEIRO ───────
# É a lei nova: versão no livro não basta; versão E SHA têm de bater.
echo
echo "-- A · livro-razao x ficheiros do repositorio"
printf '  %-6s %-12s %-18s %-18s %s\n' VERSAO RESULTADO LEDGER_SHA REPO_SHA BATE
divergentes=0
ausentes=0
while IFS='|' read -r versao resultado ledger_sha; do
  [ -z "$versao" ] && continue
  f=$(ls "$RAIZ"/supabase/migrations/${versao}_*.sql 2>/dev/null | head -1)
  if [ -z "$f" ]; then
    printf '  %-6s %-12s %-18s %-18s %s\n' "$versao" "$resultado" \
      "${ledger_sha:0:16}" "-" "FICHEIRO_AUSENTE"
    ausentes=$((ausentes + 1)); continue
  fi
  repo_sha=$(sha256sum "$f" | cut -d' ' -f1)
  if [ "$repo_sha" = "$ledger_sha" ]; then
    bate=SIM
  else
    bate=NAO; divergentes=$((divergentes + 1))
  fi
  printf '  %-6s %-12s %-18s %-18s %s\n' "$versao" "$resultado" \
    "${ledger_sha:0:16}" "${repo_sha:0:16}" "$bate"
done < <(q "select versao, resultado, sha256 from public.schema_migracao
            order by versao")

echo
[ "$divergentes" = "0" ] \
  && ok "nenhuma migration aplicada mudou de conteudo" \
  || mal "LEGACY_APPLIED_MIGRATION_DRIFT" "$divergentes versao(oes)"
[ "$ausentes" = "0" ] \
  && ok "todo registo do livro tem ficheiro no repositorio" \
  || mal "ha registo sem ficheiro" "$ausentes"

# ── B · A 022, NOMEADAMENTE ───────────────────────────────────────────
echo
echo "-- B · a 022"
sha_022=$(q "select sha256 from public.schema_migracao where versao='022'")
repo_022=$(sha256sum "$RAIZ/supabase/migrations/022_o_derivado_ganha_casa.sql" \
           | cut -d' ' -f1)
echo "  LEDGER=$sha_022"
echo "  REPO  =$repo_022"
[ "$sha_022" = "$repo_022" ] \
  && ok "a 022 continua byte a byte a que foi aplicada" \
  || mal "a 022 MUDOU desde que foi aplicada"
[ "$(q "select resultado from public.schema_migracao where versao='022'")" \
  = "APLICADA" ] && ok "a 022 esta como APLICADA no livro" \
                 || mal "a 022 nao esta APLICADA"

# ── C · O CANARIO CONTINUA A SER UM ───────────────────────────────────
echo
echo "-- C · o estado do canario"
n_run=$(q "select count(*) from public.collection_run where run_id like 'IT-CANARY-%'")
n_it=$(q "select count(*) from public.collection_run where source_country='IT'")
n_raw=$(q "select count(*) from public.raw_asset a
           join public.collection_run r on r.run_id=a.run_id
           where r.source_country='IT'")
n_der=$(q "select count(*) from public.derived_artifact")
echo "  IT-CANARY runs=$n_run · collection_run IT=$n_it · raw_asset IT=$n_raw"
echo "  derived_artifact=$n_der"
[ "$n_run" = "1" ] && ok "existe UMA corrida canario, e so uma" \
                   || mal "numero de corridas canario" "$n_run"
[ "$n_raw" = "1" ] && ok "um bruto italiano" || mal "brutos italianos" "$n_raw"
[ "$n_der" = "1" ] && ok "um derivado" || mal "derivados" "$n_der"

q "select 'run='||run_id||' status='||status from public.collection_run
   where run_id like 'IT-CANARY-%'" | sed 's/^/  /'
q "select 'derived id='||id||' raw_asset_id='||raw_asset_id||
          ' sha='||substring(sha256,1,16)||' bytes='||bytes
   from public.derived_artifact" | sed 's/^/  /'

echo
if [ "$falhou" = "0" ]; then
  echo "AUDITORIA_LIVE=PASS"; exit 0
fi
echo "AUDITORIA_LIVE=FAIL"; exit 1
