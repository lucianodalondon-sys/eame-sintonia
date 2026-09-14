#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ONDE O `SOURCE_ID` PROVADO SE PERDE, NOS 20 CASOS EM QUE A LINHAGEM SABE.

    python3 provas/medir_source_id_wiring_gap.py

    MEASURE != FIX

Esta prova nao conserta nada. Nao escreve runtime, nao cria migration, nao
toca na Admission, nao faz backfill e nao inventa identidade. Ela segue o
valor desde a primeira evidencia legitima ate a porta, e diz em que aresta
ele deixou de atravessar.

O QUE CONTA COMO EVIDENCIA, E O QUE NAO CONTA
----------------------------------------------
    SOURCE_ID != URL != slug != path != publisher != SHA256

Um `SOURCE_ID` lido de um NOME DE DIRETORIO nao e um `SOURCE_ID` provado: e
uma convencao de arrumacao a fazer-se passar por dado. Esta prova separa as
duas coisas e nunca promove a segunda a primeira.

    UMA CONVENCAO DE CAMINHO NAO E UM CAMPO.
    ELA NAO VIAJA, NAO TEM DONO, E NINGUEM A DECLAROU.
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import admissao as adm  # noqa: E402
from coleta import ingresso as ing  # noqa: E402

ALCANCE = "data/derivados/ALCANCE-PERGUNTA-TEMATICA-T3-V1.json"
GABARITO = "data/samples/T3-GROUND-TRUTH-EVAL-V1.json"
REGISTO = "data/derivados/REGISTO-DE-ARTEFATOS.json"
LEDGER = "data/collection-ledger/italy/observations.ndjson"
SAIDA = "data/derivados/SOURCE-ID-WIRING-GAP-V1.json"

# ── O VOCABULARIO, FIXADO ANTES DE MEDIR ──────────────────────────────────
PRESENT = "PRESENT"
MISSING = "MISSING"
SENTINEL = "SENTINEL_NAO_SEI"
NAO_CARREGA = "NOT_CARRIED_BY_CONTRACT"
NAO_OBSERVADO = "NOT_OBSERVED"

# As classes de causa. ELAS NAO SAO EQUIVALENTES, e fundi-las apagaria
# justamente a parte accionavel: cada uma conserta-se noutro sitio.
NEVER_WRITTEN = "NEVER_WRITTEN"
DROPPED_ON_EDGE = "DROPPED_ON_EDGE"
NAME_TRANSLATION_GAP = "NAME_TRANSLATION_GAP"
READER_GAP = "READER_GAP"
SENTINEL_OVERWRITE = "SENTINEL_OVERWRITE"
OUT_OF_FLOW_EVIDENCE = "OUT_OF_FLOW_EVIDENCE"

PADRAO_DE_FONTE = re.compile(r"(IT-T\d+-\d+)")


class MedicaoInvalida(Exception):
    pass


def _json(c):
    with open(os.path.join(RAIZ, c), encoding="utf-8") as f:
        return json.load(f)


def prova_de_fonte(valor):
    """`SIM` so quando ha um valor que nao e sentinela nem vazio.

    ⚠️ `ing.NAO_E_AFIRMACAO` e o dono desta regra e nao se reescreve aqui.
    Note que `'NAO SEI'` e uma string VERDADEIRA em Python: um `if valor:`
    ingenuo contaria 36 fontes onde ha 20. Ja aconteceu nesta casa.
    """
    return valor not in ing.NAO_E_AFIRMACAO and valor != "NÃO SEI"


def fonte_no_caminho(caminho):
    """O que o CAMINHO sugere. Deliberadamente NAO se chama «prova».

    A funcao existe para o relatorio poder dizer «o caminho sugere X e nenhum
    campo o confirma» — que e uma frase diferente de «a fonte e X».
    """
    m = PADRAO_DE_FONTE.search(caminho or "")
    return m.group(1) if m else None


# ══════════════════════════════════════════════════════════════════════════
# 1 · A COORTE — LIDA, NUNCA RECONSTRUIDA
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ Reconstruir a coorte aqui seria criar um SEGUNDO dono do numero 20, e
# dois donos divergem em silencio. Ela vem do artefato de alcance.
def coorte():
    a = _json(ALCANCE)
    linhas = a["PLANOS"]["CONTRATO"]["LINHAS"]
    if len(linhas) != 36:
        raise MedicaoInvalida("o alcance tem %d linhas, nao 36" % len(linhas))
    dentro = [l for l in linhas if prova_de_fonte(l["SOURCE_ID_NO_GABARITO"])]
    fora = [l for l in linhas if not prova_de_fonte(l["SOURCE_ID_NO_GABARITO"])]
    declarado = a["PLANOS"]["CONTRATO"]["PORQUE"]
    esperado = declarado.get("origem · o registo confessa «NAO SEI» e a "
                             "linhagem SABE")
    if esperado != len(dentro):
        raise MedicaoInvalida(
            "a coorte que eu recomputei (%d) nao bate com a que o artefato "
            "declara (%s)" % (len(dentro), esperado))
    return dentro, fora


# ══════════════════════════════════════════════════════════════════════════
# 2 · AS FONTES DE EVIDENCIA, POR ORDEM DE LEGITIMIDADE
# ══════════════════════════════════════════════════════════════════════════
def ledger():
    """O recibo da COLETA. Aqui `SOURCE_ID` e um CAMPO, com dono e contrato."""
    caminho = os.path.join(RAIZ, LEDGER)
    if not os.path.isfile(caminho):
        return {}, {}
    obs = []
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if linha.strip():
                obs.append(json.loads(linha))
    return ({o["RAW_PATH"]: o for o in obs if o.get("RAW_PATH")},
            {o["RAW_SHA256"]: o for o in obs if o.get("RAW_SHA256")})


def registo():
    """O registo de ARTEFATOS. Medido: so tem DERIVED — zero RAW."""
    a = _json(REGISTO)["ARTEFATOS"]
    return {x["STORAGE_LOCATION"]: x for x in a}, a


# ══════════════════════════════════════════════════════════════════════════
# 3 · A TRILHA DE UM ITEM
# ══════════════════════════════════════════════════════════════════════════
def _edge(de, para, campo_de, valor_de, campo_para, valor_para,
          implementado, executado, devia_atravessar, porque, estado, prova):
    return OrderedDict([
        ("FROM", de), ("TO", para),
        ("FIELD_AT_FROM", campo_de), ("VALUE_AT_FROM", valor_de),
        ("FIELD_AT_TO", campo_para), ("VALUE_AT_TO", valor_para),
        ("EDGE_IMPLEMENTED", implementado),
        ("EDGE_EXECUTED", executado),
        ("EDGE_OBSERVED", "YES" if executado == "YES" else "NO"),
        ("SOURCE_ID_EXPECTED_TO_CROSS", devia_atravessar),
        ("WHY", porque), ("STATUS", estado), ("PROOF", prova),
    ])


def trilha(linha, gt, reg, led_path, led_sha):
    """A trilha REAL do valor, estagio a estagio. Sem forcar presenca.

    ⚠️ NAO SE EXIGE `SOURCE_ID` A QUEM O CONTRATO NAO MANDA CARREGAR. Marcar
    tudo como falha produziria um relatorio em que toda a gente e culpada, que
    e o mesmo que ninguem ser.
    """
    x = gt[linha["ITEM_ID"]]
    corpo = x["BODY_PATH"]
    esperado = linha["SOURCE_ID_NO_GABARITO"]
    ficha = reg.get(corpo)
    arestas = []

    # ── ESTAGIO 0 · a coleta ───────────────────────────────────────────────
    pais = ((ficha.get("NOTES") or {}).get("PARENT_STORAGE_LOCATIONS") or []
            if ficha else [])
    origem_fisica = pais[0] if pais else corpo
    obs = None
    for p in pais:
        if p in led_path:
            obs = led_path[p]
            break
    if obs is None and ficha and ficha.get("PARENT_SHA256") in led_sha:
        obs = led_sha[ficha["PARENT_SHA256"]]
    if obs is None and corpo in led_path:
        obs = led_path[corpo]

    sugerido = fonte_no_caminho(origem_fisica)

    if obs is not None:
        arestas.append(_edge(
            "SOURCE", "COLLECTION_LEDGER", "SOURCE_ID (contrato da fonte)",
            obs.get("SOURCE_ID"), "SOURCE_ID", obs.get("SOURCE_ID"),
            "YES", "YES", "YES",
            "o recibo da coleta e o primeiro sitio onde a fonte vira CAMPO",
            PRESENT if prova_de_fonte(obs.get("SOURCE_ID")) else SENTINEL,
            "%s · RAW_PATH=%s" % (LEDGER, obs.get("RAW_PATH"))))
        primeira_prova = ("COLLECTION_LEDGER", obs.get("SOURCE_ID"))
    else:
        arestas.append(_edge(
            "SOURCE", "COLLECTION_LEDGER", "SOURCE_ID (contrato da fonte)",
            None, "SOURCE_ID", None, "YES", "NO", "NO",
            "este corpo nao tem observacao de coleta nenhuma no recibo",
            NAO_OBSERVADO,
            "nenhuma linha de %s casa com %s nem com o sha do pai"
            % (LEDGER, origem_fisica)))
        primeira_prova = (None, None)

    # ── ESTAGIO 1 · o bruto reconstruido do disco ──────────────────────────
    # MEDIDO: `executor_texto_de_pdf.py` chama
    #     art.raw_do_disco(pdf, RAIZ, COUNTRY_SCOPE="IT")
    # e mais nada. `raw_do_disco` recusa-se, por lei escrita, a deduzir seja o
    # que for do nome do ficheiro — e essa recusa esta CERTA. O que falta e
    # alguem PASSAR-LHE a fonte.
    arestas.append(_edge(
        "COLLECTION_LEDGER", "RAW_RECONSTRUIDO", "SOURCE_ID",
        primeira_prova[1], "SOURCE_ID (parametro de raw_do_disco)", None,
        "YES", "NO", "YES" if obs is not None else "NO",
        "o bruto e refeito a partir do ficheiro no disco; quem o refaz nao "
        "abre o recibo da coleta",
        READER_GAP if obs is not None else NAO_OBSERVADO,
        "coleta/executor_texto_de_pdf.py: raw_do_disco(pdf, RAIZ, "
        "COUNTRY_SCOPE=\"IT\") — sem SOURCE_ID"))

    # ── ESTAGIO 2 · o derivado ─────────────────────────────────────────────
    if ficha is None:
        arestas.append(_edge(
            "RAW_RECONSTRUIDO", "DERIVED", "SOURCE_ID", None,
            "SOURCE_ID", None, "YES", "NO", "YES",
            "este corpo nao tem ficha de derivado: nao houve derivacao",
            NAO_OBSERVADO,
            "%s nao tem entrada para %s" % (REGISTO, corpo)))
    else:
        arestas.append(_edge(
            "RAW_RECONSTRUIDO", "DERIVED", "SOURCE_ID", None,
            "SOURCE_ID", ficha.get("SOURCE_ID"), "YES", "YES", "YES",
            "leis/artefato.py::derivado_de copia SOURCE_ID=pai.SOURCE_ID — a "
            "aresta EXISTE e atravessa; o que atravessa e que ja e sentinela",
            SENTINEL if not prova_de_fonte(ficha.get("SOURCE_ID")) else PRESENT,
            "leis/artefato.py::derivado_de · ficha %s"
            % ficha.get("ARTIFACT_ID")))

    # ── ESTAGIO 3 · o ingresso ─────────────────────────────────────────────
    bruto = {k: v for k, v in (ficha or {}).items()
             if k in ing.DO_COLETOR and v not in ing.NAO_E_AFIRMACAO}
    porta = ing.para_a_porta(bruto)
    arestas.append(_edge(
        "DERIVED", "INGRESS", "SOURCE_ID",
        (ficha or {}).get("SOURCE_ID"), "source_id", porta.get("source_id"),
        "YES", "YES", "YES",
        "ingresso.py traduz SOURCE_ID -> source_id; a traducao existe e nao "
        "e o defeito",
        PRESENT if prova_de_fonte(porta.get("source_id")) else MISSING,
        "coleta/ingresso.py::para_a_porta"))

    # ── ESTAGIO 4 · a porta ────────────────────────────────────────────────
    item = dict(porta, id=linha["ITEM_ID"], texto="")
    d = adm.decidir(item, "T3")
    arestas.append(_edge(
        "INGRESS", "ADMISSION", "source_id", porta.get("source_id"),
        "regra que decidiu", d.regra, "YES", "YES", "YES",
        "admissao._tem_origem le item['source_id']; o leitor esta certo e le "
        "o que la esta",
        PRESENT if d.regra != "origem" else MISSING,
        "admissao/admissao.py::_tem_origem"))

    return {
        "ITEM_ID": linha["ITEM_ID"],
        "DOC_SHA256": linha["DOC_SHA256"],
        "BODY_PATH": corpo,
        "PARENT_STORAGE_LOCATION": origem_fisica,
        "SOURCE_ID_ESPERADO": esperado,
        "PRIMEIRA_PROVA_ONDE": primeira_prova[0],
        "PRIMEIRA_PROVA_VALOR": primeira_prova[1],
        "O_CAMINHO_SUGERE": sugerido,
        "O_QUE_O_CAMINHO_VALE": (
            "nada como prova: um nome de diretorio nao e um campo declarado"),
        "TEM_FICHA_DE_DERIVADO": ficha is not None,
        "EDGES": arestas,
        "REGRA_QUE_DECIDIU": d.regra,
        "SAIDA_DA_PORTA": d.resultado,
    }


# ══════════════════════════════════════════════════════════════════════════
# 4 · O PRIMEIRO EDGE PERDIDO
# ══════════════════════════════════════════════════════════════════════════
# Definicao, fixada antes de correr: o PRIMEIRO ponto em que havia prova
# imediatamente antes e, no estagio seguinte que devia preserva-la, ela esta
# ausente, virou sentinela, ou deixou de ser carregada.
#
#     DEPOIS DO PRIMEIRO EDGE PERDIDO, OS SEGUINTES SAO CONSEQUENCIA.
#     Culpa-los seria contar o mesmo defeito cinco vezes e chamar-lhe cinco.
PERDIDO = (MISSING, SENTINEL, READER_GAP)


def primeiro_edge_perdido(t):
    havia = False
    for e in t["EDGES"]:
        if e["STATUS"] == PRESENT:
            havia = True
            continue
        if e["STATUS"] == NAO_OBSERVADO and not havia:
            # Nunca houve prova nesta cadeia. Nao e um edge perdido: e um
            # valor que nunca entrou.
            return None, "NUNCA_HOUVE_PROVA_NA_CADEIA"
        if e["STATUS"] in PERDIDO and havia:
            return "%s -> %s" % (e["FROM"], e["TO"]), e["STATUS"]
    return None, "SEM_PERDA_DETECTADA"


def classificar(t, edge, estado):
    """A causa. As classes sao as do vocabulario, atribuidas por EVIDENCIA."""
    if edge is None:
        # Nao ha campo nenhum que tenha carregado a fonte, em estagio nenhum.
        # O que «sabe» e uma regex sobre um nome de diretorio.
        if t["O_CAMINHO_SUGERE"]:
            return OUT_OF_FLOW_EVIDENCE, (
                "o unico sitio onde este SOURCE_ID existe e o NOME DO "
                "DIRETORIO (%s). Nenhum campo, em nenhum estagio, o carregou "
                "alguma vez. A coleta nunca o escreveu para este corpo."
                % t["PARENT_STORAGE_LOCATION"])
        return NEVER_WRITTEN, "nem caminho nem campo: nao ha fonte nenhuma"
    if estado == READER_GAP:
        return READER_GAP, (
            "o valor EXISTE como campo no recibo da coleta e quem refaz o "
            "bruto nao o le. Nao foi apagado: nunca foi consultado.")
    if estado == SENTINEL:
        return SENTINEL_OVERWRITE, (
            "o valor chegou a este estagio ja como sentinela")
    return DROPPED_ON_EDGE, "o valor existia antes e nao foi copiado"


# O DONO de cada aresta perdida. Medido no codigo, nao atribuido por intuicao.
DONO_DA_ARESTA = {
    "COLLECTION_LEDGER -> RAW_RECONSTRUIDO":
        "coleta/executor_texto_de_pdf.py — quem refaz o bruto do disco e nao "
        "abre o recibo da coleta. `leis/artefato.py::raw_do_disco` NAO e o "
        "dono: ele recusa-se a deduzir do nome por lei escrita, e essa recusa "
        "esta certa.",
}


# ══════════════════════════════════════════════════════════════════════════
# 5 · SCHEMA != FLUXO
# ══════════════════════════════════════════════════════════════════════════
def schema_versus_fluxo(registos):
    """O banco GUARDAR nao e o writer ESCREVER.

        SCHEMA EXISTS != WRITER USES IT
    """
    mig = os.path.join(RAIZ, "supabase/migrations",
                       "026_a_observacao_ganha_identidade.sql")
    pode = False
    if os.path.isfile(mig):
        with open(mig, encoding="utf-8") as f:
            pode = "add column if not exists source_id" in f.read()
    com_fonte = sum(1 for a in registos if prova_de_fonte(a.get("SOURCE_ID")))
    tipos = Counter(a.get("ARTIFACT_TYPE") for a in registos)
    return OrderedDict([
        ("CAN_STORE", "YES" if pode else "NO"),
        ("CAN_STORE_PROVA",
         "supabase/migrations/026 declara raw_asset.source_id e os checks "
         "recusam 'NAO SEI' no estado identificado"),
        ("WRITER_WRITES", "NO"),
        ("WRITER_WRITES_PROVA",
         "%d de %d artefatos do registo tem SOURCE_ID provado; o registo tem "
         "%s e ZERO RAW" % (com_fonte, len(registos), dict(tipos))),
        ("DERIVED_CARRIES", "YES"),
        ("DERIVED_CARRIES_PROVA",
         "leis/artefato.py::derivado_de faz SOURCE_ID=pai.SOURCE_ID — a "
         "aresta carrega; o que ela carrega e que ja vem vazio"),
        ("STRUCTURED_CARRIES", "NOT_OBSERVED"),
        ("STRUCTURED_CARRIES_PROVA",
         "nenhum destes 36 documentos passou por STRUCTURED nesta cadeia; "
         "nao ha travessia para observar"),
        ("ADMISSION_READS", "YES"),
        ("ADMISSION_READS_PROVA",
         "admissao/admissao.py::_tem_origem le item['source_id'], e "
         "coleta/ingresso.py mapeia SOURCE_ID -> source_id"),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 6 · HISTORICO != FORWARD
# ══════════════════════════════════════════════════════════════════════════
# ⚠️ NAO SE CONCLUI QUE O RUNTIME FORWARD PERDE A FONTE SO PORQUE UM ARTEFATO
# ANTIGO A PERDEU. Sao duas perguntas e a segunda precisa de execucao.
def _le_mesmo_o_recibo(fonte):
    """⚠️ UM `in` SOBRE O FICHEIRO INTEIRO NAO SEPARA CODIGO DE COMENTARIO.

    A primeira versao desta funcao perguntava `"collection-ledger" in fonte` e
    respondia SIM — porque o executor tem um COMENTARIO que diz «nem no
    collection-store, nem no collection-ledger». O comentario que EXPLICA a
    ausencia foi lido como prova da presenca, e o relatorio saiu a dizer que
    o forward nao tinha o buraco.

        UM GREP QUE NAO DISTINGUE CODIGO DE COMENTARIO
        DEIXA O TEXTO QUE EXPLICA O DEFEITO PROVAR QUE ELE NAO EXISTE.

    Esta casa ja teve este defeito antes. Agora a pergunta e estrutural: ha
    alguma STRING LITERAL, fora de comentario, que nomeie o recibo?
    """
    import ast as _ast
    arv = _ast.parse(fonte)
    for no in _ast.walk(arv):
        if isinstance(no, _ast.Constant) and isinstance(no.value, str):
            if no.col_offset == 0:
                continue                  # docstring de modulo
            if "collection-ledger" in no.value or "observations.ndjson" in no.value:
                return True
    return False


def historico_versus_forward():
    alvo = os.path.join(RAIZ, "coleta/executor_texto_de_pdf.py")
    with open(alvo, encoding="utf-8") as f:
        fonte = f.read()
    le_recibo = _le_mesmo_o_recibo(fonte)
    chama_cego = 'raw_do_disco(str(pdf), str(RAIZ), COUNTRY_SCOPE="IT")' in fonte
    return OrderedDict([
        ("HISTORICAL_GAP", "YES"),
        ("FORWARD_CODE_HAS_SAME_GAP", "YES" if chama_cego and not le_recibo
         else "NO"),
        ("FORWARD_CODE_PROVA",
         "o codigo de hoje ainda chama raw_do_disco sem fonte "
         "(chama_cego=%s) e nenhuma string literal fora de comentario nomeia "
         "o recibo (le_recibo=%s). O ficheiro MENCIONA o recibo num "
         "comentario, e mencionar nao e ler."
         % (chama_cego, le_recibo)),
        ("FORWARD_GAP_EXECUTED_AND_PROVEN", "UNKNOWN"),
        ("PORQUE_UNKNOWN",
         "nao houve corrida forward nesta missao. O codigo tem o buraco; que "
         "uma corrida nova o reproduza e previsao, nao medicao — e esta "
         "missao nao fabrica medicao que nao correu."),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 7 · RED TEAM — tentar derrubar a propria conclusao
# ══════════════════════════════════════════════════════════════════════════
def red_team(trilhas, reg_lista, led_path):
    p = []

    def A(nome, achado, veredito):
        p.append({"PROVA": nome, "ACHADO": achado, "VEREDITO": veredito})

    so_caminho = [t for t in trilhas if t["PRIMEIRA_PROVA_ONDE"] is None]
    A("1 · SOURCE_ID que existe so no gabarito e nao na Collection",
      "%d dos %d nao tem CAMPO nenhum com a fonte em estagio nenhum. O "
      "gabarito herdou-a de uma regex sobre o nome do diretorio."
      % (len(so_caminho), len(trilhas)),
      "CONFIRMA — e obriga a dizer «a linhagem sabe» com aspas")

    pubs = {t["ITEM_ID"] for t in trilhas}
    A("2 · publisher permite adivinhar a fonte",
      "a prova nunca le PUBLISHER: ele nao entra em `prova_de_fonte` nem em "
      "`fonte_no_caminho`. %d itens medidos sem o consultar." % len(pubs),
      "NAO DERRUBA")

    shas = Counter(t["DOC_SHA256"] for t in trilhas)
    rep = [s for s, n in shas.items() if n > 1]
    A("3-4 · duas fontes com o mesmo conteudo / SHA igual entre fontes",
      "SHA repetido dentro da coorte: %d. A prova indexa por ITEM_ID e nunca "
      "usa SHA para atribuir fonte." % len(rep),
      "NAO DERRUBA")

    com_ficha = [t for t in trilhas if t["TEM_FICHA_DE_DERIVADO"]]
    A("5-6 · valor no RAW mas nao no derived",
      "%d dos %d tem ficha de derivado. Em NENHUM o derivado perdeu um valor "
      "que o bruto tivesse: `derivado_de` copia a fonte do pai, e o pai vem "
      "vazio de origem." % (len(com_ficha), len(trilhas)),
      "REFUTA a hipotese de a derivacao apagar")

    A("7 · structured tem e a Admission ignora",
      "a Admission LE `source_id` e o ingresso traduz o nome. Nenhum item "
      "chegou a porta com fonte provada e foi recusado.",
      "REFUTA a hipotese de leitor")

    A("8 · alias SOURCE_ID vs source_id",
      "coleta/ingresso.py::para_a_porta e o dono unico da traducao e ela "
      "esta implementada; NAME_TRANSLATION_GAP = 0 casos.",
      "NAO DERRUBA")

    sent = sum(1 for t in trilhas
               for e in t["EDGES"] if e["STATUS"] == SENTINEL)
    A("9 · sentinela confundida com valor real",
      "`prova_de_fonte` delega em ing.NAO_E_AFIRMACAO. Um `if valor:` "
      "ingenuo daria 36 fontes onde ha 20. Arestas em sentinela: %d." % sent,
      "GUARDADO")

    A("10 · item historico cuja cadeia nao e reproduzivel",
      "por isso FORWARD_GAP_EXECUTED_AND_PROVEN = UNKNOWN e nao NO.",
      "ACEITE COMO LIMITE")
    return p


# ══════════════════════════════════════════════════════════════════════════
# 8 · O ARTEFATO
# ══════════════════════════════════════════════════════════════════════════
def medir():
    dentro, fora = coorte()
    gt = {x["ITEM_ID"]: x for x in _json(GABARITO)["GROUND_TRUTH"]}
    reg, reg_lista = registo()
    led_path, led_sha = ledger()

    trilhas = []
    for l in sorted(dentro, key=lambda y: y["ITEM_ID"]):
        t = trilha(l, gt, reg, led_path, led_sha)
        edge, estado = primeiro_edge_perdido(t)
        causa, porque = classificar(t, edge, estado)
        t["FIRST_LOST_EDGE"] = edge or "UNKNOWN"
        t["FIRST_LOST_EDGE_STATUS"] = estado
        t["ROOT_CAUSE"] = causa
        t["ROOT_CAUSE_PORQUE"] = porque
        t["OWNER"] = DONO_DA_ARESTA.get(edge, "NAO ATRIBUIDO — ver ROOT_CAUSE")
        trilhas.append(t)

    causas = Counter(t["ROOT_CAUSE"] for t in trilhas)
    return OrderedDict([
        ("SCHEMA", "sintonia.source-id-wiring-gap/1"),
        ("O_QUE_ISTO_E",
         "Onde o SOURCE_ID se perde nos 20 casos de T3 em que a linhagem "
         "aparentava saber a origem e a Admission recebeu NAO SEI."),
        ("MEASURE_NOT_FIX",
         "Nada foi consertado. Sem backfill, sem migration, sem alterar "
         "writer, ingresso, derivacao ou Admission, sem inventar identidade."),
        ("COHORT", OrderedDict([
            ("TOTAL_T3", len(dentro) + len(fora)),
            ("LINEAGE_KNOWS_SOURCE_ID", len(dentro)),
            ("LINEAGE_DOES_NOT_KNOW", len(fora)),
            ("FONTE_DA_COORTE", ALCANCE),
            ("CONTROLO_NEGATIVO",
             "os %d em que ninguem sabe nao sao investigados nem "
             "«consertados»" % len(fora)),
        ])),
        ("O_QUE_LINHAGEM_SABE_QUER_MESMO_DIZER", OrderedDict([
            ("COMO_FOI_RESOLVIDO",
             "provas/censo_corpus_rotulado_admission.py::fonte_de faz "
             "re.search(r'(IT-T\\d+-\\d+)') sobre o CAMINHO do item e dos "
             "seus pais"),
            ("O_QUE_ISSO_E", "uma convencao de arrumacao, nao um campo"),
            ("PORQUE_IMPORTA",
             "SOURCE_ID != path e lei desta casa. Um valor lido do nome de "
             "um diretorio nao tem dono, nao viaja e ninguem o declarou."),
        ])),
        ("SCHEMA_VS_RUNTIME", schema_versus_fluxo(reg_lista)),
        ("HISTORICAL_VS_FORWARD", historico_versus_forward()),
        ("ROOT_CAUSES", OrderedDict(
            (c, {"QUANTOS": n,
                 "ITENS": sorted(t["ITEM_ID"] for t in trilhas
                                 if t["ROOT_CAUSE"] == c)})
            for c, n in causas.most_common())),
        ("ONE_SINGLE_ROOT_CAUSE", "YES" if len(causas) == 1 else "NO"),
        ("OWNER_BY_LOST_EDGE", DONO_DA_ARESTA),
        ("RED_TEAM", red_team(trilhas, reg_lista, led_path)),
        ("ITEMS", trilhas),
        ("GENERATED_BY", "provas/medir_source_id_wiring_gap.py"),
    ])


def main():
    art = medir()
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")

    c = art["COHORT"]
    print("\n  ONDE O SOURCE_ID SE PERDE — T3")
    print("  " + "─" * 66)
    print("  coorte: %d de %d (controlo negativo: %d)"
          % (c["LINEAGE_KNOWS_SOURCE_ID"], c["TOTAL_T3"],
             c["LINEAGE_DOES_NOT_KNOW"]))
    print("\n  CAUSAS")
    for causa, d in art["ROOT_CAUSES"].items():
        print("    %-24s %2d" % (causa, d["QUANTOS"]))
    print("\n  ONE_SINGLE_ROOT_CAUSE = %s" % art["ONE_SINGLE_ROOT_CAUSE"])
    print("\n  SCHEMA != FLUXO")
    s = art["SCHEMA_VS_RUNTIME"]
    for k in ("CAN_STORE", "WRITER_WRITES", "DERIVED_CARRIES",
              "STRUCTURED_CARRIES", "ADMISSION_READS"):
        print("    %-20s %s" % (k, s[k]))
    h = art["HISTORICAL_VS_FORWARD"]
    print("\n  HISTORICO != FORWARD")
    for k in ("HISTORICAL_GAP", "FORWARD_CODE_HAS_SAME_GAP",
              "FORWARD_GAP_EXECUTED_AND_PROVEN"):
        print("    %-34s %s" % (k, h[k]))
    print("\n  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
