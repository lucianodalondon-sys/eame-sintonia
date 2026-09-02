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

# Parte C: a camada de SUBSTANCIA ATIVA — entidade propria, MoA e estado europeu.
# Vem depois de B porque ancora nos produtos que A e B acabaram de escrever: uma
# substancia que nao encosta em produto ingerido nao entra, para nao criar relacao
# orfa. Le do disco, nao da memoria da parte B.
"$PY" scripts/v21_ingest_c.py

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
echo "── 5b · R2 · a procedencia que ja estava dentro do pacote ──────────────"
# Depois do rechaveamento, porque religa contra o indice de fontes que ele monta.
# ANTES da traducao, porque troca o texto de carimbo que vai a tela — e texto que
# muda depois de traduzido volta a ser portugues na tela.
"$PY" scripts/v21_procedencia_religar.py

echo
echo "── 5c · R3 · a rota medida, ligada as fontes que ela mede ──────────────"
# CONTEUDO: entra antes da traducao, porque ACCESS_EVIDENCE vai a tela.
"$PY" scripts/v21_contrato_do_pacote.py --rota

echo
echo "── 5d · R5 · sobre o mundo, ou sobre o nosso encanamento? ──────────────"
# Antes da traducao (mexe em texto) e antes do fechamento (mexe em CLIENT_SAFE).
"$PY" scripts/v21_dominio_da_alegacao.py

echo
echo "── 5e · o motor de oportunidades, sobre o proprio V2.1 ─────────────────"
# Depois de 5d porque le CLIENT_SAFE ja final; antes da traducao porque o texto
# de tela dele tem de passar pela trava como qualquer outro.
"$PY" scripts/v21_oportunidades.py

echo
echo "── 6 · a tradução, conferida antes de entrar ───────────────────────────"
# a trava recusa gravar se alguma tradução falhar. É de propósito.
"$PY" scripts/v21_traducao_trava.py --aplicar

echo
echo "── 6b · a voz do pesquisador sai da tela (o original fica) ─────────────"
"$PY" scripts/v21_dominio_da_alegacao.py --pos-traducao

echo
echo "── 7 · o fechamento: registro central, manifesto, arquivo interno ──────"
"$PY" scripts/v21_fechar.py

echo
echo "── 7b · R3 · toda quebra declarada recontada do corpo ──────────────────"
# ARITMETICA: entra depois do fechamento, quando o corpo parou de mudar.
"$PY" scripts/v21_contrato_do_pacote.py --contagens

echo
echo "── 8 · §19 · a aceitação, com todo número recontado ────────────────────"
"$PY" scripts/v21_aceitacao.py

echo
echo "── 9 · os contratos: cada lei vira contador, e o zero e medido ─────────"
# Rodam DEPOIS da aceitacao porque leem o pacote pronto — e ficam DENTRO da
# cadeia porque o passo 1 apaga a pasta: contrato que mora fora da cadeia
# desaparece no rebuild seguinte e ninguem nota.
"$PY" scripts/v21_geografia_contrato.py
"$PY" scripts/v21_procedencia_contrato.py
