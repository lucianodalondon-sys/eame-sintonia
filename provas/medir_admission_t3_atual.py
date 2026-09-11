#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MEDIR A ADMISSION DE HOJE CONTRA O GABARITO HUMANO DE T3.

    python3 provas/medir_admission_t3_atual.py
    python3 provas/medir_admission_t3_atual.py --escrever

Isto e uma BASELINE. Mede-se o mecanismo tal como ele esta, e nao se lhe toca.

    MEASURE != FIX
    CLASSIFIER_BUILT = NO · ADMISSION_CHANGED = NO · KEYWORDS_CHANGED = NO

A LEI QUE GOVERNA ESTA PROVA
----------------------------
    COPIAR AS PALAVRAS DA PORTA PARA DENTRO DA PROVA E PROIBIDO.

Uma prova que reimplementa a regra mede a PROVA, nao a porta. Aqui chama-se
`admissao.decidir` — a mesma funcao que `orquestrador.py:228` e
`coleta/rota_forward_documento.py:206` executam em producao — e captura-se o
que ela devolver, sem traduzir e sem arredondar.

AS DUAS FILAS DE ENTRADA, E POR QUE SAO DUAS
--------------------------------------------
A porta pergunta PRONTIDAO antes de tema, e isso e lei (COL-LAW-042: «as que
apuram se da para olhar vem primeiro, porque nao se julga o que nao se leu»).

O registo de artefatos desta arvore diz `SOURCE_ID = "NAO SEI"` nos 30 textos
derivados, e `coleta/ingresso.py` e claro sobre o que isso vale:

    A CONFISSAO DE IGNORANCIA NAO E UM VALOR.

Entao o item chega a porta sem origem, e a porta para antes do tema. Medir so
isso responderia a pergunta errada — diria quanto falta a LINHAGEM, e nao quanto
acerta a REGRA TEMATICA. Por isso ha dois planos, e a regra de qual e qual foi
fixada ANTES de olhar para qualquer numero:

    CONTRATO    so o que o item declara de si. E o que a producao ve hoje.
                Responde: a porta chega sequer a decidir tema?

    LINHAGEM    o mesmo, mais o `SOURCE_ID` que o gabarito ja resolveu por
                linhagem numa missao anterior. E o unico plano que exercita a
                regra tematica, e portanto E A BASELINE TEMATICA.

Nenhum dos dois e escondido, e nenhum e apresentado como «o numero».
"""
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402

GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"
REGISTO = "data/derivados/REGISTO-DE-ARTEFATOS.json"
SAIDA = "data/derivados/BASELINE-ADMISSION-T3-V1.json"
UNIVERSO = "T3"

# ── O DONO REAL, PROVADO E NAO LEMBRADO ────────────────────────────────────
# Nao basta «o modulo existe». Prova-se: modulo -> funcao -> chamador -> a rota
# que a producao corre. Cada linha abaixo e conferida contra o ficheiro.
CADEIA = [
    ("admissao/admissao.py", "PERGUNTAS_DO_UNIVERSO = {",
     "a lista de palavras, por universo"),
    ("admissao/admissao.py", "def _do_universo(",
     "a funcao que decide o tema"),
    ("admissao/admissao.py", "def decidir(",
     "a porta: prontidao primeiro, tema depois"),
    ("orquestrador/orquestrador.py", "adm.decidir(x, universo, corrida=run_id)",
     "o orquestrador corre a porta sobre a colheita"),
    ("coleta/rota_forward_documento.py",
     "admissao.decidir(item, universo, corrida=run_id)",
     "a rota de documento corre a porta"),
    ("coleta/ingresso.py", "def para_a_porta(",
     "o unico tradutor do contrato para a lingua da porta"),
]

OWNER_FILE = "admissao/admissao.py"
OWNER_FUNCTION = "_do_universo (via decidir)"
T3_RULE_LOCATION = "admissao/admissao.py :: PERGUNTAS_DO_UNIVERSO['T3']"

CONTRATO, LINHAGEM = "CONTRATO", "LINHAGEM"
PLANO_DA_BASELINE_TEMATICA = LINHAGEM


class MedicaoInvalida(Exception):
    """Nao se produz score a partir de uma copia nem de um gabarito mexido."""


def sha256_do_ficheiro(caminho):
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _json(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


def provar_cadeia():
    """Cada elo lido no ficheiro. Um elo que falte para a missao."""
    fora = []
    for ficheiro, marca, porque in CADEIA:
        with open(os.path.join(RAIZ, ficheiro), encoding="utf-8") as f:
            linhas = f.read().splitlines()
        onde = [i + 1 for i, l in enumerate(linhas) if marca in l]
        if not onde:
            raise MedicaoInvalida(
                "elo da cadeia nao encontrado: %s :: %r" % (ficheiro, marca))
        fora.append({"FILE": ficheiro, "MARCA": marca, "LINE": onde[0],
                     "PORQUE": porque})
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 1 · O ADAPTER FINO — carrega, traduz pelo dono, chama. Nada mais.
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ ELE NAO CLASSIFICA. Nao normaliza semantica, nao acrescenta palavra, nao
# escolhe trecho por conteudo, nao infere `SOURCE_ID` e nao fabrica id.
#
#     THIN_ADAPTER_HAS_SEMANTIC_LOGIC = NO
#
# A traducao de nomes e do `coleta/ingresso.py::para_a_porta`, que e o dono
# unico dela. Aqui nao se reescreve o mapa.
DA_FICHA = (ing.DO_COLETOR + ing.DA_FICHA_PARA_A_PORTA
            + ("FACT_TIME", "PUBLISHED_AT", "COLLECTED_AT"))


def texto_do_corpo(caminho):
    """O documento INTEIRO, decodificado. Sem cortar, sem escolher, sem limpar.

    Escolher um trecho seria escolher por conteudo — e o conteudo e justamente
    o que esta a ser medido.
    """
    with open(os.path.join(RAIZ, caminho), "rb") as f:
        return f.read().decode("utf-8", "replace")


def item_para_a_porta(ficha_gt, registo, plano):
    """O item na lingua da porta. `plano` decide SO a origem, e nada mais."""
    bruto = {k: v for k, v in registo.items()
             if k in DA_FICHA and v not in ing.NAO_E_AFIRMACAO}
    if plano == LINHAGEM:
        # O `SOURCE_ID` que o GABARITO ja declara — resolvido por linhagem numa
        # missao anterior e commitado. E uma LEITURA, nao uma inferencia: esta
        # funcao nao sabe derivar fonte nenhuma e nao tenta.
        sid = ficha_gt.get("SOURCE_ID")
        if sid not in ing.NAO_E_AFIRMACAO:
            bruto.setdefault("SOURCE_ID", sid)
    item = ing.para_a_porta(bruto)
    item["id"] = registo.get("ARTIFACT_ID") or ficha_gt["ITEM_ID"]
    item["texto"] = texto_do_corpo(ficha_gt["BODY_PATH"])
    return item


# ══════════════════════════════════════════════════════════════════════════
# 2 · OS ESTADOS DA PORTA, DESCOBERTOS E NAO PRESUMIDOS
# ══════════════════════════════════════════════════════════════════════════
# A porta tem cinco saidas e elas NAO sao a mesma coisa. Esmagar `NAO_SEI` em
# `NAO` transformaria uma confissao numa rejeicao, e inflaria o denominador com
# decisoes que ninguem tomou.
#
#     NAO != NAO_SEI != NAO_SE_APLICA != ERRO
PRED_POSITIVE, PRED_NEGATIVE = "PRED_POSITIVE", "PRED_NEGATIVE"
ABSTAIN, NOT_APPLICABLE, ERROR = "ABSTAIN", "NOT_APPLICABLE", "ERROR"

# Declarado DEPOIS de enumerar os estados reais do runtime, e nunca alargado.
BALDE = {
    adm.SIM: PRED_POSITIVE,
    adm.NAO: PRED_NEGATIVE,
    adm.NAO_SEI: ABSTAIN,
    adm.NAO_SE_APLICA: NOT_APPLICABLE,
    adm.ERRO: ERROR,
}
BINARIOS = (PRED_POSITIVE, PRED_NEGATIVE)


def estados_do_runtime():
    """Os estados que o runtime declara, lidos dele e nao desta prova."""
    return list(adm.RESULTADOS)


def balde_de(saida_crua):
    if saida_crua not in BALDE:
        # Um estado novo no runtime nao pode ser engolido em silencio.
        raise MedicaoInvalida("estado desconhecido da porta: %r" % saida_crua)
    return BALDE[saida_crua]


# ══════════════════════════════════════════════════════════════════════════
# 3 · A MEDICAO
# ══════════════════════════════════════════════════════════════════════════
def carregar_gabarito():
    d = _json(GABARITO)
    gt = d["GROUND_TRUTH"]
    if len(gt) != 36:
        raise MedicaoInvalida("o gabarito tem %d itens, nao 36" % len(gt))
    shas = [x["DOC_SHA256"] for x in gt]
    if len(set(shas)) != len(shas):
        raise MedicaoInvalida("ha DOC_SHA256 repetido no gabarito")
    maus = {x["LABEL"] for x in gt} - {"T3_SIM", "T3_NAO"}
    if maus:
        raise MedicaoInvalida("rotulo fora do binario: %s" % sorted(maus))
    if d.get("AUTO_LABELS_ASSIGNED") != 0:
        raise MedicaoInvalida("o gabarito declara rotulos de maquina")
    return d, gt


def medir(gt, plano):
    """Uma linha por documento. A saida crua da porta viaja intacta."""
    reg = {a["STORAGE_LOCATION"]: a
           for a in _json(REGISTO)["ARTEFATOS"]}
    fora = []
    for x in sorted(gt, key=lambda y: y["ITEM_ID"]):
        ficha = reg.get(x["BODY_PATH"], {})
        try:
            item = item_para_a_porta(x, ficha, plano)
            d = adm.decidir(item, UNIVERSO)
            cru, regra, motivo = d.resultado, d.regra, d.motivo
            evidencia = d.evidencia
        except Exception as erro:                      # noqa: BLE001
            # Uma falha de execucao e ERROR — nunca um negativo.
            cru, regra = adm.ERRO, "excecao ao correr a porta"
            motivo, evidencia = "%s: %s" % (type(erro).__name__, erro), {}
        balde = balde_de(cru)
        humano = x["LABEL"]
        if balde == PRED_POSITIVE:
            correto = "YES" if humano == "T3_SIM" else "NO"
        elif balde == PRED_NEGATIVE:
            correto = "YES" if humano == "T3_NAO" else "NO"
        elif balde == ERROR:
            correto = "ERROR"
        else:
            correto = "NOT_DECIDED"
        fora.append({
            "DOC_SHA256": x["DOC_SHA256"], "ITEM_ID": x["ITEM_ID"],
            "PUBLISHER": x["PUBLISHER"], "SOURCE_ID": x["SOURCE_ID"],
            "PUBLICATION_SERIES": x["PUBLICATION_SERIES"],
            "DOCUMENT_TYPE": x["DOCUMENT_TYPE"], "LANGUAGE": x["LANGUAGE"],
            "HUMAN_LABEL": humano,
            "RAW_OUTPUT": cru,
            "ADMISSION_RULE": regra,
            "ADMISSION_REASON": motivo,
            "ADMISSION_EVIDENCE": {k: v for k, v in evidencia.items()
                                   if k in ("palavras", "achado_noutro",
                                            "estagio", "origem")},
            "NORMALIZED_EVAL_BUCKET": balde,
            "CORRECT": correto,
        })
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 4 · A MATRIZ E AS METRICAS — com a formula a vista
# ══════════════════════════════════════════════════════════════════════════
def _div(a, b):
    """Denominador zero nao e zero: e NAO SEI."""
    return round(a / b, 4) if b else "NAO SEI"


def matriz(casos):
    tp = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == PRED_POSITIVE
             and c["HUMAN_LABEL"] == "T3_SIM")
    fp = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == PRED_POSITIVE
             and c["HUMAN_LABEL"] == "T3_NAO")
    tn = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == PRED_NEGATIVE
             and c["HUMAN_LABEL"] == "T3_NAO")
    fn = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == PRED_NEGATIVE
             and c["HUMAN_LABEL"] == "T3_SIM")
    ab = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == ABSTAIN)
    na = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == NOT_APPLICABLE)
    er = sum(1 for c in casos if c["NORMALIZED_EVAL_BUCKET"] == ERROR)
    total = len(casos)
    if tp + tn + fp + fn + ab + na + er != total:
        raise MedicaoInvalida("a matriz nao soma %d" % total)
    binarias = tp + tn + fp + fn
    certas = tp + tn
    prec = _div(tp, tp + fp)
    rec = _div(tp, tp + fn)
    f1 = ("NAO SEI" if "NAO SEI" in (prec, rec) or (prec + rec) == 0
          else round(2 * prec * rec / (prec + rec), 4))
    return {
        "TOTAL": total, "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "ABSTAIN": ab, "NOT_APPLICABLE": na, "ERROR": er,
        "BINARY_DECISIONS": binarias,
        "CORRECT_BINARY": certas, "WRONG_BINARY": fp + fn,
        "DECISION_COVERAGE": _div(binarias, total),
        "EFFECTIVE_ACCURACY": _div(certas, total),
        "CONDITIONAL_ACCURACY": _div(certas, binarias),
        "PRECISION_T3": prec, "RECALL_T3": rec,
        "SPECIFICITY": _div(tn, tn + fp), "F1_T3": f1,
        "AS_FORMULAS": {
            "DECISION_COVERAGE": "BINARY_DECISIONS / TOTAL",
            "EFFECTIVE_ACCURACY": "(TP+TN) / TOTAL",
            "CONDITIONAL_ACCURACY": "(TP+TN) / BINARY_DECISIONS",
            "PORQUE_AS_DUAS": (
                "Cobertura baixa com CONDITIONAL_ACCURACY alta parece bom e nao "
                "e: mede so os casos em que a porta se atreveu. As duas ficam "
                "lado a lado, sempre."),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# 5 · O PLANO DA OBSERVACAO INDEPENDENTE
# ══════════════════════════════════════════════════════════════════════════
# O agrupamento NAO se inventa aqui e NAO se deriva das previsoes. Vem dos
# pares quase-duplicados que o fecho do gabarito ja mediu e commitou.
#
#     REAGRUPAR DEPOIS DE VER O SCORE E ESCOLHER O GRUPO QUE DA JEITO.
def agrupamento_canonico(doc):
    pares = doc.get("NEAR_DUPLICATES", {}).get("PARES")
    if pares is None:
        return None
    pai = {x["DOC_SHA256"]: x["DOC_SHA256"] for x in doc["GROUND_TRUTH"]}

    def raiz(x):
        while pai[x] != x:
            x = pai[x]
        return x
    for p in pares:
        ra, rb = raiz(p["A"]), raiz(p["B"])
        if ra != rb:
            pai[ra] = rb
    return {s: raiz(s) for s in pai}


# A regra do score por grupo, fixada ANTES de olhar para qualquer resultado.
GROUP_PASS, GROUP_FAIL, GROUP_NOT_DECIDED = ("GROUP_PASS", "GROUP_FAIL",
                                             "GROUP_NOT_DECIDED")


def por_observacao(casos, grupos):
    """Um grupo passa so se TODOS os seus documentos acertarem, em binario.

    Sem voto de maioria, sem «a melhor edicao», sem «a ultima». Se uma edicao
    do mesmo boletim erra, o mecanismo nao resolveu aquele boletim.
    """
    por_grupo = defaultdict(list)
    for c in casos:
        por_grupo[grupos[c["DOC_SHA256"]]].append(c)

    linhas, mistos = [], []
    for g, membros in sorted(por_grupo.items()):
        rotulos = {m["HUMAN_LABEL"] for m in membros}
        if len(rotulos) > 1:
            # NAO se colapsa um grupo que o gabarito rotula dos dois jeitos.
            mistos.append({"GRUPO": g, "LABELS": sorted(rotulos),
                           "ITEM_IDS": sorted(m["ITEM_ID"] for m in membros)})
            continue
        baldes = [m["NORMALIZED_EVAL_BUCKET"] for m in membros]
        errou = any(m["CORRECT"] == "NO" for m in membros)
        indeciso = any(b not in BINARIOS for b in baldes)
        estado = (GROUP_FAIL if errou
                  else GROUP_NOT_DECIDED if indeciso else GROUP_PASS)
        linhas.append({
            "GRUPO": g, "TAMANHO": len(membros),
            "HUMAN_LABEL": rotulos.pop(),
            "ITEM_IDS": sorted(m["ITEM_ID"] for m in membros),
            "PREVISOES": sorted({m["RAW_OUTPUT"] for m in membros}),
            "ESTADO": estado,
        })
    multi = [l for l in linhas if l["TAMANHO"] > 1]
    return {
        "GROUP_TOTAL": len(linhas),
        "GROUP_POSITIVE": sum(1 for l in linhas if l["HUMAN_LABEL"] == "T3_SIM"),
        "GROUP_NEGATIVE": sum(1 for l in linhas if l["HUMAN_LABEL"] == "T3_NAO"),
        "GROUP_PASS": sum(1 for l in linhas if l["ESTADO"] == GROUP_PASS),
        "GROUP_FAIL": sum(1 for l in linhas if l["ESTADO"] == GROUP_FAIL),
        "GROUP_NOT_DECIDED": sum(1 for l in linhas
                                 if l["ESTADO"] == GROUP_NOT_DECIDED),
        "GROUP_EFFECTIVE_ACCURACY": _div(
            sum(1 for l in linhas if l["ESTADO"] == GROUP_PASS), len(linhas)),
        "MIXED_GROUND_TRUTH_GROUP": mistos,
        # Estabilidade: duas edicoes do mesmo boletim deviam ouvir o mesmo.
        "GRUPOS_COM_MAIS_DE_UM": len(multi),
        "SAME_GROUP_SAME_PREDICTION":
            sum(1 for l in multi if len(l["PREVISOES"]) == 1),
        "SAME_GROUP_MIXED_PREDICTIONS":
            sum(1 for l in multi if len(l["PREVISOES"]) > 1),
        "LINHAS": linhas,
    }


# ══════════════════════════════════════════════════════════════════════════
# 6 · O BUG DO SUBSTRING — medir se ainda existe, e NAO consertar
# ══════════════════════════════════════════════════════════════════════════
# `_do_universo` casa com `palavra in texto` — substring cru. O risco historico
# desta casa e `lancio` a acender dentro de `bilancio`.
#
#     MEDE-SE. NAO SE ESCREVE UM REGEX MELHOR NESTA MISSAO.
import re as _re  # noqa: E402  (so para a sonda; a porta nao usa regex)


def substring_falso(casos, gt_por_sha):
    """Casamentos em que a palavra so aparece DENTRO de outra palavra."""
    achados = []
    for universo, termos in adm.PERGUNTAS_DO_UNIVERSO.items():
        for termo in termos:
            t = termo.lower()
            for c in casos:
                texto = texto_do_corpo(
                    gt_por_sha[c["DOC_SHA256"]]["BODY_PATH"]).lower()
                if t not in texto:
                    continue
                # A palavra existe sozinha nalgum sitio? Se nunca, todo o
                # casamento dela neste documento e substring de outra palavra.
                if _re.search(r"(?<![a-zà-ÿ])%s(?![a-zà-ÿ])" % _re.escape(t),
                              texto):
                    continue
                m = _re.search(r"[a-zà-ÿ]*%s[a-zà-ÿ]*" % _re.escape(t), texto)
                achados.append({
                    "UNIVERSO": universo, "TERMO": termo,
                    "ITEM_ID": c["ITEM_ID"],
                    "DENTRO_DE": m.group(0) if m else "?",
                })
    return achados


def _so_substring(termo, texto):
    """A palavra aparece no texto, mas NUNCA sozinha."""
    t = termo.lower()
    if t not in texto:
        return False
    return not _re.search(r"(?<![a-zà-ÿ])%s(?![a-zà-ÿ])" % _re.escape(t), texto)


def decisoes_assentes_em_falso_casamento(casos, gt_por_sha):
    """Decisoes BINARIAS em que TODAS as palavras que as produziram sao
    substring de outra palavra.

    ⚠️ Isto nao e uma curiosidade lexical. Uma decisao inteiramente assente
    num casamento falso esta CERTA POR ACIDENTE quando bate com o humano — e
    contá-la como acerto do mecanismo seria dar-lhe credito por uma moeda ao
    ar.

        UM ACERTO QUE VEM DE UM CASAMENTO FALSO
        NAO E O MECANISMO A FUNCIONAR: E A SORTE A ALINHAR-SE.
    """
    fora = []
    for c in casos:
        if c["NORMALIZED_EVAL_BUCKET"] not in BINARIOS:
            continue
        ev = c["ADMISSION_EVIDENCE"]
        termos = list(ev.get("palavras") or [])
        for _u, ts in (ev.get("achado_noutro") or {}).items():
            termos.extend(ts)
        if not termos:
            continue
        texto = texto_do_corpo(gt_por_sha[c["DOC_SHA256"]]["BODY_PATH"]).lower()
        falsos = [t for t in termos if _so_substring(t, texto)]
        if len(falsos) == len(termos):
            fora.append({
                "ITEM_ID": c["ITEM_ID"], "DOC_SHA256": c["DOC_SHA256"],
                "HUMAN_LABEL": c["HUMAN_LABEL"], "RAW_OUTPUT": c["RAW_OUTPUT"],
                "CORRECT": c["CORRECT"], "TERMOS": termos,
            })
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 7 · AS SONDAS DE RED TEAM — mostram comportamento, nao mudam nada
# ══════════════════════════════════════════════════════════════════════════
def red_team(casos, obs, subs, gt_por_sha):
    def onde(f):
        return sorted(c["ITEM_ID"] for c in casos if f(c))

    por_publicador = defaultdict(set)
    for c in casos:
        por_publicador[c["PUBLISHER"]].add(c["HUMAN_LABEL"])
    dois_lados = sorted(p for p, l in por_publicador.items() if len(l) > 1)

    tem_fitosanitario = [c for c in casos
                         if "fitosanitario" in texto_do_corpo(
                             gt_por_sha[c["DOC_SHA256"]]["BODY_PATH"]).lower()]
    bilancio = [c for c in casos
                if "bilancio fitosanitario" in texto_do_corpo(
                    gt_por_sha[c["DOC_SHA256"]]["BODY_PATH"]).lower()]
    estados = Counter(c["RAW_OUTPUT"] for c in casos)

    return [
        {"SONDA": "1 · mesmo publicador com universos diferentes",
         "MEDIDO": "%d publicadores com SIM e NAO: %s"
                   % (len(dois_lados), dois_lados)},
        {"SONDA": "2 · ARPAV com meteorologia e fitossanidade",
         "MEDIDO": "ARPAV: %s" % sorted(
             {"%s->%s" % (c["HUMAN_LABEL"], c["RAW_OUTPUT"])
              for c in casos if c["PUBLISHER"] == "ARPAV"})},
        {"SONDA": "3 · documento T3 com muito vocabulario climatico",
         "MEDIDO": "positivos humanos que a porta nao chamou SIM: %s"
                   % onde(lambda c: c["HUMAN_LABEL"] == "T3_SIM"
                          and c["RAW_OUTPUT"] != adm.SIM)},
        {"SONDA": "4 · documento NAO que contem «fitosanitario»",
         "MEDIDO": "%d documentos contem a palavra; destes, humanos NAO: %s"
                   % (len(tem_fitosanitario),
                      sorted(c["ITEM_ID"] for c in tem_fitosanitario
                             if c["HUMAN_LABEL"] == "T3_NAO"))},
        {"SONDA": "5 · «Bilancio Fitosanitario»",
         "MEDIDO": "%s" % sorted("%s: humano %s, porta %s"
                                 % (c["ITEM_ID"], c["HUMAN_LABEL"],
                                    c["RAW_OUTPUT"]) for c in bilancio)},
        {"SONDA": "6 · registo administrativo de produtos fitossanitarios",
         "MEDIDO": "%s" % sorted(
             "%s: humano %s, porta %s" % (c["ITEM_ID"], c["HUMAN_LABEL"],
                                          c["RAW_OUTPUT"])
             for c in casos if c["DOCUMENT_TYPE"] == "CSV"
             or c["ITEM_ID"].endswith(".csv"))},
        {"SONDA": "7 · varias edicoes da mesma serie",
         "MEDIDO": "%d grupos com mais de um documento · mesma previsao %d · "
                   "previsoes mistas %d"
                   % (obs["GRUPOS_COM_MAIS_DE_UM"],
                      obs["SAME_GROUP_SAME_PREDICTION"],
                      obs["SAME_GROUP_MIXED_PREDICTIONS"])},
        {"SONDA": "8 · SOURCE_ID = NAO SEI",
         "MEDIDO": "%d sem fonte resolvida; saidas: %s"
                   % (sum(1 for c in casos if c["SOURCE_ID"] == "NAO SEI"),
                      dict(Counter(c["RAW_OUTPUT"] for c in casos
                                   if c["SOURCE_ID"] == "NAO SEI")))},
        {"SONDA": "9 · idioma nao resolvido ou ingles",
         "MEDIDO": "%s" % sorted(
             "%s (%s): humano %s, porta %s"
             % (c["ITEM_ID"], c["LANGUAGE"], c["HUMAN_LABEL"], c["RAW_OUTPUT"])
             for c in casos if not str(c["LANGUAGE"]).startswith("it"))[:6]},
        {"SONDA": "10 · os estados da porta continuam separados",
         "MEDIDO": "estados vistos: %s · vocabulario do runtime: %s"
                   % (dict(estados), estados_do_runtime())},
        {"SONDA": "11 · substring dentro de outra palavra",
         "MEDIDO": "%d casamentos so-substring%s"
                   % (len(subs),
                      "" if not subs else ": %s" % subs[:4])},
    ]


# ══════════════════════════════════════════════════════════════════════════
# 8 · O ARTEFATO E O RELATORIO
# ══════════════════════════════════════════════════════════════════════════
def _head():
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=RAIZ, text=True).strip()
    except Exception:                                   # noqa: BLE001
        return "NAO SEI"


# ══════════════════════════════════════════════════════════════════════════
# 8 · A AUDITORIA DE VAZAMENTO — o mecanismo viu o gabarito ao ser desenhado?
# ══════════════════════════════════════════════════════════════════════════
# Um mecanismo ajustado a olhar para o gabarito nao e avaliado por ele. Aqui a
# independencia nao se afirma: prova-se com datas do Git, e se nao der para
# provar escreve-se NAO SEI.
#
#     UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE.
def _git(*args):
    import subprocess
    try:
        return subprocess.check_output(["git"] + list(args), cwd=RAIZ,
                                       text=True).strip()
    except Exception:                                   # noqa: BLE001
        return ""


def auditoria_de_vazamento(doc):
    nasceu = _git("log", "-1", "--format=%ad", "--date=short", "-S",
                  "PERGUNTAS_DO_UNIVERSO = {", "--", OWNER_FILE)
    mexido = _git("log", "-1", "--format=%ad", "--date=short", "--",
                  OWNER_FILE)
    gabarito = _git("log", "-1", "--format=%ad", "--date=short", "--", GABARITO)
    revisao = doc.get("GENERATED_AT", "")[:10]
    sabe = all([nasceu, mexido, gabarito])
    antes = sabe and mexido < gabarito and mexido < (revisao or gabarito)
    return {
        "GROUND_TRUTH_AUTHORITY": doc["LABEL_AUTHORITY"],
        "MECANISMO_NASCEU_EM": nasceu or "NAO SEI",
        "MECANISMO_MEXIDO_PELA_ULTIMA_VEZ_EM": mexido or "NAO SEI",
        "REVISAO_HUMANA_FECHOU_EM": revisao or "NAO SEI",
        "GABARITO_COMMITADO_EM": gabarito or "NAO SEI",
        "CURRENT_ADMISSION_NEVER_SAW_GROUND_TRUTH_DURING_ITS_DESIGN":
            ("YES" if antes else "NAO SEI"),
        "PROVA": ("o ficheiro do mecanismo nao e tocado desde %s, e o gabarito "
                  "so existe desde %s — nenhuma palavra pode ter sido escolhida "
                  "a olhar para rotulos que ainda nao existiam"
                  % (mexido, gabarito)) if antes else
                 "nao foi possivel datar as duas coisas pelo Git",
    }


def impressao_digital(artefato):
    """Identifica ESTA medicao. A baseline e a PRIMEIRA execucao valida.

    Se alguem mexer na porta e correr outra vez, a impressao muda — e a
    baseline continua a ser esta, nao a nova.
    """
    material = json.dumps({
        "ADMISSAO_SHA256": sha256_do_ficheiro(OWNER_FILE),
        "RULE_VERSION": artefato["ADMISSION_RULE_VERSION"],
        "GROUND_TRUTH_SHA256": artefato["GROUND_TRUTH"]["SHA256"],
        "PREVISOES": sorted((c["ITEM_ID"], c["RAW_OUTPUT"])
                            for c in artefato["CASES"]),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def medir_tudo():
    cadeia = provar_cadeia()
    doc, gt = carregar_gabarito()
    gt_por_sha = {x["DOC_SHA256"]: x for x in gt}
    grupos = agrupamento_canonico(doc)

    planos = {}
    for plano in (CONTRATO, LINHAGEM):
        casos = medir(gt, plano)
        obs = (por_observacao(casos, grupos) if grupos
               else {"GROUPED_BASELINE": "NOT_RUN"})
        planos[plano] = {"DOCUMENT_PLANE": matriz(casos),
                         "OBSERVATION_PLANE": obs, "CASES": casos}

    base = planos[PLANO_DA_BASELINE_TEMATICA]
    subs = substring_falso(base["CASES"], gt_por_sha)
    acidente = decisoes_assentes_em_falso_casamento(base["CASES"], gt_por_sha)
    rt = red_team(base["CASES"], base["OBSERVATION_PLANE"], subs, gt_por_sha)
    rt.append({
        "SONDA": "12 · decisoes que assentam SO num casamento falso",
        "MEDIDO": "%d de %d decisoes binarias · %s"
                  % (len(acidente), base["DOCUMENT_PLANE"]["BINARY_DECISIONS"],
                     [(x["ITEM_ID"], x["RAW_OUTPUT"], x["CORRECT"],
                       x["TERMOS"]) for x in acidente])})

    artefato = {
        "SCHEMA": "sintonia.baseline-admission-t3/1",
        "O_QUE_ISTO_E": (
            "Uma BASELINE: o mecanismo tematico de hoje, medido contra o "
            "primeiro gabarito humano de T3. Nao corrige nada, nao propoe "
            "substituto e nao aprova nem reprova o mecanismo."),
        "MEASURE_NOT_FIX": True,
        "SOURCE_HEAD": _head(),
        "UNIVERSE": UNIVERSO,

        "ADMISSION_OWNER_FILE": OWNER_FILE,
        "ADMISSION_OWNER_FUNCTION": OWNER_FUNCTION,
        "T3_RULE_LOCATION": T3_RULE_LOCATION,
        "ADMISSION_CALL_CHAIN": cadeia,
        "THEMATIC_DECISION_OWNERS": 1,
        "PRODUCTION_MECHANISM_CALLABLE": "YES",
        "COPIED_KEYWORD_IMPLEMENTATION": "NO",
        "THIN_ADAPTER_HAS_SEMANTIC_LOGIC": "NO",
        "ADMISSION_RULE_VERSION": adm.VERSAO_DA_REGRA,
        "RUNTIME_OUTPUT_STATES": estados_do_runtime(),
        "EVAL_BUCKET_MAP": {k: v for k, v in BALDE.items()},

        "GROUND_TRUTH": {
            "PATH": GABARITO,
            "SHA256": sha256_do_ficheiro(GABARITO),
            "AUTHORITY": doc["LABEL_AUTHORITY"],
            "DOCUMENTS": len(gt),
            "POSITIVE": sum(1 for x in gt if x["LABEL"] == "T3_SIM"),
            "NEGATIVE": sum(1 for x in gt if x["LABEL"] == "T3_NAO"),
            "EXCLUIDOS_NAO_ENTRAM_NO_SCORE": len(
                doc.get("EXCLUDED_FROM_EVALUATION", [])),
            "EVALUATION_SCOPE": doc["EVALUATION_SCOPE"],
        },

        "OS_DOIS_PLANOS_DE_ENTRADA": {
            "BASELINE_TEMATICA": PLANO_DA_BASELINE_TEMATICA,
            "PORQUE": (
                "CONTRATO e o que a producao ve hoje: o registo de artefatos "
                "diz SOURCE_ID = «NAO SEI» e a porta para na prontidao, antes "
                "do tema. LINHAGEM acrescenta so o SOURCE_ID que o gabarito ja "
                "declara, e e o unico plano que exercita a regra tematica. A "
                "escolha de qual e a baseline foi fixada ANTES de correr."),
            "CONTRATO": {k: v for k, v in planos[CONTRATO].items()
                         if k != "CASES"},
            "LINHAGEM": {k: v for k, v in planos[LINHAGEM].items()
                         if k != "CASES"},
        },

        "DOCUMENT_PLANE": base["DOCUMENT_PLANE"],
        "OBSERVATION_PLANE": {k: v for k, v in
                              base["OBSERVATION_PLANE"].items() if k != "LINHAS"},
        "GROUPING_SOURCE": (
            "%s :: NEAR_DUPLICATES.PARES (medido no fecho do gabarito, antes "
            "desta missao)" % GABARITO if grupos else "NOT_RUN"),
        "CANONICAL_OBSERVATION_GROUPING_FOUND": "YES" if grupos else "NO",
        "GROUPS": base["OBSERVATION_PLANE"].get("LINHAS", []),

        "DECISIONS_RESTING_ONLY_ON_FALSE_MATCH": acidente,
        "CORRECT_BY_ACCIDENT": sum(1 for x in acidente if x["CORRECT"] == "YES"),
        "SUBSTRING_FALSE_MATCH_STILL_EXISTS": "YES" if subs else "NO",
        "SUBSTRING_FALSE_MATCHES": subs,
        "RED_TEAM": rt,

        "PERFORMANCE_GATE_PREDEFINED": "NO",
        "PERFORMANCE_GATE_PROCURADO_EM": [
            "BIBLIA-CANONICA-DA-COLETA.md", "README.md", "AGENTS.md",
            "docs/operacao/CENSO-CORPUS-ROTULADO-ADMISSION-V1.md"],
        "CURRENT_MECHANISM_ACCEPTABLE": "NOT_DECIDED",
        "PORQUE_NOT_DECIDED": (
            "Nao existe limiar canonico de aprovacao para um mecanismo de "
            "classificacao nesta arvore. Sem gate previo, medir nao aprova nem "
            "reprova — e inventar o gate agora seria desenhar o alvo a volta "
            "da flecha."),

        "CLASSIFIER_BUILT": "NO", "ADMISSION_CHANGED": "NO",
        "KEYWORDS_CHANGED": "NO", "REPLACEMENT_PROPOSED": "NO",
        "CASES": base["CASES"],
        "CASES_CONTRATO": planos[CONTRATO]["CASES"],
    }
    artefato["LEAKAGE_AUDIT"] = auditoria_de_vazamento(doc)
    artefato["FIRST_VALID_BASELINE_FINGERPRINT"] = impressao_digital(artefato)
    return artefato


def main():
    a = medir_tudo()
    d, o = a["DOCUMENT_PLANE"], a["OBSERVATION_PLANE"]
    cont = a["OS_DOIS_PLANOS_DE_ENTRADA"]["CONTRATO"]["DOCUMENT_PLANE"]

    print("BASELINE DA ADMISSION DE HOJE CONTRA O GABARITO HUMANO DE T3")
    print("=" * 74)
    print("  O DONO REAL, PROVADO ELO A ELO")
    for e in a["ADMISSION_CALL_CHAIN"]:
        print(f"    {e['FILE']}:{e['LINE']}")
        print(f"      {e['PORQUE']}")
    print(f"    THEMATIC_DECISION_OWNERS   {a['THEMATIC_DECISION_OWNERS']}")
    print(f"    PRODUCTION_MECHANISM_CALLABLE  {a['PRODUCTION_MECHANISM_CALLABLE']}")
    print(f"    ADMISSION_RULE_VERSION     {a['ADMISSION_RULE_VERSION']}")
    print(f"    RUNTIME_OUTPUT_STATES      {a['RUNTIME_OUTPUT_STATES']}")

    g = a["GROUND_TRUTH"]
    print("\n  O GABARITO")
    print(f"    SHA256      {g['SHA256']}")
    print(f"    DOCUMENTS   {g['DOCUMENTS']}  ·  SIM {g['POSITIVE']}  ·  "
          f"NAO {g['NEGATIVE']}")
    print(f"    os {g['EXCLUIDOS_NAO_ENTRAM_NO_SCORE']} excluidos NAO entram "
          f"no score")

    print("\n  PLANO CONTRATO — o que a producao ve hoje")
    print(f"    TP {cont['TP']} · TN {cont['TN']} · FP {cont['FP']} · "
          f"FN {cont['FN']} · ABSTAIN {cont['ABSTAIN']} · "
          f"NOT_APPLICABLE {cont['NOT_APPLICABLE']} · ERROR {cont['ERROR']}")
    print(f"    DECISION_COVERAGE  {cont['DECISION_COVERAGE']}")

    print("\n  PLANO LINHAGEM — A BASELINE TEMATICA")
    print(f"    TP {d['TP']} · TN {d['TN']} · FP {d['FP']} · FN {d['FN']}")
    print(f"    ABSTAIN {d['ABSTAIN']} · NOT_APPLICABLE {d['NOT_APPLICABLE']} "
          f"· ERROR {d['ERROR']}")
    print(f"    soma  {d['TP'] + d['TN'] + d['FP'] + d['FN'] + d['ABSTAIN'] + d['NOT_APPLICABLE'] + d['ERROR']}"
          f"/{d['TOTAL']}")
    print(f"    BINARY_DECISIONS      {d['BINARY_DECISIONS']}")
    print(f"    DECISION_COVERAGE     {d['DECISION_COVERAGE']}")
    print(f"    EFFECTIVE_ACCURACY    {d['EFFECTIVE_ACCURACY']}")
    print(f"    CONDITIONAL_ACCURACY  {d['CONDITIONAL_ACCURACY']}")
    print(f"    PRECISION_T3 {d['PRECISION_T3']} · RECALL_T3 {d['RECALL_T3']} "
          f"· SPECIFICITY {d['SPECIFICITY']} · F1_T3 {d['F1_T3']}")

    print("\n  PLANO DA OBSERVACAO INDEPENDENTE")
    print(f"    GROUPING_SOURCE  {a['GROUPING_SOURCE']}")
    print(f"    GROUP_TOTAL {o['GROUP_TOTAL']} · POSITIVE {o['GROUP_POSITIVE']}"
          f" · NEGATIVE {o['GROUP_NEGATIVE']}")
    print(f"    GROUP_PASS {o['GROUP_PASS']} · GROUP_FAIL {o['GROUP_FAIL']} · "
          f"GROUP_NOT_DECIDED {o['GROUP_NOT_DECIDED']}")
    print(f"    GROUP_EFFECTIVE_ACCURACY  {o['GROUP_EFFECTIVE_ACCURACY']}")
    print(f"    SAME_GROUP_SAME_PREDICTION   {o['SAME_GROUP_SAME_PREDICTION']}")
    print(f"    SAME_GROUP_MIXED_PREDICTIONS {o['SAME_GROUP_MIXED_PREDICTIONS']}")
    print(f"    MIXED_GROUND_TRUTH_GROUP     {len(o['MIXED_GROUND_TRUTH_GROUP'])}")

    print("\n  OS ERROS, UM A UM")
    for c in a["CASES"]:
        if c["CORRECT"] in ("YES",):
            continue
        print(f"    {c['NORMALIZED_EVAL_BUCKET']:<16}{c['ITEM_ID'][:38]:<40}"
              f"{c['PUBLISHER'][:22]:<24}humano {c['HUMAN_LABEL']:<8}"
              f"porta {c['RAW_OUTPUT']}")

    print("\n  QUEBRAS POR GRUPO")
    for campo in ("PUBLISHER", "DOCUMENT_TYPE", "LANGUAGE"):
        conhecidos = [c for c in a["CASES"] if c[campo] != "NAO SEI"]
        print(f"    {campo}  KNOWN {len(conhecidos)} · UNKNOWN "
              f"{len(a['CASES']) - len(conhecidos)}")
        certos = Counter()
        total = Counter()
        for c in conhecidos:
            total[c[campo]] += 1
            if c["CORRECT"] == "YES":
                certos[c[campo]] += 1
        for k in sorted(total):
            print(f"      {str(k)[:38]:<40}{certos[k]}/{total[k]}")

    print("\n  O RED TEAM — mostra comportamento, nao muda nada")
    for r in a["RED_TEAM"]:
        print(f"    {r['SONDA']}")
        print(f"      {r['MEDIDO']}")
    print(f"\n  SUBSTRING_FALSE_MATCH_STILL_EXISTS = "
          f"{a['SUBSTRING_FALSE_MATCH_STILL_EXISTS']}")
    print(f"  decisoes binarias assentes SO num casamento falso: "
          f"{len(a['DECISIONS_RESTING_ONLY_ON_FALSE_MATCH'])} de "
          f"{d['BINARY_DECISIONS']}")
    print(f"  destas, contadas como ACERTO: {a['CORRECT_BY_ACCIDENT']}")
    for x in a["DECISIONS_RESTING_ONLY_ON_FALSE_MATCH"]:
        print(f"    {x['ITEM_ID'][:40]:<42}humano {x['HUMAN_LABEL']:<8}"
              f"porta {x['RAW_OUTPUT']:<8}{x['TERMOS']}")

    la = a["LEAKAGE_AUDIT"]
    print("\n  AUDITORIA DE VAZAMENTO")
    print(f"    GROUND_TRUTH_AUTHORITY   {la['GROUND_TRUTH_AUTHORITY']}")
    print(f"    mecanismo nasceu em      {la['MECANISMO_NASCEU_EM']}")
    print(f"    mecanismo mexido em      "
          f"{la['MECANISMO_MEXIDO_PELA_ULTIMA_VEZ_EM']}")
    print(f"    gabarito commitado em    {la['GABARITO_COMMITADO_EM']}")
    print(f"    CURRENT_ADMISSION_NEVER_SAW_GROUND_TRUTH_DURING_ITS_DESIGN = "
          f"{la['CURRENT_ADMISSION_NEVER_SAW_GROUND_TRUTH_DURING_ITS_DESIGN']}")
    print(f"\n  FIRST_VALID_BASELINE_FINGERPRINT")
    print(f"    {a['FIRST_VALID_BASELINE_FINGERPRINT']}")

    print(f"\n  PERFORMANCE_GATE_PREDEFINED    {a['PERFORMANCE_GATE_PREDEFINED']}")
    print(f"  CURRENT_MECHANISM_ACCEPTABLE   {a['CURRENT_MECHANISM_ACCEPTABLE']}")
    print(f"  CLASSIFIER_BUILT NO · ADMISSION_CHANGED NO · KEYWORDS_CHANGED NO")

    if "--escrever" in sys.argv:
        alvo = os.path.join(RAIZ, SAIDA)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            json.dump(a, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\n  escrito: {SAIDA}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
