#!/usr/bin/env bash
# LUGAR-DO-PUBLICADOR · ensaio numa COPIA da Sala (Postgres descartavel), com os livros do vivo COPIADOS.
#
#   bash ferramentas/lugar_publicador/ensaio_sede_na_sala.sh <SHA do ramo> <pasta de saida>
#
# Precisa da LOCK-PESADO (quem chama a tem). Sem rede. A Sala real so e LIDA (pg_dump com
# default_transaction_read_only); o vivo so e LIDO (copia dos dois livros). No fim desliga o Postgres,
# apaga a copia e a worktree.
set -euo pipefail
SHA=$1; OUT=$2
VIVO=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
BIN=/c/Users/London1/orca/pgtmp/pgsql/bin
PORTA=54393
TMP=$(cygpath -m "${TMPDIR:-/tmp}")/lugar-publicador-$$
WT=$TMP/wt; PGD=$TMP/pgdata
mkdir -p "$OUT" "$TMP"
OUT=$(cygpath -m "$(cd "$OUT" && pwd)")
DSN_REAL=$(tr -d '\r\n' < C:/Users/London1/sintonia-sala-italia/SALA_DSN.txt)
COPIA="postgresql://postgres@127.0.0.1:$PORTA/sala"
limpar() {
  "$BIN/pg_ctl.exe" -D "$PGD" -m fast stop >/dev/null 2>&1 || true
  git worktree remove --force "$WT" >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap limpar EXIT

echo "== 1 · worktree do ramo + os dois livros do vivo (copia, sha256)"
git worktree add --detach "$WT" "$SHA" >/dev/null
for f in curadoria/italy_contracts_curator.json regras/italy_contracts_onboarded.json; do
  cp "$VIVO/$f" "$WT/$f"
done
(cd "$VIVO" && sha256sum curadoria/italy_contracts_curator.json regras/italy_contracts_onboarded.json) > "$OUT/1-LIVROS-DO-VIVO.sha256"

echo "== 2 · escrever a sede nos livros COPIADOS (mostrar -> aplicar -> 2.a passagem)"
cd "$WT"
for P in ferramentas/sede37/PAGINAS-DE-SEDE.json ferramentas/lugar_publicador/medida/PAGINAS-DE-SEDE-SALA.json; do
  n=$(basename "$P" .json)
  py -B ferramentas/sede37/escrever_sede.py --paginas "$P" --contratos curadoria/italy_contracts_curator.json \
     --tabela regras/italy_contracts_onboarded.json > "$OUT/2-$n-MOSTRAR.txt"
  py -B ferramentas/sede37/escrever_sede.py --paginas "$P" --contratos curadoria/italy_contracts_curator.json \
     --tabela regras/italy_contracts_onboarded.json --aplicar > "$OUT/2-$n-APLICAR.txt"
  py -B ferramentas/sede37/escrever_sede.py --paginas "$P" --contratos curadoria/italy_contracts_curator.json \
     --tabela regras/italy_contracts_onboarded.json > "$OUT/2-$n-SEGUNDA.txt"
  head -1 "$OUT/2-$n-MOSTRAR.txt"; head -1 "$OUT/2-$n-SEGUNDA.txt"
done
node -e "import('./regras/italy_contracts.mjs').then(m=>console.log('CONTRACTS', Object.keys(m.CONTRACTS).length))"
git diff --stat > "$OUT/2-LIVROS-DIFF-STAT.txt"; cat "$OUT/2-LIVROS-DIFF-STAT.txt"

echo "== 3 · copia da Sala: pg_dump so-leitura -> Postgres descartavel na porta $PORTA"
PGOPTIONS='-c default_transaction_read_only=on' "$BIN/pg_dump.exe" -Fc --no-owner --no-acl -f "$TMP/sala.dump" "$DSN_REAL"
sha256sum "$TMP/sala.dump" | cut -c1-64 > "$OUT/3-DUMP.sha256"
"$BIN/initdb.exe" -D "$PGD" -U postgres --auth=trust -E UTF8 >/dev/null
"$BIN/pg_ctl.exe" -D "$PGD" -o "-p $PORTA -c listen_addresses=127.0.0.1" -l "$TMP/pg.log" -w start >/dev/null 2>&1 < /dev/null
"$BIN/createdb.exe" -h 127.0.0.1 -p $PORTA -U postgres sala
"$BIN/pg_restore.exe" --no-owner --no-acl -h 127.0.0.1 -p $PORTA -U postgres -d sala "$TMP/sala.dump" 2> "$OUT/3-RESTORE.err" || true
q() { "$BIN/psql.exe" -X -q -A -t -F'|' -c "$1" "$COPIA" | tr -d '\r'; }
q "select count(*) from sala_de_espera_atual" | sed 's/^/linhas na copia: /'
FOTO="select run_id, ordem, source_id, source_location, published_at, fact_time, fact_location, completude_tempo_lugar from sala_de_espera_atual order by 1,2"
q "$FOTO" > "$OUT/3-ANTES.txt"
q "select count(*) from sala_de_espera_revisao" > "$OUT/3-REVISOES-ANTES.txt"

echo "== 4 · a porta da sede na copia: mostrar -> aplicar -> 2.a passagem"
export SINTONIA_SALA_BACKEND=POSTGRES SINTONIA_SALA_DSN="$COPIA"
py -B ferramentas/lugar_publicador/preencher_sede_na_sala.py --saida "$OUT/4-MOSTRAR.json" | head -12
py -B ferramentas/lugar_publicador/preencher_sede_na_sala.py --aplicar --saida "$OUT/4-APLICAR.json" | grep -A6 CONTA
py -B ferramentas/lugar_publicador/preencher_sede_na_sala.py --aplicar --saida "$OUT/4-SEGUNDA.json" | grep -A6 CONTA
q "$FOTO" > "$OUT/4-DEPOIS.txt"
q "select count(*) from sala_de_espera_revisao" > "$OUT/4-REVISOES-DEPOIS.txt"
q "select source_location, count(*), count(distinct source_id) from sala_de_espera_atual group by 1 order by 2 desc" | tee "$OUT/4-SEDE-DEPOIS.txt"
q "select count(*) from sala_de_espera" > "$OUT/4-LINHAS-ORIGINAIS.txt"

echo "== 5 · so a sede e a completude mudaram (os outros tres campos iguais, linha a linha)"
py -B - "$OUT" <<'EOF'
import sys
o = sys.argv[1]
def ler(n):
    return {tuple(l.split("|")[:2]): l.split("|") for l in open(o + "/" + n, encoding="utf-8").read().splitlines() if l}
A, D = ler("3-ANTES.txt"), ler("4-DEPOIS.txt")
assert A.keys() == D.keys(), "linhas diferentes"
mudou = {i: sum(1 for k in A if A[k][i] != D[k][i]) for i in range(3, 8)}
nomes = dict(zip(range(3, 8), ("source_location", "published_at", "fact_time", "fact_location", "completude")))
print({nomes[i]: n for i, n in mudou.items()})
assert mudou[4] == mudou[5] == mudou[6] == 0, "um campo que nao e a sede mudou"
print("SO_A_SEDE_E_A_COMPLETUDE=PASS")
EOF
cd - >/dev/null
echo "== fim · o Postgres desliga-se e a copia apaga-se (trap)"
