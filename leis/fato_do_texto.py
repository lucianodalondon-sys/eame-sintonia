#!/usr/bin/env python3
"""O LUGAR E O TEMPO DO FACTO, TIRADOS DO TEXTO — os quatro campos da Sala, com a prova e o TIPO.

    campos_do_fato(texto, publication_time=None, publication_time_basis=None, *, titulo=None, descricao=None) -> dict

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
    fact_time_expressao      quando CALCULADA: a expressao original («ieri», «oggi»); NAO_SE_APLICA nos outros
    fact_time_evidencia      quando CALCULADA: o trecho onde a expressao esta; NAO_SE_APLICA nos outros casos
                             (D69/D70: com a data calculada, fact_time_basis e SO «RELATIVA_A_PUBLICACAO»; um dia
                             calculado escreve-se como dia, «AAAA-MM-DD». `leis/artefato.py::conferir` refaz a conta
                             com `verificar_relativa` e reprova se nao der o mesmo valor)
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


def _palavras(l: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ']+", l))


# ── o TITULO e a DESCRICAO (EXTRATOR-EVENTO-V2, 26/09) ──────────────────────
# Medido na RENDIMENTO-POR-FONTE: o texto guardado de um video e SO o titulo (60-100 letras), e a regra das 8
# palavras deitava-o fora inteiro — «Potatura dell'olivo: a Macerata la 9a selezione studenti - YouTube»
# nunca chegava ao leitor. Um texto em que NENHUMA linha e frase longa nao e um menu com uma noticia no
# meio: e um titulo. Lido como titulo: no maximo 2 linhas de >= PALAVRAS_DO_TITULO palavras, sem o nome do
# sitio no fim («… - YouTube», «… — Arpae Emilia-Romagna»: e quem publica, nao onde o facto foi).
PALAVRAS_DO_TITULO = 3
LINHAS_DO_TITULO = 2
_RE_SUFIXO_DO_SITIO = re.compile(r"\s+(?:[-–—|])\s+[^-–—|]{2,60}$")


def titulo_limpo(t: str) -> str:
    l = re.sub(r"\s+", " ", str(t or "")).strip()
    s = _RE_SUFIXO_DO_SITIO.sub("", l)
    return s if _palavras(s) >= PALAVRAS_DO_TITULO else l


def _linhas_curtas(texto: str) -> list:
    return [titulo_limpo(l) for l in str(texto or "").splitlines()
            if l.strip() and not RODAPE.search(l) and _palavras(titulo_limpo(l)) >= PALAVRAS_DO_TITULO]


def corpo(texto: str) -> str:
    """As linhas do texto que sao frase de conteudo — menu, cabecalho e rodape ficam de fora.
    Um texto sem NENHUMA frase longa e lido como titulo (ver acima)."""
    fica = []
    for linha in str(texto or "").splitlines():
        l = linha.strip()
        if _palavras(l) < PALAVRAS_MINIMAS:
            continue
        if RODAPE.search(l):
            continue
        fica.append(l)
    if not fica:
        fica = _linhas_curtas(texto)[:LINHAS_DO_TITULO]
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
    """O dia calculado escreve-se como o DIA: «2026-09-21». (A D69 escrevia-o como intervalo desse dia
    so para fugir a comparacao de letras de `leis/artefato.py::conferir`; a D70 chamou-lhe contorno da
    lei, e a lei passou a conferir a conta — ver `verificar_relativa`.)"""
    return d.isoformat()


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


# ── D70 · A VERIFICACAO UNICA DE UMA DATA RELATIVA ───────────────────────────
# O extrator e a lei (`leis/artefato.py::conferir`) chamam ESTA funcao. Assim os dois nunca discordam:
# a lei refaz, a partir da publicacao + expressao + trecho guardados, exatamente a conta do extrator.
def verificar_relativa(expressao: str, trecho: str, publicacao: date | None):
    """((valor, resolucao) | None, porque | None).

    Confere, no TRECHO guardado: a expressao esta la; nao e «oggi» no sentido de «hoje em dia» (D64);
    nao e termo de comparacao; e tem medida. Com `publicacao` (dia provado), faz a conta. Sem ela,
    devolve (None, None) se a expressao e valida, e (None, porque) se nao e."""
    t = str(trecho or "")
    m = re.search(r"(?<![0-9a-zà-ÿ])%s(?![0-9a-zà-ÿ])" % re.escape(str(expressao or "")), t, re.I) if expressao else None
    if not m:
        return None, "a expressao «%s» nao esta no trecho guardado" % expressao
    antes, depois = t[max(0, m.start() - 50):m.start()], t[m.end():m.end() + 40]
    vale, porque = _oggi_vale(m.group(0), antes, depois)
    if not vale:
        return None, porque
    if _RE_COMPARACAO.search(antes):
        return None, "termo de comparação («%s»), não o tempo do facto" % _trecho(antes, 50)
    if _regra(m.group(0))[0] == "SEM_MEDIDA":
        return None, "«%s» não diz quanto tempo: sem medida, não vira data" % m.group(0)
    if publicacao is None:
        return None, None
    return conta_relativa(m.group(0), publicacao), None


def _janela(t: str, ini: int, fim: int) -> str:
    """O trecho de uma expressao: a frase dela, cortada a 150 letras de cada lado — a expressao fica
    SEMPRE dentro (a lei confere-a no trecho guardado)."""
    a = max(t.rfind(c, 0, ini) for c in ".!?;\n") + 1
    fins = [i for i in (t.find(c, fim) for c in ".!?;\n") if i != -1]
    b = min(fins) if fins else len(t)
    return _trecho(t[max(a, ini - 150):min(b, fim + 150)], 400)


# ── as ancoras do leitor, mas com PALAVRA INTEIRA a esquerda ────────────────
# `fato_local.tempo_do_fato` procura as suas ancoras sem fronteira: «coltura» casa dentro de
# «arboricoltura» e «agricoltura». Medido nas 78: «esame del modulo di arboricoltura … previsto per il 21
# settembre» e «Laurea … nel 2022» (agricoltura) sairam como tempo de CAMPO. A ancora so conta quando
# COMECA uma palavra (a direita fica aberta: sao raizes — «contaminaz», «superament»).
_RE_ANCORAS_DE_CAMPO = re.compile(r"(?<![0-9a-z])(?:%s)" % "|".join(FL.ANCORAS_DE_TEMPO_DO_FATO))


def _presa_ao_campo(frase: str) -> bool:
    return _RE_ANCORAS_DE_CAMPO.search(FL._baixo(frase)) is not None


# O leitor tem DUAS listas de palavras de acontecimento: uma para o tempo (ANCORAS_DE_TEMPO_DO_FATO) e outra
# para o lugar (ANCORAS_POSITIVAS). Medido no ensaio do PACOTE (IT-T3-008): «lo scarto climatico registrato
# nella settimana scorsa … su gran parte della Puglia» dava o LUGAR (âncora «registrato») e deixava a DATA
# em NAO SEI, na mesma frase — «registrato» so esta na lista do lugar. Uma relativa fica presa ao facto se a
# frase tiver palavra de QUALQUER das duas listas. «bollettino» fica de fora: «il prossimo bollettino … la
# prossima settimana» fala do boletim, nao de um acontecimento.
_ANCORAS_DE_LUGAR_PARA_O_TEMPO = tuple(a for a in FL.ANCORAS_POSITIVAS if "bollettino" not in a[0])


def _relativa_presa_ao_campo(frase: str) -> bool:
    return _presa_ao_campo(frase) or bool(FL._ancoras(frase, _ANCORAS_DE_LUGAR_PARA_O_TEMPO))


# ── o CONSELHO nao e facto acontecido ─────────────────────────────────────────
# Medido nas 78 (IT-T3-010): «- eseguire la "diagnosi precoce" in luglio e agosto per verificare…» saia
# fact_time = luglio. E uma recomendacao para o futuro: NAO SEI, e o mes fica em EVIDENCIA.JANELA_RECOMENDADA.
_RE_RECOMENDACAO = re.compile(
    r"(?<![0-9a-zà-ÿ])(?:si\s+consiglia|si\s+raccomanda|si\s+suggerisce|si\s+invita(?:no)?|si\s+ricorda\s+di|"
    r"(?:è|e['’])\s+(?:consigliabile|opportuno|necessario|bene)|occorre|bisogna|consigliat[oaie]|raccomandat[oaie]|"
    r"da\s+(?:eseguire|effettuare|fare)|si\s+dovr[àa])(?![0-9a-zà-ÿ])"
    r"|^\s*[-•*–]?\s*(?:eseguire|effettuare|fare|intervenire|trattare|monitorare|controllare|verificare|applicare|"
    r"installare|posizionare|distribuire|irrigare|potare|programmare|prevedere)(?![0-9a-zà-ÿ])", re.I)


# ── a frase institucional: data de exame, aula, curso, inscricao nao e facto do agro ──
# (coordenacao, 25/09: «exame de faculdade adiado nao e facto do ecossistema agro» -> INSTITUCIONAL_NAO_FATO,
# o mesmo nome do tipo da REGUA-FATO, `leis/tipo_do_fato.py`)
_RE_INSTITUCIONAL = re.compile(
    r"(?<![0-9a-zà-ÿ])(?:esam[ei]|appell[oi]|lezion[ei]|laure[ae]|corsi?\s+di\s+(?:laurea|studi[oa]?)|iscrizion[ei]|"
    r"immatricolazion[ei]|bando|concors[oi]|tesi|tirocini[oa]?|graduatori[ae]|cfu|didattic[ao]|dottorat[oi]|"
    r"sessione\s+di\s+laurea|colloqui[oa]?)(?![0-9a-zà-ÿ])", re.I)


# ── o que AINDA NAO ACONTECEU nao e facto ocorrido (EXTRATOR-EVENTO-V2, 26/09) ──
# Com o tempo e o fogo na lista das ancoras, uma frase de ALERTA passa a ter ancora e data: «Allerta meteo:
# previste per il 28 settembre raffiche di vento». Isso e previsao, nao acontecimento. Duas guardas:
#   1. a frase tem marca de previsao/futuro;
#   2. a data resolve para DEPOIS da publicacao PROVADA — o texto nao pode contar o que ainda nao aconteceu.
_RE_FUTURO = re.compile(
    r"(?<![0-9a-zà-ÿ])(?:allert[ae]|allarm[ei]\s+meteo|previst[oaie]|prevision[ei]|si\s+prevede|sono\s+attes[ie]|"
    r"(?:è|e['’])\s+attes[oa]|attes[oaie]\s+(?:per|nel|nella|tra)|domani|dopodomani|"
    r"nei\s+prossimi\s+giorni|nelle\s+prossime\s+(?:ore|settimane)|prossim[oaie]\s+(?:giorn|settiman|ore))(?![0-9a-zà-ÿ])",
    re.I)


def _depois_da_publicacao(valor: str, pub: date | None) -> bool:
    if not pub:
        return False
    d = FL._resolve_dia(valor, pub.year)
    return bool(d) and date(*d) > pub


def _tempo_de_campo(t: str, pub: date | None, tapados: list, janelas: list | None = None) -> dict:
    """Pergunta ao leitor; se a data que ele escolhe vem de uma frase institucional, de um CONSELHO, ou de
    uma ancora que so existia DENTRO de outra palavra, tapa-a nessa frase e pergunta de novo."""
    conselhos = []            # medido (IT-T3-010): a mesma frase de conselho repete-se partida por uma quebra
    for _ in range(12):       # de linha («precoce" in luglio…») — o pedaco de um conselho continua conselho
        r = FL.tempo_do_fato(t, pub.isoformat() if pub else None)
        v, ev = r.get("FACT_TIME"), r.get("FACT_TIME_EVIDENCE") or ""
        if v in (None, "NOT_KNOWN"):
            return r
        pedaco = _trecho(ev, 400).lower()
        e_conselho = bool(_RE_RECOMENDACAO.search(ev)) or (len(pedaco) >= 30 and any(pedaco in c for c in conselhos))
        if e_conselho:
            conselhos.append(pedaco)
        motivo = ("INSTITUCIONAL_NAO_FATO" if _RE_INSTITUCIONAL.search(ev)
                  else "RECOMENDACAO_NAO_FATO" if e_conselho
                  else "PREVISAO_NAO_E_FATO" if _RE_FUTURO.search(ev) or _depois_da_publicacao(v, pub)
                  else None if _presa_ao_campo(ev) else "ANCORA_DENTRO_DE_OUTRA_PALAVRA")
        if not motivo:
            return r
        if motivo == "RECOMENDACAO_NAO_FATO" and janelas is not None and not any(
                j["VALOR"] == v and _trecho(ev, 400).lower() in j["TRECHO"].lower() for j in janelas):
            janelas.append({"VALOR": v, "TRECHO": _trecho(ev, 400)})
        if "%s «%s»" % (motivo, v) not in tapados:
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
    # CONSERTO-REGUA (SALA-VERIFICA, 26/09): o ANO DE COMPARACAO nao e o tempo do facto. Medido na Sala
    # (IT-T10-018): «Il valore resta sotto i circa 2,80 euro/kg del 2025» saia fact_time = 2025 — e o ano
    # de um PRECO de referencia. Tapa-se o ano quando vem logo depois de uma QUANTIDADE COM UNIDADE
    # («2,80 euro/kg del 2025», «27% … del 2024») ou de uma COMPARACAO dita («rispetto al raccolto del 2025»).
    # «Nel 2025 il gruppo … ha raggiunto l'obiettivo» NAO casa: nao ha quantidade antes do ano.
    ("TERMO_DE_COMPARACAO", re.compile(
        r"(?:\d+(?:[.,]\d+)?\s*(?:%|€|euro(?:/kg)?|eur|tonnellat[ea]|quintal[ie]|ettari|kg|q\.li)"
        r"(?![0-9a-zà-ÿ])[^.;\n]{0,20}?"
        r"|(?:rispetto|in\s+confronto|a\s+confronto|contro|sotto|sopra|oltre)\s+"
        r"(?:a[il]?|all['’]|allo|alla|agli|con(?:\s+il)?|i|il|lo|la|gli)\b[^.;\n]{0,40}?)"
        r"(?<![0-9a-zà-ÿ])(?:del|dell['’]|nel)\s*(?:19|20)\d{2}(?![0-9])", re.I)),
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
        # o TIPO decide-se pela FRASE INTEIRA; o TRECHO guardado e a janela onde a lei re-encontra a expressao
        relativas.append({"EXPRESSAO": m.group(0), "TRECHO": _janela(orig, m.start(), m.end()),
                          "_FRASE": _frase_em(orig, m.start())})
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
# lojas: o preco medido em «14 punti vendita» a Firenze e MERCADO (ensaio do PACOTE, IT-T10-018). So perto
# do lugar (a mesma distancia da producao) e so palavras de loja — «prezzo» ficou de fora: os titulos da
# barra lateral («a Firenze prezzo mirtilli») repetem-se em dezenas de paginas.
_RE_LOJA = re.compile(r"(?<![0-9a-zà-ÿ])(?:punt[oi]\s+(?:di\s+)?vendita|grande\s+distribuzione|"
                      r"supermercat[oi]|ipermercat[oi])(?![0-9a-zà-ÿ])", re.I)
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


def _tempos_de_evento(t: str, pub: date | None, original: str | None = None) -> list:
    """CONSERTO-REGUA (SALA-VERIFICA, 26/09): o TRECHO de uma data de evento e uma janela em volta da data,
    tirada do texto ORIGINAL. Medido na Sala: «… in calendario dal 21 al 23 ottob» (cortado nas 200 letras,
    IT-T9-021) e «E' quanto emerso durante …» com o «oggi» ja tapado (IT-T10-018) — nos dois, o trecho
    guardado nao se re-encontrava no bruto. `_tapar` troca por espacos, e por isso as posicoes do texto
    tapado e do original sao as mesmas."""
    fora = []
    base = original if original is not None and len(original) == len(t) else t
    cursor = 0
    for frase in FL._frases(t):
        ini_f = t.find(frase, cursor)
        if ini_f >= 0:
            cursor = ini_f + len(frase)
        ev = _RE_EVENTO.search(frase)
        if not ev:
            continue
        for m in _RE_DATA_EVENTO.finditer(frase):
            d1, d2, mes, ano = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
            if pub and not d2 and int(d1) == pub.day and FL.MES_NUM[mes] == pub.month \
                    and (not ano or int(ano) == pub.year):
                continue                                   # e o carimbo da publicacao, nao o evento
            valor = ("%s-%s %s" % (d1, d2, mes) if d2 else "%s %s" % (d1, mes)) + (" %s" % ano if ano else "")
            trecho = (_janela(base, ini_f + m.start(), ini_f + m.end()) if ini_f >= 0
                      else _trecho(frase))
            fora.append({"VALOR": valor, "RESOLUCAO": "APPROXIMATE" if d2 else "DATE_EXACT",
                         "ANCORA": ev.group(0), "TRECHO": trecho})
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


def _janela_do_lugar(frase: str, lugar: str) -> str:
    """CONSERTO-REGUA (SALA-VERIFICA, 26/09): o trecho de um lugar e uma JANELA EM VOLTA DELE, e nao o
    comeco da frase. Medido na Sala (IT-T10-018): «… le ondate di calore che hanno colpito la Sicilia»
    guardava so as primeiras 200 letras da frase, e «Sicilia» ficava FORA da prova."""
    pos = _posicao_do_nome(lugar, frase)
    if pos is None:
        m = re.search(r"(?<![0-9a-zà-ÿ])%s(?![0-9a-zà-ÿ])" % re.escape(lugar.lower()), frase.lower())
        pos = m.start() if m else None
    if pos is None:
        return _trecho(frase, 400)
    return _janela(frase, pos, pos + len(lugar))


def _frase_do_corpo(c: str, evidencia: str) -> str:
    i = c.find(evidencia[:80])
    return _frase_em(c, i) if i >= 0 else evidencia


def _datas_de_evento(frase: str) -> list:
    """As datas de evento escritas numa frase, na forma de `_tempos_de_evento` (sem o filtro da publicacao)."""
    fora = []
    for m in _RE_DATA_EVENTO.finditer(frase):
        d1, d2, mes, ano = m.group(1), m.group(2), m.group(3).lower(), m.group(4)
        fora.append(("%s-%s %s" % (d1, d2, mes) if d2 else "%s %s" % (d1, mes)) + (" %s" % ano if ano else ""))
    return fora


# ── 4c · o lugar que e PEDACO DE UM NOME nao e lugar do facto (PERIODO-E-CHAVES, 26/09) ──
# Lidos a mao na QUATRO-CHAVES-MEDIR (12 regioes, 3 erradas): «oltre che Bologna Fiere, socio di
# FederBio» (Bologna e o nome de uma EMPRESA) e «ARPA Lazio – Seminario» (Lazio e o nome do ORGAO que
# publica). O lugar colado a um nome de orgao/empresa e o nome, nao o sitio do acontecimento — SALVO
# se uma preposicao de lugar vem antes do nome: «a Fiera Bolzano», «presso ARPA Lazio» sao o LOCAL.
# (O terceiro erro, a pagina com dois eventos, ja e do CONSERTO-REGUA: datas de evento diferentes.)
_ORGAO_ANTES = re.compile(r"(?<![0-9a-zà-ÿ])(?:arpa[a-z]{0,3}|appa|agenzia\s+regionale(?:\s+[a-zà-ÿ]+){0,4})\s+$", re.I)
_EMPRESA_DEPOIS = re.compile(r"^\s+(?:fiere|s\.?p\.?a\.?|s\.?r\.?l\.?|group|holding)(?![0-9a-zà-ÿ])", re.I)
_PREPOSICAO_DE_LUGAR = re.compile(r"(?<![0-9a-zà-ÿ])(?:a|ad|in|presso|alla|al|nella|nel|dalla|dal)\s+$", re.I)


def _e_pedaco_de_nome(frase: str, pos: int, lugar: str) -> str | None:
    """O nome de orgao/empresa de que o lugar e pedaco, ou None. So le a frase."""
    antes, depois = frase[:pos], frase[pos + len(lugar):]
    m = _ORGAO_ANTES.search(antes)
    if m:
        inicio = m.start()
    elif _EMPRESA_DEPOIS.match(depois):
        inicio = pos
    else:
        return None
    if _PREPOSICAO_DE_LUGAR.search(frase[:inicio]):
        return None
    fim = pos + len(lugar) + (len(_EMPRESA_DEPOIS.match(depois).group(0)) if _EMPRESA_DEPOIS.match(depois) else 0)
    return frase[inicio:fim].strip()


def _lugares(c: str) -> tuple[list, list]:
    aceitas, recusadas = FL.localizacoes_do_fato(c, origem="TEXTO_DO_CORPO")
    lugares, vistos = [], set()
    for a in aceitas:
        vistos.add((CAMPO, a["FACT_LOCATION"]))
        frase = _frase_do_corpo(c, a["FACT_LOCATION_EVIDENCE"])
        lugares.append({"LUGAR": a["FACT_LOCATION"], "PRECISAO": a["FACT_LOCATION_PRECISION"], "KIND": CAMPO,
                        "PAPEL_NA_LEI": PAPEL_NA_LEI[CAMPO], "ORIGEM": "CITADO", "ANCORA": a["FACT_LOCATION_ANCHOR"],
                        "ESPECIE": "OCORRENCIA", "TIPO_DE_EVIDENCIA": a["TYPE_OF_EVIDENCE"],
                        "TRECHO": _janela_do_lugar(frase, a["FACT_LOCATION"]),
                        "_DATAS": _datas_de_evento(frase)})
    sobra = []
    for r in recusadas:
        kind, ancora, especie = None, None, None
        # o leitor guarda so as primeiras 300 letras da frase: a palavra de evento pode vir depois (IT-T5-030,
        # «… dell'Università di Teramo ospita … seminario»). Le-se a frase INTEIRA do corpo.
        i = c.find(r["EVIDENCE"][:80])
        frase = _frase_em(c, i) if i >= 0 else r["EVIDENCE"]
        r = dict(r, EVIDENCE=frase)
        pos = _posicao_do_nome(r["PLACE"], r["EVIDENCE"])
        # Nas 78, TODO o lugar do tamanho de um pais promovido aqui estava errado (4 de 4: «focus sull'Italia»,
        # «Made in Italy», o menu de paises): numa fonte italiana, «Italia» como lugar de evento/mercado/
        # producao nao diz nada. E um nome maior que contem uma provincia nao e a provincia.
        if r["PRECISION"] == "COUNTRY" or (pos is not None and _NOME_MAIOR.search(r["EVIDENCE"][max(0, pos - 12):pos + len(r["PLACE"]) + 12])):
            pos = None
        if pos is not None and _e_pedaco_de_nome(r["EVIDENCE"], pos, r["PLACE"]):
            r = dict(r, WHY_NOME=_e_pedaco_de_nome(r["EVIDENCE"], pos, r["PLACE"]))
            pos = None
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
            if r["WHY"] in RECUSA_QUE_PODE_SER_PRODUCAO:
                cands += [(m, MERCADO, None) for m in _RE_LOJA.finditer(r["EVIDENCE"])
                          if _distancia(m, pos, len(r["PLACE"])) <= DISTANCIA_MAXIMA_DA_PRODUCAO]
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
                        "TIPO_DE_EVIDENCIA": FL.OTHER_EVIDENCE,
                        "TRECHO": _janela_do_lugar(r["EVIDENCE"], r["PLACE"]),
                        "_DATAS": _datas_de_evento(r["EVIDENCE"])})
    return lugares, sobra


_PRECISAO_ORDEM = ("MUNICIPALITY", "PROVINCE", "REGION", "COUNTRY")
# nomes maiores que contem um topónimo do gazetteer e nao sao ele (medido: «dall'America Latina» -> Latina)
_NOME_MAIOR = re.compile(r"America\s+Latina|Latinoamerica", re.I)


def corpo_com_titulo_e_descricao(texto: str, titulo: str | None = None, descricao: str | None = None) -> str:
    """O corpo, com o TITULO (uma frase, mesmo curta) e a DESCRICAO do video (as linhas dela que tenham
    PALAVRAS_DO_TITULO palavras; sem rodape) a frente. Nada disto e a data de publicacao: e texto do autor."""
    partes = []
    t = titulo_limpo(titulo) if titulo else ""
    if t and _palavras(t) >= PALAVRAS_DO_TITULO:
        partes.append(t)
    if descricao:
        partes += [l for l in _linhas_curtas(descricao) if l not in partes]
    c = corpo(texto)
    partes += [l for l in c.splitlines() if l and l not in partes]
    return "\n".join(partes)


def campos_do_fato(texto: str, publication_time: str | None = None,
                   publication_time_basis: str | None = None, *,
                   titulo: str | None = None, descricao: str | None = None) -> dict:
    c = corpo_com_titulo_e_descricao(texto, titulo, descricao)
    pub = publicacao_provada(publication_time, publication_time_basis)

    # ── lugar (os candidatos; a montagem vem depois do tempo — ver «lista de eventos»)
    lugares, recusadas = _lugares(c)
    # ── tempo · pela ordem: data explicita de CAMPO > relativa de CAMPO > data de EVENTO > relativa de EVENTO
    t, tapados, relativas = _tapar(c)
    for x in relativas:                    # a que tipo de facto a expressao esta presa, pela frase dela
        frase = x.pop("_FRASE")
        if _RE_INSTITUCIONAL.search(frase):
            x["KIND"], x["PORQUE"] = None, "frase institucional (exame, aula, curso…): não é facto do agro"
        elif _RE_RECOMENDACAO.search(frase):
            x["KIND"], x["PORQUE"] = None, "conselho / recomendação: não é facto acontecido"
        else:
            x["KIND"] = CAMPO if _relativa_presa_ao_campo(frase) else EVENTO if _RE_EVENTO.search(frase) else None
            x["PORQUE"] = None if x["KIND"] else "a frase não fala de um acontecimento nem de um evento técnico"
            if x["KIND"] == CAMPO and ((_regra(x["EXPRESSAO"])[1] or 0) > 0 or _RE_FUTURO.search(frase)):
                # EXTRATOR-EVENTO-V2: «domani», «la prossima settimana», e qualquer relativa numa frase de
                # previsao falam do que AINDA NAO aconteceu no campo — evidencia, nunca data do facto.
                # O EVENTO tecnico anunciado («il convegno si terrà domani») continua EVENTO (D62).
                x["KIND"], x["PORQUE"] = None, "futuro / previsão: o que ainda não aconteceu no campo não é facto ocorrido"
        cr, porque = verificar_relativa(x["EXPRESSAO"], x["TRECHO"], pub)
        if porque:
            x["PORQUE"] = porque
        cr = cr if x["KIND"] else None
        x["CONTA"] = {"VALOR": cr[0], "RESOLUCAO": cr[1]} if cr else None
    janelas = []
    r = _tempo_de_campo(t, pub, tapados, janelas)
    eventos = []
    for e in _tempos_de_evento(t, pub, c):
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

    # ── CONSERTO-REGUA · uma LISTA de eventos nao junta os lugares de eventos diferentes ──────────────
    # Medido na Sala (IT-T5-090): numa pagina com varios eventos, fact_time = «1-4 febbraio 2023» (Popdays,
    # Roma) e fact_location = «Roma ; Milano ; Brescia ; Padova ; Napoli» — os outros quatro sao de OUTROS
    # eventos da mesma lista. Com 2+ datas de evento diferentes na pagina, um lugar de EVENTO so vale se a
    # sua frase tiver a data do evento escolhido; os outros ficam citados, de outro evento.
    de_outro_evento = []

    def _sem_ano(v):              # «21-23 ottobre 2026» e «21-23 ottobre» sao a mesma data de evento
        return re.sub(r"\s+(?:19|20)\d{2}$", "", str(v or "").strip().lower())
    def _dentro(v, escolhido):    # «22 ottobre» esta dentro de «21-23 ottobre»: e o mesmo evento
        ma = re.match(r"(\d{1,2})(?:-(\d{1,2}))?\s+(\w+)", _sem_ano(escolhido))
        mv = re.match(r"(\d{1,2})(?:-(\d{1,2}))?\s+(\w+)", _sem_ano(v))
        if not (ma and mv) or ma.group(3) != mv.group(3):
            return False
        i, f = int(ma.group(1)), int(ma.group(2) or ma.group(1))
        return i <= int(mv.group(1)) <= f and i <= int(mv.group(2) or mv.group(1)) <= f

    escolhido = tempo["VALOR"] if tempo and tempo["KIND"] == EVENTO else None
    outras = {_sem_ano(e["VALOR"]) for e in eventos
              if not (escolhido and _dentro(e["VALOR"], escolhido))}
    if escolhido and _sem_ano(escolhido) not in outras:
        outras.add(_sem_ano(escolhido))
    if len(outras) >= 2:
        alvo = _sem_ano(tempo["VALOR"]) if tempo and tempo["KIND"] == EVENTO else None
        ficam = []
        for l in lugares:
            if l["KIND"] == EVENTO and not (alvo and alvo in {_sem_ano(d) for d in l["_DATAS"]}):
                de_outro_evento.append(l)
            else:
                ficam.append(l)
        lugares = ficam
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
    if de_outro_evento:
        fact_location_basis += (" · citados noutra frase SEM a data deste evento (a página tem várias datas "
                                "de evento; não são o lugar deste facto): ") + \
            ", ".join(sorted({l["LUGAR"] for l in de_outro_evento}))
    for l in lugares + de_outro_evento:
        l.pop("_DATAS", None)

    # D69 (corrige a DA-7): quando a data e CALCULADA, fact_time_basis = RELATIVA_A_PUBLICACAO, SEMPRE —
    # tambem para «oggi» marcado. PUBLISHED_AT_COM_PROVA afirmaria «o mesmo instante», o que nao foi provado.
    # O como/porque (expressao, conta, trecho) vai para fact_time_calculo / fact_time_evidencia.
    fact_time_calculo = fact_time_evidencia = fact_time_expressao = NAO_SE_APLICA
    if tempo:
        fact_time, fact_time_kind = tempo["VALOR"], tempo["KIND"]
        fact_time_precision = tempo["RESOLUCAO"] + ("+CALCULADA" if tempo.get("CALCULADA") else "")
        if tempo.get("CALCULADA"):
            fact_time_basis = RELATIVA
            fact_time_calculo = RELATIVA
            fact_time_expressao = tempo["EXPRESSAO"]
            fact_time_evidencia = tempo["TRECHO"]          # o trecho onde a lei re-encontra a expressao
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

    # CONSERTO-REGUA: sem o corte das 1000 letras — medido (IT-T5-090) que ele deitava fora a prova do
    # ultimo lugar. Cada trecho ja e uma janela curta (~300 letras) em volta do seu lugar.
    return {"fact_location": fact_location, "fact_location_basis": fact_location_basis,
            "fact_location_kind": kind_l or NAO_SEI, "fact_location_precision": fact_location_precision,
            "fact_time": fact_time, "fact_time_basis": fact_time_basis[:800],
            "fact_time_kind": fact_time_kind, "fact_time_precision": fact_time_precision,
            "fact_time_calculo": fact_time_calculo, "fact_time_expressao": fact_time_expressao,
            "fact_time_evidencia": fact_time_evidencia,
            "EVIDENCIA": {"LUGARES": lugares, "TEMPO": tempo, "TEMPOS_DE_EVENTO": eventos,
                          "JANELA_RECOMENDADA": janelas,
                          "EXPRESSOES_RELATIVAS": relativas,
                          "PUBLICACAO_PROVADA": pub.isoformat() if pub else None,
                          "LINHAS_DE_CORPO": len(c.splitlines()) if c else 0}}


def notas_para_o_artefato(r: dict, publication_time_basis: str | None) -> dict:
    """As NOTES que `leis/artefato.py::conferir` le para refazer a conta de uma data relativa (D70).
    Quem pousa o `campos_do_fato` num Artefato junta isto a NOTES — com os nomes que a lei espera."""
    return {"FACT_TIME_BASIS": r["fact_time_basis"], "PUBLISHED_AT_BASIS": publication_time_basis or NAO_SEI,
            "FACT_TIME_EXPRESSAO": r["fact_time_expressao"], "FACT_TIME_EVIDENCIA": r["fact_time_evidencia"],
            "FACT_TIME_CALCULO": r["fact_time_calculo"], "FACT_TIME_PRECISION": r["fact_time_precision"],
            "FACT_LOCATION_BASIS": r["fact_location_basis"]}


if __name__ == "__main__":
    ex = ("Home\nNotizie\nFusariosi constatata a Grosseto la settimana scorsa, con sintomi osservati in campo.\n"
          "Il convegno sulla difesa del grano si terrà a Bologna il 12 e 13 novembre 2026 con i tecnici regionali.\n"
          "DIREZIONE GENERALE Via Po, 5 - 40139 Bologna centralino 051 6223811")
    import json
    print(json.dumps(campos_do_fato(ex, "2026-09-23", "meta article:published_time"), ensure_ascii=False, indent=1))
