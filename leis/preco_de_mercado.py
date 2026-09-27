#!/usr/bin/env python3
"""POLSO DI MERCATO — o PRECO OBSERVADO tirado de um texto de mercado (myfruit, ISMEA, borse merci, listini).

    precos_do_texto(texto) -> dict
    texto_de_html(html)    -> str      (so tira etiquetas; nao escolhe o corpo)

Funcao PURA (sem rede, sem banco, sem ficheiros). Recebe o texto de UM documento e devolve:

    OBSERVACOES   uma por preco com numero + moeda + unidade:
                  COMMODITY · CULTURA · PRACA · PERIODO (+ _TIPO, _BASIS) · PRECO | PRECO_MIN..PRECO_MAX ·
                  MOEDA · UNIDADE · ESTAGIO (+ _BASIS) · NATUREZA · PAPEL · SERIE · TRECHO
    COMENTARIOS   o que e comentario jornalistico e NAO e preco: variacao sem nivel («+1,7% su base
                  mensile»), opiniao («ritenuto di soddisfazione»), projecao («potrebbe salire a 3 €/kg»),
                  domanda/offerta/vendite — cada um com o PORQUE
    RECUSADOS     valores em euro que nao sao preco unitario (fatturato, capitale sociale, «milioni di
                  euro», preco sem unidade) — com o PORQUE
    COMPARACOES   os trechos de comparacao («rispetto al 2025», «dello scorso anno»): sao a REGUA da
                  comparacao, NUNCA o periodo do facto

AS REGRAS (D84 · Polso di Mercato = cultura + praca + periodo + preco + unidade + estagio; Biblia CAP-MKT)

  1. PERIODO DE REFERENCIA, NUNCA A PUBLICACAO. A funcao nem recebe a data de publicacao nem a de coleta
     (a mesma porta fechada de `fato_do_texto.campos_do_fato`). Data escrita no texto depois de
     «pubblicato/pubblicazione/postato» e tapada. Sem periodo na frase do preco = NAO SEI.
  2. O ANO DE COMPARACAO NAO E DATA. «rispetto al 2025», «come nel 2025», «dello scorso anno», «sul
     2025» sao tapados antes de procurar o periodo. Caso real que motivou a regra: o preco de 2,80 €/kg
     da erba medica (Assosementi, IT-T1-013) com «2025» por perto — o 2025 virou a data do facto.
     Um preco DENTRO da comparacao («rispetto ai 2,50 €/kg del 2025») e outra observacao, com
     PAPEL=REFERENCIA_DE_COMPARACAO e o periodo dela — nunca empresta o 2025 a observacao principal.
  3. PRECO SEM UNIDADE NAO E PRECO COMPARAVEL (CAP-MKT: «comparar precos sem unidade e periodo» e
     MUST_NOT_DO). Vai para RECUSADOS. Unidades: EUR/kg, EUR/t, EUR/q, EUR/hl, EUR/l.
  4. PRECO NAO E DEMANDA NEM VENDA (CAP-MKT: registration · availability · sales · volume · price ·
     market share sao SEIS perguntas). Esta funcao so responde a quinta: nao tem campo de procura,
     venda, volume ou quota, e «fatturato»/«milioni di euro» sao recusados, nao convertidos.
  5. ESTAGIO SO COM MARCADOR ESCRITO na frase: PRODUTOR («alla produzione», «all'origine», «franco
     azienda», «riconosciuto ai soci», «prezzo di riparto»), INGROSSO («all'ingrosso», «mercato
     ortofrutticolo», «borsa merci», «CUN», «franco partenza/arrivo»), DETTAGLIO («al dettaglio», «al
     consumo», «supermercat», «GDO»). Dois estagios diferentes na mesma frase = NAO SEI (conflito dito).
  6. PROJECAO NAO E OBSERVACAO. Preco numa oracao com «potrebbe/dovrebbe/si prevede/previsto/atteso/
     stimato» vai para COMENTARIOS. «prezzo orientativo» e publicado e fica, com NATUREZA=ORIENTATIVO.
  7. SERIE = CULTURA|PRACA|ESTAGIO|UNIDADE|MOEDA, so quando os cinco sao conhecidos; senao NAO SEI com
     o que falta (CAP-MKT: JOIN_KEYS CROP x GEO x PERIOD x UNIT — o periodo e da observacao, nao da serie).

A CULTURA sai do vocabulario do dono (`regua_italia.CULTURAS`); a COMMODITY e o produto de mercado como o
texto o escreve («olio extravergine di oliva», «grano duro») e liga-se a uma chave dessa lista por uma
tabela curta e declarada (COMMODITIES). Commodity fora da tabela = CULTURA NAO SEI, nunca palpite.
"""
from __future__ import annotations

import html as _html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regua_italia as RI    # noqa: E402  (o dono do vocabulario de culturas)

NAO_SEI = "NAO SEI"
PRODUTOR, INGROSSO, DETTAGLIO = "PRODUTOR", "INGROSSO", "DETTAGLIO"
OBSERVACAO, REFERENCIA = "OBSERVACAO", "REFERENCIA_DE_COMPARACAO"

# ── a chave da cultura vem do dono; aqui so o nome de mercado -> chave ─────────────────────────────
CHAVES_DE_CULTURA = frozenset(k for k, _rx, _a in RI.CULTURAS)
# (regex do produto como o mercado o escreve, chave em regua_italia.CULTURAS). Mais especifico primeiro.
COMMODITIES = [
    (r"olio\s+extra\s?vergine(?:\s+di\s+oliva)?|olio\s+vergine(?:\s+di\s+oliva)?|olio\s+lampante|"
     r"olio\s+(?:di|d['’])\s?oliva|olive\s+da\s+(?:olio|tavola)", "OLIVO"),
    (r"grano\s+duro(?:\s+fino)?|grano\s+tenero|frumento\s+(?:duro|tenero)", "FRUMENTO"),
    (r"seme\s+(?:in\s+natura\s+)?(?:certificato\s+)?(?:e\s+pulito\s+)?(?:\(tara\s+0%\)\s+)?di\s+erba\s+medica|"
     r"erba\s+medica", "ERBA_MEDICA"),
    (r"uva\s+da\s+tavola|uva\s+da\s+vino|uve|uva|mosto|vino", "VITE"),
    (r"mais|granoturco|granturco", "MAIS"),
    (r"orzo", "ORZO"), (r"soia", "SOIA"), (r"risone|riso", "RISO"),
    (r"mele|mela", "MELO"), (r"pere|pera", "PERO"),
    (r"pomodor[oi](?:\s+da\s+industria)?", "POMODORO"),
    (r"barbabietol[ae](?:\s+da\s+zucchero)?", "BARBABIETOLA"),
    (r"patate|patata", "PATATA"), (r"girasole", "GIRASOLE"), (r"colza", "COLZA"), (r"sorgo", "SORGO"),
    (r"arance|arancia|limoni|limone|clementine|agrumi", "AGRUMI"),
    (r"pesche|pesca|nettarine|percoche", "PESCO"),
]
RX_COMMODITY = [(re.compile(r"(?<![\w])(?:%s)(?![\w])" % rx, re.I), k) for rx, k in COMMODITIES]
assert all(k in CHAVES_DE_CULTURA for _r, k in COMMODITIES), "COMMODITIES aponta para cultura fora do dono"

# ── numero, moeda, unidade ─────────────────────────────────────────────────────────────────────────
NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+(?:\.\d+)?"
MOEDA = r"(?P<m>€|euro|eur(?![a-z])|\$|usd|dollar[io])"
UNID = (r"(?P<u>kg|chilo(?:grammo)?|kilo(?:grammo)?|tonnellat[ae]|tonn?\.?|t|quintal[ei]|q\.?\s?li|q\.le|q|"
        r"ettolitr[oi]|hl|litr[oi]|l)(?![a-z])")
LIGA = r"\s*(?:/|al(?:l[ae]|l['’])?\s+|per\s+|a\s+|x\s*)\s*"
RX_PRECOS = [
    # 0,90-1,10 €/kg · tra 0,90 e 1,10 euro al chilo · 265 €/t · 47,20 euro al quintale
    re.compile(r"(?<![\d.,])(?P<a>%s)(?:\s*(?:-|–|÷)\s*|\s+e\s+)?(?P<b>%s)?\s*%s%s%s" % (NUM, NUM, MOEDA, LIGA, UNID), re.I),
    # € 1,20/kg · € 1,20 al kg
    re.compile(r"%s\s*(?P<a>%s)(?:\s*(?:-|–)\s*(?P<b>%s))?%s%s" % (MOEDA, NUM, NUM, LIGA, UNID), re.I),
    # €/kg 1,20 (a forma dos listini)
    re.compile(r"%s\s*/\s*%s\s*(?P<a>%s)(?:\s*(?:-|–)\s*(?P<b>%s))?" % (MOEDA, UNID, NUM, NUM), re.I),
]
# euro sem unidade: montante, nunca preco unitario
RX_MONTANTE = re.compile(r"(?:(?:%s)\s*(?:milion[ie]|miliard[ie]|mila|mln|mld)?\s*(?:di\s+)?(?:€|euro)(?![a-z])|"
                         r"€\s*(?:%s)(?:\s*(?:milion[ie]|miliard[ie]|mila|mln|mld))?)" % (NUM, NUM), re.I)
UNIDADE_NORMAL = [(re.compile(r"^(kg|chilo|kilo)", re.I), "kg"), (re.compile(r"^(tonn|t$|t\.)", re.I), "t"),
                  (re.compile(r"^(quintal|q)", re.I), "q"), (re.compile(r"^(ettolitr|hl)", re.I), "hl"),
                  (re.compile(r"^(litr|l$)", re.I), "l")]


def _moeda(m: str) -> str:
    return "EUR" if m.lower() in ("€", "euro", "eur") else "USD"


def _unidade(u: str) -> str:
    u = u.strip().lower()
    for rx, nome in UNIDADE_NORMAL:
        if rx.search(u):
            return nome
    return NAO_SEI


def numero(s: str) -> float:
    """Numero escrito a italiana: «1.234,56» -> 1234.56; «2,80» -> 2.8; «265» -> 265.0."""
    s = s.strip()
    if "," in s:
        return float(s.replace(".", "").replace(",", "."))
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        return float(s.replace(".", ""))
    return float(s)


# ── o que tapar antes de procurar o periodo ────────────────────────────────────────────────────────
MESES = (r"gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|"
         r"gen\.?|feb\.?|mar\.?|apr\.?|mag\.?|giu\.?|lug\.?|ago\.?|set\.?|sett\.?|ott\.?|nov\.?|dic\.?")
DATA_DMY = r"\d{1,2}[/.-]\d{1,2}[/.-](?:\d{4}|\d{2})"
DATA_EXT = r"\d{1,2}\s+(?:%s)\s+\d{4}" % MESES
RX_COMPARACAO = re.compile(
    r"(?:rispetto\s+(?:a|al|allo|alla|ai|agli|alle|all['’])|in\s+confronto\s+(?:a|al|allo|alla|con)|"
    r"a\s+confronto\s+con|confrontat[oi]\s+con|contro\s+(?:i|il|gli|le|lo|la|l['’])|come\s+(?:nel|nello|nella|l['’])|"
    r"sul(?:lo)?\s+(?=\d{4}|scorso|stesso|anno|mese|periodo)|vs\.?\s|versus|"
    r"(?:dello|della|del)\s+(?:scorso|scorsa|passato|passata|precedente)\s+(?:anno|annata|campagna|mese|settimana)|"
    r"(?:dello|del)\s+stesso\s+periodo)",
    re.I)
# base da variacao («su base mensile»): tapa-se SO a expressao — nao leva a oracao (levava «Borse Merci nazionali»)
RX_BASE_DA_VARIACAO = re.compile(r"anno\s+su\s+anno|su\s+base\s+(?:annua|annuale|mensile|settimanale|tendenziale|congiunturale)",
                                 re.I)
RX_FIM_DA_ORACAO = re.compile(r"[,;:.!?](?=\s|$)|[()]|\s(?:mentre|ma|però|pero|tuttavia)\s", re.I)
RX_PUBLICACAO = re.compile(r"(?:pubblicat[oaie]|pubblicazione|postato|data\s+articolo|aggiornamento\s+del\s+sito)"
                           r"\s*(?:il|in\s+data|:)?\s*(?:%s|%s)" % (DATA_DMY, DATA_EXT), re.I)

# ── o periodo, por ordem de precisao ───────────────────────────────────────────────────────────────
PERIODOS = [
    ("INTERVALO", re.compile(r"(?:settimana\s+)?dal\s+\d{1,2}(?:\s+(?:%s))?(?:\s+\d{4})?\s+al\s+\d{1,2}\s+(?:%s)(?:\s+\d{4})?"
                             % (MESES, MESES), re.I)),
    ("INTERVALO", re.compile(r"%s\s*(?:-|–|al|\.\.)\s*%s" % (DATA_DMY, DATA_DMY), re.I)),
    ("SEMANA", re.compile(r"settimana\s+(?:n\.?\s*)?\d{1,2}(?:\s*(?:/|del(?:l['’])?(?:\s+anno)?)\s*\d{4})?|sett\.\s*\d{1,2}", re.I)),
    ("CAMPANHA", re.compile(r"(?:campagna|annata|stagione|esercizio)(?:\s+(?:commerciale|agraria|olearia))?\s+"
                            r"\d{4}(?:\s*[/-]\s*\d{2,4})?", re.I)),
    ("DIA", re.compile(r"%s|%s" % (DATA_EXT, DATA_DMY), re.I)),
    ("MES", re.compile(r"(?:%s)\s+\d{4}" % MESES, re.I)),
    ("MES", re.compile(r"(?<![\d-])20\d{2}-(?:0?[1-9]|1[0-2])(?![\d-])")),
    ("MES", re.compile(r"(?:\b(?:a|ad|in|di|nel\s+mese\s+di|durante)\s+)(?:%s)(?![\w])" % MESES, re.I)),
    # ano solto: pontuacao DEPOIS («2025,» «2025.») e fim de oracao, nao decimal. Com «(?![.,])» o ano antes
    # da virgula nunca era lido — e o mutante que tira a tampa da comparacao sobrevivia (medido: M19).
    ("ANO", re.compile(r"(?<![\d/.,-])(?:19|20)\d{2}(?!\d|[.,/]\d|\s*%|-\d)")),
]

# ── estagio, praca, natureza ───────────────────────────────────────────────────────────────────────
ESTAGIOS = [
    (PRODUTOR, re.compile(r"alla\s+produzione|all['’]origine|franco\s+azienda|prezz\w*\s+(?:pagat|riconosciut)\w*\s+"
                          r"(?:ai|agli)\s+(?:produttori|agricoltori|soci|conferenti)|riconosciut\w*\s+ai\s+soci|"
                          r"(?:prezzo|prezzi)\s+(?:medio\s+)?di\s+(?:riparto|liquidazione)|farm\s+gate|ai\s+produttori", re.I)),
    (INGROSSO, re.compile(r"all['’]ingrosso|ingrosso|mercat\w+\s+ortofrutticol\w+|borsa\s+merci|borse\s+merci|"
                          r"(?<![\w])CUN(?![\w])|commissione\s+unica\s+nazionale|franco\s+(?:partenza|arrivo|magazzino|"
                          r"destino|molino)|centro\s+agroalimentare", re.I)),
    (DETTAGLIO, re.compile(r"al\s+dettaglio|dettaglio|al\s+consumo|consumatori?|scaffal\w+|supermercat\w+|"
                           r"(?<![\w])GDO(?![\w])|grande\s+distribuzione|ipermercat\w+", re.I)),
]
# WHY 8: o mesmo corte de `fato_do_texto.PALAVRAS_MINIMAS` — menu e titulo tem 1-5 palavras, frase de noticia 10+.
PALAVRAS_MINIMAS = 8
NOME = r"[A-Z][\w'’]+(?:\s+(?:di\s+|del\s+)?[A-Z][\w'’]+)?"
RX_PRACA = [
    re.compile(r"(?:mercato\s+(?:ortofrutticolo\s+|all['’]ingrosso\s+)?|borsa\s+merci\s+|borsa\s+|piazza\s+|"
               r"centro\s+agroalimentare\s+|camera\s+di\s+commercio\s+)(?:di|del|della|dell['’])\s*(?P<p>%s)" % NOME, re.I),
    re.compile(r"(?P<p>(?<![\w])(?:CUN(?:\s+[A-Z][\w]+(?:\s+[A-Z][\w]+)?)?|CAAB|MOF\s+di\s+[A-Z]\w+|"
               r"borse\s+merci\s+nazionali))", re.I),
]
RX_PROJECAO = re.compile(r"potrebb\w+|dovrebb\w+|si\s+prevede|previst\w+|previsione|attes[oiae]\b|stimat\w+|"
                         r"si\s+stima|potrà|salirà|scenderà|toccherà|in\s+futuro", re.I)
RX_ORIENTATIVO = re.compile(r"orientativ\w+|indicativ\w+", re.I)
RX_MEDIO = re.compile(r"prezz\w+\s+medi\w+|media\s+(?:settimanale|mensile|ponderata)|in\s+media", re.I)
RX_MERCADO = re.compile(r"prezz\w+|quotazion\w+|listin\w+|mercat\w+|domanda|offerta|rialz\w+|ribass\w+|"
                        r"aument\w+|calo|flession\w+|vendit\w+|consum\w+|fatturat\w+|export|import", re.I)
RX_DOMANDA_VENDA = re.compile(r"domanda|offerta|vendit\w+|venduto|consumi|acquist\w+|fatturat\w+|export|import|"
                              r"volum\w+|produzion\w+|tonnellat\w+|quota\s+di\s+mercato|market\s+share", re.I)
RX_OPINIAO = re.compile(r"soddisfazion\w+|preoccup\w+|positiv\w+|negativ\w+|ottim\w+|crisi|difficil\w+|"
                        r"favorevol\w+|incertezz\w+|tension\w+|secondo\s+(?:gli\s+)?operator\w+|ritenut\w+", re.I)


def texto_de_html(html: str) -> str:
    """Tira script/style/etiquetas e junta espacos. Fim de bloco vira quebra de linha."""
    t = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?i)</(p|div|li|h[1-6]|tr|br|td|th)\s*>|<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _html.unescape(t)
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


def frases(texto: str) -> list:
    """Uma frase por linha ou por ponto final seguido de maiuscula. Linha de tabela («a | b | c») fica inteira."""
    out = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        for f in re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý«\"“0-9])", linha):
            if f.strip():
                out.append(f.strip())
    return out


def _fim_da_oracao(f: str, ini: int) -> int:
    m = RX_FIM_DA_ORACAO.search(f, ini)
    return m.start() if m else len(f)


def _tapar(f: str, spans) -> str:
    t = list(f)
    for a, b in spans:
        for i in range(a, b):
            t[i] = " "
    return "".join(t)


def comparacoes_e_publicacao(f: str):
    """-> (spans da comparacao, spans da publicacao). A comparacao vai do marcador ao fim da oracao."""
    comp = []
    for m in RX_COMPARACAO.finditer(f):
        comp.append((m.start(), _fim_da_oracao(f, m.end())))
    comp += [(m.start(), m.end()) for m in RX_BASE_DA_VARIACAO.finditer(f)]
    pub = [(m.start(), m.end()) for m in RX_PUBLICACAO.finditer(f)]
    return comp, pub


def periodo_em(t: str):
    """-> (periodo, tipo, trecho) no texto ja TAPADO; ou (NAO SEI, None, None)."""
    for tipo, rx in PERIODOS:
        m = rx.search(t)
        if m:
            v = m.group(0).strip()
            v = re.sub(r"^(?:a|ad|in|di|nel\s+mese\s+di|durante)\s+", "", v, flags=re.I) if tipo == "MES" else v
            return v, tipo, m.group(0).strip()
    return NAO_SEI, None, None


def _commodity(f: str, pos: int):
    """A commodity mais perto do preco, preferindo a que vem ANTES dele na frase."""
    antes, depois = [], []
    for rx, chave in RX_COMMODITY:
        for m in rx.finditer(f):
            (antes if m.start() < pos else depois).append((m, chave))
    if antes:
        m, k = max(antes, key=lambda x: (x[0].start(), x[0].end() - x[0].start()))
    elif depois:
        m, k = min(depois, key=lambda x: (x[0].start(), -(x[0].end() - x[0].start())))
    else:
        return NAO_SEI, NAO_SEI
    return re.sub(r"\s+", " ", m.group(0)).strip(), k


def _estagio(t: str):
    achados = {}
    for nome, rx in ESTAGIOS:
        m = rx.search(t)
        if m:
            achados[nome] = m.group(0)
    if len(achados) == 1:
        (nome, trecho), = achados.items()
        return nome, "marcador escrito: «%s»" % trecho
    if not achados:
        return NAO_SEI, "nenhum marcador de estagio (produtor/ingrosso/dettaglio) escrito na frase"
    return NAO_SEI, "CONFLITO: marcadores de %s na mesma frase" % " e ".join(
        "%s «%s»" % (k, v) for k, v in sorted(achados.items()))


def _praca(t: str):
    for rx in RX_PRACA:
        m = rx.search(t)
        if m:
            return re.sub(r"\s+", " ", m.group("p")).strip()
    return NAO_SEI


def _precos_na_frase(f: str):
    """Todos os precos com moeda+unidade, sem sobreposicao (o primeiro padrao que apanha fica)."""
    achados, ocupado = [], []
    for rx in RX_PRECOS:
        for m in rx.finditer(f):
            if any(a < m.end() and m.start() < b for a, b in ocupado):
                continue
            ocupado.append((m.start(), m.end()))
            achados.append(m)
    return sorted(achados, key=lambda m: m.start())


def _serie(o: dict) -> str:
    partes = [("CULTURA", o["CULTURA"]), ("PRACA", o["PRACA"]), ("ESTAGIO", o["ESTAGIO"]),
              ("UNIDADE", o["UNIDADE"]), ("MOEDA", o["MOEDA"])]
    falta = [k for k, v in partes if v == NAO_SEI]
    if falta:
        return "%s (falta: %s)" % (NAO_SEI, ", ".join(falta))
    return "|".join(v for _k, v in partes)


def _oracoes(f: str):
    """Oracoes da frase: corta em «, » «; » (a virgula decimal nao tem espaco a seguir)."""
    out, ini = [], 0
    for m in re.finditer(r"[,;](?=\s)|\s(?:mentre|ma|però|tuttavia)\s", f):
        out.append((ini, m.start()))
        ini = m.end()
    out.append((ini, len(f)))
    return [(a, b) for a, b in out if f[a:b].strip()]


def _porque_do_comentario(t: str) -> str:
    if RX_DOMANDA_VENDA.search(t):
        return "VOLUME_DEMANDA_OU_VENDA_NAO_E_PRECO"
    if RX_PROJECAO.search(t):
        return "PROJECAO_OU_PREVISAO"
    if "%" in t:
        return "VARIACAO_SEM_NIVEL_DE_PRECO"
    if RX_OPINIAO.search(t):
        return "OPINIAO"
    return "COMENTARIO_DE_MERCADO"


def precos_do_texto(texto: str) -> dict:
    obs, comentarios, recusados, comps = [], [], [], []
    for f in frases(texto):
        spans_comp, spans_pub = comparacoes_e_publicacao(f)
        for a, b in spans_comp:
            comps.append({"TRECHO": f[a:b].strip(), "FRASE": f})
        tapado = _tapar(f, spans_comp + spans_pub)
        precos = _precos_na_frase(f)
        ocupado = [(m.start(), m.end()) for m in precos]
        # montantes em euro sem unidade: recusados (nunca viram preco, nem procura, nem venda)
        for m in RX_MONTANTE.finditer(f):
            if any(a < m.end() and m.start() < b for a, b in ocupado):
                continue
            recusados.append({"VALOR_TEXTO": m.group(0).strip(), "TRECHO": f,
                              "PORQUE": ("VALOR_DE_FATURAMENTO_OU_CAPITAL_NAO_E_PRECO"
                                         if re.search(r"milion|miliard|mln|mld|fatturat|capitale|bilancio|utile|"
                                                      r"patrimonio", f, re.I)
                                         else "PRECO_SEM_UNIDADE_NAO_E_COMPARAVEL")})
        oracoes_com_preco = set()
        for m in precos:
            oa, ob = next(((a, b) for a, b in _oracoes(f) if a <= m.start() < b), (0, len(f)))
            oracoes_com_preco.add((oa, ob))
            oracao = f[oa:ob]
            if RX_PROJECAO.search(oracao):
                comentarios.append({"TRECHO": oracao.strip(), "FRASE": f, "PORQUE": "PROJECAO_NAO_E_OBSERVACAO",
                                    "VALOR_CITADO": m.group(0).strip()})
                continue
            dentro = next(((a, b) for a, b in spans_comp if a <= m.start() < b), None)
            if dentro:
                papel = REFERENCIA
                per, tipo, trecho_per = periodo_em(f[dentro[0]:dentro[1]])
                if per == NAO_SEI and re.search(r"scors|passat|precedent", f[dentro[0]:dentro[1]], re.I):
                    per, tipo, trecho_per = f[dentro[0]:dentro[1]].strip(), "RELATIVO_A_COMPARACAO", None
                basis = ("periodo da propria comparacao: «%s»" % trecho_per if trecho_per else
                         ("comparacao sem periodo explicito" if per == NAO_SEI else
                          "periodo relativo, escrito na comparacao: «%s» (sem conta: a publicacao nao entra)" % per))
            else:
                papel = OBSERVACAO
                per, tipo, trecho_per = periodo_em(tapado)
                basis = ("escrito na frase do preco: «%s» (comparacoes e publicacao tapadas antes)%s" % (
                            trecho_per, " · MES SEM ANO: o ano nao esta escrito na frase e NAO se tira da publicacao"
                            if tipo == "MES" and not re.search(r"\d{4}", per) else "")
                         if trecho_per else "NAO SEI · nenhum periodo de referencia escrito na frase do preco; "
                                            "ano de comparacao e data de publicacao nao servem")
            commodity, cultura = _commodity(f, m.start())
            estagio, estagio_basis = _estagio(tapado)
            a = numero(m.group("a"))
            b = numero(m.group("b")) if m.group("b") else None
            natureza = ("ORIENTATIVO" if RX_ORIENTATIVO.search(f) else
                        "MEDIO" if RX_MEDIO.search(f) else "OBSERVADO")
            o = {
                "COMMODITY": commodity, "CULTURA": cultura, "PRACA": _praca(tapado),
                "PERIODO": per, "PERIODO_TIPO": tipo or NAO_SEI, "PERIODO_BASIS": basis,
                "PRECO": None if b is not None else a,
                "PRECO_MIN": min(a, b) if b is not None else None,
                "PRECO_MAX": max(a, b) if b is not None else None,
                "PRECO_TEXTO": m.group(0).strip(),
                "MOEDA": _moeda(m.group("m")), "UNIDADE": NAO_SEI,
                "ESTAGIO": estagio, "ESTAGIO_BASIS": estagio_basis,
                "NATUREZA": natureza, "PAPEL": papel, "TRECHO": f,
            }
            un = _unidade(m.group("u"))
            o["UNIDADE"] = "%s/%s" % (o["MOEDA"], un) if un != NAO_SEI else NAO_SEI
            o["SERIE"] = _serie(o)
            obs.append(o)
        # o resto da frase: comentario de mercado, separado do preco. Frase sem preco so conta se for frase
        # (>= PALAVRAS_MINIMAS): menu e titulo («Prezzi e tariffe», «Mercato cerealicolo») nao sao comentario.
        if not precos and (len(f.split()) < PALAVRAS_MINIMAS or not RX_MERCADO.search(f)):
            continue
        for oa, ob in _oracoes(f):
            if (oa, ob) in oracoes_com_preco:
                continue
            oracao = f[oa:ob]
            if (RX_MERCADO.search(oracao) if not precos else
                    (RX_OPINIAO.search(oracao) or RX_PROJECAO.search(oracao) or RX_DOMANDA_VENDA.search(oracao)
                     or "%" in oracao)):
                comentarios.append({"TRECHO": oracao.strip(), "FRASE": f, "PORQUE": _porque_do_comentario(oracao)})
    return {"OBSERVACOES": obs, "COMENTARIOS": comentarios, "RECUSADOS": recusados, "COMPARACOES": comps}


if __name__ == "__main__":
    import json
    fonte = sys.argv[1]
    t = Path(fonte).read_text(encoding="utf-8", errors="replace")
    if re.search(r"<html|<body|<div|<p[ >]", t[:5000], re.I):
        t = texto_de_html(t)
    print(json.dumps(precos_do_texto(t), ensure_ascii=False, indent=1))
