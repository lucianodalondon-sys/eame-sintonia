#!/bin/bash
# EXTRATOR-LUGAR-V2 · antes (codigo do vivo) x depois (este ramo), SO LEITURA, sem rede e sem banco.
# As entradas sao as da ACERVO-TEMPO-LUGAR (C:/Users/London1/reproc-acervo/, sha256 em entradas.sha256):
# raw.json / derivados.json / sala.json lidos da Sala real por SELECT so-leitura. Nada e escrito fora de $OUT.
# uso: bash medir_antes_depois.sh <commit do vivo> <commit do ramo> <pasta de saida C:/...>
set -u
VIVO_SHA=$1; RAMO_SHA=$2; OUT=$3
REPO=C:/Users/London1/orca/workspaces/eame-sintonia/reparo-fontes-v1
DADOS=C:/Users/London1/reproc-acervo
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1
mkdir -p "$OUT"
( cd $DADOS && sha256sum -c entradas.sha256 ) > $OUT/0-entradas.txt 2>&1 || { echo "ENTRADAS MUDARAM"; exit 2; }
RAIZES=$(cat $DADOS/raizes.txt)
LIVROS="C:/Users/London1/orca/workspaces/eame-sintonia/*/data/collection-ledger/italy/observations.ndjson;C:/*/data/collection-ledger/italy/observations.ndjson"
for lado in antes depois; do
  [ $lado = antes ] && SHA=$VIVO_SHA || SHA=$RAMO_SHA
  W=C:/leitor-$lado; git -C $REPO worktree remove --force $W 2>/dev/null; rm -rf $W
  git -C $REPO worktree add -q --detach $W $SHA || exit 1
  mkdir -p $W/scripts/leitor_medida && cp $REPO/ferramentas/lugar_v2/prever_acervo.py $W/scripts/leitor_medida/prever_acervo.py
  ( cd $W && py -B scripts/leitor_medida/prever_acervo.py --dados $DADOS --raizes "$RAIZES" --livros "$LIVROS" \
      --saida "$OUT/$lado.json" > "$OUT/$lado.log" 2>&1 ); echo "$lado rc=$? ($(git -C $W rev-parse --short HEAD))" | tee -a $OUT/0-entradas.txt
  git -C $REPO worktree remove --force $W
done
