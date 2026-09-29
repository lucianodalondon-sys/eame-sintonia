#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O BOLETIM DO CAMPO — cultura, praga/doenca e fase lidas no texto de um boletim (T3 fitossanitario,
T2 agrometeo), cada uma com o TRECHO que a prova. EXTRATOR-EVENTO-V2 (D84, 26/09).

    ler_boletim(texto) -> {"SECOES": [...], "CULTURAS": [...], "PROBLEMAS": [...], "FASES": [...]}

POR QUE EXISTE. A ferramenta n.o 1 do casco (FINESTRE COLTURALI) precisa de cultura + problema + fase +
periodo no MESMO registo. Nos 94 itens da Sala, cultura e fase estavam NAO SEI em 94/94 — e o texto dos
boletins TEM as tres: «COLTURA … ACTINIDIA … Stadio fenologico … Ingrossamento frutto … CIMICE ASIATICA
(Halyomorpha halys); Non Presente» (IT-T3-002, Salerno). A porta so lia a cultura no titulo e na frase do
lugar (`admissao._cultura_fora_da_regua`), e a fase so pela regua T1.

O QUE ELE FAZ, E O QUE NAO FAZ
  · Um boletim fala de VARIAS culturas. Ler o texto inteiro como uma lista juntaria a praga do olivo com a
    fase da vite. Por isso parte-se o texto em SECOES, uma por cultura, pela linha que NOMEIA a cultura
    (cabecalho curto: «OLIVO», «Vite da vino», «COLTURA … ACTINIDIA»), e cada praga e fase fica na secao
    onde esta escrita. Texto antes da primeira cultura fica numa secao SEM cultura — nunca emprestada.
  · PRAGA MARCADA COMO AUSENTE NAO E OCORRENCIA. «Non presente», «assente», «nessuna segnalazione»,
    «non rilevat…» junto ao nome: ESTADO = AUSENTE. Sem marca: ESTADO = CITADA (o boletim fala dela; a
    frase nao diz se foi observada). So «presente», «rilevat…», «catture», «infestazion…», «sintomi» dao
    ESTADO = PRESENTE.
  · Nao normaliza (nao e EPPO nem BBCH): a FORMA e a do texto, em minusculas. So as formas da lista
    declarada MESMO_PROBLEMA (plural, nome cientifico entre parenteses) contam com um nome so.
  · Nao le datas: o periodo do boletim e do leitor do facto (`leis/fato_do_texto.py`, DA-6).
Funcao PURA: sem rede, sem banco, sem ficheiros.
"""
from __future__ import annotations

import re
import unicodedata

# ── MEMORIA DE LEITURA (D158) ────────────────────────────────────────────────
# `ler_afirmacao` releva o DOCUMENTO INTEIRO a cada trecho: `sem_vizinhos`, `secoes_
# territoriais` e `_titulo_do_documento` percorrem as 62 mil letras de um boletim de novo
# para cada frase. Com um trecho por frase (o produtor de afirmacoes, D158) isso passou a
# ser 318 leituras do mesmo texto: 38 segundos para UM item. As tres funcoes sao PURAS —
# mesmo texto, mesma resposta —, por isso guarda-se a ultima resposta de cada uma.
# Isto NAO muda nenhuma regra: muda quantas vezes a mesma regra corre.
MEMORIA_DE_LEITURA = 8          # quantas respostas ficam guardadas por funcao
_MEMORIA = {}


#: as respostas por LINHA sao muitas e pequenas; as por DOCUMENTO sao poucas e grandes
MEMORIA_POR_LINHA = 4000


def _com_memoria(fn=None, *, quantas=None):
    """A mesma funcao, a responder do que ja leu quando a pergunta e a mesma."""
    def _decorar(f):
        guardadas = _MEMORIA.setdefault(f.__name__, {})
        limite = quantas or MEMORIA_DE_LEITURA

        def _envolta(*args):
            if args in guardadas:
                r = guardadas[args]
            else:
                if len(guardadas) >= limite:
                    guardadas.clear()
                r = guardadas[args] = f(*args)
            return list(r) if isinstance(r, list) else r

        _envolta.__name__ = f.__name__
        _envolta.__doc__ = f.__doc__
        _envolta.sem_memoria = f
        return _envolta
    return _decorar(fn) if fn is not None else _decorar


# ── os vocabularios (declarados; medidos nos 5 T3 + 1 T2 da Sala e nos boletins do acervo) ─────────────
# A cultura: o vocabulario da regua T1 (`admissao.CULTURA_OBRIGATORIA["T1"]`, copiado por nome para esta
# funcao continuar pura) + as culturas que os boletins da Campania e da Puglia nomeiam e que a regua nao tem.
CULTURAS = (
    "vite", "vigneto", "uva da tavola", "uva da vino", "olivo", "oliveto", "melo", "pero", "pesco",
    "nettarina", "ciliegio", "actinidia", "kiwi", "albicocco", "susino", "castagno", "nocciolo", "noce",
    "mandorlo", "fico", "agrumi", "arancio", "limone", "mandarino", "clementine", "fragola", "frumento",
    "grano duro", "grano tenero", "orzo", "mais", "girasole", "soia", "barbabietola", "pomodoro", "patata",
    "carciofo", "melanzana", "peperone", "zucchina", "cetriolo", "lattuga", "cavolfiore", "cavolo",
    "finocchio", "cipolla", "aglio", "fagiolo", "fagiolino", "pisello", "cece", "tabacco", "melone",
    "anguria", "cocomero", "asparago", "sedano", "spinacio", "rucola", "mirtillo", "lampone", "mora",
)
# a forma plural / a outra forma que o texto usa, apontando para a forma do vocabulario
FORMAS = {"viti": "vite", "vigneti": "vigneto", "olive": "olivo", "ulivo": "olivo", "ulivi": "olivo",
          "olivi": "olivo", "oliveti": "oliveto", "mele": "melo", "pere": "pero", "pesche": "pesco",
          "nettarine": "nettarina", "ciliegie": "ciliegio", "albicocche": "albicocco", "susine": "susino",
          "castagne": "castagno", "nocciole": "nocciolo", "noci": "noce", "mandorle": "mandorlo",
          "fragole": "fragola", "pomodori": "pomodoro", "patate": "patata", "carciofi": "carciofo",
          "melanzane": "melanzana", "peperoni": "peperone", "zucchine": "zucchina", "cetrioli": "cetriolo",
          "cavoli": "cavolo", "finocchi": "finocchio", "cipolle": "cipolla", "fagioli": "fagiolo",
          "fagiolini": "fagiolino", "piselli": "pisello", "ceci": "cece", "meloni": "melone",
          "asparagi": "asparago", "mirtilli": "mirtillo", "lamponi": "lampone", "agrume": "agrumi"}

# Pragas e doencas: a lista T3 da regua (`admissao._do_universo["T3"]`: peronospora, oidio, botrite,
# ticchiolatura) + os nomes comuns que os boletins medidos escrevem. Raizes, palavra inteira a esquerda.
PROBLEMAS = (
    r"peronospor[ae]", r"oidio", r"mal\s+bianco", r"botrite", r"muffa\s+grigia", r"ticchiolatura",
    r"cimice\s+asiatica", r"cimic[ei]", r"halyomorpha\s+halys", r"mosca\s+dell['’\s]*oliv[ao]", r"mosca\s+delle\s+olive",
    r"mosca\s+della\s+frutta", r"mosca\s+mediterranea", r"ceratitis\s+capitata", r"bactrocera\s+oleae",
    r"tignol[ae](?:tta)?(?:\s+(?:della\s+vite|dell['’\s]*olivo|delle\s+olive|orientale))?", r"lobesia(?:\s+botrana)?",
    # BOLETIM-POR-SECAO (27/09): as pragas do olivo que o GOLD-FIXTURE-PUGLIA-V1 cita e o vocabulario nao tinha
    # (C05: «Presenza di mosca dell'olivo e margaronia» guardava so a mosca; C04/C01: prays, oziorrinco, rogna)
    r"margaronia", r"palpita\s+unionalis", r"prays\s+oleae", r"oziorrinc[oh]i?", r"otiorhynchus(?:\s+cribricollis)?",
    r"rogna",
    r"carpocapsa", r"cydia(?:\s+\w+)?", r"coccinigli[ae]", r"afid[ei]", r"pidocch\w*", r"ragnetto\s+rosso",
    r"tripid[ei]", r"psill[ae]", r"flavescenza\s+dorata", r"mal\s+secco", r"occhio\s+di\s+pavone",
    r"lebbra", r"monilia", r"corineo", r"bolla", r"cercospor\w*", r"septoria", r"ruggin[ei]", r"fusari\w*",
    r"alternari\w*", r"batterios[ie]", r"xylella(?:\s+fastidiosa)?", r"drosophila\s+suzukii",
    r"popillia\s+japonica", r"dorifor[ae]", r"elateridi", r"nottu[ae]", r"piralid[ei]", r"diabrotica",
    r"escoriosi", r"black\s*rot", r"marciume\s+(?!(?:del|della|dei|delle|degli|di|da)\b)\w+", r"virosi", r"virus", r"nematod[ie]",
)
# Fases / estadios, como os boletins os escrevem (o vocabulario T1 da regua + os medidos nos boletins).
FASES = (
    r"ripresa\s+vegetativa", r"riposo\s+vegetativo", r"gemm[ae]\s+(?:gonfi[ae]|cotonos[ae]|ferm[ae])",
    r"germogliamento", r"germogli\s+di\s+\d+", r"foglie\s+distese", r"prefioritura", r"inizio\s+fioritura",
    r"piena\s+fioritura", r"fine\s+fioritura", r"fioritura", r"mignolatura", r"allegagione",
    r"accrescimento\s+(?:frutti|frutto|acini|drupe)", r"ingrossamento\s+(?:frutti|frutto|acini|drupe)",
    r"chiusura\s+(?:del\s+)?grappolo", r"pre-?chiusura\s+grappolo", r"invaiatura", r"indurimento\s+(?:del\s+)?nocciolo",
    r"inolizione", r"maturazione", r"pre-?raccolta", r"raccolta", r"vendemmia", r"post-?raccolta",
    r"caduta\s+(?:delle\s+)?foglie", r"semina", r"emergenza", r"levata", r"spigatura", r"trapianto",
    r"bbch\s*\d{1,2}(?:\s*[-–]\s*\d{1,2})?",
)
# O MESMO PROBLEMA ESCRITO DE DUAS MANEIRAS conta UMA vez (EXTRATORES-V2-JUNTOS, 26/09). Medido na D84:
# «afide» e «afidi» no mesmo boletim contavam como dois problemas, e «CIMICE ASIATICA (Halyomorpha halys)»
# tambem. Juntam-se SO as formas desta lista declarada — singular/plural da mesma raiz e o nome cientifico que
# os boletins poem entre parenteses a seguir ao comum (e os dois nomes comuns italianos da mesma doenca). Nao e
# EPPO: o que nao esta aqui fica como o texto o escreve. A forma do texto continua guardada em FORMA.
MESMO_PROBLEMA = (
    (r"afid[ei]", "afide"), (r"cimic[ei]", "cimice"), (r"tripid[ei]", "tripide"), (r"psill[ae]", "psilla"),
    (r"ruggin[ei]", "ruggine"), (r"peronospor[ae]", "peronospora"), (r"nottu[ae]", "nottua"),
    (r"nematod[ie]", "nematode"), (r"batterios[ie]", "batteriosi"), (r"pidocch[io]o?", "pidocchio"),
    (r"tignol[ae]", "tignola"), (r"tignolett[ae]", "tignoletta"), (r"coccinigli[ae]", "cocciniglia"),
    (r"dorifor[ae]", "dorifora"), (r"piralid[ei]", "piralide"),
    (r"cercospor\w*", "cercosporiosi"),       # o fungo e a doenca (IT-T3-008 escreve as duas)
    (r"mosca dell['’ ]*oliv[ao]|mosca delle olive|bactrocera oleae", "mosca dell'olivo"),
    (r"halyomorpha halys", "cimice asiatica"),
    (r"lobesia botrana|lobesia|tignoletta della vite", "tignoletta della vite"),
    (r"ceratitis capitata|mosca mediterranea", "mosca della frutta"),
    (r"mal bianco", "oidio"), (r"muffa grigia", "botrite"),
    (r"xylella fastidiosa", "xylella"),
    (r"palpita unionalis|margaronia", "margaronia"),
    (r"prays oleae|tignola delle olive|tignola dell['’ ]*olivo", "tignola dell'olivo"),
    (r"otiorhynchus cribricollis|otiorhynchus|oziorrinc[oh]i?", "oziorrinco"),
)
_RE_MESMO = [(re.compile(r"^(?:%s)$" % r), n) for r, n in MESMO_PROBLEMA]


def nome_do_problema(forma: str) -> str:
    """O nome com que o problema conta (a forma do texto, ou a da lista MESMO_PROBLEMA)."""
    f = re.sub(r"\s+", " ", str(forma or "").strip().lower())
    return next((n for r, n in _RE_MESMO if r.match(f)), f)


_AUSENTE = re.compile(r"(?:non\s+presente|non\s+present[ei]|assent[ei]|nessun[ao]?\s+segnalazion[ei]|"
                      r"non\s+rilevat[oaie]|non\s+segnalat[oaie]|non\s+(?:si\s+)?riscontra\w*|non\s+riscontrat\w*|assenza|nulla|nessun[ao]?\s+(?:cattur[ae]|sintom[oi]))",
                      re.I)
_PRESENTE = re.compile(r"(?:(?<!non\s)present[ei]|(?<!non\s)rilevat[oaie]|(?<!non\s)segnalat[oaie]|cattur[ae]|"
                       r"infestazion[ei]|sintomi|focola[io]|attacch[io])", re.I)
JANELA_DO_ESTADO = 60          # letras depois do nome da praga onde se le «Non presente»

# a linha que NOMEIA uma cultura e abre a secao dela: curta, e a cultura e o essencial dela
PALAVRAS_DO_CABECALHO = 6


def _dobrar(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "")) if not unicodedata.combining(c)).lower()


_RE_CULTURA = re.compile(r"(?<![a-z])(%s)(?![a-z])" % "|".join(
    sorted([re.escape(c) for c in CULTURAS] + [re.escape(f) for f in FORMAS], key=len, reverse=True)))
_RE_PROBLEMA = re.compile(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(PROBLEMAS))
_RE_FASE = re.compile(r"(?<![a-z])(?:%s)(?![a-z])" % "|".join(FASES))


def _forma(c: str) -> str:
    c = re.sub(r"\s+", " ", c.strip())
    return FORMAS.get(c, c)


def _estado_da_praga(d: str, fim: int, linhas: list, n: int) -> str:
    """AUSENTE («non presente» logo depois do nome), PRESENTE ou CITADA. `d` e a linha n ja dobrada."""
    depois = d[fim:fim + JANELA_DO_ESTADO] + " " + " ".join(
        _dobrar(x) for x in linhas[n + 1:n + 3])[:JANELA_DO_ESTADO]
    return ("AUSENTE" if _AUSENTE.search(depois.split(".")[0][:JANELA_DO_ESTADO])
            else "PRESENTE" if _PRESENTE.search(d) else "CITADA")


def _trecho(linha: str, ini: int, fim: int, n: int = 90) -> str:
    return re.sub(r"\s+", " ", linha[max(0, ini - n):fim + n]).strip()


@_com_memoria(quantas=MEMORIA_POR_LINHA)
def _cabecalho_de_cultura(linha: str) -> str | None:
    """A cultura que esta linha NOMEIA como cabecalho de secao, ou None."""
    d = _dobrar(linha).strip(" •·-–:;")
    palavras = re.findall(r"[a-z']+", d)
    if not palavras or len(palavras) > PALAVRAS_DO_CABECALHO:
        return None
    m = _RE_CULTURA.search(d)
    if not m:
        return None
    # «MOSCA DELLE OLIVE» (IT-T3-010) e o nome de uma praga, nao o cabecalho do olivo: a praga le-se, e a
    # regra da praga com a cultura no nome manda-a para a secao do olivo
    if any(p.start() <= m.start() and m.end() <= p.end() for p in _RE_PROBLEMA.finditer(d)):
        return None
    # «COLTURA … ACTINIDIA», «OLIVO», «Vite da vino», «Pomodoro in serra»: a cultura e o essencial da linha
    return _forma(m.group(1))


def ler_boletim(texto: str) -> dict:
    texto = sem_vizinhos(texto)              # D19: menu, barra lateral e manchetes vizinhas saem ANTES
    linhas = [l for l in str(texto or "").splitlines()]
    secoes = [{"CULTURA": None, "LINHA": 0, "PROBLEMAS": [], "FASES": []}]
    for n, linha in enumerate(linhas):
        c = _cabecalho_de_cultura(linha)
        if c:
            if secoes[-1]["CULTURA"] == c:
                continue                     # a mesma cultura outra vez (IT-T3-010: «OLIVO» dez vezes): a mesma secao
            secoes.append({"CULTURA": c, "LINHA": n + 1, "TRECHO_DA_CULTURA": linha.strip()[:120],
                           "PROBLEMAS": [], "FASES": []})
            continue
        d = _dobrar(linha)
        s = secoes[-1]
        for m in _RE_PROBLEMA.finditer(d):
            forma = re.sub(r"\s+", " ", m.group(0))
            nome = nome_do_problema(forma)
            estado = _estado_da_praga(d, m.end(), linhas, n)
            # A PRAGA QUE TRAZ A CULTURA NO NOME diz sozinha de quem e: «tignoletta della vite», «mosca
            # dell'olivo». Medido no ARIF (IT-T3-008): sem linha curta da vite, a Lobesia ia para a secao do
            # olivo, que era a ultima aberta. Vai para a secao da cultura do nome (aberta se preciso).
            # A linha inteira segue: «Tignoletta della vite (Lobesia botrana)» — o nome cientifico entre
            # parenteses e da mesma praga, da mesma cultura.
            alvo = s
            mc = next((_RE_CULTURA.search(re.sub(r"\s+", " ", x.group(0))) for x in _RE_PROBLEMA.finditer(d)
                       if _RE_CULTURA.search(x.group(0))), None)
            if mc and _forma(mc.group(1)) != s["CULTURA"]:
                cult = _forma(mc.group(1))
                alvo = next((x for x in secoes if x["CULTURA"] == cult), None)
                if alvo is None:
                    alvo = {"CULTURA": cult, "LINHA": n + 1, "TRECHO_DA_CULTURA": "no nome da praga: «%s»" % nome,
                            "PROBLEMAS": [], "FASES": [], "SO_PELO_NOME_DA_PRAGA": True}
                    secoes.insert(len(secoes) - 1, alvo)
            if not any(p["NOME"] == nome and p["ESTADO"] == estado for p in alvo["PROBLEMAS"]):
                alvo["PROBLEMAS"].append({"NOME": nome, "FORMA": forma, "ESTADO": estado,
                                          "TRECHO": _trecho(linha, m.start(), m.end())})
        for m in _RE_FASE.finditer(d):
            nome = re.sub(r"\s+", " ", m.group(0))
            if not any(f["NOME"] == nome for f in s["FASES"]):
                s["FASES"].append({"NOME": nome, "TRECHO": _trecho(linha, m.start(), m.end())})
    secoes = [s for s in secoes if s["CULTURA"] or s["PROBLEMAS"] or s["FASES"]]

    def _unicos(chave, campo):
        vistos = []
        for s in secoes:
            for x in s[chave]:
                if x[campo] not in vistos:
                    vistos.append(x[campo])
        return vistos
    return {"SECOES": secoes,
            "CULTURAS": [s["CULTURA"] for s in secoes if s["CULTURA"]],
            "PROBLEMAS": _unicos("PROBLEMAS", "NOME"),
            "PROBLEMAS_NAO_AUSENTES": sorted({p["NOME"] for s in secoes for p in s["PROBLEMAS"]
                                             if p["ESTADO"] != "AUSENTE"}),
            "FASES": _unicos("FASES", "NOME"),
            # D18: as secoes TERRITORIAIS escritas no texto. As listas de cima sao do DOCUMENTO (a chave da
            # porta); a afirmacao le a SUA secao em `ler_afirmacao`, nunca estas listas.
            "TERRITORIOS": [{"CABECALHO": s["CABECALHO"], "VALOR": s["VALOR"], "LOCATION_SOURCE": SECTION_HEADER}
                            for s in secoes_territoriais(texto)],
            "LEI": ("praga «non presente» e AUSENTE, nunca ocorrencia; cada praga e fase fica na secao da "
                    "cultura onde esta escrita; texto antes da 1.a cultura nao herda cultura")}


# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# D18 · BOLETIM-POR-SECAO (27/09) — cada AFIRMACAO herda cultura, praga e lugar da SUA secao, com a proveniencia
# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# Achado pela Intelligence R6: um boletim regional (ARIF Puglia, secoes por provincia; A.P.OL., secoes
# «COMPRENSORIO - BR - COLLINA LITORANEA»…) mistura culturas, pragas e territorios, e as fichas saiam com a
# cultura/praga/lugar do DOCUMENTO. `ler_boletim` ja partia por secao de CULTURA; faltava (1) a secao
# TERRITORIAL escrita no texto e (2) ler UMA afirmacao (um trecho) dizendo DE ONDE veio cada entidade.
# As regras sao as do dono (D112, docs/iab/puglia/DECISAO-D112.md) e os casos do GOLD-FIXTURE-PUGLIA-V1:
#
#   ENTITY_SOURCE (praga e cultura), por esta ordem — a 1.a que der, da:
#     SPAN               o nome esta DENTRO do trecho (C01, C03, C05 — as duas pragas, nenhuma a menos)
#     SECTION_TITLE      o titulo da secao que governa o trecho: marcador «• Mosca delle olive (…)» (C09 SA-32)
#                        ou linha curta que nomeia a cultura («COLTURA OLIVO», «OLIVO») dentro da secao
#     DOCUMENT_TITLE     o titulo do documento (o dado `titulo`, ou a linha de titulo repetida no topo de cada
#                        pagina — «MOSCA DELLE OLIVE» na A.P.OL.: C02, C08)
#     PARAGRAPH_CONTEXT  a frase ANTERIOR e o comeco da propria frase, SEM troca de secao/rotulo/paragrafo
#                        pelo meio, e com UM so nome (C09 SA-03)
#     UNKNOWN            nada disto; OU um nome concorrente (titulo diz A, o paragrafo diz B); OU o unico nome
#                        esta do outro lado de uma troca de secao («… Prays Oleae). Programma di Difesa: <trecho>»,
#                        C04). Nunca conhecimento agronomico de fora.
#   LOCATION_SOURCE:
#     TEXT                     o lugar esta escrito no trecho. Nome resolvido («zona costiera del Gargano», C04)
#                              -> FACT_LOCATION; expressao sem nome («zone irrigue costiere di tutti comprensori»,
#                              C08) -> UNRESOLVED, guardada em LOCATION_EXPRESSION_RAW, e SEM ponto no mapa
#     SECTION_HEADER           o cabecalho territorial ESCRITO NO TEXTO da secao do trecho (C02, C03, C07)
#     VISUAL_HEADER_CANDIDATE  o cabecalho so existe na IMAGEM da pagina: fica CANDIDATO, NUNCA FACT_LOCATION
#                              (C01, C05, C06). Cabecalho de EXCLUSAO no texto («TERRITORIO ESCLUSO GARGANO»)
#                              nao nomeia o lugar: fica como expressao, UNRESOLVED
#     UNRESOLVED               nada disto
#   O MESMO trecho repetido em N secoes do MESMO documento = N APLICACOES territoriais, 1 instituicao (C07).
#   O VOCABULARIO NAO MORA AQUI (LOTE6-INTEGRA): ENTITY_SOURCES e dono `leis/afirmacao_da_fonte.py` (COL-LAW-221)
#   e LOCATION_SOURCES e dono `leis/lugar_do_fato.py` (COL-LAW-032). Este extrator le-os de la e, se usar uma
#   palavra que a lei nao tem, nem carrega. E cada leitura passa pelas TRAVAS da lei antes de sair
#   (`_trava_da_entidade`, `_trava_do_lugar`): o extrator propoe, a lei decide.
def _leis():
    import os
    import sys
    aqui = os.path.dirname(os.path.abspath(__file__))
    if aqui not in sys.path:
        sys.path.insert(0, aqui)
    import afirmacao_da_fonte as AF     # noqa: PLC0415
    import lugar_do_fato as LF          # noqa: PLC0415
    return AF, LF


AF, LF = _leis()
ENTITY_SOURCES = AF.ENTITY_SOURCES
LOCATION_SOURCES = LF.LOCATION_SOURCES
SPAN, PARAGRAPH_CONTEXT, SECTION_TITLE, DOCUMENT_TITLE, UNKNOWN = (
    "SPAN", "PARAGRAPH_CONTEXT", "SECTION_TITLE", "DOCUMENT_TITLE", "UNKNOWN")
TEXT, SECTION_HEADER, VISUAL_HEADER_CANDIDATE, UNRESOLVED = (
    "TEXT", "SECTION_HEADER", "VISUAL_HEADER_CANDIDATE", LF.UNRESOLVED)
if {SPAN, PARAGRAPH_CONTEXT, SECTION_TITLE, DOCUMENT_TITLE, UNKNOWN} != set(ENTITY_SOURCES):
    raise ImportError("boletim_do_campo usa ENTITY_SOURCE fora da COL-LAW-221: %s" % (ENTITY_SOURCES,))
if {TEXT, SECTION_HEADER, VISUAL_HEADER_CANDIDATE, UNRESOLVED} != set(LOCATION_SOURCES):
    raise ImportError("boletim_do_campo usa LOCATION_SOURCE fora da COL-LAW-032: %s" % (LOCATION_SOURCES,))

# o cabecalho TERRITORIAL escrito no texto: linha curta, em MAIUSCULAS, que comeca pela palavra de territorio
PALAVRAS_DO_CABECALHO_TERRITORIAL = 8
_RE_CABECALHO_TERRITORIAL = re.compile(
    r"^\s*(COMPRENSORIO|TERRITORIO|PROVINCIA|FITOPATOLOGIA|DISTRETTO|ZONA|AREA)\b[\s\-–:]*(.*)$")
_RE_COMPRENSORIO = re.compile(r"^COMPRENSORIO\s*[-–]\s*([A-Z]{2})\s*[-–]\s*(.+)$")
_RE_EXCLUSAO = re.compile(r"\b(?:ESCLUS[OAIE]|ECCETTO|TRANNE|ESCLUDENDO|FUORI)\b")
# o que FECHA a secao territorial: rodape institucional, quebra de pagina, «Pag. N»
_RE_FIM_DE_PAGINA = re.compile(r"^\s*(?:\f|pag\.?\s*\d+\s*$)", re.I)
# o que corta o PARAGRAFO: linha em branco, marcador, rotulo curto com dois pontos («Programma di Difesa:»)
_RE_ROTULO = re.compile(r"(?:^|(?<=[.;!?])\s+|\n)\s*[A-ZÀ-Ý][A-Za-zà-ÿ']*(?:\s+[A-Za-zà-ÿ']+){0,3}\s*:(?=\s)")
_RE_CORTE_DE_PARAGRAFO = re.compile(r"\n\s*\n|•")
_RE_FIM_DE_FRASE = re.compile(r"[.!?;](?=\s)")
# a expressao de lugar escrita no trecho: «zona/zone/fascia» + ate 7 palavras
_RE_ZONA = re.compile(r"(?<![A-Za-zà-ÿ])(zon[ae]|fascia|fasce)\s+((?:[A-Za-zà-ÿ'’]+\s*){1,8})")
_PARA_A_ZONA = {"si", "e", "ed", "con", "su", "per", "che", "dove", "sono", "è", "ad", "a", "o", "oppure",
                "mentre", "quando", "anche", "nei", "negli", "nelle", "in"}
# a linha de rodape que fecha a secao e CURTA (a morada, o telefone); uma linha longa com «Tel.» no meio e corpo
PALAVRAS_DO_RODAPE = 20
JANELA_DO_OUTRO_LADO = 400      # letras antes do corte onde se procuram os nomes «do outro lado» (so p/ o MOTIVO)


@_com_memoria
def sem_vizinhos(texto: str) -> str:
    """`fato_do_texto.sem_vizinhos` (D19), com memoria de leitura. A regra e a do dono."""
    return _ft().sem_vizinhos(texto)


def _ft():
    """`leis/fato_do_texto.py` — dono de `sem_vizinhos` (D19) e do RODAPE; importado so quando preciso."""
    import os
    import sys
    aqui = os.path.dirname(os.path.abspath(__file__))
    if aqui not in sys.path:
        sys.path.insert(0, aqui)
    import fato_do_texto as FT          # noqa: PLC0415
    return FT


def _linhas_com_posicao(texto: str):
    pos = 0
    for linha in texto.splitlines(keepends=True):
        yield pos, linha.rstrip("\r\n")
        pos += len(linha)


def _e_maiuscula(l: str) -> bool:
    letras = [c for c in l if c.isalpha()]
    return bool(letras) and sum(c.isupper() for c in letras) >= 0.8 * len(letras)


def ler_cabecalho_territorial(cabecalho: str) -> dict:
    """O que um cabecalho territorial ESCRITO diz: o lugar (se nomeia um) ou UNRESOLVED com o porque."""
    c = re.sub(r"\s+", " ", str(cabecalho or "")).strip()
    base = {"CABECALHO": c}
    m = _RE_COMPRENSORIO.match(c)
    if m:
        return dict(base, VALOR="%s (%s)" % (m.group(2).strip().title(), m.group(1)),
                    PRECISAO="ZONA_DEFINIDA_PELA_FONTE")
    if _RE_EXCLUSAO.search(c):
        return dict(base, VALOR=UNRESOLVED,
                    PORQUE="cabecalho de EXCLUSAO («%s»): diz o que fica de fora, nao nomeia o lugar" % c)
    m = _RE_CABECALHO_TERRITORIAL.match(c)
    resto = (m.group(2) if m else "").strip(" -–:")
    resto = re.sub(r"^(?:DI|DEL|DELLA|DELLE|DEI)\s+", "", resto)
    if not resto:
        return dict(base, VALOR=UNRESOLVED, PORQUE="cabecalho sem nome de lugar")
    return dict(base, VALOR=resto.title(), PRECISAO="ZONA_DEFINIDA_PELA_FONTE")


@_com_memoria
def secoes_territoriais(texto: str) -> list:
    """As secoes TERRITORIAIS escritas no texto: [{"INICIO", "FIM", "CABECALHO", "VALOR", ...}].
    Um cabecalho que so existe na imagem da pagina NAO aparece aqui — e isso e a lei, nao uma falta."""
    t = str(texto or "")
    rodape = _ft().RODAPE
    linhas = list(_linhas_com_posicao(t))
    secoes, aberta = [], None
    for i, (pos, l) in enumerate(linhas):
        s = l.strip()
        if not s:
            continue
        if aberta and (_RE_FIM_DE_PAGINA.match(l) or (rodape.search(s) and len(s.split()) <= PALAVRAS_DO_RODAPE)):
            aberta["FIM"] = pos
            aberta = None
            continue
        if (_RE_CABECALHO_TERRITORIAL.match(s) and _e_maiuscula(s) and not s.endswith(".")
                and len(re.findall(r"[A-Za-zÀ-ÿ']+", s)) <= PALAVRAS_DO_CABECALHO_TERRITORIAL):
            cab = s
            # «COMPRENSORIO - LE - PIANURA» + «SALENTINA SUD»: o nome partido na linha seguinte (ate 3 palavras)
            prox = next((x for _, x in linhas[i + 1:] if x.strip()), "")
            if (_RE_COMPRENSORIO.match(cab) and _e_maiuscula(prox) and not re.search(r"\d", prox)
                    and len(prox.split()) <= 3 and not _RE_CABECALHO_TERRITORIAL.match(prox.strip())):
                cab = cab + " " + prox.strip()
            if aberta:
                aberta["FIM"] = pos
            aberta = dict(ler_cabecalho_territorial(cab), INICIO=pos, FIM=len(t))
            secoes.append(aberta)
    return secoes


@_com_memoria
def _titulo_do_documento(texto: str, titulo: str | None) -> list:
    """Os titulos do documento: o dado + a linha curta de titulo REPETIDA (o topo de cada pagina)."""
    fora = []
    if titulo and str(titulo).strip():
        fora.append(str(titulo).strip())
    contagem = {}
    for _, l in _linhas_com_posicao(str(texto or "")):
        s = l.strip()
        if s and len(re.findall(r"[a-z']+", _dobrar(s))) <= PALAVRAS_DO_CABECALHO and not re.search(r"\d", s):
            contagem[s] = contagem.get(s, 0) + 1
    for s, n in contagem.items():
        if n >= 2 and (_RE_PROBLEMA.search(_dobrar(s)) or _RE_CULTURA.search(_dobrar(s))) and s not in fora:
            fora.append(s)
    return fora


def _pragas_em(trecho: str) -> list:
    d = _dobrar(trecho)
    vistos = []
    for m in _RE_PROBLEMA.finditer(d):
        n = nome_do_problema(re.sub(r"\s+", " ", m.group(0)))
        if n not in vistos:
            vistos.append(n)
    return vistos


def _culturas_em(trecho: str) -> list:
    """A cultura escrita, OU a que vem no nome da praga escrita («mosca dell'olivo» -> olivo)."""
    d = _dobrar(trecho)
    vistos = []
    tapado = d
    for m in _RE_PROBLEMA.finditer(d):
        mc = _RE_CULTURA.search(nome_do_problema(re.sub(r"\s+", " ", m.group(0))))
        if mc and _forma(mc.group(1)) not in vistos:
            vistos.append(_forma(mc.group(1)))
        tapado = tapado[:m.start()] + " " * (m.end() - m.start()) + tapado[m.end():]
    for m in _RE_CULTURA.finditer(tapado):
        if _forma(m.group(1)) not in vistos:
            vistos.append(_forma(m.group(1)))
    return vistos


def _janela_do_paragrafo(t: str, ini_secao: int, inicio: int) -> tuple:
    """(comeco, corte): o PARAGRAPH_CONTEXT e t[comeco:inicio] — a frase anterior e o comeco da propria —
    e `corte` e onde a secao/rotulo/paragrafo mudou (None se a janela chegou a frase anterior sem corte)."""
    antes = t[ini_secao:inicio]
    corte = None
    for rx in (_RE_CORTE_DE_PARAGRAFO, _RE_ROTULO):
        for m in rx.finditer(antes):
            corte = max(corte or 0, m.end())
    base = corte or 0
    pedaco = antes[base:]
    # os comecos de frase; o ultimo e o da PROPRIA frase do trecho (vazia se o trecho abre a frase), o penultimo
    # e o da frase anterior — a janela vai dali ate ao trecho
    comecos = [0] + [m.end() for m in _RE_FIM_DE_FRASE.finditer(pedaco)]
    comeco = comecos[-2] if len(comecos) >= 2 else 0
    # a janela so atravessa ate ao corte; se o corte cai dentro da frase anterior, fica ali
    return ini_secao + base + comeco, (ini_secao + corte) if corte is not None else None


def _titulo_da_secao(t: str, ini: int, inicio: int) -> list:
    """Os titulos que governam o trecho DENTRO da secao: o marcador «• <praga>» do bloco onde o trecho esta,
    e a linha curta que nomeia a cultura entre o comeco da secao e o trecho."""
    fora = []
    antes = t[ini:inicio]
    b = antes.rfind("•")
    if b >= 0 and "\n\n" not in antes[b:]:
        cabeca = antes[b + 1:b + 1 + 80]
        m = _RE_PROBLEMA.search(_dobrar(cabeca))
        if m and m.start() <= 3:
            fim = cabeca.find(")", m.end()) + 1 if cabeca[m.end():m.end() + 3].lstrip().startswith("(") else m.end()
            fora.append(re.sub(r"\s+", " ", cabeca[:max(fim, m.end())]).strip())
    for _, l in _linhas_com_posicao(antes):
        c = _cabecalho_de_cultura(l)
        if c:
            fora.append(l.strip())
    return fora


# O LUGAR DA CULTURA NAO E OUTRA CULTURA: «oliveto» (o campo) e «olivo» (a planta) sao a mesma cultura, e o
# paragrafo que fala do oliveto nao concorre com o titulo «MOSCA DELLE OLIVE» (C02). So estes pares, declarados.
MESMA_CULTURA = {"oliveto": "olivo", "vigneto": "vite", "uva da tavola": "vite", "uva da vino": "vite"}


def _familia(nome: str) -> str:
    return MESMA_CULTURA.get(nome, nome)


def _resolver(no_trecho, titulos_da_secao, titulos_do_doc, no_paragrafo, do_outro_lado, corte_txt, ler):
    """A escada da ENTITY_SOURCE (ver o topo desta parte). `ler` extrai os nomes de um texto."""
    if no_trecho:
        return {"VALOR": no_trecho, "ENTITY_SOURCE": SPAN, "PROVA": "no trecho"}
    par = ler(no_paragrafo) if no_paragrafo else []
    for fonte, titulos in ((SECTION_TITLE, titulos_da_secao), (DOCUMENT_TITLE, titulos_do_doc)):
        nomes = []
        for tt in titulos:
            nomes += [n for n in ler(tt) if n not in nomes]
        if nomes:
            concorrentes = [n for n in par if _familia(n) not in {_familia(x) for x in nomes}]
            if concorrentes:
                return {"VALOR": UNKNOWN, "ENTITY_SOURCE": UNKNOWN,
                        "MOTIVO": "entidade concorrente: o titulo diz %s e o paragrafo diz %s"
                                  % (nomes, concorrentes)}
            return {"VALOR": nomes, "ENTITY_SOURCE": fonte,
                    "PROVA": " ; ".join("«%s»" % tt for tt in titulos if ler(tt))}
    if len({_familia(n) for n in par}) == 1:
        return {"VALOR": par, "ENTITY_SOURCE": PARAGRAPH_CONTEXT,
                "PROVA": "«%s»" % re.sub(r"\s+", " ", no_paragrafo).strip()[-200:]}
    if par:
        return {"VALOR": UNKNOWN, "ENTITY_SOURCE": UNKNOWN,
                "MOTIVO": "entidades concorrentes no paragrafo: %s" % par}
    if do_outro_lado:
        return {"VALOR": UNKNOWN, "ENTITY_SOURCE": UNKNOWN,
                "MOTIVO": "troca de secao entre o nome e o trecho («%s»): %s ficam do outro lado"
                          % (corte_txt, do_outro_lado)}
    return {"VALOR": UNKNOWN, "ENTITY_SOURCE": UNKNOWN, "MOTIVO": "nenhum nome no trecho, na secao nem no titulo"}


def _lugar_no_trecho(trecho: str):
    """O lugar ESCRITO no trecho: a expressao de zona e/ou o nome do gazetteer (`fato_local.mencoes`)."""
    FL = _ft().FL
    for m in _RE_ZONA.finditer(trecho):
        palavras = []
        for w in re.findall(r"[A-Za-zà-ÿ'’]+", m.group(2)):
            if w.lower() in _PARA_A_ZONA:
                break
            palavras.append(w)
        if not palavras:
            continue
        expr = "%s %s" % (m.group(1), " ".join(palavras))
        nomeado = any(w[0].isupper() for w in palavras) or FL.mencoes(expr)
        return {"LOCATION_EXPRESSION_RAW": expr, "VALOR": expr if nomeado else UNRESOLVED,
                "PRECISAO": "ZONA_DEFINIDA_PELA_FONTE" if nomeado else "NOT_KNOWN",
                "PORQUE": None if nomeado else "a expressao nao nomeia municipio, provincia nem zona: sem ponto no mapa"}
    ms = FL.mencoes(trecho)
    if ms:
        return {"LOCATION_EXPRESSION_RAW": ms[0]["PLACE"], "VALOR": " ; ".join(dict.fromkeys(x["PLACE"] for x in ms)),
                "PRECISAO": ms[0]["PRECISION"], "PORQUE": None}
    return None


def _trava_da_entidade(r: dict, nome_no_trecho: bool) -> dict:
    """COL-LAW-221 (`afirmacao_da_fonte.procedencia_da_entidade`): a lei decide se a procedencia se sustenta.
    Reprovada -> UNKNOWN, com o motivo da lei. Nunca o contrario (a trava nao promove nada)."""
    ok, porque = AF.procedencia_da_entidade(r["ENTITY_SOURCE"], nome_no_trecho=nome_no_trecho)
    if ok:
        return r
    return {"VALOR": UNKNOWN, "ENTITY_SOURCE": UNKNOWN, "MOTIVO": "COL-LAW-221 reprovou %s: %s"
            % (r["ENTITY_SOURCE"], porque)}


def _trava_do_lugar(lugar: dict) -> dict:
    """COL-LAW-032 (`lugar_do_fato.fact_location`): so TEXT e SECTION_HEADER com lugar resolvido sustentam
    FACT_LOCATION. O resto fica UNRESOLVED, sem ponto — o extrator nao consegue passar por cima da lei."""
    proposto = lugar["VALOR"] if lugar["VALOR"] != UNRESOLVED else None
    valor, porque = LF.fact_location(lugar["LOCATION_SOURCE"], proposto)
    if valor != lugar["VALOR"]:
        lugar = dict(lugar, VALOR=valor, PORQUE="COL-LAW-032: %s" % porque)
    return lugar


def ler_afirmacao(texto: str, inicio: int, fim: int, *, titulo: str | None = None,
                  cabecalhos_visuais=()) -> dict:
    """UMA afirmacao do boletim (o trecho texto[inicio:fim]): praga, cultura e lugar, cada um com a fonte.

    `cabecalhos_visuais`: [{"ROTULO", "PAGINA"?, "INICIO"?, "FIM"?, "PROVA"?}] — cabecalhos que so existem na
    IMAGEM da pagina (medidos fora do texto). Viram CANDIDATO; nunca FACT_LOCATION."""
    t = sem_vizinhos(texto)                 # D19: menu, barra lateral e manchetes vizinhas saem ANTES
    trecho = t[inicio:fim]
    todas = secoes_territoriais(t)
    secao = next((s for s in reversed(todas) if s["INICIO"] <= inicio < s["FIM"]), None)
    # o comeco do bloco do trecho: a secao dele; sem secao, depois da ultima secao territorial fechada antes dele
    ini_secao = secao["INICIO"] if secao else max([s["FIM"] for s in todas if s["FIM"] <= inicio] or [0])
    comeco, corte = _janela_do_paragrafo(t, ini_secao, inicio)
    no_paragrafo = t[comeco:inicio]
    do_outro = t[max(ini_secao, (corte or comeco) - JANELA_DO_OUTRO_LADO):(corte or comeco)] if corte else ""
    corte_txt = re.sub(r"\s+", " ", t[max(0, corte - 30):corte]).strip() if corte else ""
    tit_secao = _titulo_da_secao(t, ini_secao, inicio)
    tit_doc = _titulo_do_documento(t, titulo)
    pragas = _trava_da_entidade(_resolver(_pragas_em(trecho), tit_secao, tit_doc, no_paragrafo,
                                          _pragas_em(do_outro), corte_txt, _pragas_em),
                                bool(_pragas_em(trecho)))
    cultura = _trava_da_entidade(_resolver(_culturas_em(trecho), tit_secao, tit_doc, no_paragrafo,
                                           _culturas_em(do_outro), corte_txt, _culturas_em),
                                 bool(_culturas_em(trecho)))
    # ── o lugar ──
    visuais = [dict(v) for v in (cabecalhos_visuais or ())
               if v.get("INICIO") is None or v["INICIO"] <= inicio < v.get("FIM", len(t))]
    candidato = ({"ENTIDADE_PROPOSTA": v.get("ENTIDADE"), "ROTULO_NA_IMAGEM": v.get("ROTULO"),
                  "PAGINA_PDF": v.get("PAGINA"), "PROVA": v.get("PROVA"),
                  "ESTADO": "CANDIDATO — cabecalho so na imagem; nunca FACT_LOCATION"} for v in visuais)
    candidato = next(candidato, None)
    no_trecho = _lugar_no_trecho(trecho)
    if no_trecho:
        lugar = dict(no_trecho, LOCATION_SOURCE=TEXT, PROVA="«%s»" % re.sub(r"\s+", " ", trecho).strip()[:200])
    elif secao and secao["VALOR"] != UNRESOLVED:
        lugar = {"VALOR": secao["VALOR"], "LOCATION_SOURCE": SECTION_HEADER, "PRECISAO": secao.get("PRECISAO"),
                 "PROVA": "cabecalho da secao no texto: «%s»" % secao["CABECALHO"],
                 "LOCATION_EXPRESSION_RAW": secao["CABECALHO"]}
    elif candidato:
        lugar = {"VALOR": UNRESOLVED, "LOCATION_SOURCE": VISUAL_HEADER_CANDIDATE,
                 "PORQUE": "o cabecalho territorial so esta na imagem da pagina"}
        if secao:
            lugar["CABECALHO_NO_TEXTO"] = secao["CABECALHO"]
            lugar["PORQUE"] += "; o do texto nao resolve: %s" % secao.get("PORQUE")
    elif secao:
        lugar = {"VALOR": UNRESOLVED, "LOCATION_SOURCE": UNRESOLVED, "CABECALHO_NO_TEXTO": secao["CABECALHO"],
                 "PORQUE": secao.get("PORQUE")}
    else:
        lugar = {"VALOR": UNRESOLVED, "LOCATION_SOURCE": UNRESOLVED,
                 "PORQUE": "nem o trecho nem a secao escrevem o lugar"}
    lugar = _trava_do_lugar(lugar)
    lugar["CANDIDATO_VISUAL"] = candidato
    lugar["PONTO_NO_MAPA"] = lugar["VALOR"] != UNRESOLVED
    return {"TRECHO": trecho, "INICIO": inicio, "FIM": fim,
            "SECAO": ({"CABECALHO": secao["CABECALHO"], "VALOR": secao["VALOR"], "INICIO": secao["INICIO"]}
                      if secao else None),
            "PRAGAS": pragas, "CULTURA": cultura, "FACT_LOCATION": lugar,
            "LEI": ("D112: lugar so com a fonte escrevendo-o; cada entidade com a sua proveniencia; sem prova, "
                    "NAO SEI. Cabecalho so na imagem nunca vira FACT_LOCATION.")}


def _achar(texto: str, trecho: str) -> list:
    palavras = re.findall(r"\S+", str(trecho or ""))
    if not palavras:
        return []
    rx = re.compile(r"\s+".join(re.escape(p) for p in palavras))
    return [(m.start(), m.end()) for m in rx.finditer(str(texto or ""))]


def afirmacoes_do_trecho(texto: str, trecho: str, *, titulo: str | None = None, cabecalhos_visuais=()) -> list:
    """Cada ocorrencia do trecho no documento, lida na SUA secao (a mesma frase em 3 secoes = 3 leituras)."""
    return [ler_afirmacao(texto, i, f, titulo=titulo, cabecalhos_visuais=cabecalhos_visuais)
            for i, f in _achar(texto, trecho)]


def aplicacoes_territoriais(texto: str, trecho: str, *, publicador: str | None = None, titulo: str | None = None) -> dict:
    """C07: o MESMO trecho em N secoes territoriais do MESMO documento = N aplicacoes, 1 instituicao.
    Repeticao literal nao e observacao independente."""
    lidas = afirmacoes_do_trecho(texto, trecho, titulo=titulo)
    territorios = [a["FACT_LOCATION"]["VALOR"] for a in lidas if a["FACT_LOCATION"]["LOCATION_SOURCE"] == SECTION_HEADER]
    return {"OCORRENCIAS": len(lidas), "APLICACOES_TERRITORIAIS": len(territorios), "TERRITORIOS": territorios,
            "INSTITUICOES_INDEPENDENTES": 1 if lidas else 0, "PUBLICADOR": publicador or UNKNOWN,
            "LEI": "mesma afirmacao, mesmo documento: N aplicacoes territoriais, UMA instituicao (nao N fontes)"}


# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# CHAVE-PROBLEMA (27/09) — o PROBLEMA do item no contrato PROBLEMA/v1 (`afirmacao_da_fonte.CONTRATO_PROBLEMA`)
# ════════════════════════════════════════════════════════════════════════════════════════════════════════
# O dono da FORMA e `leis/afirmacao_da_fonte.py`; este e o UNICO que a preenche (a porta chama-o para os boletins
# T2/T3 e para os estudos T5; o reprocessamento da Sala chama a porta). Nao e um segundo extrator: as mencoes
# dos boletins saem do MESMO vocabulario, da MESMA regra de AUSENTE e da MESMA tabela MESMO_PROBLEMA de
# `ler_boletim`; as dos estudos saem dos SPANS de `leis/estudo_chaves.py`, tal como vieram.
#
#   · VEIO_DE diz ONDE o nome esta escrito — nunca de onde «deve» vir:
#       DOCUMENT_TITLE  a 1.a linha do texto, o `titulo` dado, ou a linha de titulo repetida (`_titulo_do_documento`)
#       SECTION_HEADER  uma linha CURTA sozinha (<= PALAVRAS_DO_CABECALHO palavras, sem «:», sem «;», sem «.» no
#                       fim; marcador «•» permitido) — «• Mosca delle olive (Bactrocera oleae)»
#       TEXT            o resto: o nome dentro de uma frase
#     O nome no cabecalho e no texto: a BASE e a do TEXTO (a mais proxima do que a fonte afirma); as outras
#     ocorrencias ficam em OCORRENCIAS. O nome SO no cabecalho continua SECTION_HEADER — nunca vira TEXT.
#   · Duas ou mais pragas distintas (depois de MESMO_PROBLEMA) nao marcadas ausentes = NAO SEI (D112).
#   · CODIGO EPPO so quando uma das formas ESCRITAS do problema e um binomio latino que casa EXACTAMENTE com
#     a tabela do repo (`motor/normalize_agro.py`, dicionario ES-T4-001 do MAPA, sem grupos). Nome comum
#     italiano nunca cunha EPPO (normalize_agro: «esta arvore NAO tem autoridade italiano->EPPO»).
TABELA_DO_NOME = "leis/boletim_do_campo.py::MESMO_PROBLEMA (D111: as formas da mesma praga contam uma vez)"
_ORDEM_DO_VEIO_DE = {"TEXT": 0, "SECTION_HEADER": 1, "DOCUMENT_TITLE": 2}
_BINOMIOS = {}


def mencoes_do_boletim(texto: str) -> list:
    """Cada praga/doenca ESCRITA no texto: [{NOME, FORMA, ESTADO, INICIO, FIM}], posicoes em `texto`.

    `texto` ja deve vir sem vizinhos (`fato_do_texto.sem_vizinhos`), como `ler_boletim` o le."""
    t = str(texto or "")
    linhas = t.splitlines()
    fora = []
    for n, (pos, linha) in enumerate(_linhas_com_posicao(t)):
        d = _dobrar(linha)
        for m in _RE_PROBLEMA.finditer(d):
            fora.append({"NOME": nome_do_problema(re.sub(r"\s+", " ", m.group(0))),
                         "FORMA": re.sub(r"\s+", " ", linha[m.start():m.end()]),
                         "ESTADO": _estado_da_praga(d, m.end(), linhas, n),
                         "INICIO": pos + m.start(), "FIM": pos + m.end()})
    return fora


def _e_cabecalho(linha: str) -> bool:
    s = linha.strip().lstrip("•·*-– \t").strip()
    return bool(s) and len(re.findall(r"[A-Za-zÀ-ÿ']+", s)) <= PALAVRAS_DO_CABECALHO \
        and not re.search(r"[:;]", s) and not s.endswith(".")


def _onde_esta(texto: str, ini: int, fim: int, titulos: list) -> tuple:
    """(VEIO_DE, BASE) da mencao texto[ini:fim]: a linha dela diz se e titulo, cabecalho ou frase.
    A linha parte-se como `mencoes_do_boletim` a parte (`splitlines`: «\\f» de pagina tambem corta)."""
    a, linha = next(((p, l) for p, l in _linhas_com_posicao(texto) if p <= ini < p + max(len(l), 1)),
                    (0, texto))
    s = re.sub(r"\s+", " ", linha).strip()
    primeira = next((l.strip() for l in texto.splitlines() if l.strip()), "")
    if linha.strip() == primeira or s in titulos:
        return "DOCUMENT_TITLE", s
    if _e_cabecalho(linha):
        return "SECTION_HEADER", s
    return "TEXT", _trecho(linha, ini - a, fim - a)


def _binomios() -> dict:
    """{binomio normalizado: (codigo EPPO, cientifico)} — a tabela do repo, lida pelo dono dela."""
    if not _BINOMIOS:
        import os
        import sys
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for p in (raiz, os.path.join(raiz, "motor")):
            if p not in sys.path:
                sys.path.insert(0, p)
        import normalize_agro as NA      # noqa: PLC0415
        _BINOMIOS["NORM"] = NA.norm
        _BINOMIOS["TABELA"] = NA._binomios_do_dicionario(NA.es_dict()["pests"])
        _BINOMIOS["AUTORIDADE"] = ("data/samples/ES-T4-001/eppo-dictionary.json (tabelas oficiais do MAPA), "
                                   "lido por motor/normalize_agro.py::_binomios_do_dicionario")
    return _BINOMIOS


def _codigo(nome: str, formas: list, tabelas: list) -> dict:
    b = _binomios()
    achados = {}
    for f in formas:
        hit = b["TABELA"].get(b["NORM"](f))
        if hit:
            achados.setdefault(hit[0], (hit[1], f))
    if len(achados) == 1:
        codigo, (cientifico, forma) = next(iter(achados.items()))
        return {"SISTEMA": "EPPO", "VALOR": codigo, "CIENTIFICO": cientifico, "PROVA": forma,
                "COMO": "CASAMENTO_EXACTO_DE_BINOMIO_LATINO escrito no texto", "TABELA": b["AUTORIDADE"],
                "NOME_CANONICO": nome}
    porque = ("o texto escreve binomios de codigos EPPO diferentes para o mesmo nome (%s): nenhum e escolhido"
              % ", ".join(sorted(achados)) if achados else
              "o texto nao escreve o binomio latino; nome comum nao cunha EPPO (COL-LAW-034)")
    return {"SISTEMA": "NOME_CANONICO", "VALOR": nome, "TABELA": " + ".join(tabelas) or TABELA_DO_NOME,
            "EPPO": AF.AUSENCIA_DO_PROBLEMA, "PORQUE_SEM_EPPO": porque}


def declarar_problema(texto: str, mencoes: list, *, titulo: str | None = None, ler: str = "") -> dict:
    """O bloco PROBLEMA/v1 do item, a partir das mencoes JA lidas (posicoes em `texto`).

    Cada mencao: {NOME, FORMA, ESTADO, INICIO, FIM} e, opcional, TABELA (o vocabulario que deu o NOME;
    omissao = MESMO_PROBLEMA deste ficheiro).

    `ler` diz quem leu as mencoes (entra no LEITOR; nao muda a regra)."""
    t = str(texto or "")
    nada = AF.AUSENCIA_DO_PROBLEMA
    base = {"CONTRATO": AF.CONTRATO_PROBLEMA, "LEITOR": ler or "leis/boletim_do_campo.py::declarar_problema",
            "LEI": ("D112: o nome ESCRITO, com o trecho literal; duas pragas = NAO SEI; D111: formas da mesma "
                    "praga contam uma vez (MESMO_PROBLEMA); EPPO so com o binomio escrito")}
    titulos = _titulo_do_documento(t, titulo)
    lidas = []
    for m in mencoes or []:
        veio, trecho = _onde_esta(t, m["INICIO"], m["FIM"], [re.sub(r"\s+", " ", x).strip() for x in titulos])
        lidas.append(dict(m, VEIO_DE=veio, BASE=trecho))
    ausentes = sorted({m["NOME"] for m in lidas if m["ESTADO"] == "AUSENTE"}
                      - {m["NOME"] for m in lidas if m["ESTADO"] != "AUSENTE"})
    vivas = [m for m in lidas if m["ESTADO"] != "AUSENTE"]
    nomes = list(dict.fromkeys(m["NOME"] for m in vivas))
    base["AUSENTES"] = ausentes
    base["CANDIDATOS"] = [{"NOME": n, "OCORRENCIAS": [{"VEIO_DE": m["VEIO_DE"], "FORMA": m["FORMA"],
                                                       "ESTADO": m["ESTADO"], "BASE": m["BASE"][:200]}
                                                      for m in vivas if m["NOME"] == n]} for n in nomes]
    if len(nomes) != 1:
        porque = ("D112: o item nomeia %d problemas distintos (%s); escolher um seria inferir"
                  % (len(nomes), ", ".join(nomes)) if nomes else
                  "so pragas marcadas ausentes no texto (%s): ausente nao e ocorrencia" % ", ".join(ausentes)
                  if ausentes else "o texto nao nomeia praga/doenca do vocabulario")
        return dict(base, VALOR=nada, VEIO_DE=nada, BASE=nada, FORMA=nada, ENTITY_SOURCE="UNKNOWN",
                    CODIGO={"SISTEMA": nada, "VALOR": nada}, PORQUE=porque)
    nome = nomes[0]
    doc = sorted(vivas, key=lambda m: (_ORDEM_DO_VEIO_DE[m["VEIO_DE"]], m["INICIO"]))[0]
    return dict(base, VALOR=nome, VEIO_DE=doc["VEIO_DE"], BASE=doc["BASE"], FORMA=doc["FORMA"],
                ESTADO=doc["ESTADO"], ENTITY_SOURCE=AF.ENTITY_SOURCE_DO_VEIO_DE[doc["VEIO_DE"]],
                CODIGO=_codigo(nome, [m["FORMA"] for m in vivas],
                               list(dict.fromkeys(m.get("TABELA") or TABELA_DO_NOME for m in vivas))))


def problema_do_boletim(texto: str, *, titulo: str | None = None) -> dict:
    """O bloco PROBLEMA/v1 de um BOLETIM (T2/T3): as mencoes de `mencoes_do_boletim` no texto sem vizinhos."""
    t = sem_vizinhos(texto)
    return declarar_problema(t, mencoes_do_boletim(t), titulo=titulo,
                             ler="leis/boletim_do_campo.py::mencoes_do_boletim (secoes do boletim, D84)")


# ── PORTA-UNICA-REFERENCIA (D116): o SINAL praga x cultura -> produtos ADAMA autorizados ─────────────────
# `ler_boletim` continua PURA. Esta funcao e a unica deste ficheiro que le a referencia, e le PELA PORTA
# (`motor/porta_da_referencia.py`), na mesma edicao que as outras capacidades: nunca abre bula, registo nem
# catalogo por conta propria. Praga AUSENTE nao pergunta nada (praga marcada ausente nao e ocorrencia).
# Bula nao lida -> A_CONFIRMAR; cultura/alvo que nenhuma bula escreve nesta forma -> NAO SEI.
def _porta():
    import os
    import sys
    motor = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "motor")
    if motor not in sys.path:
        sys.path.insert(0, motor)
    import porta_da_referencia as PORTA   # noqa: PLC0415
    return PORTA


def produtos_adama_do_boletim(leitura: dict, referencia: dict | None = None, hoje=None) -> dict:
    """Cada par cultura x praga ESCRITO NA MESMA SECAO -> o que a bula ADAMA autoriza, pela porta."""
    PORTA = _porta()
    ref = referencia if referencia is not None else PORTA.abrir(hoje=hoje)
    pares, vistos = [], set()
    for s in (leitura or {}).get("SECOES") or []:
        cultura = s.get("CULTURA")
        if not cultura:
            continue                     # praga sem cultura na secao nao ganha cultura emprestada
        cultura = MESMA_CULTURA.get(cultura, cultura)
        for p in s.get("PROBLEMAS") or []:
            if p.get("ESTADO") == "AUSENTE":
                continue
            chave = (cultura, p.get("NOME"))
            if chave in vistos:
                continue
            vistos.add(chave)
            r = PORTA.autorizados(ref, cultura, p.get("NOME"))
            r.pop("CARIMBO", None)
            pares.append({"CULTURA": cultura, "PRAGA": p.get("NOME"), "ESTADO_NO_BOLETIM": p.get("ESTADO"),
                          "PRODUTOS_ADAMA": r,
                          # LIGACAO-ADAMA (D123): o par da MESMA secao, ligado pela porta
                          "LIGACAO_ADAMA": PORTA.ligacao_adama(ref, {
                              "CULTURA": cultura, "PROBLEMA": p.get("NOME"),
                              "VEM_DE": {"CULTURA": "BOLETIM.SECOES.CULTURA (ler_boletim)",
                                         "PROBLEMA": "BOLETIM.SECOES.PROBLEMAS (ler_boletim)"}})})
    return {"REFERENCIA_ADAMA": PORTA.carimbo(ref), "PARES": pares,
            "NAO_E": "o boletim nao recomendou produto: e a bula a cobrir o par que o boletim escreveu"}
