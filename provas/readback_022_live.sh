#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# READBACK DA 022 — aplicar não é provar
#
# O aplicador diz `MIGRATION_022=PASS` quando o `psql` não devolveu erro.
# Isso é a opinião do cliente sobre o que aconteceu, e é exatamente a
# opinião que não vale — foi a lição que esta casa aprendeu em G-42:
#
#     SQL ACEITE NÃO É LINHA GRAVADA.
#     E DDL ACEITE NÃO É ESQUEMA VERIFICADO.
#
# Este ficheiro pergunta ao CATÁLOGO do Postgres, objeto a objeto, se cada
# trava desenhada existe mesmo. E cobra a contagem que tem de ser zero:
#
#     A MIGRATION NÃO CRIA HISTÓRIA.
#
# Só leitura. Nenhuma escrita, nenhuma correção no improviso.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail
URL="${SUPABASE_DB_URL:?falta SUPABASE_DB_URL}"
falhou=0

q() { psql "$URL" -X -q -A -t -v ON_ERROR_STOP=1 -c "$1" 2>/dev/null; }

exigir() {  # exigir <nome> <esperado> <sql>
  local got; got="$(q "$3")"
  if [ "$got" = "$2" ]; then
    printf '  PASS  %-52s %s\n' "$1" "$got"
  else
    printf '  FAIL  %-52s esperado=%s obtido=%s\n' "$1" "$2" "$got"
    falhou=1
  fi
}

echo "=== READBACK 022 · SOMENTE LEITURA ==="

exigir "a_tabela_existe" "1" \
  "select count(*) from information_schema.tables
   where table_schema='public' and table_name='derived_artifact'"

# ── AS COLUNAS ────────────────────────────────────────────────────────
for c in raw_asset_id parent_sha256 kind producer producer_version \
         pipeline_version parameters parameters_hash serie_posicao sha256 \
         bytes media_type storage_path derived_at derivation_batch; do
  exigir "coluna_$c" "1" \
    "select count(*) from information_schema.columns
     where table_schema='public' and table_name='derived_artifact'
       and column_name='$c'"
done

# ── AS TRAVAS QUE FAZEM A TABELA VALER ────────────────────────────────
# A chave estrangeira COMPOSTA: o pai por id e o pai por sha sao o mesmo.
exigir "fk_composta_pai_id_e_pai_sha" "1" \
  "select count(*) from pg_constraint
   where conname='o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo' and contype='f'"

exigir "fk_e_ON_DELETE_RESTRICT" "r" \
  "select confdeltype from pg_constraint
   where conname='o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo'"

exigir "unique_da_receita" "1" \
  "select count(*) from pg_constraint
   where conname='derivacao_e_unica_por_regua' and contype='u'"

exigir "unique_do_pai_no_raw_asset" "1" \
  "select count(*) from pg_constraint
   where conname='raw_asset_id_e_sha_juntos' and contype='u'"

exigir "storage_path_unico" "1" \
  "select count(*) from pg_constraint c
   join pg_class t on t.oid=c.conrelid
   where t.relname='derived_artifact' and c.contype='u'
     and pg_get_constraintdef(c.oid) like '%storage_path%'"

for k in sha256_do_filho_tem_formato sha256_do_pai_tem_formato \
         parameters_hash_tem_formato derivado_declara_quando_nasceu; do
  exigir "check_$k" "1" \
    "select count(*) from pg_constraint where conname='$k' and contype='c'"
done

for i in derived_parent_idx derived_raw_idx derived_kind_idx derived_sha_idx; do
  exigir "index_$i" "1" \
    "select count(*) from pg_indexes
     where schemaname='public' and indexname='$i'"
done

# ── A MIGRATION NAO CRIA HISTORIA ─────────────────────────────────────
exigir "linhas_logo_apos_a_migration" "0" \
  "select count(*) from public.derived_artifact"

# ── E O QUE ELA NAO PODIA TER TOCADO ──────────────────────────────────
# Ate aqui so houve DDL. Se estes numeros mudaram, alguem escreveu dado.
echo "-- invariantes (comparar com o BEFORE do pre-voo)"
echo "  collection_run_total=$(q 'select count(*) from public.collection_run')"
echo "  collection_run_IT=$(q "select count(*) from public.collection_run
                               where source_country='IT'")"
echo "  raw_asset_total=$(q 'select count(*) from public.raw_asset')"

echo
if [ "$falhou" = "0" ]; then
  echo "READBACK_022=PASS · o esquema esta como foi desenhado, e vazio"
  exit 0
fi
echo "READBACK_022=FAIL · PARAR. Nao consertar producao no improviso."
exit 1
