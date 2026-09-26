#!/bin/bash
# REPROC-SALA-PLANO — reprocessar o tempo e o lugar da Sala pelo caderno de revisoes (033),
# por passadas ate INSERIDAS=0. A linha original nunca muda; o RAW nunca e tocado; sem rede.
#
#   bash scripts/reproc_sala/reprocessar_sala.sh <pasta-de-saida> [--sala-real]
#
# Precisa no ambiente: SINTONIA_SALA_DSN, SINTONIA_PSQL_EXE, SINTONIA_SALA_BACKEND=POSTGRES.
# Opcionais: LIV (globs dos livros do coletor, ';'), RZ (onde estao os bytes, ';'), PY, VIVA.
# Na Sala real (porta 54330) so corre com --sala-real E com o robo parado (PARAR.flag no vivo).
# Ultima linha: REPROC_SALA=PASS ou REPROC_SALA=FAIL (com o PARAR: que falhou antes).
set -u
OUT=${1:?pasta de saida}
REAL=${2:-}
RAIZ=$(cd "$(dirname "$0")/../.." && pwd)
PY=${PY:-py}
VIVA=${VIVA:-$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1}
LIV=${LIV:-$VIVA/data/collection-ledger/italy/observations.ndjson;$HOME/orca/workspaces/eame-sintonia/*/data/collection-ledger/italy/observations.ndjson}
RZ=${RZ:-$HOME/sintonia-sala-italia/armazem;$HOME/orca/workspaces/eame-sintonia/*}
DSN="$SINTONIA_SALA_DSN"
PASSADAS_MAX=5
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
export HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9   # sem rede
mkdir -p "$OUT"

falha() { echo "PARAR: $*"; echo "REPROC_SALA=FAIL"; exit 1; }
q() { "$SINTONIA_PSQL_EXE" -X -q -A -t -F'|' -v ON_ERROR_STOP=1 -c "$1" "$DSN" | tr -d '\r'; }

# ── 0 · onde estou ────────────────────────────────────────────────────────────
case "$DSN" in
  *:54330/*) [ "$REAL" = "--sala-real" ] || falha "a DSN e a Sala real (54330) e faltou --sala-real" ;;
  *)         [ "$REAL" = "--sala-real" ] && falha "--sala-real, mas a DSN nao e a 54330" ;;
esac
if [ "$REAL" = "--sala-real" ]; then
  [ -f "$VIVA/curadoria/PARAR.flag" ] || falha "o robo nao esta parado (falta $VIVA/curadoria/PARAR.flag)"
fi
echo "0 · codigo: $(git -C "$RAIZ" rev-parse --short HEAD) · DSN porta ${DSN##*:}" | sed -E 's#/.*##'

# ── 1 · validacao da 033: 5 colunas, 3 objetos, 2 gatilhos, livro-razao ───────
COLS=$(q "select string_agg(column_name, ',' order by column_name) from information_schema.columns
          where table_schema='public' and table_name='sala_de_espera' and column_name in
          ('published_at_basis','source_location_basis','completude_tempo_lugar','tempo_lugar_evidencia','janela_declarada')")
[ "$COLS" = "completude_tempo_lugar,janela_declarada,published_at_basis,source_location_basis,tempo_lugar_evidencia" ] \
  || falha "colunas da 033: «$COLS»"
OBJ=$(q "select to_regclass('public.sala_de_espera_revisao') is not null, to_regclass('public.sala_de_espera_gaveta') is not null,
         to_regclass('public.sala_de_espera_atual') is not null")
[ "$OBJ" = "t|t|t" ] || falha "revisao|gaveta|vista: «$OBJ»"
TRG=$(q "select string_agg(pg_get_triggerdef(oid), ' ## ' order by tgname) from pg_trigger
         where tgrelid='public.sala_de_espera_revisao'::regclass and not tgisinternal")
echo "$TRG" | grep -q "BEFORE DELETE OR UPDATE" || falha "gatilho UPDATE/DELETE: «$TRG»"
echo "$TRG" | grep -q "BEFORE TRUNCATE" || falha "gatilho TRUNCATE: «$TRG»"
LIVRO=$(q "select resultado || ' ' || left(sha256, 16) from schema_migracao where versao='033'")
[ "$LIVRO" = "APLICADA b980c76e6b164d93" ] || falha "livro-razao da 033: «$LIVRO»"
echo "1 · 033: 5 colunas · revisao/gaveta/vista · 2 gatilhos · $LIVRO"

# ── 2 · fotografia ANTES ──────────────────────────────────────────────────────
ORIGINAIS="select count(*) || ' ' || md5(string_agg(t::text, E'\n' order by run_id, ordem)) from public.sala_de_espera t"
REVS="select count(*) from public.sala_de_espera_revisao"
VISTA="select json_agg(json_build_object('run_id', run_id, 'ordem', ordem, 'source_id', source_id,
         'published_at', published_at, 'published_at_basis', published_at_basis,
         'source_location', source_location, 'source_location_basis', source_location_basis,
         'fact_time', fact_time, 'fact_time_basis', fact_time_basis,
         'fact_location', fact_location, 'fact_location_basis', fact_location_basis,
         'revisoes', revisoes) order by run_id, ordem) from public.sala_de_espera_atual"
ORIG_ANTES=$(q "$ORIGINAIS"); REVS_ANTES=$(q "$REVS")
q "$VISTA" > "$OUT/vista-antes.json" || falha "vista antes"
echo "2 · antes: linhas+md5 das originais «$ORIG_ANTES» · revisoes $REVS_ANTES"

# ── 3 · plano SEM escrever ────────────────────────────────────────────────────
cd "$RAIZ" || falha "raiz"
$PY -B admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --saida "$OUT/plano.json" > "$OUT/plano.log" 2>&1 \
  || { tail -5 "$OUT/plano.log"; falha "reprocesso sem escrever"; }
[ "$(q "$REVS")" = "$REVS_ANTES" ] || falha "o reprocesso SEM --aplicar escreveu"
conta() { $PY -B -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['CONTA']['$2'])" "$1" 2>/dev/null | tail -1; }
echo "3 · versao do extrator: $($PY -B -c "import json,sys; print(json.load(open(sys.argv[1],encoding='utf-8'))['VERSAO_DO_EXTRATOR'])" "$OUT/plano.json" 2>/dev/null | tail -1)"
echo "3 · plano: linhas $(conta "$OUT/plano.json" LINHAS) · sem livro $(conta "$OUT/plano.json" SEM_LIVRO) · com pagina $(conta "$OUT/plano.json" COM_PAGINA)"

# ── 4 · passadas ate INSERIDAS=0 ──────────────────────────────────────────────
N=0; INS=x
while [ "$INS" != "0" ]; do
  N=$((N + 1))
  [ $N -gt $PASSADAS_MAX ] && falha "$PASSADAS_MAX passadas e ainda insere (o reprocesso nao converge)"
  $PY -B admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --aplicar \
      --saida "$OUT/passada-$N.json" > "$OUT/passada-$N.log" 2>&1 || { tail -5 "$OUT/passada-$N.log"; falha "passada $N"; }
  INS=$(conta "$OUT/passada-$N.json" INSERIDAS)
  echo "4 · passada $N: INSERIDAS $INS · JA_ERAM_ASSIM $(conta "$OUT/passada-$N.json" JA_ERAM_ASSIM)"
done

# ── 5 · fotografia DEPOIS e a vista campo a campo ─────────────────────────────
q "$VISTA" > "$OUT/vista-depois.json" || falha "vista depois"
$PY -B scripts/reproc_sala/comparar_vista.py "$OUT/vista-antes.json" "$OUT/vista-depois.json" "$OUT/comparacao.json" 2>/dev/null \
  || falha "comparar a vista"
REVS_DEPOIS=$(q "$REVS")
echo "5 · revisoes $REVS_ANTES -> $REVS_DEPOIS"

# ── 6 · a ORIGINAL intacta ────────────────────────────────────────────────────
ORIG_DEPOIS=$(q "$ORIGINAIS")
[ "$ORIG_DEPOIS" = "$ORIG_ANTES" ] || falha "as linhas originais mudaram: «$ORIG_ANTES» -> «$ORIG_DEPOIS»"
echo "6 · originais iguais: «$ORIG_DEPOIS»"

# ── 7 · o caderno so acrescenta: UPDATE e DELETE recusados (dentro de BEGIN/ROLLBACK) ──
tenta() {
  "$SINTONIA_PSQL_EXE" -X -q -A -t -v ON_ERROR_STOP=1 "$DSN" 2>&1 <<SQL | tr -d '\r'
begin;
$1;
rollback;
SQL
}
U=$(tenta "update public.sala_de_espera_revisao set valor = valor where (run_id, ordem, campo, revisao) = (select run_id, ordem, campo, revisao from public.sala_de_espera_revisao limit 1)")
echo "$U" | grep -qiE "ERRO(R)?:" || falha "UPDATE na revisao NAO foi recusado: «$U»"
D=$(tenta "delete from public.sala_de_espera_revisao where (run_id, ordem, campo, revisao) = (select run_id, ordem, campo, revisao from public.sala_de_espera_revisao limit 1)")
echo "$D" | grep -qiE "ERRO(R)?:" || falha "DELETE na revisao NAO foi recusado: «$D»"
[ "$(q "$REVS")" = "$REVS_DEPOIS" ] || falha "o caderno mudou com o UPDATE/DELETE"
echo "7 · UPDATE recusado: $(echo "$U" | grep -iE "ERRO(R)?:" | head -1 | cut -c1-110)"
echo "7 · DELETE recusado: $(echo "$D" | grep -iE "ERRO(R)?:" | head -1 | cut -c1-110)"

echo "REPROC_SALA=PASS"
