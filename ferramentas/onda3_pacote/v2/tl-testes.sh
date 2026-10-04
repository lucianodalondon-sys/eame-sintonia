#!/bin/bash
# corre os testes de tempo/lugar (e os que a producao trouxe desde 88ee046f) numa arvore; uma linha por ficheiro
# uso: tl-testes.sh <arvore> <saida>
cd "$1"
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 PYTHONUTF8=1
: > "$2"
for t in $(git diff --name-only 88ee046f e5cd691f | grep -E '(^|/)test_[^/]*\.py$' | sort); do
  [ -f "$t" ] || { echo "$t AUSENTE" >> "$2"; continue; }
  r=$(timeout 600 py -B "$t" 2>&1 | grep -E '^Ran |^OK|^FAILED' | tr '\n' ' ')
  echo "$t | $r" >> "$2"
done
cat "$2"
