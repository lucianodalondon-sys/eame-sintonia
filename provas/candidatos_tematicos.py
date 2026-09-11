#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS CANDIDATOS TEMATICOS — definidos e CONGELADOS antes de verem o corpus.

    python3 provas/candidatos_tematicos.py
    python3 provas/candidatos_tematicos.py --escrever

Esta missao DEFINE. Nao executa candidato, nao corre benchmark, nao toca na
Admission e nao mexe no gate.

    DEFINIR CANDIDATO   != EXECUTAR CANDIDATO
    ESCREVER REGRA      != MEDIR REGRA
    IMPLEMENTAR         != AUTORIZAR AJUSTE
    EVALUATION SET      != TRAINING SET

POR QUE O CONGELAMENTO E A MISSAO INTEIRA
------------------------------------------
Um candidato desenhado depois de ver onde o corpus de avaliacao aperta nao e um
candidato: e uma resposta decorada com cara de hipotese. O gabarito de T3 ja foi
declarado `EVALUATION`, e a partir daqui a unica coisa que separa uma comparacao
honesta de um teatro e a ORDEM:

    A HIPOTESE VEM PRIMEIRO, E FICA ESCRITA.
    DEPOIS MEDE-SE. NUNCA AO CONTRARIO.

O fingerprint existe para isso: qualquer alteracao posterior muda o hash, e um
hash que mudou depois da medicao e uma confissao.
"""
import hashlib
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

MANIFESTO = "data/derivados/CANDIDATOS-TEMATICOS-V1.json"
DOCUMENTO = "docs/operacao/CANDIDATOS-TEMATICOS-V1.md"
CANDIDATE_SET_VERSION = "V1"


# ══════════════════════════════════════════════════════════════════════════
# 1 · A SUPERFICIE PROIBIDA — medida, nao lembrada
# ══════════════════════════════════════════════════════════════════════════
# Estes ficheiros carregam a RESPOSTA. Abrir qualquer um deles para desenhar um
# candidato contamina-o, e a contaminacao nao se desfaz depois.
#
#     UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE.
FICHEIROS_PROIBIDOS = (
    "data/samples/T3-GROUND-TRUTH-EVAL-V1.json",
    "data/derivados/BASELINE-ADMISSION-T3-V1.json",
    "data/review/t3/T3-HUMAN-REVIEW-A-V1.json",
    "data/review/inbox/T3-HUMAN-QUALITY-GATE-RESULTS-V1.json",
    "data/review/t3/T3-CONTEXTO-CEGO-PTBR-V1.json",
    "data/review/t3/T3-TRADUCAO-CONTEXTO-CEGO-PTBR-V1.json",
)

# Campos que, se um candidato os lesse, entregavam-lhe a resposta feita.
CAMPOS_PROIBIDOS = (
    "REVIEWER_A", "REVIEWER_B", "AGREEMENT", "FINAL_LABEL", "HUMAN_LABEL",
    "LABEL", "LABEL_A", "LABEL_A2", "EVAL_ELIGIBLE", "GROUND_TRUTH",
    "resultado", "universo",          # o veredicto anterior da propria porta
)

# ⚠️ E ESTE E O MENOS OBVIO DOS TRES.
# `SOURCE_ID` nao e um identificador neutro: ele CARREGA o token do universo
# DECLARADO da fonte — `IT-T3-002` diz «fonte 002 do territorio T3». Um
# candidato que o use como feature esta a ler um rotulo de FONTE e a chama-lo
# decisao de DOCUMENTO.
#
#     DECLARED != OBSERVED.
#     SOURCE_RELEVANCE != DOCUMENT_RELEVANCE.
#
# O contraexemplo canonico desta casa e a ARPAV: uma mesma instituicao publica
# material de universos diferentes. Se a fonte decidisse, ela decidiria errado
# em todos os documentos que fogem ao territorio declarado dela — e decidiria
# com ar de certeza.
# ⚠️ E NAO E SO O `SOURCE_ID`. MEDIDO NO ATLAS: **78 de 78** identificadores de
# fonte carregam o token do universo dentro do proprio id. E como o CAMINHO do
# ficheiro embute o `SOURCE_ID` (`data/samples/IT-SOURCE-SAMPLES/IT-T3-002/...`),
# o caminho carrega a classe declarada tambem.
#
#     ENTREGA-SE OS BYTES AO CANDIDATO. NUNCA O CAMINHO.
#
# Um candidato que leia caminho, nome de ficheiro ou pasta esta a ler o
# territorio declarado da fonte — e a chamar-lhe leitura do documento.
CAMINHO_COMO_FEATURE = "PROIBIDO"
CAMPOS_DE_CAMINHO = ("CONTENT_PATH", "BODY_PATH", "CANONICAL_PATH",
                     "ALL_PATHS", "STORAGE_LOCATION", "ITEM_ID", "filename")
SOURCE_ID_COMO_FEATURE = "PROIBIDO"
PORQUE_SOURCE_ID_PROIBIDO = (
    "a string do SOURCE_ID contem o token do universo DECLARADO da fonte "
    "(`IT-T3-002` -> territorio T3). Usa-la como feature e usar um rotulo de "
    "fonte como resposta de documento, e DECLARED != OBSERVED.")


class FichaInvalida(Exception):
    """Uma ficha de candidato nao passa. NAO se conserta em silencio: para-se."""


# ══════════════════════════════════════════════════════════════════════════
# 2 · O SCHEMA DA FICHA
# ══════════════════════════════════════════════════════════════════════════
CAMPOS_OBRIGATORIOS = (
    "CANDIDATE_ID", "NAME", "VERSION", "FAMILY", "HYPOTHESIS",
    "INPUTS_ALLOWED", "INPUTS_FORBIDDEN",
    "TEXT_FIELDS_USED", "LANGUAGE_HANDLING",
    "DECISION_OUTPUT", "ABSTENTION_SUPPORTED",
    "DETERMINISTIC", "MODEL_DEPENDENCY", "EXTERNAL_API_DEPENDENCY",
    "TRAINING_REQUIRED", "TRAINING_SOURCE",
    "TRAINING_SET_INDEPENDENT_FROM_EVALUATION",
    "TUNABLE_PARAMETERS", "FROZEN_PARAMETERS",
    "EXPECTED_STRENGTH", "EXPECTED_WEAKNESS",
    "FALSE_NEGATIVE_RISK", "FALSE_POSITIVE_RISK",
    "EXPLAINABILITY", "AUDITABILITY",
    "COST_MODEL", "LATENCY_MODEL", "OFFLINE_CAPABLE",
    "FAILURE_BEHAVIOR", "WHAT_WOULD_INVALIDATE_THIS_CANDIDATE",
    "IMPLEMENTATION_STATUS", "CANDIDATE_STATUS",
)

# Nesta missao ninguem mediu nada. Declarar «validado» seria mentir com uma
# palavra que so a medicao pode dizer.
STATUS_PERMITIDO = ("DEFINED_NOT_IMPLEMENTED", "EXISTING_COMPONENT_REUSABLE",
                    "PROTOTYPE_SKELETON")
STATUS_PROIBIDO = ("VALIDATED", "ACCEPTED", "PRODUCTION_READY", "APPROVED",
                   "BENCHMARKED")

# A saida tem de falar a lingua da porta. Um candidato que devolva `True/False`
# perde a diferenca entre «nao» e «nao sei», que e justamente onde o custo vive.
SAIDAS_DA_PORTA = ("SIM", "NAO", "NAO_SEI", "NAO_SE_APLICA", "ERRO")


# ══════════════════════════════════════════════════════════════════════════
# 3 · A VALIDACAO DE UMA FICHA
# ══════════════════════════════════════════════════════════════════════════
def _termos_da_porta():
    """Os termos da regra lexical de hoje. Nenhum pode aparecer numa ficha.

    ⚠️ A razao nao e higiene: e que eu, ao desenhar, JA TINHA VISTO a saida do
    baseline por documento numa missao anterior desta mesma sessao. Nao da para
    desver. O que da e impedir estruturalmente que essa memoria entre numa
    ficha — e um termo da lista actual e a forma mais directa de ela entrar.
    """
    import admissao as adm
    return sorted({t.lower() for ts in adm.PERGUNTAS_DO_UNIVERSO.values()
                   for t in ts})


def _texto_da_ficha(f):
    """Tudo o que a ficha diz, numa string. E onde se procura contaminacao."""
    return json.dumps(f, ensure_ascii=False).lower()


def validar_ficha(f, termos_proibidos):
    faltam = [c for c in CAMPOS_OBRIGATORIOS if c not in f]
    if faltam:
        raise FichaInvalida("%s: faltam campos %s"
                            % (f.get("CANDIDATE_ID", "?"), faltam))

    cid = f["CANDIDATE_ID"]
    if f["IMPLEMENTATION_STATUS"] not in STATUS_PERMITIDO:
        raise FichaInvalida("%s: IMPLEMENTATION_STATUS = %r nao e permitido "
                            "nesta missao" % (cid, f["IMPLEMENTATION_STATUS"]))

    texto = _texto_da_ficha(f)
    for mau in STATUS_PROIBIDO:
        if mau.lower() in texto:
            raise FichaInvalida("%s: a ficha diz «%s» e ninguem mediu nada"
                                % (cid, mau))

    # ── CONTAMINACAO ──────────────────────────────────────────────────────
    for caminho in FICHEIROS_PROIBIDOS:
        if caminho.lower() in texto and caminho not in f["INPUTS_FORBIDDEN"]:
            raise FichaInvalida("%s: cita %s fora de INPUTS_FORBIDDEN"
                                % (cid, caminho))
    for campo in CAMPOS_PROIBIDOS:
        if campo in f["INPUTS_ALLOWED"]:
            raise FichaInvalida("%s: %s nao pode estar em INPUTS_ALLOWED"
                                % (cid, campo))
    # Um termo da lista de hoje numa ficha e memoria do corpus a vazar.
    achados = [t for t in termos_proibidos
               if re.search(r"(?<![a-zà-ÿ])%s(?![a-zà-ÿ])" % re.escape(t), texto)]
    if achados:
        raise FichaInvalida("%s: a ficha contem termos da regra actual: %s"
                            % (cid, achados[:5]))
    # Nenhum candidato pode ler a fonte como resposta.
    if any("source_id" == str(x).lower() for x in f["INPUTS_ALLOWED"]):
        raise FichaInvalida("%s: SOURCE_ID nao pode ser INPUT_ALLOWED — %s"
                            % (cid, PORQUE_SOURCE_ID_PROIBIDO))
    # Nem o caminho, que embute o SOURCE_ID e portanto o universo declarado.
    caminhos = [x for x in f["INPUTS_ALLOWED"]
                if str(x) in CAMPOS_DE_CAMINHO]
    if caminhos:
        raise FichaInvalida(
            "%s: caminho/nome de ficheiro nao pode ser INPUT_ALLOWED (%s) — o "
            "caminho embute o SOURCE_ID, e 78 de 78 ids do atlas carregam o "
            "token do universo declarado" % (cid, caminhos))

    # ── COERENCIA INTERNA ─────────────────────────────────────────────────
    if f["ABSTENTION_SUPPORTED"] not in ("YES", "NO"):
        raise FichaInvalida("%s: ABSTENTION_SUPPORTED tem de ser YES ou NO" % cid)
    if f["ABSTENTION_SUPPORTED"] == "YES" and "NAO_SEI" not in f["DECISION_OUTPUT"]:
        raise FichaInvalida("%s: declara abstencao e nao a devolve na saida" % cid)
    maus = [s for s in f["DECISION_OUTPUT"] if s not in SAIDAS_DA_PORTA]
    if maus:
        raise FichaInvalida("%s: saida fora do vocabulario da porta: %s"
                            % (cid, maus))
    if f["TRAINING_REQUIRED"] == "YES":
        if f["TRAINING_SET_INDEPENDENT_FROM_EVALUATION"] == "YES" \
                and not f["TRAINING_SOURCE"]:
            raise FichaInvalida("%s: alega treino independente e nao diz de onde"
                                % cid)
        if f["TRAINING_SET_INDEPENDENT_FROM_EVALUATION"] != "YES" \
                and f["CANDIDATE_STATUS"] != "BLOCKED_PENDING_INDEPENDENT_TRAINING_SET":
            raise FichaInvalida(
                "%s: precisa de treino, nao tem conjunto independente, e nao "
                "esta BLOCKED_PENDING_INDEPENDENT_TRAINING_SET" % cid)
    # Um parametro afinavel que nao esta congelado e uma porta aberta para
    # afinar depois de ver o resultado.
    soltos = [p for p in f["TUNABLE_PARAMETERS"] if p not in f["FROZEN_PARAMETERS"]]
    if soltos:
        raise FichaInvalida("%s: parametros afinaveis nao congelados: %s"
                            % (cid, soltos))
    if f["EXTERNAL_API_DEPENDENCY"] == "YES" and not f["FAILURE_BEHAVIOR"]:
        raise FichaInvalida("%s: depende de API externa e nao diz o que faz "
                            "quando ela falha" % cid)
    # Escopo: ninguem promete o que nao mediu.
    for promessa in ("franca", "espanha", "eame", "france", "spain"):
        if promessa in texto and "nao autoriza" not in texto:
            raise FichaInvalida("%s: promete escopo por medir (%s)"
                                % (cid, promessa))
    return True


def impressao_da_ficha(f):
    """O hash de UMA ficha. Mexer nela muda o hash — e e essa a prova."""
    return hashlib.sha256(
        json.dumps(f, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def validar_conjunto(fichas):
    termos = _termos_da_porta()
    ids = [f["CANDIDATE_ID"] for f in fichas]
    if len(set(ids)) != len(ids):
        raise FichaInvalida("ha CANDIDATE_ID repetido: %s" % ids)
    familias = [f["FAMILY"] for f in fichas]
    if len(set(familias)) != len(familias):
        raise FichaInvalida("duas fichas na mesma familia: %s" % familias)
    if not 3 <= len(fichas) <= 5:
        raise FichaInvalida("o conjunto tem %d candidatos; o contrato pede 3 a 5"
                            % len(fichas))
    for f in fichas:
        validar_ficha(f, termos)
    return True


def impressao_do_conjunto(fichas):
    return hashlib.sha256(
        json.dumps([impressao_da_ficha(f) for f in fichas],
                   ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
