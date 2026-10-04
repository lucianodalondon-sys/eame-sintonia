#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# PRÉ-VOO DA 022 — SÓ LEITURA, E É ESSE O PONTO
#
# Esta missão autoriza tocar a produção. Autorização não é capacidade, e
# capacidade não é segurança: antes de qualquer DDL é preciso saber o que
# está lá, e — sobretudo — o que o aplicador canónico TENTARIA fazer.
#
# O PERIGO QUE ESTE FICHEIRO EXISTE PARA MEDIR
# --------------------------------------------
# `motor/cadeia_canonica.sh` percorre TODAS as migrations e pula as que já
# estão no livro-razão `public.schema_migracao`. Se esse livro estiver
# vazio em produção, a cadeia tentaria aplicar 001–021 outra vez — e o
# próprio ficheiro avisa, por escrito, o que isso custaria:
#
#     «a 015 tem `add column if not exists fact_geografia_origem`, e a 018
#      APOSENTA essa coluna. Reaplicar a 015 a RESSUSCITARIA.»
#
# `add column if not exists` NÃO devolve «already exists»: ele passa em
# silêncio. Uma coluna aposentada voltaria sem que ninguém visse.
#
#     A MISSÃO PEDE `APPLIED_SET = {022}`,
#     NÃO «provavelmente só a 022».
#
# Por isso este pré-voo lê o livro-razão e imprime, migration a migration,
# o que a cadeia faria. Se a resposta não for exatamente `{022}`, o portão
# fecha e ninguém aplica nada.
#
# NENHUMA ESCRITA. Nem `create table if not exists`, que é DDL na mesma.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${SUPABASE_DB_URL:?falta SUPABASE_DB_URL}"

# Nunca ecoar a URL: um erro do psql pode traze-la dentro da mensagem.
sanitiza() { sed -E 's#postgres(ql)?://[^ ]*#<URL_OMITIDA>#g'; }

q() { psql "$URL" -X -q -A -t -F '|' -v ON_ERROR_STOP=1 -c "$1" 2>/tmp/e || {
        echo "ERRO_DE_LEITURA"; sanitiza </tmp/e | head -3; }; }

echo "=== PRE-VOO 022 · SOMENTE LEITURA ==="
echo "medido_em=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# ── A · A CASA DO DERIVADO JA EXISTE? ─────────────────────────────────
echo "-- A · derived_artifact"
echo "existe=$(q "select count(*) from information_schema.tables
                  where table_schema='public' and table_name='derived_artifact'")"

# ── B · AS PRE-CONDICOES DA 022 ───────────────────────────────────────
# Ela precisa de raw_asset(id, sha256) e vai criar um unique sobre esse par.
echo
echo "-- B · pre-condicoes em raw_asset"
q "select column_name||' '||data_type||' null='||is_nullable
   from information_schema.columns
   where table_schema='public' and table_name='raw_asset'
     and column_name in ('id','sha256') order by column_name"
echo "constraints_ja_com_os_nomes_da_022=$(q "
   select count(*) from pg_constraint
   where conname in ('raw_asset_id_e_sha_juntos',
                     'o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo',
                     'derivacao_e_unica_por_regua')")"

# ── C · O ESTOQUE, ANTES ──────────────────────────────────────────────
echo
echo "-- C · estoque BEFORE"
echo "collection_run_total=$(q "select count(*) from public.collection_run")"
echo "collection_run_IT=$(q "select count(*) from public.collection_run
                             where source_country='IT'")"
echo "raw_asset_total=$(q "select count(*) from public.raw_asset")"
echo "raw_asset_IT=$(q "select count(*) from public.raw_asset a
                        join public.collection_run r on r.run_id=a.run_id
                        where r.source_country='IT'")"

# ── D · O LIVRO-RAZAO, E O QUE A CADEIA FARIA ─────────────────────────
# E aqui que o portao se decide.
echo
echo "-- D · livro-razao do aplicador"
tem_livro=$(q "select count(*) from information_schema.tables
               where table_schema='public' and table_name='schema_migracao'")
echo "schema_migracao_existe=$tem_livro"

if [ "$tem_livro" = "1" ]; then
  echo "versoes_no_livro=$(q "select count(*) from public.schema_migracao")"
  q "select versao||' '||resultado from public.schema_migracao order by versao" \
    | sed 's/^/  /'
else
  echo "  ⚠️  O LIVRO NAO EXISTE. A cadeia canonica cria-o na primeira corrida"
  echo "     e, com ele vazio, TENTARIA aplicar TODAS as migrations."
fi

echo
echo "-- D2 · o que a cadeia canonica TENTARIA aplicar, hoje"
tentaria=""
for f in $(ls "$RAIZ"/supabase/migrations/*.sql | grep -v '/008_' | sort); do
  num=$(basename "$f" | cut -c1-3)
  ja=""
  [ "$tem_livro" = "1" ] && ja=$(q "select 1 from public.schema_migracao
                                    where versao='$num'")
  if [ -n "$ja" ]; then
    echo "  $num SKIP (no livro)"
  else
    echo "  $num TENTARIA APLICAR"
    tentaria="$tentaria $num"
  fi
done

# ── E · O PORTAO ──────────────────────────────────────────────────────
echo
echo "=== PORTAO ==="
conjunto=$(echo $tentaria | tr -s ' ')
echo "APPLIED_SET_PREVISTO={$(echo $conjunto | tr ' ' ',')}"
if [ "$conjunto" = "022" ]; then
  echo "PORTAO=ABERTO · a cadeia aplicaria SOMENTE a 022"
  exit 0
fi
echo "PORTAO=FECHADO"
echo "A cadeia canonica aplicaria mais do que a 022. NAO APLICAR."
echo "Lembrete do proprio motor/cadeia_canonica.sh: reaplicar a 015"
echo "RESSUSCITARIA uma coluna que a 018 aposentou — e `add column if not"
echo "exists` passa em silencio, sem dizer «already exists»."
exit 1
