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
PARES=v1/dados/IT-ROTULOS-PARES-RECONSTRUIDO.json

echo "== 0 · cadeia TLS (o host das etichette manda cadeia incompleta)"
sh $P/bin/chain.sh >/dev/null

echo "== 0b · FONTE PRIMARIA: rebaixar e conferir os 223 arquivos pelo sha256"
python3 v1/fonte/recoletar.py .

echo "== 1-4 · registro oficial: check, snapshot, hash, identidade de versao"
python3 $P/bin/registro_it.py --weeks "$SEMANAS" --end 2026-08-31

echo "== 5-7 · documento do rotulo: conferir hash, baixar so o que mudou, preservar"
# O manifesto de leitura (LABEL_URL, sha e vigencia por etichetta) vive em
# sintonia/canonical e NAO esta neste repositorio. O passo 0b ja confere os 163
# PDFs byte a byte contra MANIFESTO-FONTE.json, que e a mesma pergunta de
# integridade; o que so canonical responde e "o documento MUDOU desde a linha de
# base". Com $CANON apontado, este passo roda; sem ele, fica dito que nao rodou.
if [ -n "$CANON" ] && [ -f "$CANON/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json" ]; then
  python3 $P/bin/rotulo_reverificar.py \
    --manifesto $CANON/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json \
    --observed-at "$HOJE"
else
  echo "   PULADO — MANIFESTO_DE_LEITURA_NOT_AVAILABLE (sintonia/canonical). Isto e"
  echo "   passo nao executado, NAO 'nenhum rotulo mudou'."
fi

echo "== 8-9 · ler e estruturar: dose por geometria"
python3 $P/bin/dose_rodar.py --todos --cachedir /tmp/dosecache

echo "== 10 · conferir cada dose contra os fios desenhados da tabela"
python3 $P/bin/dose_validar.py --cache-fios /tmp/fioscache

echo "== 10b · descartar tabela que o extrator achou onde nao havia"
python3 v1/inteligencia/dose_plausibilidade.py

echo "== 10c · EXCLUSAO NAO E PERMISSAO: reconciliar cada par contra o PDF oficial"
python3 v1/coleta/exclusao.py \
  --pares "$PARES" \
  --cache /tmp/exclusao-txt

echo "== 10d · R-11: a cultura de cada linha de dose sobrevive aos fios desenhados?"
python3 v1/inteligencia/cultura_validar.py --fios /tmp/fioscache --bbox /tmp/bboxcache

echo "== 10e · R-12: teto de dose por cultura escrito FORA da tabela"
python3 v1/inteligencia/teto_dose.py

echo "== 10f · R-13: o texto do alvo existe literalmente no rotulo?"
python3 v1/inteligencia/alvo_literal.py

echo "== 10g · R-14: o PAR DE USO sobrevive aos fios desenhados?"
python3 v1/inteligencia/par_validar.py --fios /tmp/fioscache --bbox /tmp/bboxcache

echo "== 10h · R-15: MAX. APLICACOES e INTERVALO herdados de celula mesclada"
python3 v1/inteligencia/heranca_validar.py --fios /tmp/fioscache --bbox /tmp/bboxcache

echo "== 10i · R-17: o NOME do alvo publicado esta escrito no rotulo?"
python3 v1/inteligencia/alvo_nomeado.py

echo "== 10j · DIAGNOSTICO da camada de prosa (R-16 NAO entra em producao)"
python3 v1/inteligencia/prosa_escopo.py --fios /tmp/fioscache --bbox /tmp/bboxcache
python3 v1/inteligencia/prosa_censo.py

echo "== 11 · COLETA: empacotar com proveniencia e coberturas separadas"
# Mesmo motivo do passo 5-7: empacotar.py precisa do manifesto de leitura.
if [ -n "$CANON" ] && [ -f "$CANON/data/samples/IT-ROTULOS-V1/IT-ROTULOS-LEITURA-RUN.json" ]; then
  python3 v1/coleta/empacotar.py --run-id "$RUN" --pares "$PARES"
else
  echo "   PULADO — usa o v1/dados/COLLECTION-PACKAGE.json ja versionado."
fi

echo "== 12 · INTELIGENCIA: objetos, com a regra que autoriza cada derivacao"
python3 v1/inteligencia/objetos.py --hoje "$HOJE"

echo "== 13 · PORTAO: o filtro de ruido tem de passar antes de publicar"
python3 v1/testes/test_ruido.py

echo "== 10j2 · R-19: em que forma a etichetta declara a propria vigencia?"
python3 v1/inteligencia/vigencia_etichetta.py

echo "== 10k · R-18: toda frase entre aspas existe no documento?"
python3 v1/inteligencia/citacao_verificar.py

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
