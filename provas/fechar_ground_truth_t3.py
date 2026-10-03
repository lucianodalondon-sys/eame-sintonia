#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FECHAR O GABARITO DE T3 — sem decidir onde os humanos nao fecharam.

    python3 provas/fechar_ground_truth_t3.py
    python3 provas/fechar_ground_truth_t3.py --escrever

Sem rede, sem banco, sem recoleta. Nenhum classificador e construido aqui,
nenhum modelo e escolhido, e a Admission nao e tocada.

    CLASSIFIER_BUILT = NO
    ADMISSION_CHANGED = NO

O QUE ESTA MISSAO TEM NA MAO
----------------------------
Duas leituras humanas do mesmo material:

    REVIEW_A     a primeira passagem, 53 respostas
    A2           o portao de qualidade — 32 confirmacoes e 21 releituras cegas

Ambas de UMA pessoa. Os dois ficheiros sao READ_ONLY e nunca sao reescritos.

A REGRA QUE GOVERNA O FECHO
---------------------------
Onde as duas leituras fecham, ha gabarito. Onde nao fecham, NAO ha — e a
ausencia fica escrita com o nome dela.

    A != A2  ->  UNRESOLVED, e mais nada.
    NUNCA A, NUNCA A2, NUNCA A MAIORIA, NUNCA A ULTIMA RESPOSTA.

E o caso que mais tenta:

    EVIDENCIA_INSUFICIENTE  !=  NAO

«Nao deu para saber» e um buraco na evidencia. Convertê-lo em negativo
enche o dataset e mente sobre o que foi visto.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401


def _modulo(nome, ficheiro):
    spec = importlib.util.spec_from_file_location(
        nome, os.path.join(RAIZ, "provas", ficheiro))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


censo = _modulo("_censo_gt", "censo_corpus_rotulado_admission.py")

REVISAO_A = "data/review/t3/T3-HUMAN-REVIEW-A-V1.json"
PORTAO = "data/review/inbox/T3-HUMAN-QUALITY-GATE-RESULTS-V1.json"
PACOTE = "data/samples/T3-HUMAN-REVIEW-PENDING-V1.json"
GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"

SCHEMA_PORTAO = "sintonia.t3-human-quality-gate-results/1"
SCHEMA_GABARITO = "sintonia.t3-ground-truth-eval/1"
GERADOR = "provas/fechar_ground_truth_t3.py"

BINARIOS = ("T3_SIM", "T3_NAO")

# ── O LIMIAR DE QUASE-DUPLICADO, ESCRITO ANTES DE CONTAR ──────────────────
# Quatro boletins da mesma instituicao em semanas seguidas partilham a pagina
# de abertura quase inteira. Conta-los como quatro observacoes independentes
# infla o gabarito sem acrescentar uma unica evidencia nova.
#
#     QUATRO COPIAS DO MESMO BOLETIM NAO SAO QUATRO PROVAS.
#
# Mede-se sobre a EVIDENCIA que a pessoa viu — que e o texto de onde o rotulo
# nasceu. Jaccard de 5-gramas de palavras, limiar fixado aqui e nao depois.
SHINGLE = 5
LIMIAR_QUASE_DUPLICADO = 0.60


class FechoInvalido(Exception):
    """Uma entrada humana nao passa na conferencia. NAO se conserta: para-se."""


def sha256_do_ficheiro(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _json(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════
# 1 · AS DUAS ENTRADAS HUMANAS
# ══════════════════════════════════════════════════════════════════════════
def carregar():
    """Le A e A2 e prova-os um contra o outro. Nunca escreve em nenhum."""
    if not os.path.isfile(os.path.join(RAIZ, PORTAO)):
        raise FechoInvalido("o portao de qualidade nao existe em %s" % PORTAO)
    a = _json(REVISAO_A)["REVIEW_A"]
    g = _json(PORTAO)

    if g.get("SCHEMA") != SCHEMA_PORTAO:
        raise FechoInvalido("schema inesperado: %r" % g.get("SCHEMA"))
    if g.get("STATUS") != "COMPLETE":
        raise FechoInvalido("STATUS = %r; so entra portao completo"
                            % g.get("STATUS"))
    if not (g["TOTAL_EXPECTED"] == g["TOTAL_ANSWERED"] == len(g["ITEMS"]) == 53):
        raise FechoInvalido("contagens do portao nao fecham")
    if g.get("AUTO_LABELS_ASSIGNED") != 0:
        raise FechoInvalido("o portao declara rotulos atribuidos por maquina")
    if g.get("INDEPENDENT_SECOND_REVIEWER") is not False:
        raise FechoInvalido("o portao alega revisor independente")
    if g.get("FINAL_LABEL_DECIDIDO_AQUI") is not False:
        raise FechoInvalido("o portao alega ter decidido o rotulo final")

    shas = [x["DOC_SHA256"] for x in g["ITEMS"]]
    if len(set(shas)) != len(shas):
        raise FechoInvalido("ha DOC_SHA256 repetido no portao")
    A = {x["DOC_SHA256"]: x for x in a["ITEMS"]}
    faltam = [s for s in shas if s not in A]
    if faltam:
        raise FechoInvalido("%d itens do portao nao existem na revisao A"
                            % len(faltam))
    sobram = [s for s in A if s not in set(shas)]
    if sobram:
        raise FechoInvalido("%d itens da revisao A sem passagem pelo portao"
                            % len(sobram))
    return a, g, A


# ══════════════════════════════════════════════════════════════════════════
# 2 · A ADJUDICACAO
# ══════════════════════════════════════════════════════════════════════════
# Cinco saidas, e so uma delas produz rotulo. As outras quatro sao formas
# diferentes de dizer «aqui nao ha gabarito», e cada uma guarda o proprio nome
# porque as causas nao sao a mesma coisa.
CONFIRMED = "CONFIRMED"
CONFIRMED_CEGO = "CONFIRMED_BY_BLIND_REREVIEW"
EVIDENCE_GAP = "EVIDENCE_GAP"
UNRESOLVED = "UNRESOLVED"
AMBIGUOUS = "AMBIGUOUS"


def adjudicar(item_a, item_g):
    """Uma decisao, e a razao dela. Nada aqui escolhe entre A e A2."""
    la = item_a["LABEL"]
    if item_g["QUEUE"] == "CONFIRMACAO":
        if item_g.get("CONFIRMED") is not True:
            raise FechoInvalido("confirmacao sem CONFIRMED em %s"
                                % item_g["ITEM_ID"])
        if item_g.get("EVIDENCE_ATTESTED") is not True:
            raise FechoInvalido("confirmacao sem evidencia atestada em %s"
                                % item_g["ITEM_ID"])
        if not item_g.get("REASON_CODE"):
            raise FechoInvalido("confirmacao sem razao em %s"
                                % item_g["ITEM_ID"])
        if la == "T3_AMBIGUO":
            return AMBIGUOUS, None
        if la == "EVIDENCIA_INSUFICIENTE":
            return EVIDENCE_GAP, None
        return CONFIRMED, la

    a2 = item_g.get("LABEL_A2")
    if item_g.get("EVIDENCE_ATTESTED") is not True:
        raise FechoInvalido("segunda leitura sem evidencia atestada em %s"
                            % item_g["ITEM_ID"])
    if not item_g.get("REASON_CODE"):
        raise FechoInvalido("segunda leitura sem razao em %s"
                            % item_g["ITEM_ID"])
    if la != a2:
        # As duas leituras nao fecham. Fim. Nao se escolhe uma delas.
        return UNRESOLVED, None
    if la in BINARIOS:
        return CONFIRMED_CEGO, la
    if la == "EVIDENCIA_INSUFICIENTE":
        # Concordaram em «nao deu para saber». Isso e um buraco na evidencia,
        # e um buraco NAO e um negativo.
        return EVIDENCE_GAP, None
    return AMBIGUOUS, None


def fechar(a, g, A):
    portao = {x["DOC_SHA256"]: x for x in g["ITEMS"]}
    fora = []
    for sha, item_a in A.items():
        item_g = portao[sha]
        estado, rotulo = adjudicar(item_a, item_g)
        fora.append({
            "DOC_SHA256": sha,
            "ITEM_ID": item_a["ITEM_ID"],
            "FINAL_STATUS": estado,
            "FINAL_LABEL": rotulo,
            "EVAL_ELIGIBLE": "YES" if rotulo else "NO",
            "LABEL_A": item_a["LABEL"],
            "LABEL_A2": item_g.get("LABEL_A2"),
            "REASON_CODE_A2": item_g.get("REASON_CODE"),
            "REASON_TEXT_A2": item_g.get("REASON_TEXT"),
            "EVIDENCE_ATTESTED": item_g.get("EVIDENCE_ATTESTED") is True,
            "QUEUE": item_g["QUEUE"],
            "REOPENED_BY_HUMAN": item_g.get("REOPENED_BY_HUMAN", "NO"),
            "REVIEW_A_DECIDED_AT": item_a.get("DECIDED_AT"),
            "QUALITY_GATE_DECIDED_AT": item_g.get("DECIDED_AT"),
            "ORIGINAL_EVIDENCE": item_a["ORIGINAL_EVIDENCE"],
        })
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 3 · A DIVERSIDADE DO CONJUNTO CONFIRMADO
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ «NAO SEI» e a AUSENCIA de fonte, nao uma fonte. 27 dos 53 itens nao
# resolvem `SOURCE_ID`; conta-los como uma fonte distinta seria repetir, aqui,
# o defeito que o censo ja apanhou uma vez.
#
#     UM BALDE DE DESCONHECIDOS CONTADO COMO CATEGORIA
#     E DIVERSIDADE FABRICADA.
SEM_VALOR = "NAO SEI"

# A serie de publicacao: a identidade recorrente por tras das edicoes. Deriva
# do nome do documento com os MARCADORES DE EDICAO apagados — datas, `N<num>`,
# numeros soltos e sufixos de versao.
#
# A normalizacao e deliberadamente AGRESSIVA: na duvida, funde. O numero de
# series sai assim por baixo, e e por baixo que ele tem de errar — porque o
# que se afirma com ele e uma RESSALVA («ha menos independencia do que
# documentos»), e uma ressalva exagerada nao inventa confianca nenhuma.
EDICAO = [
    (r"\d{4}-\d{2}-\d{2}", ""), (r"\d{2}-\d{2}-\d{4}", ""),
    (r"\d{8}", ""), (r"\d{6}", ""),
    (r"\bv\d+\b", ""), (r"\bn[._-]?\d+\b", ""), (r"\b\d{1,4}\b", ""),
]


def serie_de(caminho, publicador):
    nome = os.path.basename(caminho).lower()
    nome = os.path.splitext(nome)[0]
    for padrao, troca in EDICAO:
        nome = re.sub(padrao, troca, nome)
    nome = re.sub(r"[^a-z]+", "-", nome).strip("-")
    return "%s · %s" % (publicador, nome or "(sem nome)")


def _palavras(evidencia):
    texto = " ".join([evidencia["TITLE"], evidencia["OPENING"]]
                     + evidencia["SELF_DESCRIPTION"]
                     + evidencia["SECTION_HEADERS"]).lower()
    return re.findall(r"[a-zà-ÿ]+", texto)


def _shingles(evidencia):
    p = _palavras(evidencia)
    return {tuple(p[i:i + SHINGLE]) for i in range(max(0, len(p) - SHINGLE + 1))}


def quase_duplicados(itens):
    """Pares cuja evidencia e quase a mesma. Nao remove nada — mede."""
    sh = {i["DOC_SHA256"]: _shingles(i["ORIGINAL_EVIDENCE"]) for i in itens}
    pares = []
    ids = [i["DOC_SHA256"] for i in itens]
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = sh[ids[x]], sh[ids[y]]
            if not a or not b:
                continue
            j = len(a & b) / len(a | b)
            if j >= LIMIAR_QUASE_DUPLICADO:
                pares.append((ids[x], ids[y], round(j, 3)))
    return pares


def agrupar_duplicados(itens, pares):
    """Junta num grupo os itens cuja evidencia e quase a mesma.

    ⚠️ ISTO MUDA A UNIDADE DE CONTAGEM, NAO O LIMIAR. Os criterios do censo
    continuam 10/10/3, escritos antes de qualquer numero. O que se corrige e
    o que conta como UM: quatro edicoes do mesmo boletim regional sao quatro
    ficheiros e uma observacao.
    """
    pai = {i["DOC_SHA256"]: i["DOC_SHA256"] for i in itens}

    def raiz(x):
        while pai[x] != x:
            x = pai[x]
        return x
    for a, b, _ in pares:
        ra, rb = raiz(a), raiz(b)
        if ra != rb:
            pai[ra] = rb
    for i in itens:
        i["GRUPO"] = raiz(i["DOC_SHA256"])
    return itens


def _um_por_grupo(itens):
    """Um representante por grupo, escolhido por ITEM_ID para ser estavel."""
    visto, fora = set(), []
    for i in sorted(itens, key=lambda x: x["ITEM_ID"]):
        if i["GRUPO"] not in visto:
            visto.add(i["GRUPO"])
            fora.append(i)
    return fora


def enriquecer(itens):
    """Cola a cada item o que o pacote sabe da proveniencia dele."""
    pacote = {x["DOC_SHA256"]: x for x in _json(PACOTE)["ITENS"]}
    for i in itens:
        p = pacote[i["DOC_SHA256"]]
        i["SOURCE_ID"] = p["SOURCE_ID"]
        i["PUBLISHER"] = p["PUBLISHER"]
        i["CONTENT_PATH"] = p["CANONICAL_PATH"]
        i["BODY_PATH"] = p["BODY_PATH"]
        i["DOCUMENT_TYPE"] = p["DOCUMENT_TYPE"]
        i["LANGUAGE"] = p["LANGUAGE"]
        i["COUNTRY"] = "IT"
        i["PUBLICATION_SERIES"] = serie_de(p["CANONICAL_PATH"], p["PUBLISHER"])
        i["CORPO_NO_DISCO"] = os.path.isfile(
            os.path.join(RAIZ, p["BODY_PATH"]))
    return itens


def _distintos(itens, campo):
    return sorted({i[campo] for i in itens} - {SEM_VALOR})


# ── O PORTAO DE AVALIACAO, CRITERIO A CRITERIO ────────────────────────────
# Os limiares sao os do censo, congelados antes de qualquer contagem desta
# missao. Nao se simplifica para «36 > 20»: cada linha e verificada sozinha,
# e a que falhar reprova o conjunto inteiro.
def portao_de_avaliacao(positivos, negativos, holdout_publicador):
    c = censo.CRITERIOS["EVALUATION"]
    pub_pos = set(_distintos(positivos, "PUBLISHER"))
    com_razao = [i for i in positivos + negativos if i["REASON_CODE_A2"]]
    atestados = [i for i in positivos + negativos if i["EVIDENCE_ATTESTED"]]
    corpo = [i for i in positivos + negativos if i["CORPO_NO_DISCO"]]
    n = len(positivos) + len(negativos)
    linhas = [
        ("POSITIVOS >= %d" % c["POSITIVOS_MIN"],
         len(positivos), len(positivos) >= c["POSITIVOS_MIN"]),
        ("NEGATIVOS >= %d" % c["NEGATIVOS_MIN"],
         len(negativos), len(negativos) >= c["NEGATIVOS_MIN"]),
        ("PUBLICADORES NO LADO POSITIVO >= %d" % c["PUBLICADORES_MIN"],
         len(pub_pos), len(pub_pos) >= c["PUBLICADORES_MIN"]),
        ("HOLDOUT DE PUBLICADOR COM AS DUAS CLASSES",
         "YES" if holdout_publicador else "NO", holdout_publicador),
        ("CORPO RECUPERAVEL EM TODOS", "%d/%d" % (len(corpo), n), len(corpo) == n),
        ("RAZAO ESTRUTURADA EM TODOS", "%d/%d" % (len(com_razao), n),
         len(com_razao) == n),
        ("EVIDENCIA ATESTADA EM TODOS", "%d/%d" % (len(atestados), n),
         len(atestados) == n),
    ]
    return {"LINHAS": [{"CRITERIO": a, "MEDIDO": b, "PASSA": c_} for a, b, c_ in linhas],
            "PASSA": all(l[2] for l in linhas)}


def holdout_possivel(positivos, negativos, campo):
    """Tirar QUALQUER valor tem de deixar positivo E negativo do outro lado.

    ESTRUTURA NAO E COBERTURA: ter tres publicadores nao chega; e preciso que
    retirar qualquer um deles ainda deixe as duas classes representadas.
    """
    valores = set(_distintos(positivos, campo)) | set(_distintos(negativos, campo))
    if len(valores) < 3:
        return False, sorted(valores)
    ok = all(
        any(p[campo] != fora for p in positivos)
        and any(n[campo] != fora for n in negativos)
        for fora in valores)
    return ok, sorted(valores)


# ══════════════════════════════════════════════════════════════════════════
# 4 · O ARTEFATO
# ══════════════════════════════════════════════════════════════════════════
def construir(a, g, itens):
    """Um artefato so. Sem MASTER, sem FINAL, sem V2 paralelo."""
    dentro = [i for i in itens if i["EVAL_ELIGIBLE"] == "YES"]
    fora = [i for i in itens if i["EVAL_ELIGIBLE"] == "NO"]
    caminho = {CONFIRMED: "A_CONFIRMED", CONFIRMED_CEGO: "A_CONFIRMED_BY_BLIND_REREVIEW"}

    gt = [{
        "DOC_SHA256": i["DOC_SHA256"],
        "ITEM_ID": i["ITEM_ID"],
        "SOURCE_ID": i["SOURCE_ID"],
        "PUBLISHER": i["PUBLISHER"],
        "PUBLICATION_SERIES": i["PUBLICATION_SERIES"],
        "CONTENT_PATH": i["CONTENT_PATH"],
        "BODY_PATH": i["BODY_PATH"],
        "DOCUMENT_TYPE": i["DOCUMENT_TYPE"],
        "LANGUAGE": i["LANGUAGE"],
        "COUNTRY": i["COUNTRY"],
        "LABEL": i["FINAL_LABEL"],
        "LABEL_AUTHORITY": "HUMAN_VERIFIED",
        "REVIEW_PATH": caminho[i["FINAL_STATUS"]],
        "HUMAN_REASON_CODE": i["REASON_CODE_A2"],
        # Nao se inventa texto de razao. Se a pessoa nao escreveu, fica null.
        "HUMAN_REASON_TEXT": i["REASON_TEXT_A2"],
        "EVIDENCE_ATTESTED": i["EVIDENCE_ATTESTED"],
        "ORIGINAL_EVIDENCE": i["ORIGINAL_EVIDENCE"],
        "REVIEW_A_DECIDED_AT": i["REVIEW_A_DECIDED_AT"],
        "QUALITY_GATE_DECIDED_AT": i["QUALITY_GATE_DECIDED_AT"],
    } for i in sorted(dentro, key=lambda x: x["ITEM_ID"])]

    excluidos = [{
        "DOC_SHA256": i["DOC_SHA256"],
        "ITEM_ID": i["ITEM_ID"],
        "STATUS": i["FINAL_STATUS"],
        "LABEL_A": i["LABEL_A"],
        "LABEL_A2": i["LABEL_A2"],
        "REASON_CODE_A2": i["REASON_CODE_A2"],
        "PUBLISHER": i["PUBLISHER"],
        "SOURCE_ID": i["SOURCE_ID"],
    } for i in sorted(fora, key=lambda x: x["ITEM_ID"])]

    pos = [i for i in dentro if i["FINAL_LABEL"] == "T3_SIM"]
    neg = [i for i in dentro if i["FINAL_LABEL"] == "T3_NAO"]
    hp, pubs = holdout_possivel(pos, neg, "PUBLISHER")
    hs, srcs = holdout_possivel(pos, neg, "SOURCE_ID")
    pares = quase_duplicados(dentro)
    agrupar_duplicados(dentro, [(p[0], p[1], p[2]) for p in pares])
    upos, uneg = _um_por_grupo(pos), _um_por_grupo(neg)
    hpu, _ = holdout_possivel(upos, uneg, "PUBLISHER")
    hsu, _ = holdout_possivel(upos, uneg, "SOURCE_ID")
    portao_gate = portao_de_avaliacao(upos, uneg, hpu)

    doc = {
        "SCHEMA": SCHEMA_GABARITO,
        "UNIVERSE": "T3",
        "DESCRIPTION": "Praga e doença",
        "O_QUE_ISTO_E": (
            "O gabarito de T3 para AVALIACAO. Cada item aqui foi rotulado por "
            "uma PESSOA e fechou em duas leituras. Nao ha rotulo de maquina, "
            "nao ha rotulo derivado das palavras da Admission, e nao ha item "
            "cujas duas leituras tenham divergido."),
        "REGRA": (
            "A != A2 -> UNRESOLVED, e nada mais. EVIDENCIA_INSUFICIENTE nunca "
            "vira NAO. AMBIGUO nunca vira SIM."),
        "QUEM_ROTULOU": (
            "Uma pessoa, em duas passagens. A segunda foi cega nos 21 itens da "
            "fila de releitura. NAO houve segundo revisor independente."),
        "AUTO_LABELS_ASSIGNED": 0,
        "LABEL_AUTHORITY": "HUMAN_VERIFIED",

        "EVALUATION_SCOPE": "ITALIAN_AGRO_INSTITUTIONAL_CORPUS",
        "O_LIMITE_DO_ESCOPO": (
            "Todo o corpus vem de instituicoes italianas (COUNTRY = IT em "
            "36/36). O IDIOMA nao esta resolvido em todos os itens e ha pelo "
            "menos um em ingles — ver IDIOMA_MEDIDO. Este gabarito NAO "
            "autoriza afirmar generalizacao para Franca, Espanha ou EAME."),

        "SOURCE_REVIEW_A": REVISAO_A,
        "SOURCE_REVIEW_A_SHA256": sha256_do_ficheiro(REVISAO_A),
        "SOURCE_QUALITY_GATE": PORTAO,
        "SOURCE_QUALITY_GATE_SHA256": sha256_do_ficheiro(PORTAO),
        "SOURCE_PACKET": PACOTE,
        "GENERATED_AT": g["COMPLETED_AT"],
        "GENERATED_AT_PORQUE": (
            "E a hora em que a ULTIMA decisao humana foi tomada, nao a hora em "
            "que este ficheiro foi escrito. Reescrever o gerador nao muda "
            "quando a pessoa decidiu, e o artefato tem de sair igual duas "
            "vezes seguidas."),
        "GENERATOR": GERADOR,

        "TOTAL_REVIEWED": len(itens),
        "COUNTS": {
            "EVAL_ELIGIBLE": len(dentro),
            "CONFIRMED_SIM": len(pos),
            "CONFIRMED_NAO": len(neg),
            "CONFIRMED": sum(1 for i in itens if i["FINAL_STATUS"] == CONFIRMED),
            "CONFIRMED_BY_BLIND_REREVIEW":
                sum(1 for i in itens if i["FINAL_STATUS"] == CONFIRMED_CEGO),
            "UNRESOLVED": sum(1 for i in itens if i["FINAL_STATUS"] == UNRESOLVED),
            "EVIDENCE_GAP": sum(1 for i in itens if i["FINAL_STATUS"] == EVIDENCE_GAP),
            "AMBIGUOUS": sum(1 for i in itens if i["FINAL_STATUS"] == AMBIGUOUS),
        },
        "DIVERSITY": {
            "POSITIVE_PUBLISHERS": _distintos(pos, "PUBLISHER"),
            "NEGATIVE_PUBLISHERS": _distintos(neg, "PUBLISHER"),
            "POSITIVE_SOURCE_IDS": _distintos(pos, "SOURCE_ID"),
            "NEGATIVE_SOURCE_IDS": _distintos(neg, "SOURCE_ID"),
            "PUBLICATION_SERIES": sorted({i["PUBLICATION_SERIES"] for i in dentro}),
            "POSITIVE_PUBLICATION_SERIES":
                sorted({i["PUBLICATION_SERIES"] for i in pos}),
            "DOCUMENT_FAMILIES": sorted({i["DOCUMENT_TYPE"] for i in dentro}),
            "LANGUAGES": sorted({i["LANGUAGE"] for i in dentro}),
            "COUNTRIES": sorted({i["COUNTRY"] for i in dentro}),
            "SOURCE_ID_AUSENTE": sum(1 for i in dentro
                                     if i["SOURCE_ID"] == SEM_VALOR),
        },
        "HOLDOUT": {
            "PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE": "YES" if hp else "NO",
            "PUBLISHERS_CONSIDERADOS": pubs,
            "SOURCE_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE": "YES" if hs else "NO",
            "SOURCES_CONSIDERADAS": srcs,
            "COUNTRY_HOLDOUT_POSSIBLE": "NO",
            "LANGUAGE_HOLDOUT_POSSIBLE": "NO",
            "O_QUE_HOLDOUT_EXIGE": (
                "Tirar QUALQUER valor tem de deixar positivo E negativo do "
                "outro lado. ESTRUTURA NAO E COBERTURA."),
        },
        "NEAR_DUPLICATES": {
            "MEDIDO_SOBRE": "a evidencia que a pessoa viu (titulo, abertura, "
                            "auto-descricao, titulos de seccao)",
            "METODO": "Jaccard de %d-gramas de palavras" % SHINGLE,
            "LIMIAR": LIMIAR_QUASE_DUPLICADO,
            "PARES": [{"A": p[0], "B": p[1], "JACCARD": p[2]} for p in pares],
            "TOTAL_PARES": len(pares),
        },
        # ── O QUE SOBRA DEPOIS DE FUNDIR AS EDICOES DA MESMA SERIE ────────
        "INDEPENDENCIA": {
            "PORQUE": (
                "Quatro edicoes seguidas do mesmo boletim regional sao quatro "
                "ficheiros e uma observacao. O portao conta GRUPOS, nao "
                "ficheiros — os limiares nao mudaram, mudou o que conta como "
                "um."),
            "DOCUMENTS": len(dentro),
            "GRUPOS_INDEPENDENTES": len({i["GRUPO"] for i in dentro}),
            "POSITIVOS_DOCUMENTOS": len(pos),
            "POSITIVOS_INDEPENDENTES": len(upos),
            "NEGATIVOS_DOCUMENTOS": len(neg),
            "NEGATIVOS_INDEPENDENTES": len(uneg),
            "PUBLISHER_HOLDOUT_APOS_FUNDIR": "YES" if hpu else "NO",
            "SOURCE_HOLDOUT_APOS_FUNDIR": "YES" if hsu else "NO",
        },
        "EVALUATION_GATE": portao_gate,
        "IDIOMA_MEDIDO": {
            "PORQUE": (
                "O campo LANGUAGE do pacote nao esta resolvido em todos. "
                "Declarar «tudo italiano» sem o ter medido seria afirmar o "
                "que nao foi visto."),
            "CONTAGEM": dict(Counter(i["LANGUAGE"] for i in dentro)),
            "RESOLVIDO_COMO_IT": sum(1 for i in dentro
                                     if i["LANGUAGE"].startswith("it")),
            "NAO_RESOLVIDO": sum(1 for i in dentro
                                 if i["LANGUAGE"] == SEM_VALOR),
            "NAO_ITALIANO": sorted(i["ITEM_ID"] for i in dentro
                                   if i["LANGUAGE"] not in (SEM_VALOR,)
                                   and not i["LANGUAGE"].startswith("it")),
        },
        "CORPO_NO_DISCO": sum(1 for i in dentro if i["CORPO_NO_DISCO"]),
        "GROUND_TRUTH": gt,
        "EXCLUDED_FROM_EVALUATION": excluidos,
        "O_QUE_EXCLUDED_NAO_E": (
            "Isto NAO e ground truth. Fica registado para nao se perder o "
            "trabalho humano e para se saber onde a evidencia falhou."),
    }
    # As sondas leem o artefato ja montado — incluindo a propria ressalva de
    # escopo, que a sonda 10 procura no texto e nao no bom senso de quem le.
    doc["RED_TEAM"] = red_team(itens, doc)
    return doc


# ══════════════════════════════════════════════════════════════════════════
# 5 · O RED TEAM — tentar provar que este verde e falso
# ══════════════════════════════════════════════════════════════════════════
# Um gabarito que passa o portao e um gabarito que ninguem tentou derrubar sao
# a mesma folha de papel. Cada sonda abaixo procura uma maneira concreta de o
# numero estar certo e a conclusao errada.
#
#     PASSAR NO PORTAO NAO E O MESMO QUE AGUENTAR UM ATAQUE.
# Afirmacoes que este gabarito NAO pode sustentar. A sonda 10 procura-as no
# artefato inteiro — e a ressalva tem de estar la escrita, nao subentendida.
AFIRMACOES_PROIBIDAS = ("GENERALIZA PARA", "VALE PARA EAME", "COBRE EAME",
                        "VALIDO PARA FRANCA", "VALIDO PARA ESPANHA")


def linha_de(doc, prefixo):
    """O numero que o PORTAO usou — nao o que o relatorio diz ao lado."""
    for l in doc["EVALUATION_GATE"]["LINHAS"]:
        if l["CRITERIO"].startswith(prefixo):
            return l["MEDIDO"]
    return None


def red_team(itens, doc):
    dentro = [i for i in itens if i["EVAL_ELIGIBLE"] == "YES"]
    pos = [i for i in dentro if i["FINAL_LABEL"] == "T3_SIM"]
    neg = [i for i in dentro if i["FINAL_LABEL"] == "T3_NAO"]
    d, ind, idi = doc["DIVERSITY"], doc["INDEPENDENCIA"], doc["IDIOMA_MEDIDO"]
    gt = {x["DOC_SHA256"]: x for x in doc["GROUND_TRUTH"]}
    A = {i["DOC_SHA256"]: i for i in itens}

    maior_serie = Counter(i["PUBLICATION_SERIES"] for i in pos).most_common(1)
    maior = maior_serie[0][1] if maior_serie else 0

    # Um par quase-duplicado que atravesse publicadores poe duas copias do
    # mesmo boletim em lados opostos de qualquer divisao por publicador.
    atravessa = [p for p in doc["NEAR_DUPLICATES"]["PARES"]
                 if A[p["A"]]["PUBLISHER"] != A[p["B"]]["PUBLISHER"]]
    troca_silenciosa = [x["ITEM_ID"] for x in doc["GROUND_TRUTH"]
                        if x["REVIEW_PATH"] == "A_CONFIRMED"
                        and x["LABEL"] != A[x["DOC_SHA256"]]["LABEL_A"]]
    divergentes = {i["DOC_SHA256"] for i in itens
                   if i["FINAL_STATUS"] == UNRESOLVED}
    insuficientes = {i["DOC_SHA256"] for i in itens
                     if i["FINAL_STATUS"] == EVIDENCE_GAP}
    bruto = json.dumps(doc, ensure_ascii=False).upper()

    sondas = [
        ("1 · positivos concentrados numa unica serie",
         "%d de %d positivos na maior serie; %d series positivas"
         % (maior, len(pos), len(d["POSITIVE_PUBLICATION_SERIES"])),
         maior < len(pos)),
        ("2 · documentos iguais contados como independentes",
         "%d pares quase-duplicados; %d ficheiros -> %d grupos; "
         "positivos %d -> %d" % (doc["NEAR_DUPLICATES"]["TOTAL_PARES"],
                                 ind["DOCUMENTS"], ind["GRUPOS_INDEPENDENTES"],
                                 ind["POSITIVOS_DOCUMENTOS"],
                                 ind["POSITIVOS_INDEPENDENTES"]),
         # A pergunta nao e «medi os grupos?»: e «o VEREDICTO assenta neles?».
         linha_de(doc, "POSITIVOS") == ind["POSITIVOS_INDEPENDENTES"]),
        ("3 · copia do mesmo boletim atravessa o holdout de publicador",
         "%d pares quase-duplicados atravessam publicadores" % len(atravessa),
         not atravessa),
        ("4 · razao existe mas evidencia nao foi atestada",
         "%d/%d com razao · %d/%d atestados"
         % (sum(1 for x in gt.values() if x["HUMAN_REASON_CODE"]), len(gt),
            sum(1 for x in gt.values() if x["EVIDENCE_ATTESTED"]), len(gt)),
         all(x["HUMAN_REASON_CODE"] and x["EVIDENCE_ATTESTED"]
             for x in gt.values())),
        ("5 · item divergente entrou por engano",
         "%d divergentes; %d deles no gabarito"
         % (len(divergentes), len(divergentes & set(gt))),
         not (divergentes & set(gt))),
        ("6 · «nao deu para saber» virou negativo",
         "%d buracos de evidencia; %d deles no gabarito"
         % (len(insuficientes), len(insuficientes & set(gt))),
         not (insuficientes & set(gt))),
        ("7 · A2 substituiu A em silencio",
         "%d confirmacoes com rotulo diferente de A" % len(troca_silenciosa),
         not troca_silenciosa),
        ("8 · «NAO SEI» contado como fonte distinta",
         "%d dos %d sem SOURCE_ID; excluidos de toda a contagem"
         % (d["SOURCE_ID_AUSENTE"], len(gt)),
         SEM_VALOR not in d["POSITIVE_SOURCE_IDS"] + d["NEGATIVE_SOURCE_IDS"]),
        ("9 · pais e idioma unicos ignorados",
         "paises %s · idioma resolvido em %d/%d · nao italiano: %s"
         % (d["COUNTRIES"], idi["RESOLVIDO_COMO_IT"], len(gt),
            idi["NAO_ITALIANO"] or "nenhum"),
         # Cada item tem de estar contado numa das tres caixas de idioma.
         doc["HOLDOUT"]["COUNTRY_HOLDOUT_POSSIBLE"] == "NO"
         and (idi["RESOLVIDO_COMO_IT"] + idi["NAO_RESOLVIDO"]
              + len(idi["NAO_ITALIANO"]) == len(gt))),
        ("10 · gabarito italiano a afirmar EAME",
         "EVALUATION_SCOPE = %s · ressalva escrita: %s"
         % (doc["EVALUATION_SCOPE"],
            "SIM" if "NAO AUTORIZA AFIRMAR GENERALIZACAO" in bruto else "NAO"),
         doc["EVALUATION_SCOPE"] == "ITALIAN_AGRO_INSTITUTIONAL_CORPUS"
         and "NAO AUTORIZA AFIRMAR GENERALIZACAO" in bruto
         and not any(m in bruto for m in AFIRMACOES_PROIBIDAS)),
    ]
    return [{"SONDA": a, "MEDIDO": b, "AGUENTA": c} for a, b, c in sondas]


# ══════════════════════════════════════════════════════════════════════════
# 6 · O RELATORIO
# ══════════════════════════════════════════════════════════════════════════
def gerar():
    a, g, A = carregar()
    itens = enriquecer(fechar(a, g, A))
    return a, g, itens, construir(a, g, itens)


def main():
    a, g, itens, doc = gerar()
    c, d, h = doc["COUNTS"], doc["DIVERSITY"], doc["HOLDOUT"]

    print("FECHAR O GABARITO DE T3")
    print("=" * 74)
    print("  AS DUAS ENTRADAS HUMANAS")
    print(f"    REVIEW_A_SHA256          {doc['SOURCE_REVIEW_A_SHA256']}")
    print(f"    QUALITY_GATE_SHA256      {doc['SOURCE_QUALITY_GATE_SHA256']}")
    print(f"    STATUS                   {g['STATUS']}")
    print(f"    TOTAL_ANSWERED           {g['TOTAL_ANSWERED']}/{g['TOTAL_EXPECTED']}")
    print(f"    CONFIRMACAO              "
          f"{sum(1 for x in g['ITEMS'] if x['QUEUE'] == 'CONFIRMACAO')}")
    print(f"    SEGUNDA_LEITURA          "
          f"{sum(1 for x in g['ITEMS'] if x['QUEUE'] == 'SEGUNDA_LEITURA')}")
    print(f"    AUTO_LABELS_ASSIGNED     {g['AUTO_LABELS_ASSIGNED']}")
    print(f"    INDEPENDENT_SECOND_REVIEWER  {g['INDEPENDENT_SECOND_REVIEWER']}")

    print("\n  O CRUZAMENTO A x A2")
    cruz = Counter((i["LABEL_A"], i["LABEL_A2"] or "—", i["FINAL_STATUS"])
                   for i in itens)
    print(f"    {'LABEL_A':<24}{'LABEL_A2':<24}{'FINAL_STATUS':<30}N")
    for (la, a2, st), n in sorted(cruz.items()):
        print(f"    {la:<24}{a2:<24}{st:<30}{n}")

    print("\n  O FECHO")
    print(f"    EVAL_ELIGIBLE            {c['EVAL_ELIGIBLE']}")
    print(f"      CONFIRMED_SIM          {c['CONFIRMED_SIM']}")
    print(f"      CONFIRMED_NAO          {c['CONFIRMED_NAO']}")
    print(f"      via A_CONFIRMED        {c['CONFIRMED']}")
    print(f"      via RELEITURA CEGA     {c['CONFIRMED_BY_BLIND_REREVIEW']}")
    print(f"    UNRESOLVED               {c['UNRESOLVED']}")
    print(f"    EVIDENCE_GAP             {c['EVIDENCE_GAP']}")
    print(f"    AMBIGUOUS                {c['AMBIGUOUS']}")
    print(f"    soma                     "
          f"{c['EVAL_ELIGIBLE'] + c['UNRESOLVED'] + c['EVIDENCE_GAP'] + c['AMBIGUOUS']}"
          f"/{doc['TOTAL_REVIEWED']}")

    print("\n  A DIVERSIDADE DOS CONFIRMADOS")
    print(f"    POSITIVE_PUBLISHERS      {len(d['POSITIVE_PUBLISHERS'])}  "
          f"{d['POSITIVE_PUBLISHERS']}")
    print(f"    NEGATIVE_PUBLISHERS      {len(d['NEGATIVE_PUBLISHERS'])}  "
          f"{d['NEGATIVE_PUBLISHERS']}")
    print(f"    POSITIVE_SOURCE_IDS      {len(d['POSITIVE_SOURCE_IDS'])}")
    print(f"    NEGATIVE_SOURCE_IDS      {len(d['NEGATIVE_SOURCE_IDS'])}")
    print(f"    SOURCE_ID ausente        {d['SOURCE_ID_AUSENTE']} de "
          f"{c['EVAL_ELIGIBLE']}   («NAO SEI» nao conta como fonte)")
    print(f"    DOCUMENT_FAMILIES        {d['DOCUMENT_FAMILIES']}")
    print(f"    LANGUAGES                {d['LANGUAGES']}")
    print(f"    COUNTRIES                {d['COUNTRIES']}")
    print(f"\n    DOCUMENTS                {c['EVAL_ELIGIBLE']}")
    print(f"    PUBLICATION_SERIES       {len(d['PUBLICATION_SERIES'])}"
          f"   (positivo: {len(d['POSITIVE_PUBLICATION_SERIES'])})")
    print(f"    PUBLISHERS               "
          f"{len(set(d['POSITIVE_PUBLISHERS']) | set(d['NEGATIVE_PUBLISHERS']))}")
    print(f"    SOURCES                  "
          f"{len(set(d['POSITIVE_SOURCE_IDS']) | set(d['NEGATIVE_SOURCE_IDS']))}")

    print("\n  O HOLDOUT, MEDIDO")
    print(f"    PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE = "
          f"{h['PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE']}")
    print(f"    SOURCE_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE    = "
          f"{h['SOURCE_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE']}")
    print(f"    COUNTRY_HOLDOUT_POSSIBLE                     = "
          f"{h['COUNTRY_HOLDOUT_POSSIBLE']}")
    print(f"    LANGUAGE_HOLDOUT_POSSIBLE                    = "
          f"{h['LANGUAGE_HOLDOUT_POSSIBLE']}")

    nd = doc["NEAR_DUPLICATES"]
    print(f"\n  QUASE-DUPLICADOS (Jaccard {SHINGLE}-gramas >= "
          f"{LIMIAR_QUASE_DUPLICADO})")
    print(f"    TOTAL_PARES              {nd['TOTAL_PARES']}")
    por_id = {i["DOC_SHA256"]: i["ITEM_ID"] for i in itens}
    for p in nd["PARES"][:8]:
        print(f"      {por_id[p['A']]:<40}{por_id[p['B']]:<40}{p['JACCARD']}")

    ind = doc["INDEPENDENCIA"]
    print("\n  O QUE SOBRA DEPOIS DE FUNDIR AS EDICOES DA MESMA SERIE")
    print(f"    DOCUMENTS                {ind['DOCUMENTS']}"
          f"  ->  GRUPOS {ind['GRUPOS_INDEPENDENTES']}")
    print(f"    POSITIVOS                {ind['POSITIVOS_DOCUMENTOS']}"
          f"  ->  {ind['POSITIVOS_INDEPENDENTES']}")
    print(f"    NEGATIVOS                {ind['NEGATIVOS_DOCUMENTOS']}"
          f"  ->  {ind['NEGATIVOS_INDEPENDENTES']}")
    print(f"    holdout de publicador apos fundir  "
          f"{ind['PUBLISHER_HOLDOUT_APOS_FUNDIR']}")

    print("\n  O PORTAO DE AVALIACAO, CRITERIO A CRITERIO (sobre os grupos)")
    for l in doc["EVALUATION_GATE"]["LINHAS"]:
        print(f"    {'PASSA' if l['PASSA'] else 'FALHA':<6}"
              f"{str(l['MEDIDO']):>8}   {l['CRITERIO']}")
    print(f"    -> EVALUATION = "
          f"{'YES' if doc['EVALUATION_GATE']['PASSA'] else 'NO'}")

    idi = doc["IDIOMA_MEDIDO"]
    print("\n  O IDIOMA, MEDIDO E NAO PRESUMIDO")
    print(f"    resolvido como italiano  {idi['RESOLVIDO_COMO_IT']}"
          f"/{c['EVAL_ELIGIBLE']}")
    print(f"    nao resolvido            {idi['NAO_RESOLVIDO']}")
    print(f"    nao italiano             {idi['NAO_ITALIANO']}")

    print(f"\n  CORPO_NO_DISCO             {doc['CORPO_NO_DISCO']}"
          f"/{c['EVAL_ELIGIBLE']}")
    print(f"  EVALUATION_SCOPE           {doc['EVALUATION_SCOPE']}")
    print(f"  CLASSIFIER_BUILT           NO")
    print(f"  ADMISSION_CHANGED          NO")

    print("\n  O RED TEAM — dez maneiras de este verde ser falso")
    rt = doc["RED_TEAM"]
    for r in rt:
        print(f"    {'AGUENTA' if r['AGUENTA'] else 'CEDE':<8}{r['SONDA']}")
        print(f"             {r['MEDIDO']}")
    print(f"    RED_TEAM = {sum(1 for r in rt if r['AGUENTA'])}/{len(rt)} "
          f"sondas aguentam")

    if "--escrever" in sys.argv:
        alvo = os.path.join(RAIZ, GABARITO)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\n  escrito: {GABARITO}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
