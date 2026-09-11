#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O GATE DE ACEITACAO DE UM MECANISMO TEMATICO — escrito ANTES dos candidatos.

    python3 provas/gate_de_aceitacao_tematica.py
    python3 provas/gate_de_aceitacao_tematica.py --escrever

Esta missao DEFINE o gate. Nao testa substituto, nao toca na Admission, nao
constroi classificador.

    GATE_VERSION = V1
    THIS_IS = THEMATIC_MECHANISM_EVALUATION_GATE_V1
    NAO E:   FULL_EAME_PRODUCTION_RELEASE_GATE

POR QUE ISTO EXISTE
-------------------
A baseline de T3 mediu o mecanismo de hoje e nao pode dizer se ele presta —
porque nao havia criterio escrito. Sem gate previo, qualquer numero se defende:

    SEM ALVO DESENHADO ANTES,
    A FLECHA ATERRA SEMPRE NO CENTRO DE ALGUMA COISA.

E o contrario tambem e proibido: escolher os numeros para o mecanismo de hoje
passar — ou para ele falhar — seria a mesma fraude com o sinal trocado.

    OS LIMIARES ABAIXO NASCEM DO CUSTO OPERACIONAL,
    NAO DO RESULTADO QUE JA CONHECEMOS.

O QUE O ESTUDO EXTERNO DEVOLVEU
-------------------------------
Quatro sistemas maduros foram lidos nas fontes oficiais — Google Cloud
Document AI, Azure AI Document Intelligence, scikit-learn e o NIST AI RMF.

    THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD = NO

Nenhum prescreve um numero universal. Todos dizem a mesma coisa por palavras
diferentes: o limiar sai da FUNCAO DE CUSTO de quem opera, e nao da estatistica.
Por isso o numero tem de ser escolhido aqui — e justificado aqui.

    PADRAO EXTERNO NAO REVOGA LEI CANONICA.
    E TAMBEM NAO DISPENSA A CASA DE ESCOLHER O PROPRIO CUSTO.
"""
import json
import os
import sys
from fractions import Fraction

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

BASELINE = "data/derivados/BASELINE-ADMISSION-T3-V1.json"
GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"
SAIDA = "data/derivados/GATE-ACEITACAO-TEMATICA-V1.json"

GATE_OWNER = "provas/gate_de_aceitacao_tematica.py"
GATE_VERSION = "V1"


# ══════════════════════════════════════════════════════════════════════════
# 1 · A ASSIMETRIA DO ERRO — a decisao operacional de onde tudo vem
# ══════════════════════════════════════════════════════════════════════════
#     FALSE_NEGATIVE_COST > FALSE_POSITIVE_COST
#
# Um FALSO POSITIVO deixa entrar material a mais num universo. A Inteligencia
# ainda o ve e ainda o pode descartar: o erro fica VISIVEL e reparavel.
#
# Um FALSO NEGATIVO manda embora material que pertencia ao universo. Ninguem
# olha para ele outra vez, e nao ha como saber o que se perdeu — porque o que
# se perdeu nao deixou rasto nenhum do lado de la.
#
#     UM FALSO POSITIVO CUSTA TRABALHO.
#     UM FALSO NEGATIVO CUSTA CONHECIMENTO, E EM SILENCIO.
#
# Daqui sai a ordem de dureza dos limiares:
#
#     falso negativo explicito   ZERO tolerancia
#     captura de positivos       quase total
#     precisao                   exigente, mas nao absoluta
#
# E daqui sai tambem por que ABSTER-SE e melhor do que errar um NAO: uma
# abstencao e uma confissao que alguem pode ir ver. Um NAO errado fecha o
# assunto com ar de decisao tomada.
#
#     ABSTAIN > NEGATIVO ERRADO
#
# Mas abster-se sempre tambem falha: um mecanismo que nunca decide nao e
# cauteloso, e inutil. Por isso ha limiar de COBERTURA.
ASSIMETRIA = {
    "FALSE_NEGATIVE_COST_VS_FALSE_POSITIVE_COST": "GREATER",
    "PORQUE_FP": ("material a mais chega ao universo; a Inteligencia ainda "
                  "julga, e o erro fica visivel"),
    "PORQUE_FN": ("material que pertencia ao universo pode nao chegar la, e "
                  "ninguem volta a olhar — o erro e invisivel"),
    "ABSTAIN_VS_NEGATIVO_ERRADO": "ABSTAIN e preferivel",
    "MAS": ("abstencao excessiva tambem reprova: um mecanismo que nunca "
            "decide nao e cauteloso, e inutil"),
}


# ══════════════════════════════════════════════════════════════════════════
# 2 · A UNIDADE PRIMARIA — observacao, nao ficheiro
# ══════════════════════════════════════════════════════════════════════════
#     DOCUMENT != INDEPENDENT_OBSERVATION
#
# Quatro edicoes seguidas do mesmo boletim regional sao quatro ficheiros e uma
# observacao. Pontuar por ficheiro daria ao mecanismo quatro creditos por
# resolver um documento — e tiraria quatro por falhar o mesmo.
#
# O plano de 36 documentos continua OBRIGATORIO como diagnostico. O PASS/FAIL
# usa as 31 observacoes.
UNIDADE_PRIMARIA = "INDEPENDENT_OBSERVATION"
UNIDADE_DIAGNOSTICA = "DOCUMENT"


# ══════════════════════════════════════════════════════════════════════════
# 3 · OS LIMIARES — e a conta de custo que produz cada um
# ══════════════════════════════════════════════════════════════════════════
# Cada limiar tem a razao ao lado. Um numero sem razao e um numero que a
# proxima missao muda sem perceber que mudou.
LIMIARES = {
    "POSITIVE_CAPTURE_MINIMUM": {
        "VALOR": Fraction(10, 11),
        "COMO_SE_LE": "10 de 11 observacoes positivas capturadas",
        "PORQUE": (
            "O positivo perdido e o erro caro e invisivel. Tolera-se UM — "
            "porque exigir 11/11 num conjunto de 11 transforma qualquer caso "
            "de fronteira em reprovacao automatica, e um gate que so passa "
            "com perfeicao nao separa mecanismos: rejeita todos. UM e o "
            "maximo que ainda deixa o gate discriminar."),
        "ABSTENCAO_CONTA": "NAO — abster-se num positivo nao e captura-lo",
    },
    "EXPLICIT_FALSE_NEGATIVE_MAX": {
        "VALOR": 0,
        "COMO_SE_LE": "nenhum NAO explicito sobre observacao positiva",
        "PORQUE": (
            "Afirmar «isto nao e T3» sobre algo que E T3 e a unica saida que "
            "fecha o assunto com ar de decisao. Ninguem reabre. E diferente de "
            "abster-se, e por isso tem limiar proprio e zero."),
        "ABSTENCAO_CONTA": "NAO — abstencao nao e falso negativo explicito",
    },
    "SPECIFICITY_MINIMUM": {
        "VALOR": Fraction(18, 20),
        "COMO_SE_LE": "18 de 20 observacoes negativas resolvidas certas",
        "PORQUE": (
            "O negativo errado custa menos, mas custa: cada um inunda a "
            "Inteligencia com material que ela tera de descartar a mao. Dois "
            "em vinte e o que a operacao absorve sem a fila deixar de ser "
            "util."),
        "ABSTENCAO_CONTA": "NAO — abstencao nao e negativo resolvido",
    },
    "PRECISION_T3_MINIMUM": {
        "VALOR": Fraction(4, 5),
        "COMO_SE_LE": "4 em cada 5 «isto e T3» estao certos",
        "PORQUE": (
            "Quando o mecanismo AFIRMA, quem recebe tem de poder confiar. "
            "Abaixo de 4/5, um em cada quatro itens da fila e ruido e a fila "
            "deixa de ser lida — e uma fila que ninguem le e pior do que fila "
            "nenhuma, porque parece que o trabalho esta a ser feito."),
    },
    "DECISION_COVERAGE_MINIMUM": {
        "VALOR": Fraction(28, 31),
        "COMO_SE_LE": "no maximo 3 observacoes sem decisao binaria",
        "PORQUE": (
            "ABSTAIN e melhor do que errar, e por isso e permitido. Mas um "
            "mecanismo que se abstem em muitos casos empurra o trabalho todo "
            "para a pessoa e nao substitui nada. Tres em trinta e uma e a fila "
            "de revisao que uma pessoa despacha sem a fila crescer."),
    },
    "GROUP_PASS_MINIMUM": {
        "VALOR": Fraction(28, 31),
        "COMO_SE_LE": "28 de 31 observacoes resolvidas e certas",
        "PORQUE": (
            "O resultado efetivo, e nao o condicional. Acuracia condicional "
            "alta com cobertura baixa mede so os casos em que o mecanismo se "
            "atreveu — e e exactamente assim que um mecanismo fraco parece "
            "forte."),
        "NAO_SE_USA": "CONDITIONAL_ACCURACY para aprovar",
    },
    "ERROR_MAX": {
        "VALOR": 0,
        "COMO_SE_LE": "nenhuma falha de execucao",
        "PORQUE": (
            "ERRO nao e rejeicao e nao e duvida: e «ninguem chegou a olhar». "
            "Um mecanismo que rebenta sobre o corpus de avaliacao nao foi "
            "avaliado nesses casos, e contar isso como qualquer outra coisa "
            "seria inventar uma medicao que nao houve."),
        "NUNCA_VIRA": ["NAO", "ABSTAIN", "UNKNOWN"],
    },
    "KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY_MAX": {
        "VALOR": 0,
        "COMO_SE_LE": ("nenhum resultado depende de um casamento que a propria "
                       "regra nao pretendia representar"),
        "PORQUE": (
            "A baseline mostrou `lancio` a acender dentro de `bilancio` e a "
            "PRODUZIR uma das negativas «certas». Um acerto desses nao e o "
            "mecanismo a funcionar: e a sorte a alinhar-se, e ela desalinha-se "
            "no proximo corpus.\n"
            "ISTO NAO PROIBE substring matching. Proibe que um RESULTADO "
            "dependa de um casamento nao pretendido."),
    },
}

# O gate de alcance: quando a procedencia ja esta comprovada, o item TEM de
# chegar a pergunta tematica. Nao chegar nao e um erro do tema — e a linhagem
# a nao atravessar.
#
# ⚠️ ISTO NAO AUTORIZA FABRICAR `SOURCE_ID`. Avalia-se so o conjunto cuja
# origem JA esta comprovada. Origem legitimamente desconhecida fica de fora do
# denominador; inventa-la para o gate passar seria mentir com a palavra certa.
REACHABILITY_REQUIRED = Fraction(1, 1)
REACHABILITY_DENOMINADOR_T3 = 36

# Os hard gates. NENHUMA media compensa a falha de um.
#
#     PRECISAO EXCELENTE NAO COMPENSA CAPTURA POSITIVA RUIM.
#     UM GATE QUE SE COMPENSA E UMA MEDIA COM NOME DE REGRA.
CONDICOES = (
    ("POSITIVE_CAPTURE_RATE", ">=", "POSITIVE_CAPTURE_MINIMUM"),
    ("EXPLICIT_FALSE_NEGATIVE", "<=", "EXPLICIT_FALSE_NEGATIVE_MAX"),
    ("SPECIFICITY", ">=", "SPECIFICITY_MINIMUM"),
    ("PRECISION_T3", ">=", "PRECISION_T3_MINIMUM"),
    ("DECISION_COVERAGE", ">=", "DECISION_COVERAGE_MINIMUM"),
    ("GROUP_PASS_RATE", ">=", "GROUP_PASS_MINIMUM"),
    ("ERROR", "<=", "ERROR_MAX"),
    ("FALSE_SUBSTRING_OUTCOME_DEPENDENCY", "<=",
     "KNOWN_FALSE_SUBSTRING_OUTCOME_DEPENDENCY_MAX"),
)

ESCOPO = "ITALIAN_AGRO_INSTITUTIONAL_CORPUS"
NAO_AUTORIZA = ("FRANCE", "SPAIN", "EAME")
T3_GROUND_TRUTH_ROLE = "EVALUATION"


# ══════════════════════════════════════════════════════════════════════════
# 4 · O ESTUDO EXTERNO — e onde ele concorda MENOS do que parece
# ══════════════════════════════════════════════════════════════════════════
# Quatro sistemas maduros lidos nas fontes oficiais. Registar so a concordancia
# seria fabricar consenso: onde uma fonte se cala ou discorda, fica escrito.
#
#     CONVERGENCIA FABRICADA E PIOR DO QUE DISCORDANCIA REGISTADA.
ESTUDO_EXTERNO = {
    "THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD": "NO",
    "SISTEMAS": [
        {
            "NOME": "Google Cloud Document AI",
            "PRESCREVE_LIMIAR_UNIVERSAL": "NO",
            "O_QUE_DIZ": (
                "calcula o limiar que maximiza F1 e entrega a escolha ao "
                "utilizador («You are free to choose your own confidence "
                "threshold»). RECUSA publicar «accuracy»: «less meaningful»."),
            "FONTES": ["https://docs.cloud.google.com/document-ai/docs/evaluate",
                       "https://docs.cloud.google.com/document-ai/docs/custom-classifier"],
        },
        {
            "NOME": "Microsoft Azure AI Document Intelligence",
            "PRESCREVE_LIMIAR_UNIVERSAL": "NO",
            "O_QUE_DIZ": (
                "«To set the threshold for your application, use the "
                "confidence score from the response». Tres cenarios com custos "
                "diferentes produzem limiares diferentes."),
            "FONTES": ["https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-classifier",
                       "https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/document-intelligence/transparency-note"],
        },
        {
            "NOME": "scikit-learn",
            "PRESCREVE_LIMIAR_UNIVERSAL": "NO",
            "O_QUE_DIZ": (
                "sobre o 0.5 por omissao: «most certainly not ideal for most "
                "use cases». O limiar sai de «a utility metric defined by the "
                "business», com matriz de custo explicita."),
            "FONTES": ["https://scikit-learn.org/stable/modules/classification_threshold.html",
                       "https://scikit-learn.org/stable/auto_examples/model_selection/plot_cost_sensitive_learning.html"],
        },
        {
            "NOME": "NIST AI Risk Management Framework 1.0",
            "PRESCREVE_LIMIAR_UNIVERSAL": "NO",
            "O_QUE_DIZ": (
                "«it does not prescribe risk tolerance … highly contextual and "
                "application and use-case specific». E: «Human judgment should "
                "be employed when deciding … the precise threshold values»."),
            "FONTES": ["https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"],
        },
    ],
    "CONVERGENCIA": {
        "a · o compromisso precisao/recall exige uma escolha": "4 de 4",
        "b · o limiar sai da funcao de custo": (
            "3 de 4 — a Google CALA-SE sobre assimetria de custo, e o seu "
            "default de maximizar F1 assume que FP e FN custam o mesmo"),
        "c · confianca pode encaminhar para abstencao/revisao humana": (
            "3 de 4 — a Google nao: o produto Human-in-the-Loop esta "
            "descontinuado e a doc atual nao descreve encaminhamento"),
        "d · avaliar com gabarito separado do que ajustou o modelo": "4 de 4",
        "e · criterio de implantacao reflete o contexto real e o risco": (
            "3 de 4 — a doc da Google e um manual de MEDICAO, nao de DECISAO "
            "de implantacao"),
    },
    "ONDE_A_CONVERGENCIA_E_MAIS_FRACA_DO_QUE_PARECE": [
        ("A Azure e a UNICA fonte que nomeia um numero («target 80% or "
         "higher») — e nomeia-o contra uma estimativa de TREINO, nao contra "
         "holdout. E exactamente o tipo de numero de que a scikit-learn e o "
         "NIST avisam. Nao serve de barra portavel."),
        ("Maximizar F1 (Google) e maximizar utilidade sob custo assimetrico "
         "(scikit-learn) escolhem limiares DIFERENTES no mesmo modelo. Nao "
         "sao duas expressoes do mesmo principio."),
        ("O NIST esta noutra altitude: manda DOCUMENTAR a tolerancia, nao diz "
         "qual ela e. Concorda com os outros por se recusar a prescrever — o "
         "que e acordo sobre a AUSENCIA de regra, nao uma regra partilhada."),
        ("O proprio NIST avisa que o problema esta por resolver: «The current "
         "lack of consensus on robust and verifiable measurement methods for "
         "risk and trustworthiness … is an AI risk measurement challenge». "
         "Nenhuma das tres fontes de fornecedor reconhece isto."),
    ],
    "O_QUE_ISTO_OBRIGA": (
        "Se ninguem prescreve o numero, ele tem de ser escolhido AQUI e "
        "justificado AQUI pela funcao de custo desta casa. Foi o que a seccao "
        "da ASSIMETRIA faz. O padrao externo nao revoga lei canonica e "
        "tambem nao dispensa a casa de escolher o proprio custo."),
}


# ══════════════════════════════════════════════════════════════════════════
# 5 · A FUNCAO PURA — recebe metricas, devolve PASS/FAIL e os motivos
# ══════════════════════════════════════════════════════════════════════════
# Ela NAO chama a Admission, NAO le documento e NAO classifica nada. Julga
# numeros. Se precisasse de um documento para decidir, deixava de ser um gate
# e passava a ser mais um mecanismo com opiniao.
class MetricaEmFalta(Exception):
    """Falta uma metrica do gate. NAO se assume zero: para-se.

    Assumir zero num campo em falta e a maneira mais silenciosa de passar:
    `ERROR` ausente viraria `ERROR = 0`, e um mecanismo que rebentou passaria
    por um que nunca falhou.
    """


EXIGIDAS = tuple(nome for nome, _op, _lim in CONDICOES)


def _compara(valor, op, limiar):
    return valor >= limiar if op == ">=" else valor <= limiar


def avaliar_gate(metricas):
    """PASS/FAIL, e a linha de cada condicao — a que falhou e as que passaram.

    Nenhuma media compensa a falha de um hard gate: basta UMA linha em FALHA
    para o veredicto ser FAIL, por melhores que sejam as outras.
    """
    faltam = [n for n in EXIGIDAS if n not in metricas]
    if faltam:
        raise MetricaEmFalta("faltam metricas do gate: %s" % faltam)

    linhas = []
    for nome, op, chave in CONDICOES:
        limiar = LIMIARES[chave]["VALOR"]
        valor = metricas[nome]
        passa = _compara(valor, op, limiar)
        linhas.append({
            "CONDICAO": nome,
            "OPERADOR": op,
            "LIMIAR": str(limiar),
            "LIMIAR_DECIMAL": (round(float(limiar), 4)
                               if isinstance(limiar, Fraction) else limiar),
            "MEDIDO": (round(float(valor), 4)
                       if isinstance(valor, (Fraction, float)) else valor),
            "PASSA": passa,
            "PORQUE_O_LIMIAR": LIMIARES[chave]["PORQUE"],
        })
    falhadas = [l["CONDICAO"] for l in linhas if not l["PASSA"]]
    return {
        "GATE_VERSION": GATE_VERSION,
        "GATE_OWNER": GATE_OWNER,
        "PRIMARY_UNIT": UNIDADE_PRIMARIA,
        "THEMATIC_GATE_PASS": not falhadas,
        "VEREDICTO": "FAIL" if falhadas else "PASS",
        "FAILED_CONDITIONS": falhadas,
        "LINHAS": linhas,
        "NENHUMA_MEDIA_COMPENSA": (
            "basta uma condicao em falha para o veredicto ser FAIL. Precisao "
            "excelente nao compensa captura positiva ruim."),
    }


def avaliar_reachability(alcancados, comprovados):
    """Com a procedencia comprovada, o item TEM de chegar a pergunta tematica.

    ⚠️ `comprovados` e o conjunto cuja origem JA esta provada. Origem
    legitimamente desconhecida fica fora do denominador — inventa-la para o
    gate passar seria mentir com a palavra certa.
    """
    if not comprovados:
        raise MetricaEmFalta("denominador de alcance vazio")
    taxa = Fraction(alcancados, comprovados)
    return {
        "REACHABILITY": str(taxa),
        "REACHABILITY_DECIMAL": round(float(taxa), 4),
        "REQUIRED": str(REACHABILITY_REQUIRED),
        "REACHABILITY_GATE_PASS": taxa >= REACHABILITY_REQUIRED,
        "ALCANCADOS": alcancados, "COMPROVADOS": comprovados,
        "NAO_AUTORIZA": "fabricar SOURCE_ID para engrossar o numerador",
    }


def avaliar_integracao(reachability, tematico):
    """Aprovado offline ainda NAO e pronto para runtime.

        CLASSIFIER_GOOD + LINEAGE_BROKEN = NOT_READY
        LINEAGE_GOOD + CLASSIFIER_BAD    = NOT_READY
    """
    passa = (reachability["REACHABILITY_GATE_PASS"]
             and tematico["THEMATIC_GATE_PASS"])
    return {
        "INTEGRATION_GATE_PASS": passa,
        "VEREDICTO": "READY_FOR_INTEGRATION" if passa else "NOT_READY",
        "REACHABILITY_GATE_PASS": reachability["REACHABILITY_GATE_PASS"],
        "THEMATIC_GATE_PASS": tematico["THEMATIC_GATE_PASS"],
        "PORQUE": ("um mecanismo bom com linhagem partida nao decide nada em "
                   "runtime; uma linhagem boa com mecanismo mau decide errado"),
    }


# ══════════════════════════════════════════════════════════════════════════
# 6 · A EXTRACCAO — mecanica, e com a regra escrita antes de correr
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ A REGRA DA PREVISAO DE UM GRUPO, FIXADA ANTES DE VER QUALQUER NUMERO:
#
#     Um grupo tem previsao BINARIA so quando TODOS os seus documentos
#     receberam a MESMA previsao binaria. Se um se abstem, rebenta, ou
#     discorda dos irmaos, o grupo NAO tem previsao binaria.
#
# E a mesma disciplina do GROUP_PASS: quatro edicoes do mesmo boletim nao se
# resolvem por maioria. Ou o mecanismo resolveu aquele boletim, ou nao.
SIM, NAO = "SIM", "NAO"
BINARIOS_CRUS = (SIM, NAO)


def previsao_do_grupo(previsoes):
    """A previsao binaria do grupo, ou None se ele nao tem uma."""
    unicas = set(previsoes)
    if len(unicas) == 1 and previsoes[0] in BINARIOS_CRUS:
        return previsoes[0]
    return None


def metricas_do_baseline(artefato):
    """As metricas do gate, tiradas de um artefato de baseline ja congelado.

    Nao recalcula previsao nenhuma e nao chama a Admission: le o que ja foi
    medido. O agrupamento vem do artefato, que por sua vez o herdou do
    gabarito — nunca das previsoes.
    """
    grupos = artefato["GROUPS"]
    obs = artefato["OBSERVATION_PLANE"]
    total = obs["GROUP_TOTAL"]
    positivos = [g for g in grupos if g["HUMAN_LABEL"] == "T3_SIM"]
    negativos = [g for g in grupos if g["HUMAN_LABEL"] == "T3_NAO"]

    def prev(g):
        return previsao_do_grupo(g["PREVISOES"])

    tp = sum(1 for g in positivos if prev(g) == SIM)
    fn = sum(1 for g in positivos if prev(g) == NAO)
    tn = sum(1 for g in negativos if prev(g) == NAO)
    fp = sum(1 for g in negativos if prev(g) == SIM)
    binarias = tp + fn + tn + fp
    erros = sum(1 for g in grupos if "ERRO" in g["PREVISOES"])

    return {
        # os oito hard gates
        "POSITIVE_CAPTURE_RATE": Fraction(tp, len(positivos)),
        "EXPLICIT_FALSE_NEGATIVE": fn,
        "SPECIFICITY": Fraction(tn, len(negativos)),
        "PRECISION_T3": (Fraction(tp, tp + fp) if (tp + fp)
                         else Fraction(0, 1)),
        "DECISION_COVERAGE": Fraction(binarias, total),
        "GROUP_PASS_RATE": Fraction(obs["GROUP_PASS"], total),
        "ERROR": erros,
        "FALSE_SUBSTRING_OUTCOME_DEPENDENCY":
            len(artefato.get("DECISIONS_RESTING_ONLY_ON_FALSE_MATCH", [])),
        # o que nao e gate, mas explica o gate
        "_DIAGNOSTICO": {
            "GROUP_TOTAL": total,
            "GROUP_POSITIVE": len(positivos), "GROUP_NEGATIVE": len(negativos),
            "TP": tp, "FN": fn, "TN": tn, "FP": fp,
            "GRUPOS_SEM_PREVISAO_BINARIA": total - binarias,
            "GROUP_PASS": obs["GROUP_PASS"], "GROUP_FAIL": obs["GROUP_FAIL"],
            "GROUP_NOT_DECIDED": obs["GROUP_NOT_DECIDED"],
            "PRECISION_SEM_AFIRMACOES": (tp + fp) == 0,
        },
    }


def reachability_do_baseline(artefato):
    """Quantos itens com procedencia comprovada chegaram a pergunta tematica.

    «Chegou» = a porta respondeu pela regra do TEMA, e nao parou antes numa
    pergunta de prontidao. O proprio artefato guarda a regra que decidiu.
    """
    casos = artefato["CASES"]
    chegaram = sum(1 for c in casos
                   if c["ADMISSION_RULE"] == "pertence ao universo")
    return avaliar_reachability(chegaram, len(casos))


# ══════════════════════════════════════════════════════════════════════════
# 7 · O CONTRATO E O RELATORIO
# ══════════════════════════════════════════════════════════════════════════
def _json(caminho):
    with open(os.path.join(RAIZ, caminho), encoding="utf-8") as f:
        return json.load(f)


def _limiar_publicavel(c):
    v = c["VALOR"]
    return {"VALOR": str(v),
            "DECIMAL": round(float(v), 4) if isinstance(v, Fraction) else v,
            "COMO_SE_LE": c["COMO_SE_LE"], "PORQUE": c["PORQUE"],
            **{k: v2 for k, v2 in c.items()
               if k not in ("VALOR", "COMO_SE_LE", "PORQUE")}}


def contrato():
    """O gate, sem nenhum resultado dentro. E o alvo, nao a flecha."""
    return {
        "SCHEMA": "sintonia.thematic-acceptance-gate/1",
        "THIS_IS": "THEMATIC_MECHANISM_EVALUATION_GATE_V1",
        "THIS_IS_NOT": "FULL_EAME_PRODUCTION_RELEASE_GATE",
        "GATE_OWNER": GATE_OWNER,
        "GATE_VERSION": GATE_VERSION,
        "O_QUE_ISTO_E": (
            "As condicoes que um mecanismo tematico tem de cumprir para ser "
            "considerado suficientemente bom para AVALIACAO no SINTONIA. "
            "Escrito ANTES de qualquer candidato existir."),
        "PRIMARY_UNIT": UNIDADE_PRIMARIA,
        "DIAGNOSTIC_UNIT": UNIDADE_DIAGNOSTICA,
        "PORQUE_A_UNIDADE": (
            "DOCUMENT != INDEPENDENT_OBSERVATION. Quatro edicoes do mesmo "
            "boletim sao quatro ficheiros e uma observacao. O plano de "
            "documentos continua obrigatorio como diagnostico; o PASS/FAIL "
            "usa observacoes."),
        "ASSIMETRIA_DO_ERRO": ASSIMETRIA,
        "ESTUDO_EXTERNO": ESTUDO_EXTERNO,
        "LIMIARES": {k: _limiar_publicavel(v) for k, v in LIMIARES.items()},
        "REACHABILITY_REQUIRED": str(REACHABILITY_REQUIRED),
        "REACHABILITY_DENOMINADOR_T3": REACHABILITY_DENOMINADOR_T3,
        "CONDICOES": [{"METRICA": n, "OPERADOR": o, "LIMIAR": l}
                      for n, o, l in CONDICOES],
        "INTEGRATION_GATE": (
            "INTEGRATION_GATE_PASS = REACHABILITY_GATE_PASS AND "
            "THEMATIC_GATE_PASS. Aprovado offline nao e pronto para runtime."),
        "EVALUATION_SCOPE": ESCOPO,
        "NAO_AUTORIZA": list(NAO_AUTORIZA),
        "T3_GROUND_TRUTH_ROLE": T3_GROUND_TRUTH_ROLE,
        "INDEPENDENCIA": (
            "A partir deste commit, um mecanismo ajustado a olhar para "
            "T3-GROUND-TRUTH-EVAL-V1 NAO pode depois usar os mesmos 36 como "
            "prova final independente. Candidatos futuros tem de ser definidos "
            "ANTES de receberem os seus resultados; havendo afinacao "
            "posterior, e preciso holdout novo.\n"
            "UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE."),
        "PRODUCAO_AINDA_EXIGE": [
            "validacao fresca e trancada", "prova de integracao",
            "prova de runtime", "regressao", "auditoria em live"],
        "NAO_DERIVADO_DO_BASELINE": (
            "Nenhum limiar foi escolhido para o mecanismo de hoje passar nem "
            "para ele falhar. Cada um nasce da funcao de custo declarada na "
            "ASSIMETRIA_DO_ERRO, e a razao esta ao lado do numero."),
    }


def aplicar_ao_baseline():
    art = _json(BASELINE)
    metricas = metricas_do_baseline(art)
    alcance = reachability_do_baseline(art)
    tematico = avaliar_gate({k: v for k, v in metricas.items()
                             if not k.startswith("_")})
    integracao = avaliar_integracao(alcance, tematico)
    return art, metricas, alcance, tematico, integracao


def main():
    c = contrato()
    art, metricas, alcance, tematico, integracao = aplicar_ao_baseline()
    diag = metricas["_DIAGNOSTICO"]

    print("GATE DE ACEITACAO DE MECANISMO TEMATICO — %s" % GATE_VERSION)
    print("=" * 74)
    print(f"  GATE_OWNER    {GATE_OWNER}")
    print(f"  THIS_IS       {c['THIS_IS']}")
    print(f"  THIS_IS_NOT   {c['THIS_IS_NOT']}")
    print(f"  PRIMARY_UNIT  {c['PRIMARY_UNIT']}   "
          f"(diagnostico: {c['DIAGNOSTIC_UNIT']})")

    print("\n  O ESTUDO EXTERNO")
    print(f"    UNIVERSAL_THRESHOLD_FOUND = "
          f"{ESTUDO_EXTERNO['THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD']}")
    for s in ESTUDO_EXTERNO["SISTEMAS"]:
        print(f"    {s['NOME']:<42}prescreve: "
              f"{s['PRESCREVE_LIMIAR_UNIVERSAL']}")
    print("    convergencia (e onde ela e mais fraca do que parece):")
    for k, v in ESTUDO_EXTERNO["CONVERGENCIA"].items():
        print(f"      {k}")
        print(f"        {v}")

    print("\n  A ASSIMETRIA QUE PRODUZ OS NUMEROS")
    print(f"    FALSE_NEGATIVE_COST > FALSE_POSITIVE_COST")
    print(f"    ABSTAIN e preferivel a NEGATIVO ERRADO — mas abster-se "
          f"sempre tambem reprova")

    print("\n  OS LIMIARES, ESCRITOS ANTES DE QUALQUER CANDIDATO")
    for chave, v in LIMIARES.items():
        val = v["VALOR"]
        mostra = ("%s (%.4f)" % (val, float(val))
                  if isinstance(val, Fraction) else str(val))
        print(f"    {chave:<46}{mostra}")
        print(f"        {v['COMO_SE_LE']}")
    print(f"    {'REACHABILITY_REQUIRED':<46}{REACHABILITY_REQUIRED} "
          f"(sobre {REACHABILITY_DENOMINADOR_T3} com procedencia comprovada)")

    print("\n" + "=" * 74)
    print("  O GATE APLICADO AO BASELINE CONGELADO — mecanicamente")
    print("=" * 74)
    print(f"    baseline: {BASELINE}")
    print(f"    fingerprint: {art['FIRST_VALID_BASELINE_FINGERPRINT'][:32]}…")
    print(f"\n    unidade: {diag['GROUP_TOTAL']} observacoes "
          f"({diag['GROUP_POSITIVE']} positivas · "
          f"{diag['GROUP_NEGATIVE']} negativas)")
    print(f"    TP {diag['TP']} · FN {diag['FN']} · TN {diag['TN']} · "
          f"FP {diag['FP']} · sem previsao binaria "
          f"{diag['GRUPOS_SEM_PREVISAO_BINARIA']}")

    print("\n  GATE A — REACHABILITY")
    print(f"    {alcance['ALCANCADOS']}/{alcance['COMPROVADOS']} = "
          f"{alcance['REACHABILITY']}   exigido {alcance['REQUIRED']}   "
          f"{'PASSA' if alcance['REACHABILITY_GATE_PASS'] else 'FALHA'}")

    print("\n  GATE B — TEMATICO")
    for l in tematico["LINHAS"]:
        print(f"    {'PASSA' if l['PASSA'] else 'FALHA':<6}"
              f"{l['CONDICAO']:<38}{str(l['MEDIDO']):>8} "
              f"{l['OPERADOR']} {l['LIMIAR']}")
    print(f"\n    THEMATIC_GATE_PASS = {tematico['THEMATIC_GATE_PASS']}")
    if tematico["FAILED_CONDITIONS"]:
        print(f"    FAILED_CONDITIONS  = {tematico['FAILED_CONDITIONS']}")

    print(f"\n  GATE DE INTEGRACAO")
    print(f"    INTEGRATION_GATE_PASS = {integracao['INTEGRATION_GATE_PASS']}"
          f"   -> {integracao['VEREDICTO']}")

    print(f"\n  CURRENT_ADMISSION_GATE_RESULT = {tematico['VEREDICTO']}")
    print(f"  EVALUATION_SCOPE = {ESCOPO}   nao autoriza {list(NAO_AUTORIZA)}")
    print(f"  ADMISSION_CHANGED = NO · KEYWORDS_CHANGED = NO · "
          f"CLASSIFIER_BUILT = NO")

    if "--escrever" in sys.argv:
        doc = dict(c)
        doc["APLICACAO_AO_BASELINE_CONGELADO"] = {
            "BASELINE": BASELINE,
            "BASELINE_FINGERPRINT": art["FIRST_VALID_BASELINE_FINGERPRINT"],
            "DIAGNOSTICO": diag,
            "REACHABILITY": alcance,
            "THEMATIC": tematico,
            "INTEGRATION": integracao,
            "CURRENT_ADMISSION_GATE_RESULT": tematico["VEREDICTO"],
            "O_QUE_ISTO_NAO_AUTORIZA": (
                "consertar. Mesmo com FAIL: ADMISSION_CHANGED = NO, "
                "KEYWORDS_CHANGED = NO, CLASSIFIER_BUILT = NO."),
        }
        alvo = os.path.join(RAIZ, SAIDA)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\n  escrito: {SAIDA}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
