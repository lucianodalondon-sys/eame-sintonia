#!/usr/bin/env bash
# A CADEIA DO V2.1 — a ordem em que o pacote se constrói, e por que é esta.
#
#     bash scripts/v21_cadeia.sh
#
# POR QUE UMA CADEIA, E NÃO SETE COMANDOS SOLTOS
# -----------------------------------------------
# Porque a ordem importa e não é adivinhável. Rodar `v21_ingest_b.py` sozinho —
# como aconteceu — regrava as coleções e apaga em silêncio o carimbo de origem,
# o rechaveamento das fontes e as traduções já aplicadas. Nada quebra, nada
# reclama: o pacote fica com menos do que tinha, e parece inteiro.
#
#     O PASSO QUE APAGA SEM AVISAR É PIOR QUE O PASSO QUE FALHA.
#     O que falha, se vê.
#
# Cada etapa aqui embaixo depende do que veio antes. Se você precisa rodar uma
# no meio, rode desta linha até o fim — nunca só ela.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8:replace

# O INTERPRETADOR SE DESCOBRE, NAO SE FIXA.
# Esta cadeia nasceu no Windows, onde o Python chama-se `py`. Ao ser retomada em
# Linux, `py` nao existia e a cadeia inteira ficava inexecutavel — ou seja, o
# pacote deixava de ser reconstruivel por quem herdasse o repositorio.
#
#     CADEIA QUE SO RODA NA MAQUINA DE QUEM A ESCREVEU NAO E CADEIA: E LEMBRANCA.
#
# Ordem de preferencia; a primeira que existir manda. Pode-se forcar com PY=...
if [ -z "${PY:-}" ]; then
  for c in py python3 python; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
fi
[ -n "${PY:-}" ] || { echo "nenhum interpretador Python encontrado (py/python3/python)" >&2; exit 1; }
echo "interpretador: $PY ($($PY --version 2>&1))"

echo "── 1 · as coleções, do handoff anterior e da last-mile ─────────────────"
# ⚠️ ESTES DOIS REESCREVEM TUDO. Tudo que vier depois tem de rodar de novo.
"$PY" scripts/v21_ingest.py
"$PY" scripts/v21_ingest_b.py

echo
echo "── 2 · os cruzamentos, sobre identificadores normalizados ──────────────"
# depois do ingest, porque lê os IDs que ele acabou de escrever
"$PY" scripts/v21_crossings.py

echo
echo "── 3 · §13 · a reconciliação das vozes ─────────────────────────────────"
"$PY" scripts/v21_vozes_reconciliar.py

echo
echo "── 4 · a camada de origem, sem default silencioso ──────────────────────"
# antes do fechamento: o registro central não inventa origem para quem chega
# sem carimbo — ele mostra SEM_CARIMBO, e aí a falha aparece.
"$PY" scripts/v21_carimbar_origem.py

echo
echo "── 5 · as fontes, rechaveadas para a chave que o pacote já cita ────────"
"$PY" scripts/v21_fontes_rechavear.py
# e cadastra a fonte que ja era citada mas nao tinha linha — a URL ja estava no
# pacote, dentro do registro que a cita. Sem isto, 174 citacoes de SRC_DOI_ORG
# viram link que nao abre.
"$PY" scripts/v21_fontes_faltantes.py

echo
echo "── 6 · a tradução, conferida antes de entrar ───────────────────────────"
# a trava recusa gravar se alguma tradução falhar. É de propósito.
"$PY" scripts/v21_traducao_trava.py --aplicar

echo
echo "── 7 · o fechamento: registro central, manifesto, arquivo interno ──────"
"$PY" scripts/v21_fechar.py

echo
echo "── 8 · §19 · a aceitação, com todo número recontado ────────────────────"
"$PY" scripts/v21_aceitacao.py
