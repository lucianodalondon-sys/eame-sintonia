#!/usr/bin/env python3
"""O LUGAR E O TEMPO DO FACTO, TIRADOS DO TEXTO — os quatro campos da Sala, com a prova e o TIPO.

    campos_do_fato(texto, publication_time=None, publication_time_basis=None) -> dict

Funcao PURA (sem rede, sem banco, sem ficheiros): recebe o texto de UM documento e devolve

    fact_location            "NAO SEI" ou os lugares do facto (todos do MESMO tipo), separados por " ; "
    fact_location_basis      como se soube, com o trecho do texto; ou porque NAO SEI
    fact_location_kind       CAMPO | EVENTO | MERCADO | NAO SEI   — o tipo do facto a que o lugar pertence
    fact_location_precision  COUNTRY | REGION | PROVINCE | NAO SEI
    fact_time                "NAO SEI" ou a data/periodo do facto como o texto a escreve
    fact_time_basis          como se soube (origem, resolucao, trecho); ou porque NAO SEI
    fact_time_kind           CAMPO | EVENTO | NAO SEI
    fact_time_precision      o vocabulario `lugar_do_fato.RESOLUCAO_TEMPORAL` (NOT_KNOWN quando NAO SEI),
                             com «+CALCULADA» quando a data veio da conta a partir da publicacao
    fact_time_calculo        RELATIVA_A_PUBLICACAO quando a data foi CALCULADA; NAO_SE_APLICA nos outros casos
    fact_time_evidencia      quando CALCULADA: a expressao, o trecho e a conta; NAO_SE_APLICA nos outros casos
                             (D69: com a data calculada, fact_time_basis e SO «RELATIVA_A_PUBLICACAO», e o valor
                             e sempre um intervalo ISO — um dia calculado e «AAAA-MM-DD/AAAA-MM-DD»)
    EVIDENCIA                tudo estruturado: todos os lugares de todos os tipos, os tempos,
                             as EXPRESSOES RELATIVAS encontradas e a publicacao, SEPARADA

Os quatro primeiros nomes sao as colunas da Sala (`sala_de_espera`) e do tradutor da porta. `_kind` e
`_precision` nao tem coluna na Sala: o tipo e a precisao vao tambem, por extenso, no inicio da `_basis`.

QUEM LE O ITALIANO E `leis/fato_local.py` — nao se edita aqui («repuxar da Italia»). Este ficheiro poe
a volta dele:

  1. O CORPO, NAO A PAGINA. Linha curta (menu, titulo de seccao) e linha de rodape/institucional (morada,
     CAP, tel, p.iva, cookie…) nao alimentam nem lugar nem tempo. O lugar da fonte nao entra: a funcao
     nem recebe SOURCE_LOCATION.
  2. D62 · O QUE E FACTO. Facto e o que muda no campo (CAMPO) E tambem os eventos tecnicos — feira,
     congresso, dia de campo — como facto de OUTRO tipo (EVENTO). O leitor italiano recusa o lugar de
     evento e de mercado de proposito (falso positivo medido no Brasil: a feira virava «lugar da
     doenca»). Aqui essa recusa vira TIPO: o lugar de evento sai com kind EVENTO, o de mercado com kind
     MERCADO — e NUNCA como CAMPO. Havendo lugar CAMPO, `fact_location` so tem CAMPO; os outros ficam
     na EVIDENCIA com o seu tipo.
  3. D63 (substitui o ponto 3 da D62) · RELATIVO SO COM A CONTA FEITA. «ieri», «la settimana scorsa»,
     «lunedì scorso» valem como fact_time SO se a PUBLICATION_TIME estiver PROVADA: a data sai da conta a
     partir dela, a base diz RELATIVA_A_PUBLICACAO com a expressao original, e a precisao diz CALCULADA.
     «ieri» = um dia; «la settimana scorsa» = o INTERVALO segunda–domingo da semana anterior, nunca um dia
     inventado. Sem publicacao provada = NAO SEI (a expressao fica na EVIDENCIA). A data de COLETA nunca
     serve de ancora: a funcao nem a recebe. A publicacao continua a parte, em EVIDENCIA.
  4. O que nao e tempo do facto e tapado antes de perguntar ao leitor: serie de anos, carimbo de lista
     no inicio da linha, fim de prazo.

Nada disto descarta o item: sem lugar e sem data, a funcao devolve NAO SEI com o porque (D62: nada e
obrigatorio; quanto mais dados, mais precisao).
"""
from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fato_local as FL          # noqa: E402  (o leitor italiano: nao se reescreve aqui)

NAO_SEI = "NAO SEI"
SEP = " ; "
CAMPO, EVENTO, MERCADO = "CAMPO", "EVENTO", "MERCADO"
RELATIVA = "RELATIVA_A_PUBLICACAO"
NAO_SE_APLICA = "NAO_SE_APLICA"
# o mesmo tipo, dito no vocabulario da lei (`lugar_do_fato.PAPEIS_NO_CONTEUDO`)
PAPEL_NA_LEI = {CAMPO: "FACT", EVENTO: "EVENT", MERCADO: "AREA_COMERCIAL"}
ORDEM_DOS_TIPOS = (CAMPO, EVENTO, MERCADO)

# ── 1 · o corpo ─────────────────────────────────────────────────────────────
# Uma linha e corpo se tem frase (>= PALAVRAS_MINIMAS palavras) e nao e rodape/institucional.
# WHY 8: nos 78 textos da Sala, menu e titulos de seccao tem 1-5 palavras ("Home", "Notizie",
# "Temi ambientali"); frases de noticia tem 10+. Heuristica declarada, medida no relatorio.
PALAVRAS_MINIMAS = 8
RODAPE = re.compile(
    r"(cookie|privacy|p\.?\s?iva|partita\s+iva|codice\s+fiscale|c\.f\.|\btel\b|\bfax\b|e-?mail|pec\b|"
    r"copyright|©|tutti\s+i\s+diritti|registro\s+stampa|iscrizione\s+(?:sul|al)\s+registro|direttore\s+responsabile|"
    r"seguici|newsletter|iscriviti|\bvia\s+[a-z']+(?:\s+[a-z']+)?,?\s*\d+|\b\d{5}\s*[-–]?\s*[A-Z][a-z]+|"
    r"sede\s+legale|centralino|orari\s+di\s+apertura|mappa\s+del\s+sito|note\s+legali|accessibilit)",
    re.I)


def corpo(texto: str) -> str:
    """As linhas do texto que sao frase de conteudo — menu, cabecalho e rodape ficam de fora."""
    fica = []
    for linha in str(texto or "").splitlines():
        l = linha.strip()
        if len(re.findall(r"[A-Za-zÀ-ÿ']+", l)) < PALAVRAS_MINIMAS:
            continue
        if RODAPE.search(l):
            continue
        fica.append(l)
    return "\n".join(fica)


# ── 2 · a publicacao: so ela, separada ──────────────────────────────────────
def publicacao_provada(publication_time, publication_time_basis) -> date | None:
    """A data de publicacao so conta se for uma data ISO E tiver base que nao seja NAO SEI.
    Serve para duas coisas: descartar a data do texto que e o carimbo da publicacao, e ancorar a conta
    das expressoes relativas (D63). Nunca preenche fact_time sozinha."""
    if not publication_time or not publication_time_basis:
        return None
    if str(publication_time_basis).strip().upper().startswith(("NAO SEI", "NÃO SEI", "UNKNOWN")):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(publication_time))
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


# ── 3 · o tempo relativo: vale com a conta feita a partir da publicacao provada (D63) ──
_MES = "|".join(FL.MESES)
_DIA = r"(?:luned[iì]|marted[iì]|mercoled[iì]|gioved[iì]|venerd[iì]|sabato|domenica)"
# (expressao, regra) — a regra diz a conta.
RELATIVOS = (
    (r"l['’]altro\s*ieri|altroieri", ("DIA", -2)),
    (r"ieri", ("DIA", -1)),
    (r"oggi|stamattina|stamane|stasera|stanotte", ("DIA", 0)),
    (r"dopodomani", ("DIA", 2)),
    (r"domani", ("DIA", 1)),
    (r"(?:la\s+)?settimana\s+scorsa|(?:la\s+)?scorsa\s+settimana", ("SEMANA", -1)),
    (r"questa\s+settimana", ("SEMANA", 0)),
    (r"(?:la\s+)?prossima\s+settimana|(?:la\s+)?settimana\s+prossima", ("SEMANA", 1)),
    (r"(?:il\s+)?mese\s+scorso|(?:lo\s+)?scorso\s+mese", ("MES", -1)),
    (r"(?:l['’])?anno\s+scorso|(?:lo\s+)?scorso\s+anno", ("ANO", -1)),
    (r"%s\s+scors[oa]|(?:lo\s+|la\s+)?scors[oa]\s+%s" % (_DIA, _DIA), ("DIA_DA_SEMANA", -1)),
    # sem medida: «nei giorni scorsi» nao diz quantos dias — fica como evidencia, nunca vira data
    (r"nei\s+giorni\s+scorsi|di\s+recente|recentemente", ("SEM_MEDIDA", None)),
)
_RE_RELATIVOS = re.compile(r"(?<![0-9a-zà-ÿ])(" + "|".join("(?:%s)" % p for p, _ in RELATIVOS) + r")(?![0-9a-zà-ÿ])", re.I)
_DIAS_RAIZ = ("luned", "marted", "mercoled", "gioved", "venerd", "sabato", "domenica")


def _regra(expr: str):
    for p, regra in RELATIVOS:
        if re.fullmatch(p, expr, re.I):
            return regra
    return ("SEM_MEDIDA", None)


def _um_dia(d: date) -> str:
    """D69: o dia CALCULADO escreve-se como o intervalo desse dia, «2026-09-21/2026-09-21» — o padrao
    que o projeto ja usa (`leis/calendario_handoff.py`: DATE_EXACT «EXIBIR_COMO intervalo de datas»; a
    tabela do calendario guarda data_inicio/data_fim; as semanas e meses daqui ja sao «inicio/fim»).
    «oggi» e o DIA do facto, nao a copia do instante de publicacao: por isso nunca se escreve igual a
    PUBLISHED_AT, e a lei `leis/artefato.py::conferir` fica como esta."""
    return "%s/%s" % (d.isoformat(), d.isoformat())


def conta_relativa(expr: str, pub: date):
    """(valor, resolucao) a partir da publicacao provada; None se a expressao nao tem medida.
    Intervalo em ISO 8601 «inicio/fim». Nunca inventa um dia dentro de um intervalo."""
    tipo, n = _regra(expr)
    if tipo == "DIA":
        return _um_dia(pub + timedelta(days=n)), "DATE_EXACT"
    if tipo == "SEMANA":
        seg = pub - timedelta(days=pub.weekday()) + timedelta(weeks=n)
        return "%s/%s" % (seg.isoformat(), (seg + timedelta(days=6)).isoformat()), "WEEK"
    if tipo == "MES":
        fim = pub.replace(day=1) - timedelta(days=1)
        return "%s/%s" % (fim.replace(day=1).isoformat(), fim.isoformat()), "MONTH"
    if tipo == "ANO":
        return "%d-01-01/%d-12-31" % (pub.year - 1, pub.year - 1), "APPROXIMATE"
    if tipo == "DIA_DA_SEMANA":
        alvo = next(i for i, d in enumerate(_DIAS_RAIZ) if d in expr.lower())
        atras = (pub.weekday() - alvo) % 7 or 7          # «lunedì scorso» dito numa segunda = a segunda anterior
        return _um_dia(pub - timedelta(days=atras)), "DATE_EXACT"
    return None


# ── D64 · «oggi» so e o dia quando o texto o diz ────────────────────────────
# «oggi, lunedì», «oggi è stato», «oggi alle 10», «oggi 25 settembre», «oggi pomeriggio»,
# «nella giornata di oggi» = o proprio dia. «oggi i consumatori», «ad oggi», «al giorno d'oggi»,
# «fino ad oggi» = «hoje em dia» / «ate agora» = NAO SEI. Sem marca nenhuma, tambem NAO SEI.
_OGGI_DIA_DEPOIS = re.compile(
    r"^\s*,?\s*(?:%s\b|\d{1,2}\s+(?:%s)\b|alle\b|(?:è|e['’]|sono)\s+stat[oaie]\b|pomeriggio\b|mattina\b|sera\b|"
    r"in\s+mattinata\b|in\s+serata\b)" % (_DIA, _MES), re.I)
_OGGI_DIA_ANTES = re.compile(r"(?:giornata\s+di|proprio)\s*$", re.I)
_OGGI_HOJE_EM_DIA_ANTES = re.compile(r"(?:(?<![0-9a-zà-ÿ])ad?|fino\s+ad?|al\s+giorno\s+d['’]|(?<![0-9a-zà-ÿ])d['’])\s*$", re.I)


def _oggi_vale(expr: str, antes: str, depois: str) -> tuple[bool, str | None]:
    if expr.lower() != "oggi":
        return True, None
    if _OGGI_HOJE_EM_DIA_ANTES.search(antes):
        return False, "«%s%s» quer dizer até agora / hoje em dia, não um dia (D64)" % (antes.split()[-1] + " " if antes.split() else "", expr)
    if _OGGI_DIA_DEPOIS.search(depois) or _OGGI_DIA_ANTES.search(antes):
        return True, None
    return False, "«oggi» sem marca de que é o próprio dia — pode ser «hoje em dia» (D64)"


# ── a relativa que e o TERMO DE COMPARACAO nao data o facto ──────────────────
# Medido nas 78 (IT-T3-008): «in minor misura rispetto allo stesso periodo dello scorso anno» — o ano
# passado e a regua, o facto e deste ano. O mesmo para «rispetto alla settimana scorsa».
_RE_COMPARACAO = re.compile(r"(?:rispetto|confront\w*|paragon\w*|stesso\s+periodo|analogo\s+periodo|in\s+linea\s+con)"
                            r"[^.;!?]*$", re.I)


# ── as ancoras do leitor, mas com PALAVRA INTEIRA a esquerda ────────────────
# `fato_local.tempo_do_fato` procura as suas ancoras sem fronteira: «coltura» casa dentro de
# «arboricoltura» e «agricoltura». Medido nas 78: «esame del modulo di arboricoltura … previsto per il 21
# settembre» e «Laurea … nel 2022» (agricoltura) sairam como tempo de CAMPO. A ancora so conta quando
# COMECA uma palavra (a direita fica aberta: sao raizes — «contaminaz», «superament»).
_RE_ANCORAS_DE_CAMPO = re.compile(r"(?<![0-9a-z])(?:%s)" % "|".join(FL.ANCORAS_DE_TEMPO_DO_FATO))


def _presa_ao_campo(frase: str) -> bool:
    return _RE_ANCORAS_DE_CAMPO.search(FL._baixo(frase)) is not None


# ── a frase institucional: data de exame, aula, curso, inscricao nao e facto do agro ──
# (coordenacao, 25/09: «exame de faculdade adiado nao e facto do ecossistema agro» -> INSTITUCIONAL_NAO_FATO,
# o mesmo nome do tipo da REGUA-FATO, `leis/tipo_do_fato.py`)
_RE_INSTITUCIONAL = re.compile(
    r"(?<![0-9a-zà-ÿ])(?:esam[ei]|appell[oi]|lezion[ei]|laure[ae]|corsi?\s+di\s+(?:laurea|studi[oa]?)|iscrizion[ei]|"
    r"immatricolazion[ei]|bando|concors[oi]|tesi|tirocini[oa]?|graduatori[ae]|cfu|didattic[ao]|dottorat[oi]|"
    r"sessione\s+di\s+laurea|colloqui[oa]?)(?![0-9a-zà-ÿ])", re.I)


def _tempo_de_campo(t: str, pub: date | None, tapados: list) -> dict:
    """Pergunta ao leitor; se a data que ele escolhe vem de uma frase institucional ou de uma ancora que
    so existia DENTRO de outra palavra, tapa-a nessa frase e pergunta de novo."""
    for _ in range(12):
        r = FL.tempo_do_fato(t, pub.isoformat() if pub else None)
        v, ev = r.get("FACT_TIME"), r.get("FACT_TIME_EVIDENCE") or ""
        if v in (None, "NOT_KNOWN"):
            return r
        motivo = ("INSTITUCIONAL_NAO_FATO" if _RE_INSTITUCIONAL.search(ev)
                  else None if _presa_ao_campo(ev) else "ANCORA_DENTRO_DE_OUTRA_PALAVRA")
        if not motivo:
            return r
        tapados.append("%s «%s»" % (motivo, v))
        i = t.find(ev[:60])
        if i < 0:
            break
        fim = i + len(_frase_em(t, i))
        seg = re.sub(re.escape(v), lambda m: " " * len(m.group(0)), t[i:fim], flags=re.I)
        if seg == t[i:fim]:
            break
        t = t[:i] + seg + t[fim:]
    return {"FACT_TIME": "NOT_KNOWN"}


# a precisao do leitor, dita no vocabulario da lei (`lugar_do_fato.RESOLUCAO_TEMPORAL`)
RESOLUCAO = {"DAY": "DATE_EXACT", "WEEK": "WEEK", "MONTH": "MONTH", "SEASON": "SEASON", "YEAR": "APPROXIMATE"}

# ── o que NAO e tempo do facto, tapado antes de perguntar ao leitor ───────────
# Medido a mao nos 78 da Sala (25/09): das 15 datas que o leitor dava, 4 erradas; 3 destas eram estas
# formas — a lei ja as nomeia (SERIES_RANGE_NOT_FACT_TIME, PUBLICATION_STAMP_NOT_FACT_TIME) ou sao prazo:
#   · SERIE DE ANOS    «le settimane 35-39 del 2024, 2025 e 2026» -> nao e o ano do facto
#   · CARIMBO DE LISTA «1 Settembre 2026 Risultati ...» no inicio da linha -> data do item da lista
#   · FIM DE PRAZO     «fino a novembre», «entro il 30 settembre» -> limite, nao a data do facto
NAO_E_TEMPO_DO_FACTO = (
    ("SERIE_DE_ANOS", re.compile(r"\b(?:19|20)\d{2}(?:\s*(?:,|\be\b|\bed\b)\s*(?:19|20)\d{2})+\b", re.I)),
    ("CARIMBO_DE_LISTA", re.compile(r"^\s*\d{1,2}\s+(?:%s)\s+\d{4}\b" % _MES, re.I | re.M)),
    ("FIM_DE_PRAZO", re.compile(r"\b(?:fino\s+a(?:l(?:la)?)?|entro(?:\s+il)?)\s+(?:\d{1,2}\s+)?(?:%s)(?:\s+\d{4})?\b" % _MES, re.I)),
)


def _trecho(s: str, n: int = 200) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def _frase_em(t: str, pos: int) -> str:
    ini = max(t.rfind(c, 0, pos) for c in ".!?;\n") + 1
    fins = [i for i in (t.find(c, pos) for c in ".!?;\n") if i != -1]
    return t[ini:min(fins) if fins else len(t)]


def _tapar(t: str) -> tuple[str, list, list]:
    """(texto tapado, datas tapadas por nao serem tempo do facto, expressoes relativas com o trecho)."""
    tapados, relativas = [], []
    for nome, rx in NAO_E_TEMPO_DO_FACTO:
        def _sub(m, nome=nome):
            tapados.append("%s «%s»" % (nome, m.group(0).strip()))
            return " " * len(m.group(0))
        t = rx.sub(_sub, t)
    orig = t

    def _rel(m):
        relativas.append({"EXPRESSAO": m.group(0), "TRECHO": _trecho(_frase_em(orig, m.start())),
                          "_ANTES": orig[max(0, m.start() - 50):m.start()], "_DEPOIS": orig[m.end():m.end() + 40]})
        return " " * len(m.group(0))
    t = _RE_RELATIVOS.sub(_rel, t)
    return t, tapados, relativas


# ── 4 · os eventos tecnicos (D62) ───────────────────────────────────────────
# ⚠️ Palavras deste ficheiro, NAO do leitor italiano (que nao se edita aqui e ja nao existe no ramo da
# Italia para repuxar). Estao listadas no relatorio como proposta para o leitor.
ANCORAS_DE_EVENTO = (
    r"fier[ae]", r"salone", r"convegn[oi]", r"congress[oi]", r"workshop", r"seminari[oa]?", r"webinar",
    r"giornat[ae]\s+(?:tecnic[ah]e?|in\s+campo|dimostrativ[ae]|di\s+studio|di\s+campo|aperte?|internazional[ei]|nazional[ei]|mondial[ei])",
    r"dimostrazion[ei]\s+in\s+campo", r"open\s+day", r"field\s+day", r"rassegna", r"expo",
    # «eventi estremi / meteorologici / atmosferici» e tempo que muda o campo (CAMPO), nao evento tecnico
    r"event[oi](?!\s+(?:estrem|meteo|atmosferic|climatic|calamitos|alluvional|avvers))", r"incontr[oi]\s+tecnic[oi]", r"forum", r"manifestazion[ei]",
    r"in\s+programma", r"si\s+terr[aà]", r"si\s+svolger[aà]",
)
_RE_EVENTO = re.compile(r"(?<![0-9a-zà-ÿ])(?:%s)(?![0-9a-zà-ÿ])" % "|".join(ANCORAS_DE_EVENTO), re.I)
# Porque o leitor recusou um lugar numa frase de evento, e se isso ainda pode ser o LUGAR DO EVENTO.
# «presso» e o local do evento numa frase de evento («si terra … presso la Sala Seminari»);
# sede/residencia/formacao/ambito continuam a nao ser lugar de nada.
RECUSA_QUE_PODE_SER_EVENTO = ("local de evento", "afiliação institucional",
                              "topônimo sem relação semântica com o acontecimento")
RECUSA_QUE_E_MERCADO = ("área econômica",)
_RE_MERCADO = re.compile(r"(?<![0-9a-zà-ÿ])mercat[oi](?![0-9a-zà-ÿ])", re.I)

# ── 4b · o lugar onde se PLANTA / COLHE e CAMPO, mesmo numa noticia de mercado (coordenacao, 25/09) ──
# Medido nas 78: «Più shelf-life per allargare i confini del mercato In Sardegna si producono tante
# fragole» saia MERCADO; a Sardenha e onde se produz. O lugar sai CAMPO com ESPECIE=PRODUCAO (o do
# leitor italiano e ESPECIE=OCORRENCIA): produzir ali nao e praga ali — a base e a EVIDENCIA dizem qual.
ANCORAS_DE_PRODUCAO = (
    # So verbos e palavras de PLANTAR / COLHER. Medido nas 78 e retirado por apanhar outra coisa:
    #   «produzione» (scientifica, industriale, «Istituto di Produzioni Vegetali»), «raccolta» (de textos),
    #   «colture» («la protezione delle colture»), «campi», «produttori di Firenze» (onde a entidade esta).
    r"si\s+produc\w*", r"(?:viene|vengono|è|sono)\s+prodott[oaie]", r"coltivat[oaie]", r"coltivazion[ei]",
    r"si\s+coltiv\w*", r"raccolto", r"vendemmi[ae]", r"piantat[oaie]", r"ettari", r"frutteti", r"vigneti",
    r"oliveti", r"agrumeti",
)
DISTANCIA_MAXIMA_DA_PRODUCAO = 60      # letras entre a palavra de producao e o lugar
_RE_PRODUCAO = re.compile(r"(?<![0-9a-zà-ÿ])(?:%s)(?![0-9a-zà-ÿ])" % "|".join(ANCORAS_DE_PRODUCAO), re.I)
RECUSA_QUE_PODE_SER_PRODUCAO = ("área econômica", "topônimo sem relação semântica com o acontecimento")

# data explicita de evento: «12 e 13 novembre 2026», «dal 6 all'8 ottobre 2026», «16-24 maggio 2026», «8 ottobre»
_RE_DATA_EVENTO = re.compile(
    r"(?:\bdal(?:l['’])?\s*)?\b(\d{1,2})(?:\s*(?:-|–|\be\b|\bal\b|\ball['’])\s*(\d{1,2}))?\s+(%s)(?:\s+(\d{4}))?\b" % _MES,
    re.I)


def _tempos_de_evento(t: str, pub: date | None) -> list:
    fora = []
    for frase in FL._frases(t):
        ev = _RE_EVENTO.search(frase)
        if not ev:
            continue
        for m in _RE_DATA_EVENTO.finditer(frase):
            d1, d2, mes, ano = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
            if pub and not d2 and int(d1) == pub.day and FL.MES_NUM[mes] == pub.month \
                    and (not ano or int(ano) == pub.year):
                continue                                   # e o carimbo da publicacao, nao o evento
            valor = ("%s-%s %s" % (d1, d2, mes) if d2 else "%s %s" % (d1, mes)) + (" %s" % ano if ano else "")
            fora.append({"VALOR": valor, "RESOLUCAO": "APPROXIMATE" if d2 else "DATE_EXACT",
                         "ANCORA": ev.group(0), "TRECHO": _trecho(frase)})
    return fora


# ── 5 · os campos ───────────────────────────────────────────────────────────
def _posicao_do_nome(lugar: str, frase: str):
    """Onde o lugar aparece na frase ESCRITO COM MAIUSCULA inicial; None se so aparece em minusculas.
    O leitor compara em minusculas, e «fermo» (parado) casava com a provincia de Fermo — medido nas 78
    (IT-T10-018: «il mercato … resta sostanzialmente fermo»). So se aplica aos lugares que ESTE
    ficheiro promove (EVENTO/MERCADO/CAMPO de producao)."""
    m = re.search(r"(?<![0-9A-Za-zÀ-ÿ])%s(?![0-9A-Za-zÀ-ÿ])" % re.escape(lugar), str(frase or ""))
    return m.start() if m else None


def _distancia(m, pos: int, n: int) -> int:
    if m.end() <= pos:
        return pos - m.end()
    if m.start() >= pos + n:
        return m.start() - (pos + n)
    return 0


def _lugares(c: str) -> tuple[list, list]:
    aceitas, recusadas = FL.localizacoes_do_fato(c, origem="TEXTO_DO_CORPO")
    lugares, vistos = [], set()
    for a in aceitas:
        vistos.add((CAMPO, a["FACT_LOCATION"]))
        lugares.append({"LUGAR": a["FACT_LOCATION"], "PRECISAO": a["FACT_LOCATION_PRECISION"], "KIND": CAMPO,
                        "PAPEL_NA_LEI": PAPEL_NA_LEI[CAMPO], "ORIGEM": "CITADO", "ANCORA": a["FACT_LOCATION_ANCHOR"],
                        "ESPECIE": "OCORRENCIA", "TIPO_DE_EVIDENCIA": a["TYPE_OF_EVIDENCE"], "TRECHO": _trecho(a["FACT_LOCATION_EVIDENCE"])})
    sobra = []
    for r in recusadas:
        kind, ancora, especie = None, None, None
        pos = _posicao_do_nome(r["PLACE"], r["EVIDENCE"])
        if r["STATE"] != FL.TERRITORIAL_LIST and pos is not None:
            # a ancora MAIS PERTO do lugar decide, antes ou depois dele («del mercato In Sardegna si producono»)
            cands = []
            if r["WHY"] in RECUSA_QUE_PODE_SER_EVENTO:
                cands += [(m, EVENTO, None) for m in _RE_EVENTO.finditer(r["EVIDENCE"])]
            if r["WHY"] in RECUSA_QUE_PODE_SER_PRODUCAO:
                cands += [(m, CAMPO, "PRODUCAO") for m in _RE_PRODUCAO.finditer(r["EVIDENCE"])
                          if _distancia(m, pos, len(r["PLACE"])) <= DISTANCIA_MAXIMA_DA_PRODUCAO]
            if r["WHY"] in RECUSA_QUE_E_MERCADO:
                cands += [(m, MERCADO, None) for m in _RE_MERCADO.finditer(r["EVIDENCE"])]
            if cands:
                m, kind, especie = min(cands, key=lambda c: _distancia(c[0], pos, len(r["PLACE"])))
                ancora = m.group(0)
        if not kind or (kind, r["PLACE"]) in vistos or (CAMPO, r["PLACE"]) in vistos:
            sobra.append(r)
            continue
        vistos.add((kind, r["PLACE"]))
        # TIPO_DE_EVIDENCIA fica OTHER: evento, mercado e lugar de producao nunca sao foco/observacao/amostra.
        lugares.append({"LUGAR": r["PLACE"], "PRECISAO": r["PRECISION"], "KIND": kind,
                        "PAPEL_NA_LEI": PAPEL_NA_LEI[kind], "ORIGEM": "CITADO", "ANCORA": ancora,
                        "ESPECIE": especie or kind,
                        "TIPO_DE_EVIDENCIA": FL.OTHER_EVIDENCE, "TRECHO": _trecho(r["EVIDENCE"])})
    return lugares, sobra


_PRECISAO_ORDEM = ("MUNICIPALITY", "PROVINCE", "REGION", "COUNTRY")


def campos_do_fato(texto: str, publication_time: str | None = None,
                   publication_time_basis: str | None = None) -> dict:
    c = corpo(texto)
    pub = publicacao_provada(publication_time, publication_time_basis)

    # ── lugar
    lugares, recusadas = _lugares(c)
    kind_l = next((k for k in ORDEM_DOS_TIPOS if any(l["KIND"] == k for l in lugares)), None)
    if kind_l:
        esc = [l for l in lugares if l["KIND"] == kind_l]
        fact_location = SEP.join(l["LUGAR"] for l in esc)
        fact_location_precision = next((p for p in _PRECISAO_ORDEM if any(l["PRECISAO"] == p for l in esc)), esc[0]["PRECISAO"])
        fact_location_basis = SEP.join("%s · %s · CITADO · %s · âncora «%s» · %s · «%s»"
                                       % (kind_l, l["ESPECIE"], l["PRECISAO"], l["ANCORA"], l["TIPO_DE_EVIDENCIA"], l["TRECHO"]) for l in esc)
        outros = [l for l in lugares if l["KIND"] != kind_l]
        if outros:
            fact_location_basis += " · também citados, de outro tipo: " + ", ".join("%s (%s)" % (l["LUGAR"], l["KIND"]) for l in outros)
    else:
        mencionados = sorted({r["PLACE"] for r in recusadas})
        fact_location = fact_location_precision = NAO_SEI
        fact_location_basis = ("NAO SEI · nenhum lugar ligado a um acontecimento, evento técnico ou mercado no corpo do texto"
                               + (" (só mencionados: %s)" % ", ".join(mencionados[:8]) if mencionados else "")
                               + ("" if c else " · o texto não tem corpo (só menu/rodapé)"))

    # ── tempo · pela ordem: data explicita de CAMPO > relativa de CAMPO > data de EVENTO > relativa de EVENTO
    t, tapados, relativas = _tapar(c)
    for x in relativas:                    # a que tipo de facto a expressao esta presa, pela frase dela
        antes, depois = x.pop("_ANTES"), x.pop("_DEPOIS")
        if _RE_INSTITUCIONAL.search(x["TRECHO"]):
            x["KIND"], x["PORQUE"] = None, "frase institucional (exame, aula, curso…): não é facto do agro"
        else:
            x["KIND"] = CAMPO if _presa_ao_campo(x["TRECHO"]) else EVENTO if _RE_EVENTO.search(x["TRECHO"]) else None
            x["PORQUE"] = None if x["KIND"] else "a frase não fala de um acontecimento nem de um evento técnico"
        vale, porque = _oggi_vale(x["EXPRESSAO"], antes, depois)
        if vale and _RE_COMPARACAO.search(antes):
            vale, porque = False, "termo de comparação («%s»), não o tempo do facto" % _trecho(antes, 50)
        if not vale:
            x["PORQUE"] = porque
        cr = conta_relativa(x["EXPRESSAO"], pub) if (pub and x["KIND"] and vale) else None
        x["CONTA"] = {"VALOR": cr[0], "RESOLUCAO": cr[1]} if cr else None
    r = _tempo_de_campo(t, pub, tapados)
    eventos = []
    for e in _tempos_de_evento(t, pub):
        if _RE_INSTITUCIONAL.search(e["TRECHO"]):
            tapados.append("INSTITUCIONAL_NAO_FATO «%s»" % e["VALOR"])
        else:
            eventos.append(e)

    ambiguas = {}

    def _rel_de(kind):
        xs = [x for x in relativas if x["KIND"] == kind and x["CONTA"]]
        if len({x["CONTA"]["VALOR"] for x in xs}) > 1:
            # duas contas diferentes presas ao mesmo tipo de facto: nao se sabe qual e a do facto
            ambiguas[kind] = ", ".join("«%s» → %s" % (x["EXPRESSAO"], x["CONTA"]["VALOR"]) for x in xs[:4])
            return None
        x = xs[0] if xs else None
        return x and {"VALOR": x["CONTA"]["VALOR"], "KIND": kind, "ORIGEM": RELATIVA,
                      "RESOLUCAO": x["CONTA"]["RESOLUCAO"], "CALCULADA": True, "EXPRESSAO": x["EXPRESSAO"],
                      "TRECHO": x["TRECHO"]}
    tempo = None
    if r.get("FACT_TIME") not in (None, "NOT_KNOWN"):
        tempo = {"VALOR": r["FACT_TIME"], "KIND": CAMPO, "ORIGEM": "AMARRADO_AO_ACONTECIMENTO",
                 "RESOLUCAO": RESOLUCAO.get(r.get("FACT_TIME_PRECISION"), "APPROXIMATE"),
                 "TRECHO": _trecho(r.get("FACT_TIME_EVIDENCE"))}
    tempo = tempo or _rel_de(CAMPO)
    if not tempo and eventos:
        e = eventos[0]
        tempo = {"VALOR": e["VALOR"], "KIND": EVENTO, "ORIGEM": "ESCRITO_NO_TEXTO", "RESOLUCAO": e["RESOLUCAO"],
                 "ANCORA": e["ANCORA"], "TRECHO": e["TRECHO"]}
    tempo = tempo or _rel_de(EVENTO)
    # D69 (corrige a DA-7): quando a data e CALCULADA, fact_time_basis = RELATIVA_A_PUBLICACAO, SEMPRE —
    # tambem para «oggi» marcado. PUBLISHED_AT_COM_PROVA afirmaria «o mesmo instante», o que nao foi provado.
    # O como/porque (expressao, conta, trecho) vai para fact_time_calculo / fact_time_evidencia.
    fact_time_calculo = fact_time_evidencia = NAO_SE_APLICA
    if tempo:
        fact_time, fact_time_kind = tempo["VALOR"], tempo["KIND"]
        fact_time_precision = tempo["RESOLUCAO"] + ("+CALCULADA" if tempo.get("CALCULADA") else "")
        if tempo.get("CALCULADA"):
            fact_time_basis = RELATIVA
            fact_time_calculo = RELATIVA
            fact_time_evidencia = ("%s · %s · «%s» contado a partir da publicação provada %s (%s) · «%s»"
                                   % (tempo["KIND"], fact_time_precision, tempo["EXPRESSAO"], pub.isoformat(),
                                      _trecho(publication_time_basis, 60), tempo["TRECHO"]))[:800]
        else:
            fact_time_basis = "%s · %s · %s%s · «%s»" % (tempo["KIND"], tempo["ORIGEM"], tempo["RESOLUCAO"],
                                                         " · âncora «%s»" % tempo["ANCORA"] if tempo.get("ANCORA") else "",
                                                         tempo["TRECHO"])
    else:
        fact_time = fact_time_kind = NAO_SEI
        fact_time_precision = "NOT_KNOWN"
        why = "nenhuma data explícita do texto ligada ao acontecimento ou a um evento técnico"
        if tapados:
            why += "; descartadas (não são tempo do facto): %s" % ", ".join(tapados)
        for k, v in ambiguas.items():
            why += "; AMBIGUO (%s): contas diferentes no mesmo texto, não se sabe qual é a do facto: %s" % (k, v)
        if relativas and not pub:
            why += ("; expressões relativas guardadas como evidência, sem conta (publicação não provada): %s"
                    % ", ".join("«%s»" % x["EXPRESSAO"] for x in relativas[:6]))
        elif relativas and not ambiguas:
            why += "; expressões relativas guardadas como evidência, sem conta: %s" % ", ".join(
                "«%s» (%s)" % (x["EXPRESSAO"], x.get("PORQUE") or "sem medida") for x in relativas[:6])
        fact_time_basis = "NAO SEI · " + why
    if fact_time_calculo == NAO_SE_APLICA:
        fact_time_basis += " · a data de publicação sozinha nunca preenche este campo"

    return {"fact_location": fact_location, "fact_location_basis": fact_location_basis[:1000],
            "fact_location_kind": kind_l or NAO_SEI, "fact_location_precision": fact_location_precision,
            "fact_time": fact_time, "fact_time_basis": fact_time_basis[:800],
            "fact_time_kind": fact_time_kind, "fact_time_precision": fact_time_precision,
            "fact_time_calculo": fact_time_calculo, "fact_time_evidencia": fact_time_evidencia,
            "EVIDENCIA": {"LUGARES": lugares, "TEMPO": tempo, "TEMPOS_DE_EVENTO": eventos,
                          "EXPRESSOES_RELATIVAS": relativas,
                          "PUBLICACAO_PROVADA": pub.isoformat() if pub else None,
                          "LINHAS_DE_CORPO": len(c.splitlines()) if c else 0}}


if __name__ == "__main__":
    ex = ("Home\nNotizie\nFusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo.\n"
          "Il convegno sulla difesa del grano si terrà a Bologna il 12 e 13 novembre 2026 con i tecnici regionali.\n"
          "DIREZIONE GENERALE Via Po, 5 - 40139 Bologna centralino 051 6223811")
    import json
    print(json.dumps(campos_do_fato(ex, "2026-09-23", "meta article:published_time"), ensure_ascii=False, indent=1))
