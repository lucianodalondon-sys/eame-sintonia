#!/bin/bash
# testes por NOME numa arvore: uma linha "estado nome" por teste
# uso: c9-testes.sh <arvore> <saida>
cd "$1"
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 PYTHONUTF8=1
: > "$2"
for t in tests/test_c9_idioma.py tests/test_micro_coleta_instrumento.py tests/test_ensaio_offline_micro.py tests/test_micro_rede_real.py; do
  if [ ! -f "$t" ]; then echo "AUSENTE $t" >> "$2"; continue; fi
  m=$(basename $t .py)
  ( cd tests && timeout 900 py -B -m unittest -v $m 2>&1 ) | grep -E " \.\.\. (ok|FAIL|ERROR|skipped)" \
    | sed -E 's/^(test[^ ]*) \(([^)]*)\).* \.\.\. (ok|FAIL|ERROR|skipped.*)$/\3 \2.\1/' >> "$2"
done
sort -o "$2" "$2"
echo "$(grep -c '^ok' $2) ok · $(grep -c '^FAIL' $2) FAIL · $(grep -c '^ERROR' $2) ERROR · $(grep -c '^skipped' $2) saltados · $(grep -c AUSENTE $2) ficheiros ausentes"
