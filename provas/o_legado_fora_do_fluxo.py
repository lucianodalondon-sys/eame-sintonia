#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OS TREZE CORPOS QUE TEM BYTES E NAO TEM AQUISICAO PROVADA.

    python3 provas/o_legado_fora_do_fluxo.py

    DECIDE != IMPLEMENT

Esta prova mede e classifica. Nao recolhe, nao reingere, nao faz backfill,
nao escreve runtime, nao toca em banco e nao inventa identidade.

A PERGUNTA
----------
Existe um corpo no disco. A actividade que o adquiriu nao pode ser provada.
Que estado canonico e esse?

A HIERARQUIA DE EVIDENCIA, FIXADA ANTES DE MEDIR
-------------------------------------------------
    A · PROVA CANONICA        campo que a arquitectura reconhece
    B · PROVA EXTERNA         a fonte oficial, hoje, verificavel
    C · O DOCUMENTO DIZ       o proprio conteudo identifica quem publica
    D · PISTA HISTORICA       caminho, pasta, nome, convencao antiga
    E · AUSENCIA              nada prova

    `D` NUNCA PROMOVE IDENTIDADE SOZINHO.
    Um nome de pasta e arrumacao, e arrumacao nao e um campo.

E A DISTINCAO QUE DECIDE TUDO
------------------------------
    CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN

Um documento pode provar «fui publicado por X» sem provar «esta copia foi
adquirida de X por esta corrida». Sao dois factos e podem divergir.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
from coleta import ingresso as ing  # noqa: E402

MEDICAO = "data/derivados/SOURCE-ID-WIRING-GAP-V1.json"
LEDGER = "data/collection-ledger/italy/observations.ndjson"
CATALOGO = "system-map/data/sources.generated.json"
SAIDA = "data/derivados/OUT-OF-FLOW-LEGACY-DECISION-V1.json"

# ── AS CLASSES DE EVIDENCIA ───────────────────────────────────────────────
A_CANONICA = "A_PROVA_CANONICA"
B_EXTERNA = "B_PROVA_EXTERNA_INDEPENDENTE"
C_DOCUMENTO = "C_O_DOCUMENTO_SE_IDENTIFICA"
D_PISTA = "D_PISTA_HISTORICA"
E_AUSENCIA = "E_AUSENCIA"

# ── AS DISPOSICOES POSSIVEIS ──────────────────────────────────────────────
# ⚠️ NAO HA DONO PREVIO PARA ESTE VOCABULARIO. `raw_asset.identity_state`
# (migration 026) tem tres estados — LEGACY_PRE_IDEMPOTENCY,
# FORWARD_IDENTIFIED, FORWARD_IDENTITY_UNPROVEN — e os TRES pressupoem uma
# LINHA em `raw_asset`. Estes treze nao tem observacao nenhuma: nao estao no
# corte do legado, estao antes da porta.
#
#     UM ESTADO PARA LINHAS NAO CLASSIFICA QUEM NAO TEM LINHA.
LEGACY_KEEP = "LEGACY_KEEP_OUT_OF_FLOW"
RECOLLECT = "RECOLLECT_FROM_SOURCE"
EQUIVALENTE = "CANONICAL_EQUIVALENT_ALREADY_EXISTS"
IMPORT_HOJE = "LEGACY_IMPORT_WITH_CURRENT_PROVENANCE"
UNRESOLVED = "UNRESOLVED"

PADRAO_DE_FONTE = re.compile(r"(IT-T\d+-\d+)")


class MedicaoInvalida(Exception):
    pass


def _json(c):
    with open(os.path.join(RAIZ, c), encoding="utf-8") as f:
        return json.load(f)


def coorte():
    """Os treze, LIDOS da medicao anterior. Nunca reconstruidos."""
    d = _json(MEDICAO)
    fora = [x for x in d["ITEMS"]
            if x["ROOT_CAUSE"] == "OUT_OF_FLOW_EVIDENCE"]
    declarado = d["ROOT_CAUSES"]["OUT_OF_FLOW_EVIDENCE"]["QUANTOS"]
    if len(fora) != declarado:
        raise MedicaoInvalida("coorte %d != declarada %d"
                              % (len(fora), declarado))
    return sorted(fora, key=lambda x: x["ITEM_ID"])


def catalogo():
    return {s["source_id"]: s
            for s in _json(CATALOGO)["MASTER_ITALIANO"]}


def shas_canonicos():
    """Os bytes que JA tem observacao legitima no recibo da coleta."""
    fora = {}
    p = os.path.join(RAIZ, LEDGER)
    if not os.path.isfile(p):
        return fora
    with open(p, encoding="utf-8") as f:
        for linha in f:
            if not linha.strip():
                continue
            try:
                o = json.loads(linha)
            except json.JSONDecodeError:
                continue
            if o.get("RAW_SHA256"):
                fora.setdefault(o["RAW_SHA256"], []).append(o)
    return fora


def _texto(caminho, paginas=3):
    """As primeiras paginas, so para ver se o documento se identifica."""
    p = os.path.join(RAIZ, caminho)
    if caminho.lower().endswith(".pdf"):
        try:
            r = subprocess.run(["pdftotext", "-l", str(paginas), p, "-"],
                               capture_output=True, text=True, timeout=120)
            return r.stdout or ""
        except Exception:                                   # noqa: BLE001
            return ""
    with open(p, "rb") as f:
        return f.read(120000).decode("utf-8", "replace")


def _marcas_da_fonte(ficha):
    """Que palavras identificariam esta fonte dentro de um documento.

    Do CATALOGO, que e o dono de quem e cada fonte. Nao se inventam marcas.
    """
    marcas = set()
    dom = re.sub(r"^https?://(www\.)?", "", ficha.get("url") or "")
    dom = dom.split("/")[0].strip()
    if dom and "." in dom:
        marcas.add(dom.lower())
        marcas.add(dom.split(".")[0].lower())
    for campo in ("name", "owner"):
        v = (ficha.get(campo) or "").strip()
        for pedaco in re.split(r"[—–\-/(,]", v):
            pedaco = pedaco.strip().lower()
            # so pedacos com forma de NOME, e nao palavras comuns soltas
            if len(pedaco) >= 4 and not pedaco.startswith("nao sei"):
                marcas.add(pedaco)
    return {m for m in marcas if len(m) >= 4}


# ══════════════════════════════════════════════════════════════════════════
# 1 · A FICHA DE UM CORPO
# ══════════════════════════════════════════════════════════════════════════
def ficha(item, cat, canonicos, disponibilidade):
    caminho = item["PARENT_STORAGE_LOCATION"]
    absoluto = os.path.join(RAIZ, caminho)
    existe = os.path.isfile(absoluto)
    sha = None
    if existe:
        with open(absoluto, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()

    # D · a pista. Fica registada COMO PISTA, e o nome do campo di-lo.
    pista = item.get("O_CAMINHO_SUGERE")
    fonte_no_catalogo = cat.get(pista) if pista else None

    # C · o documento identifica-se?
    marcas, achadas = set(), []
    if existe and fonte_no_catalogo:
        marcas = _marcas_da_fonte(fonte_no_catalogo)
        texto = _texto(caminho).lower()
        achadas = sorted(m for m in marcas if m in texto)

    # A · prova canonica: ha observacao para ESTES bytes?
    obs = canonicos.get(sha or "", [])

    # B · prova externa: a fonte oficial responde HOJE?
    disp = disponibilidade.get(pista or "", {})

    # ⚠️ O DOCUMENTO PROVAR O PUBLICADOR NAO PROVA A AQUISICAO.
    # Sao dois factos, e o segundo e o que falta a todos os treze.
    conteudo_prova_publicador = bool(achadas)
    aquisicao_provada = bool(obs)

    return OrderedDict([
        ("ITEM", item["ITEM_ID"]),
        ("BODY_PATH", caminho),
        ("SHA256", sha),
        ("BODY_EXISTS", existe),
        ("BODY_FORMAT", (os.path.splitext(caminho)[1] or "SEM_EXTENSAO")
         .lstrip(".").upper()),
        ("BODY_BYTES", os.path.getsize(absoluto) if existe else 0),

        ("PATH_HINT", pista),
        ("PATH_HINT_CLASSE", D_PISTA),
        ("O_QUE_A_PISTA_NAO_E",
         "nao e SOURCE_ID provado; e o nome de um diretorio"),

        ("SOURCE_ID_PROVEN", None),
        ("SOURCE_ID_EVIDENCE", A_CANONICA if obs else E_AUSENCIA),

        ("DOCUMENT_ID_PROVEN", None),
        ("DOCUMENT_ID_EVIDENCE", E_AUSENCIA),

        ("ORIGINAL_URL_PROVEN", None),
        ("ORIGINAL_URL_EVIDENCE", E_AUSENCIA),

        ("CONTENT_PROVES_PUBLISHER", conteudo_prova_publicador),
        ("CONTENT_PROVES_PUBLISHER_EVIDENCE",
         C_DOCUMENTO if conteudo_prova_publicador else E_AUSENCIA),
        ("CONTENT_MARKS_FOUND", achadas),

        ("ACQUISITION_PROVENANCE_PROVEN", aquisicao_provada),
        ("ORIGINAL_ACQUISITION_EVENT_PROVEN", aquisicao_provada),
        ("ORIGINAL_RUN_PROVEN", aquisicao_provada),
        ("ORIGINAL_COLLECTED_AT_PROVEN", aquisicao_provada),
        ("ORIGINAL_ACTOR_PROVEN", aquisicao_provada),
        ("ORIGINAL_METHOD_PROVEN", aquisicao_provada),

        ("SAME_BYTES_EXIST_IN_CANONICAL_FLOW", bool(obs)),
        ("CANONICAL_RAW_OBSERVATION_ID",
         obs[0].get("DOCUMENT_VERSION_ID") if obs else None),

        ("OFFICIAL_SOURCE_STILL_AVAILABLE", disp.get("VEREDITO", "NAO SEI")),
        ("OFFICIAL_SOURCE_PROBE", disp),
        ("RECOLLECTION_POSSIBLE", None),      # preenchido a seguir
    ])


# ══════════════════════════════════════════════════════════════════════════
# 2 · RECOLHER E POSSIVEL?
# ══════════════════════════════════════════════════════════════════════════
def recoleta_possivel(f):
    """⚠️ O SITE RESPONDER NAO TORNA ESTE DOCUMENTO BUSCAVEL.

    Para voltar a buscar era preciso saber O QUE buscar: o endpoint deste
    documento. Ele viveria na observacao — e observacao e exactamente o que
    falta. O catalogo da a morada da FONTE, nao a deste ficheiro.

        SABER ONDE FICA A BIBLIOTECA
        NAO E SABER QUE LIVRO SE FOI LA BUSCAR.

    Por isso a resposta honesta e NAO SEI, e nao «sim, o site esta de pe».
    """
    if f["ORIGINAL_URL_PROVEN"]:
        return ("SIM" if f["OFFICIAL_SOURCE_STILL_AVAILABLE"] == "SIM"
                else "NAO SEI")
    return "NAO SEI"


# ══════════════════════════════════════════════════════════════════════════
# 3 · A DISPOSICAO
# ══════════════════════════════════════════════════════════════════════════
def dispor(f):
    """Uma disposicao por corpo, e cada uma com a prova que a sustenta."""
    if f["SAME_BYTES_EXIST_IN_CANONICAL_FLOW"]:
        # ⚠️ MESMOS BYTES NAO SAO A MESMA OBSERVACAO. A observacao legitima
        # serve a operacao; o corpo historico continua historico, e NAO herda
        # a identidade dela.
        return EQUIVALENTE, (
            "ha observacao canonica destes mesmos bytes. Ela e que serve a "
            "operacao. Este corpo fica historico e NAO recebe a identidade "
            "da outra: CONTENT_EQUIVALENCE != SAME_OBSERVATION.")
    if f["RECOLLECTION_POSSIBLE"] == "SIM":
        return RECOLLECT, (
            "o endpoint deste documento esta provado e a fonte responde: "
            "uma corrida nova pode fazer nascer a observacao que falta.")
    if not f["BODY_EXISTS"]:
        return UNRESOLVED, "o corpo nao esta no disco"
    return LEGACY_KEEP, (
        "o corpo existe e a aquisicao nao se prova. Preserva-se como "
        "evidencia historica e nao entra na Collection operacional. "
        "PRESERVAR != ADMITIR.")


# ══════════════════════════════════════════════════════════════════════════
# 4 · A SONDA EXTERNA — minima, so leitura, e com data
# ══════════════════════════════════════════════════════════════════════════
def sondar_fontes(pistas, cat, fazer=True):
    """A fonte oficial responde HOJE? Uma cabeca por FONTE, nao por ficheiro.

    ⚠️ ISTO MEDE O SITIO, E NAO O DOCUMENTO. Um 200 na pagina inicial diz que
    a instituicao vive; nao diz que o boletim de 2026 continua la.
    """
    fora = {}
    for p in sorted(pistas):
        s = cat.get(p) or {}
        url = s.get("url") or ""
        if not url or url in ing.NAO_E_AFIRMACAO or url == "NÃO SEI":
            fora[p] = {"VEREDITO": "NAO SEI",
                       "PORQUE": "o catalogo nao tem morada desta fonte"}
            continue
        if not fazer:
            fora[p] = {"VEREDITO": "NAO SEI", "PORQUE": "sonda desligada"}
            continue
        try:
            r = subprocess.run(
                ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
                 "-I", "-L", "--max-time", "25", url],
                capture_output=True, text=True, timeout=40)
            codigo = (r.stdout or "").strip()
        except Exception as e:                              # noqa: BLE001
            codigo, = ("ERRO:%s" % type(e).__name__,)
        ok = codigo[:1] == "2"
        fora[p] = {
            "URL": url, "HTTP": codigo,
            "VEREDITO": "SIM" if ok else "NAO SEI",
            "O_QUE_ISTO_NAO_PROVA": (
                "que ESTE documento continua buscavel. A sonda toca o sitio "
                "da fonte, e o documento tinha o seu proprio endereco — que "
                "viveria na observacao que falta."),
        }
    return fora


# ══════════════════════════════════════════════════════════════════════════
# 5 · RED TEAM
# ══════════════════════════════════════════════════════════════════════════
def red_team(fichas, canonicos):
    p = []

    def A(nome, achado, veredito):
        p.append({"PROVA": nome, "ACHADO": achado, "VEREDITO": veredito})

    A("1 · o caminho diz uma fonte e o conteudo nao a prova",
      "%d de %d tem pista de caminho; NENHUM recebeu SOURCE_ID_PROVEN."
      % (sum(1 for f in fichas if f["PATH_HINT"]), len(fichas)),
      "A PISTA NAO PROMOVE")

    com = [f for f in fichas if f["CONTENT_PROVES_PUBLISHER"]]
    A("2 · o conteudo prova o publicador e a aquisicao nao",
      "%d documentos identificam quem publica. Em TODOS, "
      "ACQUISITION_PROVENANCE_PROVEN = False." % len(com),
      "OS DOIS FACTOS FICAM SEPARADOS")

    A("3-4 · sha igual a item canonico / duas observacoes legitimas",
      "%d dos %d tem bytes iguais a uma observacao canonica. A disposicao "
      "EQUIVALENTE nunca copia identidade: o corpo historico continua "
      "historico."
      % (sum(1 for f in fichas
             if f["SAME_BYTES_EXIST_IN_CANONICAL_FLOW"]), len(fichas)),
      "CONTENT_EQUIVALENCE != SAME_OBSERVATION")

    A("5-6 · URL num comentario / logotipo no documento",
      "ORIGINAL_URL_PROVEN e None em %d de %d. Um logotipo e classe C e "
      "prova publicador, nunca aquisicao."
      % (sum(1 for f in fichas if f["ORIGINAL_URL_PROVEN"] is None),
         len(fichas)),
      "NAO DERRUBA")

    A("7 · a fonte oferece hoje um documento diferente com o mesmo titulo",
      "por isso RECOLLECTION_POSSIBLE exige ORIGINAL_URL_PROVEN e nao o "
      "titulo. Sem endpoint provado fica NAO SEI.",
      "GUARDADO")

    A("8 · o documento ja nao esta na origem",
      "a sonda mede o SITIO da fonte e di-lo por escrito. Nenhuma "
      "disposicao usa «o site responde» como prova sobre o ficheiro.",
      "GUARDADO")

    A("9-10 · a importacao de hoje tenta herdar COLLECTED_AT ou RUN antigos",
      "nenhuma ficha escreve COLLECTED_AT, RUN_ID ou ACTOR. Os cinco campos "
      "de aquisicao sao False em %d de %d."
      % (sum(1 for f in fichas
             if not f["ORIGINAL_COLLECTED_AT_PROVEN"]), len(fichas)),
      "NAO HA O QUE HERDAR")

    A("11 · fonte legitima mas METHOD/ACTOR ausentes",
      "ORIGINAL_METHOD_PROVEN e ORIGINAL_ACTOR_PROVEN sao medidos a parte "
      "de SOURCE_ID, exactamente para nao se cobrirem um ao outro.",
      "SEPARADOS")

    A("12 · a fonte e provavel, mas nao demonstravel",
      "e este o caso dos %d. «Provavel» nao tem campo nesta casa: ou ha "
      "prova, ou fica UNKNOWN." % len(fichas),
      "ACEITE — E E A RAZAO DA DISPOSICAO")
    return p


# ══════════════════════════════════════════════════════════════════════════
# 6 · O QUE O CONTRATO DE HOJE RESPONDE, E O QUE NAO RESPONDE
# ══════════════════════════════════════════════════════════════════════════
def contrato():
    return OrderedDict([
        ("EXISTING_CONTRACT_SUFFICIENT", "PARTIAL"),
        ("O_QUE_JA_TEM_DONO", [
            {"LEI": "COL-LAW-044",
             "RESPONDE": "onde esta != em que estado. O corpo pode viver em "
                         "`data/samples/` versionado e ter estado logico "
                         "proprio; QUARANTINED ja existe no vocabulario."},
            {"LEI": "COL-LAW-045",
             "RESPONDE": "coleta manual/assistida entra pelo MESMO contrato "
                         "de evidencia, preservando ACTOR_TYPE, ACTOR, "
                         "METHOD, SOURCE, RUN, ARTIFACT, PROVENANCE."},
            {"LEI": "COL-LAW-008",
             "RESPONDE": "copia orfa NAO DEVE existir: um derivado sem pai e "
                         "indistinguivel de um texto digitado."},
            {"LEI": "COL-LAW-006",
             "RESPONDE": "RAW primeiro, e o RAW nao se sobrescreve — o corpo "
                         "historico nao se apaga para arrumar o numero."},
        ]),
        ("A_PERGUNTA_QUE_NAO_TEM_DONO_HOJE", (
            "Qual e o estado canonico de um CORPO QUE EXISTE e cuja "
            "AQUISICAO nunca foi registada — isto e, que nunca teve "
            "observacao nenhuma?")),
        ("PORQUE_O_VOCABULARIO_ACTUAL_NAO_CHEGA", (
            "`raw_asset.identity_state` (migration 026) tem tres estados e "
            "os TRES pressupoem uma LINHA em `raw_asset`. "
            "LEGACY_PRE_IDEMPOTENCY e para observacoes que ja la estavam no "
            "corte; estes treze nao estao no corte, estao antes da porta. "
            "Um estado para linhas nao classifica quem nao tem linha."),),
        ("BIBLE_CHANGE_REQUIRED", "NO"),
        ("PORQUE_A_BIBLIA_NAO_MUDA", (
            "Nenhuma lei existente esta errada. COL-LAW-045 ja obriga a "
            "coleta manual a entrar pelo contrato; ela nao autoriza nem "
            "proibe o corpo que entrou ANTES dela existir. Falta um estado, "
            "e nao uma lei nova — e um estado que so se escreve depois de "
            "haver um dono para ele.")),
        ("CONTRACT_CHANGE_REQUIRED", "YES"),
        ("QUAL_CONTRATO", (
            "O contrato de estado do acervo precisa de um estado explicito "
            "para «corpo preservado, aquisicao nao provada, fora da "
            "Collection operacional». Hoje esse corpo nao e nada: nao e "
            "RAW admitido, nao e QUARANTINED por regra escrita, e nao e "
            "legado de idempotencia. Ele existe no disco e nao existe no "
            "vocabulario.")),
        ("O_QUE_ESTA_MISSAO_NAO_FAZ", (
            "Escrever esse estado. DECIDE != IMPLEMENT: quem o escreve "
            "decide onde ele vive, e isso e migration e contrato, nao uma "
            "prova de medicao.")),
    ])


def estudo_externo():
    """⚠️ NAO SE COPIA ARQUITECTURA DE FORA. Le-se o que ja foi resolvido."""
    return OrderedDict([
        ("PERGUNTA", (
            "Quando existe um corpo historico mas a actividade que o "
            "adquiriu nao pode ser provada, sistemas maduros preservam, "
            "promovem, reingerem, recolhem ou isolam?")),
        ("SISTEMAS", [
            {"NOME": "W3C PROV-DM",
             "FAMILIA": "modelo de proveniencia",
             "FONTE": "https://www.w3.org/TR/prov-dm/",
             "ACHADO": (
                 "uma entidade pode ser afirmada SEM `wasGeneratedBy`. A "
                 "atribuicao a um agente aplica-se «quando a actividade nao "
                 "e conhecida, ou e irrelevante». Ha marcador explicito "
                 "para actividade desconhecida, e proveniencia parcial e "
                 "valida.")},
            {"NOME": "Archivematica / pratica arquivistica",
             "FAMILIA": "preservacao digital",
             "FONTE": ("https://www.archivematica.org/en/docs/"
                       "archivematica-1.16/user-manual/transfer/transfer/"),
             "ACHADO": (
                 "material transferido pode ficar em BACKLOG: guardado, "
                 "sujeito a avaliacao, e EXPLICITAMENTE ainda nao um AIP. "
                 "Na descricao arquivistica, «immediate source of "
                 "acquisition» e obrigatorio e «custodial history» e "
                 "separado e opcional.")},
            {"NOME": "Apache Beam",
             "FAMILIA": "processamento de dados / streaming",
             "FONTE": ("https://beam.apache.org/documentation/"
                       "programming-guide/"),
             "ACHADO": (
                 "quando a fonte nao da tempo do evento, atribui-se um "
                 "sentinela (`Long.MIN_VALUE`) — nunca um valor inventado. "
                 "So se atribui tempo quando ele e extraivel do proprio "
                 "elemento.")},
        ]),
        ("CONVERGENCIA", [
            "preservar o corpo — nenhum manda apagar;",
            "registar honestamente o evento de custodia ACTUAL;",
            "nunca fabricar a aquisicao original;",
            "manter o desconhecido marcado como desconhecido, com campo "
            "proprio em vez de um valor plausivel.",
        ]),
        ("DIVERGENCIA", [
            "o arquivo ADMITE o objecto na coleccao com historia custodial "
            "desconhecida, porque a funcao dele E a custodia;",
            "o sistema de dados MANTEM-NO fora da semantica operacional, "
            "porque as contas a jusante dependem da proveniencia.",
        ]),
        ("O_QUE_ISTO_DECIDE_PARA_ESTA_CASA", (
            "A Collection nao e um arquivo de custodia: e uma cadeia de "
            "evidencia onde a decisao a jusante depende da origem. Por isso "
            "vale a postura dos dois lados — guardar o corpo como o arquivo "
            "guarda, e mante-lo fora da operacao como o sistema de dados "
            "mantem.")),
    ])


# ══════════════════════════════════════════════════════════════════════════
# 7 · O ARTEFATO
# ══════════════════════════════════════════════════════════════════════════
def medir(sondar=True):
    itens = coorte()
    cat = catalogo()
    canonicos = shas_canonicos()
    pistas = {x.get("O_CAMINHO_SUGERE") for x in itens if x.get("O_CAMINHO_SUGERE")}
    disp = sondar_fontes(pistas, cat, fazer=sondar)

    fichas = []
    for x in itens:
        f = ficha(x, cat, canonicos, disp)
        f["RECOLLECTION_POSSIBLE"] = recoleta_possivel(f)
        d, porque = dispor(f)
        f["DISPOSITION"] = d
        f["WHY"] = porque
        f["PROOF"] = OrderedDict([
            ("EVIDENCIA_MAIS_FORTE",
             A_CANONICA if f["SAME_BYTES_EXIST_IN_CANONICAL_FLOW"]
             else C_DOCUMENTO if f["CONTENT_PROVES_PUBLISHER"]
             else D_PISTA if f["PATH_HINT"] else E_AUSENCIA),
            ("AQUISICAO", "NAO PROVADA" if not
             f["ACQUISITION_PROVENANCE_PROVEN"] else "PROVADA"),
        ])
        fichas.append(f)

    contagem = Counter(f["DISPOSITION"] for f in fichas)
    return OrderedDict([
        ("SCHEMA", "sintonia.out-of-flow-legacy-decision/1"),
        ("O_QUE_ISTO_E", (
            "O tratamento canonico dos treze corpos historicos de T3 que tem "
            "bytes e nao tem observacao que prove a sua aquisicao.")),
        ("DECIDE_NOT_IMPLEMENT", (
            "Nada foi recolhido, reingerido nem corrigido. Sem backfill, sem "
            "migration, sem escrita em banco, sem alterar runtime.")),
        ("COHORT", OrderedDict([
            ("OUT_OF_FLOW_TOTAL", len(fichas)),
            ("FONTE_DA_COORTE", MEDICAO),
            ("NAO_RECONSTRUIDA", "lida do artefato, e conferida contra o "
                                 "numero que ele declara"),
        ])),
        ("HIERARQUIA_DE_EVIDENCIA", OrderedDict([
            (A_CANONICA, "campo que a arquitectura reconhece"),
            (B_EXTERNA, "a fonte oficial, hoje, verificavel"),
            (C_DOCUMENTO, "o proprio conteudo identifica quem publica"),
            (D_PISTA, "caminho, pasta, nome — NUNCA promove sozinho"),
            (E_AUSENCIA, "nada prova"),
        ])),
        ("A_DISTINCAO_QUE_DECIDE",
         "CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN"),
        ("SOURCE_PROOF", OrderedDict([
            ("PROVEN", sum(1 for f in fichas if f["SOURCE_ID_PROVEN"])),
            ("UNPROVEN", sum(1 for f in fichas if not f["SOURCE_ID_PROVEN"])),
        ])),
        ("ACQUISITION_PROVENANCE", OrderedDict([
            ("PROVEN", sum(1 for f in fichas
                           if f["ACQUISITION_PROVENANCE_PROVEN"])),
            ("UNPROVEN", sum(1 for f in fichas
                             if not f["ACQUISITION_PROVENANCE_PROVEN"])),
        ])),
        ("CANONICAL_EQUIVALENTS", sum(
            1 for f in fichas if f["SAME_BYTES_EXIST_IN_CANONICAL_FLOW"])),
        ("RECOLLECTION", dict(Counter(
            f["RECOLLECTION_POSSIBLE"] for f in fichas))),
        ("DISPOSITIONS", OrderedDict(
            (d, {"QUANTOS": n,
                 "ITENS": sorted(f["ITEM"] for f in fichas
                                 if f["DISPOSITION"] == d)})
            for d, n in contagem.most_common())),
        ("EXTERNAL_STUDY", estudo_externo()),
        ("CONTRATO", contrato()),
        ("RED_TEAM", red_team(fichas, canonicos)),
        ("PRESERVAR_NAO_E_ADMITIR", (
            "Nenhuma disposicao manda apagar corpo nenhum. Um objecto pode "
            "ser preservado e nao ser admissivel — sao duas perguntas.")),
        ("ITEMS", fichas),
        ("GENERATED_BY", "provas/o_legado_fora_do_fluxo.py"),
    ])


def main():
    sondar = "--sem-rede" not in sys.argv
    art = medir(sondar=sondar)
    caminho = os.path.join(RAIZ, SAIDA)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print("\n  O LEGADO FORA DO FLUXO — os treze")
    print("  " + "─" * 66)
    print("  aquisicao provada: %d · nao provada: %d"
          % (art["ACQUISITION_PROVENANCE"]["PROVEN"],
             art["ACQUISITION_PROVENANCE"]["UNPROVEN"]))
    print("  equivalente canonico: %d" % art["CANONICAL_EQUIVALENTS"])
    print("  recoleta: %s" % art["RECOLLECTION"])
    print("\n  DISPOSICOES")
    for d, x in art["DISPOSITIONS"].items():
        print("    %-38s %2d" % (d, x["QUANTOS"]))
    print("\n  O DOCUMENTO IDENTIFICA-SE?")
    com = [f for f in art["ITEMS"] if f["CONTENT_PROVES_PUBLISHER"]]
    print("    sim: %d · e em NENHUM isso prova a aquisicao" % len(com))
    c = art["CONTRATO"]
    print("\n  EXISTING_CONTRACT_SUFFICIENT = %s"
          % c["EXISTING_CONTRACT_SUFFICIENT"])
    print("  BIBLE_CHANGE_REQUIRED        = %s" % c["BIBLE_CHANGE_REQUIRED"])
    print("  CONTRACT_CHANGE_REQUIRED     = %s"
          % c["CONTRACT_CHANGE_REQUIRED"])
    print("\n  escrito: %s\n" % SAIDA)
    return 0


if __name__ == "__main__":
    sys.exit(main())
