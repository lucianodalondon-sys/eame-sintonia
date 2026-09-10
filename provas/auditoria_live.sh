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

# ═══════════════════════════════════════════════════════════════════════
# D · O CENSO DA 025 — SÓ SELECT, E EXISTE PARA UMA MISSÃO SÓ
#
# A C-LIVE-025 exige congelar o estado ANTES de escrever e prová-lo igual
# DEPOIS. Contagem não chega: o contrato da 025 é que NENHUM `raw_asset.id`
# muda, e um conjunto não se prova com um número.
#
#     COUNT IGUAL NÃO É CONJUNTO IGUAL.
#
# Este bloco vive num ramo operacional temporário e não entra na fundação.
# Quando a missão fechar, ele sai com o ramo — porta de missão única é porta
# que se fecha.
# ═══════════════════════════════════════════════════════════════════════
echo
echo "-- D · censo da 025 (BEFORE/AFTER, as mesmas perguntas)"
echo "  CENSO_MEDIDO_EM=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

for par in \
  "RAW_ASSET_COUNT|select count(*) from public.raw_asset" \
  "RAW_ASSET_MIN_ID|select coalesce(min(id)::text,'-') from public.raw_asset" \
  "RAW_ASSET_MAX_ID|select coalesce(max(id)::text,'-') from public.raw_asset" \
  "RAW_ASSET_DISTINCT_IDS|select count(distinct id) from public.raw_asset" \
  "RAW_ASSET_DISTINCT_STORAGE_PATHS|select count(distinct storage_path) from public.raw_asset" \
  "PRESERVED_RAW_ASSETS|select count(*) from public.raw_asset where preserved" \
  "NULL_STORAGE_PATH|select count(*) from public.raw_asset where storage_path is null" \
  "BLANK_STORAGE_PATH|select count(*) from public.raw_asset where btrim(coalesce(storage_path,'x'))=''" \
  "NULL_SHA256|select count(*) from public.raw_asset where sha256 is null" \
  "INVALID_SHA256|select count(*) from public.raw_asset where sha256 is not null and btrim(sha256) !~ '^[0-9a-f]{64}\$'" \
  ; do
  echo "  ${par%%|*}=$(q "${par#*|}")"
done

# O CONJUNTO, e não um resumo dele. O md5 serve para comparar de relance; a
# lista inteira está aqui para que a comparação seja conferível por gente.
echo "  RAW_ASSET_ID_SET_MD5=$(q "select coalesce(md5(string_agg(id::text, ',' order by id)),'-') from public.raw_asset")"
echo "  RAW_ASSET_ID_SET_INICIO=$(q "select coalesce(string_agg(id::text, ',' order by id),'-') from public.raw_asset" | cut -c1-160)"
echo "  RAW_ASSET_ID_SET_FIM=$(q "select coalesce(string_agg(id::text, ',' order by id),'-') from public.raw_asset" | tail -c 160)"

# ── O QUE A 025 CRIA, E O QUE A 026 CRIARIA ──────────────────────────
echo "  STORAGE_OBJECT_EXISTS=$(q "select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='storage_object' and c.relkind='r'")"
echo "  STORAGE_OBJECT_ROWS=$(q "select case when to_regclass('public.storage_object') is null then '-' else (select count(*)::text from public.storage_object) end")"
echo "  STORAGE_OBJECT_RLS=$(q "select coalesce((select relrowsecurity::text from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='storage_object'),'-')")"
for col in storage_object_id identity_state source_id document_key document_key_basis attempts last_attempt_at; do
  echo "  RAW_ASSET_TEM_$col=$(q "select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='$col'")"
done
echo "  LINKED_RAW_ASSETS=$(q "select case when (select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='storage_object_id')=0 then '-' else (select count(*)::text from public.raw_asset where storage_object_id is not null) end")"
echo "  PRESERVED_WITHOUT_OBJECT=$(q "select case when (select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='storage_object_id')=0 then '-' else (select count(*)::text from public.raw_asset where preserved and storage_object_id is null) end")"
# A LIGACAO E PELO ENDERECO. Um par que discorde de caminho e a copia errada.
echo "  RAW_STORAGE_PATH_MISMATCHES=$(q "select case when to_regclass('public.storage_object') is null then '-' else (select count(*)::text from public.raw_asset a join public.storage_object o on o.id = a.storage_object_id where o.storage_path is distinct from a.storage_path) end")"
echo "  RAW_STORAGE_SHA_MISMATCHES=$(q "select case when to_regclass('public.storage_object') is null then '-' else (select count(*)::text from public.raw_asset a join public.storage_object o on o.id = a.storage_object_id where o.sha256 is distinct from a.sha256) end")"

# ── AS TRAVAS, LIDAS DE `pg_constraint` E NAO DA PROSA ────────────────
echo "  CONSTRAINTS_DE_RAW_ASSET:"
q "select '    '||conname||' | '||contype||' | convalidated='||convalidated
   from pg_constraint where conrelid='public.raw_asset'::regclass order by conname"
echo "  UNIQUE_STORAGE_PATH_PRESENTE=$(q "select count(*) from pg_indexes where schemaname='public' and tablename='raw_asset' and indexdef ilike '%unique%' and indexdef ilike '%storage_path%'")"

# ── E · A PROVA SECA: O QUE A CADEIA VERIA COMO PENDENTE ──────────────
# O aplicador percorre os ficheiros e salta os que estao no livro-razao. Aqui
# faz-se a mesma conta, sem escrever nada: se aparecer mais do que a 025, o
# portao fecha e ninguem dispara.
echo
echo "-- E · o que a cadeia veria como PENDENTE neste ref"
pendentes=""
for f in "$RAIZ"/supabase/migrations/*.sql; do
  n=$(basename "$f" | cut -c1-3)
  [ "$n" = "008" ] && continue
  no_livro=$(q "select count(*) from public.schema_migracao where versao='$n'")
  [ "$no_livro" = "0" ] && pendentes="$pendentes $n"
done
echo "  MIGRATIONS_PENDENTES=${pendentes:-nenhuma}"
echo "  026_PRESENTE_NESTE_REF=$([ -f "$RAIZ/supabase/migrations/026_a_observacao_ganha_identidade.sql" ] && echo YES || echo NO)"
echo "  026_NO_LIVRO_RAZAO=$(q "select count(*) from public.schema_migracao where versao='026'")"

echo
if [ "$falhou" = "0" ]; then
  echo "AUDITORIA_LIVE=PASS"; exit 0
fi
echo "AUDITORIA_LIVE=FAIL"; exit 1
