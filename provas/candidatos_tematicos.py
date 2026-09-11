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
    # ⚠️ O RED TEAM APANHOU ESTA GUARDA A DEIXAR PASSAR DOIS ATAQUES.
    # A primeira versao perguntava «o caminho proibido aparece na ficha e NAO
    # esta em INPUTS_FORBIDDEN?». Como toda ficha boa LISTA os proibidos, a
    # condicao nunca era verdadeira — e uma ficha podia citar o gabarito na
    # HYPOTHESIS, ou po-lo em TEXT_FIELDS_USED, e passar.
    #
    #     DECLARAR QUE NAO SE LE UM FICHEIRO
    #     NAO E LICENCA PARA O CITAR EM TODO O LADO.
    #
    # Agora o caminho proibido so pode aparecer DENTRO de INPUTS_FORBIDDEN, e
    # em mais lado nenhum da ficha.
    resto = json.dumps({k: v for k, v in f.items() if k != "INPUTS_FORBIDDEN"},
                       ensure_ascii=False).lower()
    for caminho in FICHEIROS_PROIBIDOS:
        if caminho.lower() in resto:
            raise FichaInvalida(
                "%s: cita %s fora de INPUTS_FORBIDDEN — declarar que nao se le "
                "um ficheiro nao e licenca para o citar noutro campo"
                % (cid, caminho))
    for campo in CAMPOS_PROIBIDOS:
        if campo in f["INPUTS_ALLOWED"]:
            raise FichaInvalida("%s: %s nao pode estar em INPUTS_ALLOWED"
                                % (cid, campo))
    # ⚠️ E AQUI A GUARDA TEVE DE SER AFINADA, E A RAZAO IMPORTA.
    # A primeira versao procurava os 57 termos da regra actual na ficha
    # INTEIRA. So que a lista de hoje contem palavras portuguesas comuns —
    # `prova`, `registro`, `evento`, `produto` — e esta arvore escreve «prova»
    # em cada segundo paragrafo. A guarda reprovava prosa legitima.
    #
    #     UM MARCADOR QUE NAO DISTINGUE O TERMO DA PALAVRA
    #     REPROVA O TEXTO QUE EXPLICA O MECANISMO.
    #
    # O risco real nao e a prosa: e uma ficha que ENUMERA termos, isto e, que
    # traz a lista de palavras para dentro da configuracao. Entao a guarda
    # olha para os campos que CONFIGURAM o mecanismo, e deixa a prosa em paz.
    CAMPOS_DE_CONFIGURACAO = ("INPUTS_ALLOWED", "TEXT_FIELDS_USED",
                              "TUNABLE_PARAMETERS", "FROZEN_PARAMETERS",
                              "DECISION_OUTPUT")
    config = json.dumps({k: f[k] for k in CAMPOS_DE_CONFIGURACAO},
                        ensure_ascii=False).lower()
    achados = [t for t in termos_proibidos
               if re.search(r"(?<![a-zà-ÿ])%s(?![a-zà-ÿ])" % re.escape(t), config)]
    if achados:
        raise FichaInvalida(
            "%s: a CONFIGURACAO da ficha enumera termos da regra actual: %s. "
            "Uma lista de palavras dentro de um candidato e a memoria do "
            "corpus a entrar pela porta dos fundos." % (cid, achados[:5]))
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


# ══════════════════════════════════════════════════════════════════════════
# 4 · OS CANDIDATOS — congelados antes de verem o corpus
# ══════════════════════════════════════════════════════════════════════════
# Quatro familias genuinamente diferentes, e nenhuma inventada para encher
# quantidade. Duas familias estudadas ficaram DE FORA, e a razao de cada uma
# esta escrita em FAMILIAS_EXCLUIDAS — uma exclusao medida vale mais do que um
# quinto candidato de enfeite.
ENTRADAS_PERMITIDAS = ["texto", "ITEM_LANGUAGE", "COUNTRY_SCOPE",
                       "artifact_type", "DOCUMENT_TYPE"]
ENTRADAS_PROIBIDAS = [
    "source_id", "CONTENT_PATH", "BODY_PATH", "CANONICAL_PATH", "ALL_PATHS",
    "ITEM_ID", "REVIEWER_A", "REVIEWER_B", "AGREEMENT", "FINAL_LABEL",
    "resultado", "universo",
] + list(FICHEIROS_PROIBIDOS)

# `PUBLISHER` chega a porta e NAO entra como feature. Fica so como estrato de
# avaliacao — medir por publicador e diferente de decidir por publicador.
SOURCE_IS_CONTEXT_ONLY = (
    "PUBLISHER pode ser usado para ESTRATIFICAR a medicao e nunca para decidir. "
    "O contraexemplo canonico desta casa e a ARPAV: uma mesma instituicao "
    "publica material de universos diferentes. Externamente, e o caso Clever "
    "Hans do classificador de cavalos que lia a MARCA DA FONTE na imagem "
    "(Lapuschkin et al., Nature Communications 10:1096, 2019).")

CANDIDATOS = [
    {
        "CANDIDATE_ID": "C1-LEXICAL-STRUCTURED",
        "NAME": "Regra lexical estruturada",
        "VERSION": "1",
        "FAMILY": "LEXICAL_RULE",
        "HYPOTHESIS": (
            "O que falha hoje e o CASAMENTO, nao o inventario. Trocando "
            "correspondencia por posicao de caracteres por fronteira de "
            "palavra (Unicode UAX #29), acrescentando escopo de negacao "
            "(NegEx/ConText) e peso por evidencia, a mesma lista de hoje "
            "decide melhor.\n"
            "ESTE CANDIDATO E O CONTROLO: ele isola UMA variavel. Se ele "
            "subir muito, o defeito era o mecanismo; se nao subir, o defeito "
            "esta no inventario, e nenhuma lista escrita a mao o conserta."),
        "INPUTS_ALLOWED": ["texto", "ITEM_LANGUAGE"],
        "INPUTS_FORBIDDEN": ENTRADAS_PROIBIDAS,
        "TEXT_FIELDS_USED": ["texto"],
        "LANGUAGE_HANDLING": (
            "Artefacto POR LINGUA. Idioma nao resolvido cai para a lista "
            "italiana e isso e uma fraqueza declarada, nao um acaso."),
        "DECISION_OUTPUT": ["SIM", "NAO", "NAO_SEI"],
        "ABSTENTION_SUPPORTED": "YES",
        "DETERMINISTIC": "YES",
        "MODEL_DEPENDENCY": "NONE",
        "EXTERNAL_API_DEPENDENCY": "NO",
        "TRAINING_REQUIRED": "NO",
        "TRAINING_SOURCE": None,
        "TRAINING_SET_INDEPENDENT_FROM_EVALUATION": "NOT_APPLICABLE",
        "TUNABLE_PARAMETERS": ["limiar_de_peso", "janela_de_escopo"],
        "FROZEN_PARAMETERS": ["limiar_de_peso", "janela_de_escopo"],
        "EXPECTED_STRENGTH": (
            "Deterministico, sem dependencia externa, explicavel ao nivel do "
            "trecho que disparou. Mata por construcao o defeito de substring "
            "que a baseline mediu."),
        "EXPECTED_WEAKNESS": (
            "O inventario continua escrito a mao, e ha prova externa de que "
            "isso e fragil: King, Lam & Roberts (AJPS 2017) pediram a 43 "
            "pessoas a lista de termos de um tema com exemplos a vista — "
            "mediana de 8 termos, 149 termos unicos no total, e em 66% deles "
            "NENHUMA das outras 42 pessoas se lembrou do mesmo. Duas listas "
            "diferentes produzem conjuntos diferentes."),
        "FALSE_NEGATIVE_RISK": (
            "ALTO — o termo que ninguem escreveu nunca acende"),
        "FALSE_POSITIVE_RISK": (
            "MEDIO — cai com fronteira de palavra e escopo de negacao"),
        "EXPLAINABILITY": "ALTA — a decisao E a regra que disparou",
        "AUDITABILITY": "ALTA — inventario versionado, diff legivel",
        "COST_MODEL": "LOCAL · sem custo por documento",
        "LATENCY_MODEL": "milissegundos",
        "OFFLINE_CAPABLE": "YES",
        "FAILURE_BEHAVIOR": "sem regra acima do limiar -> NAO_SEI",
        "WHAT_WOULD_INVALIDATE_THIS_CANDIDATE": (
            "Se ele empatar com o mecanismo actual, a hipotese cai: o defeito "
            "nao era o casamento, e melhorar o casamento nao resolve."),
        "IMPLEMENTATION_STATUS": "DEFINED_NOT_IMPLEMENTED",
        "CANDIDATE_STATUS": "READY_FOR_IMPLEMENTATION",
        "FONTES": [
            "http://www.unicode.org/reports/tr29/",
            "https://www.sciencedirect.com/science/article/pii/S1532046409000744",
            "https://gking.harvard.edu/files/ajps12291_final.pdf"],
    },
    {
        "CANDIDATE_ID": "C2-TAXONOMY-CONCEPT",
        "NAME": "Taxonomia controlada com evidencia lexical",
        "VERSION": "1",
        "FAMILY": "TAXONOMY_ONTOLOGY",
        "HYPOTHESIS": (
            "O alvo da decisao nao e a palavra: e o CONCEITO. Um vocabulario "
            "controlado ja existente da o inventario que ninguem desta casa "
            "consegue recordar, e da-o em varias linguas de uma vez — porque "
            "o conceito e neutro e as etiquetas e que sao por lingua.\n"
            "Esta arvore JA TEM metade do material: `coleta/eppo_gd.py` le "
            "nomes por codigo EPPO (italiano incluido) e o dicionario local "
            "tem 1381 codigos de alvo e 492 de cultura, com nome cientifico."),
        "INPUTS_ALLOWED": ["texto", "ITEM_LANGUAGE"],
        "INPUTS_FORBIDDEN": ENTRADAS_PROIBIDAS,
        "TEXT_FIELDS_USED": ["texto"],
        "LANGUAGE_HANDLING": (
            "NEUTRO POR CONSTRUCAO. O nome cientifico e latim e nao muda de "
            "lingua; as etiquetas comuns vem por lingua do mesmo conceito. "
            "Documento de idioma nao resolvido degrada suavemente, porque "
            "etiquetas de linguas diferentes apontam ao mesmo conceito."),
        "DECISION_OUTPUT": ["SIM", "NAO", "NAO_SEI"],
        "ABSTENTION_SUPPORTED": "YES",
        "DETERMINISTIC": "YES",
        "MODEL_DEPENDENCY": "NONE",
        "EXTERNAL_API_DEPENDENCY": "YES",
        "TRAINING_REQUIRED": "NO",
        "TRAINING_SOURCE": None,
        "TRAINING_SET_INDEPENDENT_FROM_EVALUATION": "NOT_APPLICABLE",
        "TUNABLE_PARAMETERS": ["limiar_de_conceitos", "profundidade_hierarquia"],
        "FROZEN_PARAMETERS": ["limiar_de_conceitos", "profundidade_hierarquia"],
        "EXPECTED_STRENGTH": (
            "Zero dados rotulados, deterministico, multilingue por "
            "construcao e explicavel ate ao conceito. O indexador oficial da "
            "UE (JEX) mede F1 0.48-0.54 em 22 linguas com parametros "
            "por omissao e conclui que o algoritmo e «nearly "
            "language-independent» — raro, e directamente util ao problema de "
            "idioma nao resolvido desta casa."),
        "EXPECTED_WEAKNESS": (
            "Cobertura do vocabulario, e ela JA ESTA MEDIDA nesta arvore: o "
            "dicionario local veio de tabelas espanholas e generos so "
            "italianos passam sem conferencia (`Scaphoideus` nao esta nele). "
            "E o JEX documenta o outro buraco: texto institucional repetitivo "
            "polui a evidencia lexical e precisou de lista de paragem "
            "multi-palavra."),
        "FALSE_NEGATIVE_RISK": (
            "MEDIO — conceito ausente do vocabulario nao acende"),
        "FALSE_POSITIVE_RISK": (
            "BAIXO — o conceito e especifico; mencao nao e tratamento, e a "
            "hierarquia deixa exigir profundidade"),
        "EXPLAINABILITY": (
            "ALTA — «etiqueta X do conceito C, que desce de U», com a "
            "definicao oficial por tras"),
        "AUDITABILITY": "ALTA — o conceito tem identificador estavel e publico",
        "COST_MODEL": "LOCAL apos cache; a colheita de nomes e uma vez",
        "LATENCY_MODEL": "milissegundos apos cache",
        "OFFLINE_CAPABLE": "YES apos cache",
        "FAILURE_BEHAVIOR": (
            "vocabulario indisponivel -> ERRO, nunca NAO. E se nenhum "
            "conceito passa o limiar -> NAO_SEI"),
        "WHAT_WOULD_INVALIDATE_THIS_CANDIDATE": (
            "Se a cobertura do vocabulario no corpus real for baixa ao ponto "
            "de a abstencao estourar o limite de cobertura do gate."),
        "IMPLEMENTATION_STATUS": "EXISTING_COMPONENT_REUSABLE",
        "CANDIDATE_STATUS": "READY_FOR_IMPLEMENTATION",
        "FONTES": [
            "https://www.w3.org/TR/skos-reference/",
            "https://aims.fao.org/standards/AGROVOC/concept-scheme",
            "https://arxiv.org/pdf/1309.5223",
            "https://github.com/NatLibFi/Annif/wiki/Backend:-MLLM"],
    },
    {
        "CANDIDATE_ID": "C3-LLM-STRUCTURED",
        "NAME": "Modelo de linguagem com saida estruturada",
        "VERSION": "1",
        "FAMILY": "LANGUAGE_MODEL",
        "HYPOTHESIS": (
            "A decisao e de LEITURA, e nao de casamento. Um modelo que le o "
            "documento inteiro distingue «menciona» de «trata de» — que e "
            "exactamente onde a baseline falhou — e nao precisa de artefacto "
            "por lingua nem de deteccao de idioma.\n"
            "A saida e forcada ao vocabulario da porta por esquema, para o "
            "candidato nao poder inventar um estado que a porta nao tem."),
        "INPUTS_ALLOWED": ["texto", "ITEM_LANGUAGE"],
        "INPUTS_FORBIDDEN": ENTRADAS_PROIBIDAS,
        "TEXT_FIELDS_USED": ["texto"],
        "LANGUAGE_HANDLING": (
            "SEM ARTEFACTO POR LINGUA — e a vantagem estrutural desta "
            "familia sobre C1 e C2. Nao ha passo de deteccao de idioma, e "
            "texto misturado nao precisa de tratamento especial."),
        "DECISION_OUTPUT": ["SIM", "NAO", "NAO_SEI"],
        "ABSTENTION_SUPPORTED": "YES",
        "DETERMINISTIC": "NO",
        "MODEL_DEPENDENCY": "EXTERNAL_LLM_PINNED_VERSION",
        "EXTERNAL_API_DEPENDENCY": "YES",
        "TRAINING_REQUIRED": "NO",
        "TRAINING_SOURCE": None,
        "TRAINING_SET_INDEPENDENT_FROM_EVALUATION": "NOT_APPLICABLE",
        "TUNABLE_PARAMETERS": ["k_amostras", "ordem_das_opcoes", "modelo_fixado"],
        "FROZEN_PARAMETERS": ["k_amostras", "ordem_das_opcoes", "modelo_fixado"],
        "EXPECTED_STRENGTH": (
            "Le o documento em vez de o procurar. Nao precisa de inventario "
            "escrito a mao, e por isso escapa ao defeito que King, Lam & "
            "Roberts mediram. Melhor das quatro familias para idioma nao "
            "resolvido ou misturado."),
        "EXPECTED_WEAKNESS": (
            "NAO E DETERMINISTICO, e nem sequer a temperatura zero: a causa "
            "documentada e a dependencia do tamanho do lote nos nucleos de "
            "reducao do servidor, que varia com carga alheia. Por isso "
            "`k_amostras` e parametro congelado — a saida trata-se como "
            "distribuicao, nao como valor.\n"
            "E ha vies de seleccao medido: modelos preferem certos "
            "identificadores de opcao (Zheng et al., ICLR 2024, 20 modelos), "
            "o que faz da ORDEM das opcoes um hiperparametro — por isso ela "
            "tambem esta congelada."),
        "FALSE_NEGATIVE_RISK": "BAIXO a MEDIO — por medir",
        "FALSE_POSITIVE_RISK": (
            "MEDIO — o esquema garante saida VALIDA, nao saida CERTA: a "
            "propria documentacao avisa que entrada nao relacionada com o "
            "esquema pode produzir alucinacao dentro do enum"),
        "EXPLAINABILITY": (
            "APARENTE, e essa e a armadilha. Da para pedir uma justificacao, "
            "mas nao ha fonte primaria que estabeleca que a justificacao "
            "gerada e FIEL a decisao tomada. NAO conta como prova de "
            "auditoria."),
        "AUDITABILITY": (
            "MEDIA — versao do modelo e prompt versionados; a computacao nao "
            "e reproduzivel bit a bit"),
        "COST_MODEL": "POR DOCUMENTO · o unico candidato com custo marginal",
        "LATENCY_MODEL": "segundos por documento",
        "OFFLINE_CAPABLE": "NO",
        "FAILURE_BEHAVIOR": (
            "API indisponivel, tempo esgotado ou saida invalida -> ERRO. "
            "NUNCA NAO, NUNCA NAO_SEI: uma falha de execucao nao e uma "
            "opiniao, e o gate conta-as em caixas diferentes."),
        "WHAT_WOULD_INVALIDATE_THIS_CANDIDATE": (
            "Se k amostras da mesma entrada divergirem acima do que o gate "
            "tolera, ou se a abstencao so aparecer quando o prompt a sugere — "
            "ha prova de que a taxa de abstencao pode medir a redaccao do "
            "prompt e nao a incerteza do modelo."),
        "IMPLEMENTATION_STATUS": "DEFINED_NOT_IMPLEMENTED",
        "CANDIDATE_STATUS": "READY_FOR_IMPLEMENTATION",
        "FONTES": [
            "https://developers.openai.com/api/docs/guides/structured-outputs",
            "https://arxiv.org/abs/2309.03882",
            "https://arxiv.org/abs/2506.09038",
            "https://aclanthology.org/2024.emnlp-industry.91/",
            "https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/"],
    },
    {
        "CANDIDATE_ID": "C4-HYBRID-CASCADE",
        "NAME": "Cascata: conceito primeiro, leitura depois",
        "VERSION": "1",
        "FAMILY": "HYBRID_CASCADE",
        "HYPOTHESIS": (
            "As fraquezas de C2 e C3 sao COMPLEMENTARES, e uma cascata "
            "cobre-as: o conceito decide o que consegue decidir — "
            "deterministico, barato, explicavel — e so o que sobra paga a "
            "leitura.\n"
            "A propriedade auditavel que so esta familia da: «tantos por "
            "cento dos documentos foram decididos por regra deterministica». "
            "Isso e uma medida de confianca que nenhuma das outras produz."),
        "INPUTS_ALLOWED": ["texto", "ITEM_LANGUAGE"],
        "INPUTS_FORBIDDEN": ENTRADAS_PROIBIDAS,
        "TEXT_FIELDS_USED": ["texto"],
        "LANGUAGE_HANDLING": (
            "Primeiro andar neutro por conceito; segundo andar sem artefacto "
            "por lingua. Idioma nao resolvido e precisamente o caso que cai "
            "para o segundo andar."),
        "DECISION_OUTPUT": ["SIM", "NAO", "NAO_SEI", "ERRO"],
        "ABSTENTION_SUPPORTED": "YES",
        "DETERMINISTIC": "PARTIAL",
        "MODEL_DEPENDENCY": "EXTERNAL_LLM_PINNED_VERSION",
        "EXTERNAL_API_DEPENDENCY": "YES",
        "TRAINING_REQUIRED": "NO",
        "TRAINING_SOURCE": None,
        "TRAINING_SET_INDEPENDENT_FROM_EVALUATION": "NOT_APPLICABLE",
        "TUNABLE_PARAMETERS": ["limiar_de_escalada", "ordem_dos_andares"],
        "FROZEN_PARAMETERS": ["limiar_de_escalada", "ordem_dos_andares"],
        "EXPECTED_STRENGTH": (
            "A fraccao decidida pelo primeiro andar e deterministica, "
            "gratuita e explicavel; o custo por documento so incide no resto. "
            "Arquitectura documentada em producao: os ensembles do Annif "
            "correm nas bibliotecas nacionais finlandesa, alema e polaca."),
        "EXPECTED_WEAKNESS": (
            "Depende do sinal de escalada estar calibrado, e e ai que ela "
            "herda o pior dos dois andares. Nao encontrei fonte primaria que "
            "isole um modo de falha caracteristico de cascatas — a literatura "
            "publica os sucessos. Isso e uma lacuna, e fica escrita como "
            "lacuna, nao como seguranca."),
        "FALSE_NEGATIVE_RISK": (
            "BAIXO por desenho — o que o primeiro andar nao resolve nao e "
            "recusado, e escalado"),
        "FALSE_POSITIVE_RISK": "MEDIO — herda o do andar que decidiu",
        "EXPLAINABILITY": (
            "ALTA ao nivel do sistema, porque o registo NOMEIA o andar que "
            "decidiu — melhor do que uma mistura, onde ninguem sabe quem "
            "decidiu"),
        "AUDITABILITY": (
            "ALTA se a decisao de escalada for registada, e nao so o rotulo "
            "final"),
        "COST_MODEL": "MISTO · custo marginal so na fraccao escalada",
        "LATENCY_MODEL": "milissegundos na fraccao resolvida, segundos no resto",
        "OFFLINE_CAPABLE": "PARTIAL",
        "FAILURE_BEHAVIOR": (
            "segundo andar indisponivel -> o que foi escalado sai ERRO, e o "
            "que o primeiro andar ja tinha resolvido MANTEM-SE. Degradacao "
            "parcial, nao queda total."),
        "WHAT_WOULD_INVALIDATE_THIS_CANDIDATE": (
            "Se a fraccao resolvida deterministicamente for pequena, a "
            "cascata e C3 com um passo a mais e o custo nao se justifica."),
        "IMPLEMENTATION_STATUS": "DEFINED_NOT_IMPLEMENTED",
        "CANDIDATE_STATUS": "READY_FOR_IMPLEMENTATION",
        "FONTES": [
            "https://arxiv.org/abs/2305.05176",
            "https://github.com/NatLibFi/Annif/wiki/Backend:-nn_ensemble",
            "https://arxiv.org/abs/1711.10160"],
    },
]


# ══════════════════════════════════════════════════════════════════════════
# 5 · AS FAMILIAS QUE FICARAM DE FORA — e por que medido, nao por gosto
# ══════════════════════════════════════════════════════════════════════════
#     UMA EXCLUSAO MEDIDA VALE MAIS DO QUE UM QUINTO CANDIDATO DE ENFEITE.
FAMILIAS_EXCLUIDAS = [
    {
        "FAMILY": "SUPERVISED_CLASSIFIER",
        "STATUS": "BLOCKED_PENDING_INDEPENDENT_TRAINING_SET",
        "PORQUE": (
            "MEDIDO nesta arvore: nao existe corpus de treino de T3 "
            "independente. As unicas duas origens que servem de gabarito sao "
            "o gabarito de T2 (universo errado) e o proprio conjunto de "
            "avaliacao, ja declarado EVALUATION. O livro de decisoes tem 813 "
            "itens e nasceu das palavras de hoje — treinar nele ensinaria o "
            "substituto a repetir o mecanismo que ele substitui.\n"
            "E os 36 NAO se partem em treino e teste: ja foram declarados "
            "avaliacao, e parti-los seria fabricar independencia."),
        "O_QUE_DESBLOQUEIA": (
            "Um conjunto rotulado por pessoa, independente dos 36. A "
            "literatura da a ordem de grandeza: com 8 exemplos por classe o "
            "desvio-padrao entre 10 particoes e de ~5 pontos — abaixo disso a "
            "diferenca entre dois candidatos e menor do que a diferenca entre "
            "duas particoes do mesmo."),
        "FONTES": ["https://arxiv.org/abs/2209.11055",
                   "https://pmc.ncbi.nlm.nih.gov/articles/PMC8981604/"],
    },
    {
        "FAMILY": "DENSE_EMBEDDING",
        "STATUS": "DEFERRED",
        "PORQUE": (
            "Nao e falta de merito — e que o proximo passo dela seria um "
            "acto de contaminacao. Um classificador por semelhanca precisa de "
            "um PROTOTIPO, e a unica definicao canonica escrita de T3 nesta "
            "arvore tem quatro palavras. Escrever um prototipo mais rico "
            "AGORA, tendo eu ja visto o corpus numa missao anterior, seria "
            "escrever a resposta e chamar-lhe hipotese.\n"
            "A alternativa limpa — embeber as etiquetas do vocabulario "
            "controlado — usa a MESMA fonte de evidencia que C2 e "
            "transforma-se numa variacao dele, nao numa familia nova.\n"
            "Ha ainda duas medicoes externas contra a pressa: nenhum modelo "
            "de embedding domina todas as tarefas (MTEB, 58 conjuntos, 112 "
            "linguas), logo a ESCOLHA DO MODELO passaria a ser ela propria um "
            "benchmark dentro do benchmark; e o espaco vectorial codifica "
            "IDENTIDADE DE LINGUA e nao so significado, o que num corpus de "
            "idioma nao resolvido e um erro de encaminhamento silencioso."),
        "O_QUE_DESBLOQUEIA": (
            "Um prototipo cuja origem seja anterior ao conjunto de avaliacao "
            "e um codificador fixado em arvore, com busca exacta."),
        "FONTES": ["https://aclanthology.org/2023.eacl-main.148/",
                   "https://aclanthology.org/2021.emnlp-main.612/"],
    },
]

# ── A ABSTENCAO NAO E UM CANDIDATO: E UMA CAMADA ───────────────────────────
# A familia da abstencao foi estudada e NAO entra na lista — nao por ser
# fraca, mas porque nao compete com as outras: ela EMBRULHA qualquer uma
# delas sem a modificar. Po-la a concorrer seria comparar um mecanismo com um
# acessorio.
#
# E ha uma razao forte para a guardar para depois do benchmark: o controlo de
# risco conformal permite FIXAR a taxa de falso negativo como a quantidade
# controlada, em vez de afinar um limiar e torcer para que ela caia onde se
# quer. Isso e um encaixe exacto com a assimetria do gate desta casa.
CAMADA_DE_ABSTENCAO = {
    "NAO_E_CANDIDATO": True,
    "PORQUE": ("embrulha qualquer um dos quatro sem os modificar; compara-la "
               "com eles seria comparar um mecanismo com um acessorio"),
    "O_QUE_OFERECE": (
        "garantia de amostra finita sem suposicao de distribuicao, e — na "
        "variante de controlo de risco — a possibilidade de fixar a TAXA DE "
        "FALSO NEGATIVO como alvo, que e exactamente o lado caro do custo "
        "assimetrico deste gate"),
    "O_QUE_EXIGE": (
        "um conjunto de calibracao separado do treino E do teste. A ordem de "
        "grandeza publicada: ~1000 para a maioria dos casos, 102 para folga "
        "de 0.05. NAO pode ser os 36."),
    "A_ARMADILHA_REGISTADA": (
        "a cobertura e MARGINAL, nao condicional: da para ter 90% no total e "
        "zero num estrato. E ha prova de que a abstencao pode AUMENTAR a "
        "disparidade entre grupos, porque o mecanismo abstem-se onde ja "
        "acertava. Medir por universo e por lingua, nunca so no agregado."),
    "FONTES": ["https://arxiv.org/abs/2208.02814",
               "https://arxiv.org/abs/2107.07511",
               "https://arxiv.org/abs/2010.14134"],
}

# O que o estudo externo devolveu e que NAO da para fechar com seguranca.
LACUNAS_DO_ESTUDO = [
    "nenhuma fonte primaria isola um modo de falha caracteristico de cascatas",
    "nenhuma fonte primaria quantifica a precisao POR LINGUA de classificacao "
    "por modelo de linguagem com saida estruturada — a vantagem multilingue "
    "de C3 e plausivel por arquitectura e NAO medida",
    "nenhuma fonte primaria estabelece que a justificacao gerada por um "
    "modelo seja FIEL a decisao que ele tomou",
    "nenhuma fonte primaria mede a transicao especifica desta casa (lista "
    "plana de substring -> qualquer outra coisa) em documentos institucionais",
]


# ══════════════════════════════════════════════════════════════════════════
# 6 · O MANIFESTO E O RELATORIO
# ══════════════════════════════════════════════════════════════════════════
def manifesto():
    validar_conjunto(CANDIDATOS)
    fichas = [dict(f, CANDIDATE_SPEC_SHA256=impressao_da_ficha(f))
              for f in CANDIDATOS]
    return {
        "SCHEMA": "sintonia.thematic-candidates/1",
        "O_QUE_ISTO_E": (
            "Os mecanismos candidatos a substituir a decisao tematica, "
            "DEFINIDOS E CONGELADOS antes de verem o corpus de avaliacao. "
            "Nenhum foi executado, nenhum foi medido, nenhum venceu."),
        "CANDIDATE_SET_VERSION": CANDIDATE_SET_VERSION,
        "CANDIDATE_SET_SHA256": impressao_do_conjunto(CANDIDATOS),
        "FROZEN_BEFORE_EVALUATION": "YES",
        "CANDIDATE_COUNT": len(CANDIDATOS),
        "BENCHMARK_EXECUTED": "NO",
        "CANDIDATE_RESULTS_VIEWED": "NO",

        "O_MECANISMO_ACTUAL_NAO_E_CANDIDATO": (
            "Ele entra depois como BASELINE / CONTROL, e fica intacto: "
            "corrigi-lo agora destruiria a comparacao."),

        "ENTRADAS_PERMITIDAS": ENTRADAS_PERMITIDAS,
        "ENTRADAS_PROIBIDAS": ENTRADAS_PROIBIDAS,
        "PORQUE_O_CAMINHO_E_PROIBIDO": (
            "medido no atlas: 78 de 78 identificadores de fonte embutem o "
            "token do universo declarado, e o caminho do ficheiro embute o "
            "identificador. ENTREGA-SE OS BYTES, NUNCA O CAMINHO."),
        "SOURCE_IS_CONTEXT_ONLY": SOURCE_IS_CONTEXT_ONLY,
        "CAMPOS_MORTOS_QUE_A_PORTA_ACTUAL_LE": (
            "title, nome, topics, crops, resumo — lidos pela regra de hoje e "
            "povoados por ninguem no caminho do documento"),

        "CANDIDATES": fichas,
        "FAMILIAS_EXCLUIDAS": FAMILIAS_EXCLUIDAS,
        "CAMADA_DE_ABSTENCAO": CAMADA_DE_ABSTENCAO,
        "LACUNAS_DO_ESTUDO": LACUNAS_DO_ESTUDO,

        "EVALUATION_SCOPE": "ITALIAN_AGRO_INSTITUTIONAL_CORPUS",
        "NAO_AUTORIZA": ["FRANCE", "SPAIN", "EAME"],
        "T3_GROUND_TRUTH_ROLE": "EVALUATION",

        "EXPOSICAO_PREVIA_DE_QUEM_DESENHOU": {
            "DESIGNER_PRIOR_EXPOSURE": "YES",
            "O_QUE": (
                "numa missao anterior da MESMA sessao, quem desenhou estas "
                "fichas correu a baseline e viu a saida POR DOCUMENTO, os "
                "termos que acenderam e quais itens eram falso positivo."),
            "PORQUE_ESTA_ESCRITO": (
                "nao da para desver, e fingir que da seria a propria "
                "contaminacao. Declarar e a unica mitigacao honesta."),
            "MITIGACAO_ESTRUTURAL": (
                "nenhuma ficha pode ENUMERAR termos da regra actual nos "
                "campos de configuracao, nem citar publicador, ITEM_ID ou "
                "SHA. O validador recusa a ficha que o fizer, e ha teste que "
                "prova que ele recusa."),
            "O_QUE_ISTO_NAO_RESOLVE": (
                "a escolha das FAMILIAS pode ter sido informada por saber "
                "onde o mecanismo actual falha. Isso e mitigado pelas fontes: "
                "as quatro familias vem do estudo externo e nao do corpus."),
        },
    }


def main():
    m = manifesto()
    print("CANDIDATOS TEMATICOS — %s" % CANDIDATE_SET_VERSION)
    print("=" * 74)
    print(f"  CANDIDATE_COUNT            {m['CANDIDATE_COUNT']}")
    print(f"  CANDIDATE_SET_SHA256       {m['CANDIDATE_SET_SHA256']}")
    print(f"  FROZEN_BEFORE_EVALUATION   {m['FROZEN_BEFORE_EVALUATION']}")
    print(f"  BENCHMARK_EXECUTED         {m['BENCHMARK_EXECUTED']}")

    print("\n  OS CANDIDATOS")
    for f in m["CANDIDATES"]:
        print(f"\n    {f['CANDIDATE_ID']}   [{f['FAMILY']}]")
        print(f"      {f['NAME']}")
        print(f"      determinismo {f['DETERMINISTIC']:<10}"
              f"abstencao {f['ABSTENTION_SUPPORTED']:<6}"
              f"treino {f['TRAINING_REQUIRED']:<5}"
              f"API externa {f['EXTERNAL_API_DEPENDENCY']}")
        print(f"      status  {f['IMPLEMENTATION_STATUS']}")
        print(f"      sha     {f['CANDIDATE_SPEC_SHA256'][:32]}…")

    print("\n  AS FAMILIAS QUE FICARAM DE FORA")
    for x in m["FAMILIAS_EXCLUIDAS"]:
        print(f"    {x['FAMILY']:<26}{x['STATUS']}")

    print(f"\n  A ABSTENCAO E UMA CAMADA, NAO UM CANDIDATO")
    print(f"    {CAMADA_DE_ABSTENCAO['PORQUE']}")

    print(f"\n  ENTRADAS PERMITIDAS   {ENTRADAS_PERMITIDAS}")
    print(f"  o caminho e proibido  78/78 ids do atlas embutem o universo")

    e = m["EXPOSICAO_PREVIA_DE_QUEM_DESENHOU"]
    print(f"\n  DESIGNER_PRIOR_EXPOSURE = {e['DESIGNER_PRIOR_EXPOSURE']}")
    print(f"    {e['MITIGACAO_ESTRUTURAL']}")

    print(f"\n  LACUNAS DO ESTUDO EXTERNO ({len(LACUNAS_DO_ESTUDO)})")
    for l in LACUNAS_DO_ESTUDO:
        print(f"    · {l}")

    if "--escrever" in sys.argv:
        alvo = os.path.join(RAIZ, MANIFESTO)
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"\n  escrito: {MANIFESTO}")
    else:
        print("\n  (nada escrito — passe --escrever)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
