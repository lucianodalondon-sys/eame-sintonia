#!/bin/bash
# ENSAIO C9-INSTALAR-PREP numa copia fiel do vivo. Sem rede HTTP; a Sala real e so LIDA
# (micro_coleta liga com PGOPTIONS=-c default_transaction_read_only=on; a DSN vem do ficheiro e nunca e impressa).
# uso: bash ensaio_c9.sh <commit do ramo> <pasta de saida C:/...>
set -u
RAMO=$1; OUT=$2
REPO=C:/Users/London1/orca/workspaces/eame-sintonia/reparo-fontes-v1
VIVO=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
ESTADO=C:/Users/London1/sintonia-sala-italia/ondas/ONDA3-WEB-20260925-1934/ONDA-WEB-ESTADO.json
C=C:/ens-c9; FOTO=C:/ens-c9-foto
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 NO_PROXY= PYTHONUTF8=1
G="git -c user.name=ensaio -c user.email=ensaio@local -C $C"
rm -rf "$OUT"; mkdir -p "$OUT"
git -C $REPO worktree remove --force $C 2>/dev/null; rm -rf $C $FOTO
HEAD_VIVO=$(git -C $VIVO rev-parse HEAD)
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '\n' ' ')
git -C $REPO worktree add -q --detach $C $HEAD_VIVO || exit 1
echo "COPIA: HEAD do vivo $(git -C $VIVO rev-parse --short HEAD) · ramo $(git -C $REPO rev-parse --short $RAMO) · livros $(echo $LIVROS | wc -w)" | tee $OUT/0-copia.txt
echo "livros que o ramo muda no Git: $(git -C $REPO diff --name-only $HEAD_VIVO $RAMO -- $LIVROS | wc -l)" | tee -a $OUT/0-copia.txt
git -C $REPO merge-base --is-ancestor $HEAD_VIVO $RAMO && echo "ff-only possivel: SIM" | tee -a $OUT/0-copia.txt || echo "ff-only possivel: NAO" | tee -a $OUT/0-copia.txt
for f in $LIVROS; do mkdir -p $FOTO/$(dirname $f); cp $VIVO/$f $FOTO/$f; cp $FOTO/$f $C/$f; done
( cd $FOTO && for f in $LIVROS; do sha256sum $f; done ) > $OUT/0-livros-foto.sha
cd $C
py -c "import urllib.request;urllib.request.urlopen('https://www.cia.it',timeout=5)" >/dev/null 2>&1 && { echo "REDE ABERTA - PARAR"; exit 2; } || echo "rede HTTP fechada: confirmada" | tee -a $OUT/0-copia.txt
IDS=$(py -c "
import json
e=json.load(open(r'$ESTADO',encoding='utf-8'))
print(' '.join('--run-id='+f['RUN_ID'] for f in e['FONTES'] if f.get('RUN_ID')))")
echo "RUN_IDs da 3.a onda: $(echo $IDS | wc -w)" | tee -a $OUT/0-copia.txt

# ── ANTES: o codigo da producao, a linha de comando como estava ──
py -B scripts/micro_coleta/micro_coleta.py relatorio $IDS --saida=$OUT/antes > $OUT/antes.json 2> $OUT/antes.err
# ── o ramo entra como na instalacao ──
$G merge --ff-only -q $RAMO > $OUT/1-merge.txt 2>&1; echo "merge --ff-only rc=$? HEAD $($G rev-parse --short HEAD)" | tee -a $OUT/1-merge.txt
( for f in $LIVROS; do sha256sum $f; done ) | diff -q - $OUT/0-livros-foto.sha >/dev/null && echo "livros IGUAIS depois do merge" | tee -a $OUT/1-merge.txt || echo "LIVROS MUDARAM" | tee -a $OUT/1-merge.txt
# ── DEPOIS: o codigo do C9, com as corridas do estado da onda ──
py -B scripts/micro_coleta/micro_coleta.py relatorio $IDS --estado=$ESTADO --saida=$OUT/depois > $OUT/depois.json 2> $OUT/depois.err
( for f in $LIVROS; do sha256sum $f; done ) | diff -q - $OUT/0-livros-foto.sha >/dev/null && echo "livros IGUAIS depois do relatorio" | tee -a $OUT/1-merge.txt || echo "LIVROS MUDARAM" | tee -a $OUT/1-merge.txt
# ── DESFAZER ──
$G reset -q --keep $HEAD_VIVO; echo "reset --keep rc=$?" | tee $OUT/2-desfazer.txt
for f in $LIVROS; do cp $FOTO/$f $C/$f; done
DIF=$($G diff --name-only $HEAD_VIVO | grep -v -x -F -f <(echo "$LIVROS" | tr ' ' '\n') | wc -l)
echo "ficheiros de codigo diferentes do vivo: $DIF · HEAD = vivo: $([ "$($G rev-parse HEAD)" = "$HEAD_VIVO" ] && echo SIM || echo NAO)" | tee -a $OUT/2-desfazer.txt
cd /c; git -C $REPO worktree remove --force $C; rm -rf $FOTO; echo "copia removida"
