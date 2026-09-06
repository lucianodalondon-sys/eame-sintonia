#!/bin/sh
# pipeline.sh — a esteira inteira, executavel a mao, pronta para scheduling.
#
#   SCHEDULE -> CHECK REGISTRY -> SNAPSHOT -> HASH/IDENTITY -> DOCUMENT CHECK
#   -> DOWNLOAD IF NEEDED -> PRESERVE RAW -> READ -> STRUCTURE -> COMPARE
#   -> FILTER NOISE -> CHANGE EVENTS -> INTELLIGENCE -> REVIEW GATE -> PUBLISH
#
# NADA aqui e agendado. Nao ha cron, nao ha webhook, nao ha deploy. A automacao
# esta DESENHADA e EXECUTAVEL, e ligar e decisao de quem opera.
#
#   uso:  sh v1/pipeline.sh 2026-09-06 [--semanas N]
set -e
HOJE="${1:?uso: sh v1/pipeline.sh AAAA-MM-DD [--semanas N]}"
SEMANAS="${3:-60}"
RUN="RUN-$HOJE-$(date -u +%H%M%S)"
cd "$(dirname "$0")/.."
P=pilot-label-intelligence
CANON=/tmp/claude-0/-home-user-eame-sintonia/113d92e8-e962-52b2-b6d1-c8c3e286096e/scratchpad/canonical

echo "== 0 · cadeia TLS (o host das etichette manda cadeia incompleta)"
sh $P/bin/chain.sh >/dev/null

echo "== 1-4 · registro oficial: check, snapshot, hash, identidade de versao"
python3 $P/bin/registro_it.py --weeks "$SEMANAS" --end 2026-08-31

echo "== 5-7 · documento do rotulo: conferir hash, baixar so o que mudou, preservar"
python3 $P/bin/rotulo_reverificar.py \
  --manifesto $CANON/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json \
  --observed-at "$HOJE"

echo "== 8-9 · ler e estruturar: dose por geometria"
python3 $P/bin/dose_rodar.py --todos --cachedir /tmp/dosecache

echo "== 10 · conferir cada dose contra os fios desenhados da tabela"
python3 $P/bin/dose_validar.py --cache-fios /tmp/fioscache

echo "== 10b · descartar tabela que o extrator achou onde nao havia"
python3 v1/inteligencia/dose_plausibilidade.py

echo "== 10c · EXCLUSAO NAO E PERMISSAO: reconciliar cada par contra o PDF oficial"
python3 v1/coleta/exclusao.py \
  --pares "$CANON/data/samples/IT-ROTULOS-V1/IT-ROTULOS-PARES-V3.json" \
  --cache /tmp/exclusao-txt

echo "== 11 · COLETA: empacotar com proveniencia e coberturas separadas"
python3 v1/coleta/empacotar.py --run-id "$RUN"

echo "== 12 · INTELIGENCIA: objetos, com a regra que autoriza cada derivacao"
python3 v1/inteligencia/objetos.py --hoje "$HOJE"

echo "== 13 · PORTAO: o filtro de ruido tem de passar antes de publicar"
python3 v1/testes/test_ruido.py

echo "== 14 · CASCO: payload e ferramenta"
python3 v1/casco/payload.py --hoje "$HOJE"
sh v1/casco/build.sh

echo "== 14b · PORTAO: a interface renderizada tem de aguentar os testes de tela"
node v1/testes/test_casco.js

echo "== 15 · auditoria do piloto (recontagem independente)"
python3 $P/bin/auditar.py | tail -2

echo
echo "  RUN = $RUN"
echo "  ferramenta: v1/casco/label-intelligence.html"
echo "  o portao de ruido roda ANTES de publicar: se ele falhar, o pipeline para"
