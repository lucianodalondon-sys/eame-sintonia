# -*- coding: utf-8 -*-
"""PROPOSTA L5-P3 · tempo TIPADO, com precisao literal e base com offset.

NAO INSTALADO. Nada em `leis/` importa este ficheiro. Ele existe para ser medido
contra o extrator vivo (`leis/fato_local.tempo_do_fato` + `leis/fato_do_texto`).

O QUE MUDA em relacao ao vivo
-----------------------------
1. O vivo tem UM campo (`fact_time`) para cinco coisas diferentes. Aqui cada tempo
   sai no seu proprio balde:
       FACT_TIME        o acontecimento no campo (observacao, captura, chuva, foco)
       VALIDITY_TIME    a janela em que uma regra/boletim vale (nunca e o facto)
       PUBLICATION_TIME o carimbo de quem publicou (edicao, assinatura, «aggiornato al»)
       ACT_TIME         a data do decreto/determina/ordinanza
       MARKET_PERIOD    safra, campanha, semana de rilevacao de preco
   Data de validade, de edicao ou de publicacao NUNCA entra em FACT_TIME.
2. Le as formas que o vivo nao le (medidas pelo LAB em 28/09/2026):
   dd/mm/aaaa · dd.mm.aaaa · aaaa-mm-dd · «(gennaio 2026)» · «settimana 39/2026»
   · «mese di maggio 2026» (o vivo perdia o ano) · intervalos («dal 1 al 4 settembre
   2026» — o vivo devolvia so o fim) · «(18-24.05)» · «maggio-giugno 2026».
3. NUNCA inventa ano. Se o texto nao escreve o ano, o valor sai `SEM_ANO-09-17` e
   `ANO = 'NAO SEI'`. O ano da publicacao nao preenche o ano do facto.
4. NUNCA inventa precisao. Texto que so da o mes sai com PRECISAO='MONTH'; texto
   que so da a semana sai 'WEEK'. Nao se fabrica um dia a partir de um mes.
5. Nao depende de quebras de linha. 123 dos 275 itens da copia da Sala tem o texto
   inteiro numa linha so, e o filtro «corpo, nao pagina» do vivo achava 0 linhas de
   corpo e devolvia NAO SEI. Aqui o corpo e o texto todo quando nao ha linhas.
6. Um limite ganho por raciocinio («o achado e anterior a publicacao») sai em
   LIMITES_INFERIDOS, marcado INFERENCIA=True, e nunca no valor de FACT_TIME.

VOLTA 2 (D147 + D150) — o que mudou depois da prova as cegas
------------------------------------------------------------
A 1.a candidata (117799143) tirou 0/20. As causas vieram do coordenador, sem gabarito:
· o ano do cabecalho passou a ser o que o dono decidiu (`_ano_governante`): cabecalho
  inequivoco da MESMA edicao, ano que governa a afirmacao, nenhum ano concorrente, os
  dois trechos citados e a procedencia escrita. A janela de 40 letras da 1.a versao
  desapareceu — lia qualquer ano perto, incluindo o de outro assunto.
· «ano sozinho nunca data observacao» FOI RETIRADA: contrariava a D147 item 3. Um ano
  economico atribuido ao facto («fechou 2025») e FACT_TIME com precisao ANO. So o ano
  HISTORICO de OUTRO facto («per la prima volta nel 2004») continua barrado.
· cabecalho com as letras dobradas pelo PDF passa a ser lido (`_colapsa_duplicadas`).
· relativa de SEMANA ancora no periodo IMPRESSO do proprio boletim (D63/D149), com a
  composicao registada — antes so a publicacao provada ancorava.
· quem procura o ATO ligado a afirmacao e a interface: o extrator devolve todos, e
  `provas/l5-p3/interface.py` so deixa passar o que a afirmacao usa (era DATA_INVENTADA).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta

# ── os cinco tipos de tempo ──────────────────────────────────────────────────
FACT_TIME = "FACT_TIME"
VALIDITY_TIME = "VALIDITY_TIME"
PUBLICATION_TIME = "PUBLICATION_TIME"
ACT_TIME = "ACT_TIME"
MARKET_PERIOD = "MARKET_PERIOD"
# D147: o periodo que a EDICAO cobre nao e validade nenhuma. «BOLLETTINO settimana 39
# dal 22/09/2026 al 29/09/2026» diz de que dias o boletim fala; «validita dal 01/03 al
# 28/06» diz ate quando uma derroga vale. Misturar os dois foi o erro medido (derived:7).
PERIODO_DA_EDICAO = "PERIODO_DA_EDICAO"
TIPOS = (FACT_TIME, VALIDITY_TIME, PUBLICATION_TIME, ACT_TIME, MARKET_PERIOD, PERIODO_DA_EDICAO)

# ── de onde vem o valor (D147) ───────────────────────────────────────────────
LITERAL = "LITERAL"              # escrito na propria expressao
CABECALHO = "CABECALHO"          # o ano veio de outro trecho do MESMO documento
RELATIVO_D63 = "RELATIVO_D63"    # contado a partir de publicacao PROVADA

# ── precisao literal: o que o texto escreveu, nem mais nem menos ─────────────
DAY, WEEK, MONTH, YEAR, SEASON, INTERVAL = "DAY", "WEEK", "MONTH", "YEAR", "SEASON", "INTERVAL"

NAO_SEI = "NAO SEI"
SEM_ANO = "SEM_ANO"

MESES = ("gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
         "agosto", "settembre", "ottobre", "novembre", "dicembre")
MES_NUM = {m: i + 1 for i, m in enumerate(MESES)}
_MES = "|".join(MESES)


def _fold(s: str) -> str:
    """Minusculas sem acento MANTENDO O COMPRIMENTO — os offsets tem de bater.

    `leis/fato_local._sem_acento` deita fora o caractere combinante e encurta a
    string; aqui isso estragaria o offset, que e metade da prova.
    """
    saida = []
    for ch in str(s or ""):
        d = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in d if not unicodedata.combining(c)) or ch
        saida.append((base[0] if base else ch).lower())
    return "".join(saida)


# ── superficie: o que e uma expressao de tempo escrita ───────────────────────
# A ordem importa: o intervalo vem antes da data solta, senao «dal 1 al 4 settembre»
# partia-se em duas datas e perdia-se o inicio (foi exatamente o que o vivo fazia).
_D = r"\d{1,2}"
_A = r"\d{4}"
SUPERFICIES = (
    ("INTERVALO_NUM_DAL", re.compile(r"dal\s+(%s[/.]%s[/.]\d{2,4})\s+al\s+(%s[/.]%s[/.]\d{2,4})" % (_D, _D, _D, _D))),
    ("INTERVALO_NUM_TRACO", re.compile(r"(%s[/.]%s[/.]%s)\s*[-–—]\s*(%s[/.]%s[/.]%s)" % (_D, _D, _A, _D, _D, _A))),
    ("INTERVALO_DIA_MES_DAL", re.compile(
        r"dal(?:l['’])?\s+(%s)\s*(?:°|º|o\b)?\s*(?:(%s)\s+)?(?:%s)?\s*al(?:l['’])?\s+(%s)\s*(?:°|º)?\s+(%s)(?:\s+(%s))?"
        % (_D, _MES, _A, _D, _MES, _A))),
    ("INTERVALO_DIA_TRACO", re.compile(
        r"(%s)\s*(?:°|º)?\s*[-–—]\s*(%s)\s*(?:°|º)?\s+(%s)(?:\s+(%s))?" % (_D, _D, _MES, _A))),
    ("INTERVALO_DIA_E", re.compile(r"(%s)\s+e(?:d)?\s+(%s)\s+(%s)(?:\s+(%s))?" % (_D, _D, _MES, _A))),
    ("INTERVALO_DIA_PONTO", re.compile(r"(%s)\s*[-–]\s*(%s)\s*\.\s*(%s)(?:\.(\d{2,4}))?" % (_D, _D, _D))),
    ("INTERVALO_MES_MES", re.compile(r"(%s)\s*[-–]\s*(%s)\s+(%s)" % (_MES, _MES, _A))),
    ("SEMANA_ANO", re.compile(r"settimana\s+(\d{1,2})\s*(?:/\s*|\s+del\s+)(%s)" % _A)),
    ("SEMANA_SO", re.compile(r"settimana\s+(\d{1,2})(?!\s*[/\-–]?\s*\d)")),
    ("DATA_NUM", re.compile(r"(?<![\d/.])(%s)[/.](%s)[/.](\d{2,4})(?![\d/.])" % (_D, _D))),
    ("DATA_ISO", re.compile(r"(?<!\d)(%s)-(\d{2})-(\d{2})(?!\d)" % _A)),
    ("DIA_MES_ANO", re.compile(r"(?<!\d)(%s)\s*(?:°|º)?\s+(%s)\s+(%s)(?!\d)" % (_D, _MES, _A))),
    ("DIA_MES", re.compile(r"(?<!\d)(%s)\s*(?:°|º)?\s+(%s)\b" % (_D, _MES))),
    ("MES_ANO", re.compile(r"(?<![a-z0-9])(%s)\s+(?:del\s+)?(%s)(?!\d)" % (_MES, _A))),
    ("SAFRA", re.compile(r"(?:campagna|annata|stagione|raccolt[oa])\s+(%s(?:[/-]\d{2,4})?)" % _A)),
    ("SAFRA_SOLTA", re.compile(r"(?<![\d/.-])((?:19|20)\d{2}[/-]\d{2,4})(?![\d-])")),
    ("MES_SO", re.compile(r"(?:mese\s+di|durante\s+il\s+mese\s+di|nel\s+mese\s+di|durante|in|ad?)\s+(%s)(?![a-z0-9])" % _MES)),
    ("ANO_SO", re.compile(r"(?<![\d/.-])(?:19|20)\d{2}(?![\d/.-])")),
    ("RELATIVA", re.compile(r"\b(oggi|ieri|stamattina|la\s+settimana\s+scorsa|questa\s+settimana|"
                            r"nei\s+giorni\s+scorsi|lo\s+scorso\s+mese|la\s+settimana\s+appena\s+trascorsa|"
                            r"la\s+settimana\s+in\s+corso)\b")),
)

# ── as pistas que dizem DE QUEM e a data ─────────────────────────────────────
# Um ATO: a data que vem colada a um decreto e a data do decreto, nunca a do facto.
# As alternativas tem fronteira de palavra a esquerda de proposito: sem ela, o
# «n.» solto casava dentro de «monitoraggio della» («n» + «itoraggio» + «del»la) e
# punha a data do monitoramento no balde dos atos — medido a correr esta proposta.
_RE_ATO = re.compile(
    r"(?<![a-z])(?:decret[oi]|dirigenzial|determin[ai]|delibera|ordinanz|circolar|"
    r"gazzetta\s+ufficial|bollettino\s+ufficial|burc|b\.u\.r|d\.?lgs|dlgs|decreto\s+legislativo|"
    r"legge|reg(?:olamento)?\.?\s*(?:ue|ce)\b|direttiva|dds|drd|dpd|d\.m\.|"
    r"approvat[oaie]\s+con|emanat[oaie]\s+il|firmat[oaie]\s+il|concess[oa]\s+(?:la\s+)?deroga|"
    r"in\s+data)")
# VALIDADE: a janela em que a regra/boletim vale.
_RE_VALIDADE = re.compile(
    r"valid[oaei]|validit|scadenz|in\s+scadenza|prorog|fino\s+a|entro\s+(?:il|e\s+non\s+oltre|sabato|"
    r"domenica|luned|marted|mercoled|gioved|venerd)?|deroga|autorizzazione\s+temporanea|"
    r"periodo\s+di\s+validit|trattamento\s+\d?\s*dal|comprensorio")
# PUBLICACAO / EDICAO: o carimbo de quem publica. O numero de edicao («n. 27 del»)
# so conta como edicao quando ha um nome de peca publicada antes dele — senao casava
# com «Decreto n. 15068 DEL», que e um ATO.
_RE_PUBLICACAO = re.compile(
    r"(?<![a-z])(?:pubblicat[oaie]|aggiornato\s+al|articolo\s+id|comunicato\s+del|"
    r"nota\s+per\s+la\s+difesa[^.]{0,80}?\sdel)")
_RE_EDICAO = re.compile(
    r"(?<![a-z])(?:bollettino|comunicato|notiziario|avviso|nota|edizione|riferimento)"
    r"[^.;]{0,80}?(?:n[.°]?\s*\d+(?:\s*/\s*\d{2,4})?\s*(?:del\s*|[^.;]{0,25})|\sdel\s*)$")
# 25 letras: «Bollettino fitosanitario n. 20/2026 1 di 3 26.05.2026» — a data do
# cabecalho e a edicao. Em «Bollettino N.20 … Situazione fitosanitaria al 22 maggio
# 2026» o numero fica a 57 letras e a data continua do facto, como o LAB leu.
# MERCADO: safra, campanha, semana de preco.
_RE_MERCADO = re.compile(
    r"prezz|quotazion|mercat|euro\s*/\s*kg|euro/kg|€|rilevazion|panel|borsa|ingrosso|listino|"
    r"campagna|annata|stagione|raccolt|export|fatturat|trend")
# A pista FORTE de mercado — a que decide se uma safra e periodo de mercado. «campagna»
# e «raccolto» nao contam aqui: eles estao dentro da propria expressao de safra.
_RE_MERCADO_FORTE = re.compile(
    r"prezz|quotazion|mercat|euro\s*/?\s*kg|€|rilevazion|panel|borsa|ingrosso|listino|fatturat|export")
# A safra que vem depois de uma destas nao encabeca nada: qualifica uma cotacao ou e
# termo de comparacao («nella settimana 38 il prezzo», «in linea con la campagna 2024»).
_RE_QUALIFICA_COTACAO = re.compile(
    r"(?:rispetto|confronto|in\s+linea\s+con|nell[ao]|ne[il]|dell[ao]|de[il]|con\s+l[ao]|contro|vs\.?|"
    r"pari\s+a|come\s+(?:nel|nella))\s*(?:l[ao'’]?\s*)?$""", re.I)
# O ano HISTORICO de OUTRO facto — a unica coisa que continua a barrar um ano sozinho.
# «rilevata per la prima volta in Europa nel 2004» data a primeira detecao, nao o que
# este documento relata.
_RE_HISTORICO_DE_OUTRO = re.compile(
    r"(?<![a-z])(?:per\s+la\s+prima\s+volta|prima\s+(?:segnalazione|comparsa|rilevazione)|"
    r"storicamente|risal(?:e|iva)\s+a|nel\s+passato|gia\s+nel|fin\s+dagli\s+anni|"
    r"fu\s+(?:individuat|rilevat|segnalat|introdott))")
# A ASSINATURA de quem escreve: «Di Giuseppe Francesco Sportelli 13 Settembre 2026».
# Vai contra o texto ORIGINAL (com maiusculas), porque e a maiuscula do nome que a
# distingue de um «di» qualquer.
_RE_ASSINATURA = re.compile(
    r"(?:(?<![A-Za-z])[Dd]i|(?<![A-Za-z])[Dd]a|A\s+cura\s+di|Redazione|Autore)\s+"
    r"(?:[A-ZÀ-Ý][\w'’À-ÿ]+\s+){1,3}$")
# Uma afirmacao SEM acontecimento datavel: conhecimento geral, biologia, definicao.
# Serve para separar NAO_EXISTE (nao ha o que datar) de NAO_SEI (houve, nao diz quando).
_RE_DEFINICAO = re.compile(
    r"(?<![a-z])(?:e\s+un[ao]?\b|sono\s+(?:insetti|funghi|batteri|acari|specie)|"
    r"si\s+tratta\s+di|la\s+specie|il\s+ciclo|si\s+nutre|puo\s+causare|in\s+generale|"
    r"di\s+solito|normalmente|caratteristic|descrizion|biologia|morfologia|appartiene|"
    r"si\s+riproduce|le\s+larve|gli\s+adulti|preferisce|predilige|si\s+consiglia)")
# FACTO: o acontecimento no campo. Lista do vivo MAIS as ancoras que faltavam
# (medidas pelo LAB: «segnalazione», «situazione ... al», «effettuato», «catture»).
_RE_FACTO = re.compile(
    r"monitoraggi|campion|osservat|rilevat|constatat|riscontrat|colpit|contaminaz|superament|"
    r"infezion|infestazion|attacch|sintom|coltura|colture|segnalazion|segnalat|situazione|"
    r"effettuat|rilievi|rilievo|cattur|positivit|individuat|presenz|piogg|precipitazion|focolai|"
    r"comparse|voli|volo\b|danni|concentrazion|raggiunt|fase\s+fenologica|invaiatura|"
    r"incendi|grandin|gelat[ae]|brinat[ae]|alluvion|esondazion|nubifragi|siccit|raffich|"
    r"tromb[ae]\s+d.aria|mareggiat|maltempo|fran[ae]|ondat[ae]\s+di\s+calore|calamit|anomali|"
    r"vent[oi]\s+(?:fort|intens|impetuos|di\s+burrasca)|event[oi]\s+(?:atmosferic|meteorologic|meteo\b|estrem)")
# o que NUNCA e facto de campo, mesmo com ancora perto
_RE_PREVISAO = re.compile(r"previst|previsione|si\s+prevede|si\s+terr|prossim|domani|"
                          r"attes[ae]|in\s+arrivo|outlook|potrebbero|potrebbe")
_RE_CONSELHO = re.compile(r"si\s+consiglia|consigliat|raccomand|si\s+suggerisce|intervenire|"
                          r"obbligatori|dovr[aà]|si\s+ricorda")
# A fronteira a esquerda nao e enfeite: sem ela, «lo scorso mese» tem «corso» dentro e
# o mes da segnalazione da Sicilia (C5 do LAB) morria como «evento tecnico».
_RE_EVENTO_TECNICO = re.compile(r"(?<![a-z])(?:convegno|corso\b|corsi\b|seminario|fiera|congress|webinar|"
                                r"iscrizion|giornata\s+di\s+studio|open\s+day|sial\b|macfrut|edizione)")
_RE_INICIO_DE_SERIE = re.compile(
    r"(?:avviat|iniziat|partit|cominciat|attivat|istituit|intrapres|lanciat)[oaie]\s+"
    r"(?:gia\s+)?(?:nel|dal|a\s+partire\s+dal|in|ad?)\s*$|"
    r"(?:a\s+partire\s+dal|sin\s+dal|fin\s+dal|dal(?:l['’]anno)?)\s*$")
_RE_COMPARACAO = re.compile(
    r"(?:rispetto\s+%(art)s|in\s+confronto|a\s+confronto|confronto\s+(?:con|fra|tra)|paragonat[oaie]?\s*%(art)s?|"
    r"contro\s+%(art)s|stess[oa]\s+(?:periodo|mese|settimana)|vs\.?|versus|"
    r"dalla\s+campagna|dall['’]annata|"
    r"(?:superiore|inferiore|pari)\s+%(art)s)\s*(?:del\s+|dell['’]\s*|nel\s+|nella\s+|alla\s+)?$"
    # os parenteses nao sao enfeite: sem eles a alternacao do artigo VAZA para o topo
    # da expressao e qualquer «la»/«il» antes de uma data passa a ser comparacao — e as
    # chuvas datadas morriam todas (medido: 4 casos do LAB a cair de uma vez).
    % {"art": r"(?:a(?:l(?:la|lo|le|l['’])?|i|gli|d)?|con(?:\s+(?:il|la|lo|i|gli|le))?|il|lo|la|i|gli|le)"})
_RE_QUANTIDADE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:%|€|euro(?:/kg)?|eur|tonnellat|quintal|ettar|kg|q\.li)"
                            r"[^.;]{0,25}$")
_RE_PROGRAMA = re.compile(r"(?:dpi|piano|programma|norme|bando|psr|pac|piani)\s*$")
# Os DOIS anos inteiros, de proposito: «2026 - 20/09/2026» (um intervalo de dias) nao
# e uma serie; «maggio-giugno 2000-2026» e, e o vivo dava-lhe o mes como facto.
_RE_SERIE_DE_ANOS = re.compile(r"(?:19|20)\d{2}\s*(?:[-–]\s*(?:19|20)\d{2}|"
                               r"(?:,|\be\b|\bed\b)\s*(?:19|20)\d{2})")

JANELA_ANTES = 90          # letras antes da data em que se procura a pista
DISTANCIA_DA_ANCORA = 160  # a ancora do facto tem de estar perto da data, na mesma oracao


# ── valores normalizados, sem inventar nada ──────────────────────────────────
def _val_dia(ano, mes, dia):
    return "%s-%02d-%02d" % (ano if ano else SEM_ANO, int(mes), int(dia))


def _val_mes(ano, mes):
    return "%s-%02d" % (ano if ano else SEM_ANO, int(mes))


def _val_semana(ano, n):
    return "%s-W%02d" % (ano if ano else SEM_ANO, int(n))


def _ano4(a):
    """«26» e 2026; «206» e um erro de digitacao da fonte e fica como esta."""
    a = str(a)
    if len(a) == 4:
        return a
    if len(a) == 2:
        return "20" + a if int(a) < 70 else "19" + a
    return None


def _e_safra(valor):
    """«2025/26» e «2025-2026» sao safra. «2011-2025» e serie historica — a mesma regra
    que `leis/fato_local._e_campanha` ja usa no vivo."""
    m = re.match(r"^(\d{4})[/-](\d{2,4})$", str(valor).strip())
    if not m:
        return True
    a, b = int(m.group(1)), m.group(2)
    return b == str(a + 1)[-len(b):] and int(b) != 0


def _mes_de(nome):
    return MES_NUM.get(str(nome or "").strip())


def _leitura(nome, m):
    """Traduz um casamento de superficie em (VALOR, INICIO, FIM, PRECISAO, ANO)."""
    g = m.groups()
    if nome == "INTERVALO_NUM_DAL" or nome == "INTERVALO_NUM_TRACO":
        a, b = [re.split(r"[/.]", x) for x in (g[0], g[1])]
        aa, ab = _ano4(a[2]), _ano4(b[2])
        ini, fim = _val_dia(aa, a[1], a[0]), _val_dia(ab, b[1], b[0])
        return "%s/%s" % (ini, fim), ini, fim, INTERVAL, aa or ab
    if nome == "INTERVALO_DIA_MES_DAL":
        d1, m1, d2, m2, ano = g[0], g[1], g[2], g[3], g[4]
        ano = _ano4(ano) if ano else None
        n1, n2 = _mes_de(m1) or _mes_de(m2), _mes_de(m2)
        if not n2:
            return None
        ini, fim = _val_dia(ano, n1, d1), _val_dia(ano, n2, d2)
        return "%s/%s" % (ini, fim), ini, fim, INTERVAL, ano
    if nome in ("INTERVALO_DIA_TRACO", "INTERVALO_DIA_E"):
        d1, d2, mes, ano = g[0], g[1], g[2], g[3]
        n = _mes_de(mes)
        ano = _ano4(ano) if ano else None
        if not n:
            return None
        ini, fim = _val_dia(ano, n, d1), _val_dia(ano, n, d2)
        return "%s/%s" % (ini, fim), ini, fim, INTERVAL, ano
    if nome == "INTERVALO_DIA_PONTO":
        d1, d2, mes, ano = g[0], g[1], g[2], g[3]
        ano = _ano4(ano) if ano else None
        ini, fim = _val_dia(ano, mes, d1), _val_dia(ano, mes, d2)
        return "%s/%s" % (ini, fim), ini, fim, INTERVAL, ano
    if nome == "INTERVALO_MES_MES":
        n1, n2, ano = _mes_de(g[0]), _mes_de(g[1]), _ano4(g[2])
        if not (n1 and n2):
            return None
        ini, fim = _val_mes(ano, n1), _val_mes(ano, n2)
        return "%s/%s" % (ini, fim), ini, fim, INTERVAL, ano
    if nome == "SEMANA_ANO":
        ano = _ano4(g[1])
        v = _val_semana(ano, g[0])
        return v, v, v, WEEK, ano
    if nome == "SEMANA_SO":
        v = _val_semana(None, g[0])
        return v, v, v, WEEK, None
    if nome == "DATA_NUM":
        ano = _ano4(g[2])
        v = _val_dia(ano, g[1], g[0])
        return v, v, v, DAY, ano
    if nome == "DATA_ISO":
        v = _val_dia(g[0], g[1], g[2])
        return v, v, v, DAY, g[0]
    if nome == "DIA_MES_ANO":
        n = _mes_de(g[1])
        if not n:
            return None
        v = _val_dia(_ano4(g[2]), n, g[0])
        return v, v, v, DAY, _ano4(g[2])
    if nome == "DIA_MES":
        n = _mes_de(g[1])
        if not n:
            return None
        v = _val_dia(None, n, g[0])
        return v, v, v, DAY, None
    if nome == "MES_ANO":
        n = _mes_de(g[0])
        if not n:
            return None
        v = _val_mes(_ano4(g[1]), n)
        return v, v, v, MONTH, _ano4(g[1])
    if nome == "MES_SO":
        n = _mes_de(g[0])
        if not n:
            return None
        v = _val_mes(None, n)
        return v, v, v, MONTH, None
    if nome in ("SAFRA", "SAFRA_SOLTA"):
        v = g[0]
        if nome == "SAFRA_SOLTA" and not _e_safra(v):
            return None          # «2011-2025» e serie historica, nao safra
        return v, v, v, SEASON, v[:4]
    if nome == "ANO_SO":
        v = m.group(0)
        return v, v, v, YEAR, v
    if nome == "RELATIVA":
        v = re.sub(r"\s+", " ", m.group(1))
        return v, v, v, NAO_SEI, None
    return None


_FIM_DE_ORACAO = ".!?;\n"


def _limites_da_oracao(low, ini, fim):
    """Onde comeca e onde acaba a oracao que contem a expressao."""
    a = max([low.rfind(c, 0, ini) for c in _FIM_DE_ORACAO] + [-1]) + 1
    bs = [low.find(c, fim) for c in _FIM_DE_ORACAO]
    return a, min([x for x in bs if x >= 0] + [len(low)])


_RE_ANO = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
_RE_TOKEN = re.compile(r"\S+")

# R2 item 8 · titulo de secao vindo de PDF chega com cada letra dobrada (efeito do
# negrito): «SSIITTUUAAZZIIOONNEE», «22002266». Um ano dobrado nao casa com padrao
# nenhum, e o cabecalho ficava sem ano.
def _colapsa_duplicadas(token: str) -> str:
    """«SSIITTUUAAZZIIOONNEE» -> «SITUAZIONE». So colapsa quando TODOS os caracteres do
    token vem em pares — «settimana», que tem um «tt» legitimo, nao casa, porque o «s»
    nao vem dobrado. Nao se aplica ao texto inteiro: so a leitura do cabecalho passa
    por aqui, e o trecho citado continua a ser o original."""
    if len(token) < 6 or len(token) % 2:
        return token
    if all(token[i] == token[i + 1] for i in range(0, len(token), 2)):
        return token[::2]
    return token


# (a) o cabecalho tem de ser inequivocamente de UMA edicao: sem uma destas marcas, nao
# se aceita ano nenhum dele.
_RE_CABECALHO_DE_EDICAO = re.compile(
    r"(?<![a-z])(?:bollettino|comunicato|notiziario|avviso|nota\b|report|newsletter|"
    r"n[.°]\s*\d|del\s+\d|aggiornato|settimana|edizione|anno\s+\d)")
# ATOS citados no meio do texto trazem anos de OUTRO assunto («D.lgs 14 agosto 2012»):
# esses nao tornam o cabecalho ambiguo, porque nao datam afirmacao nenhuma daqui.
LIMITE_DO_CABECALHO = 600


LETRAS_DE_PROSA = 80      # uma linha desta largura ja e corpo, nao cabecalho


def _fim_do_cabecalho(alvo: str) -> int:
    """Onde acaba o cabecalho: na primeira linha de PROSA.

    Cabecalho e linha curta («Bollettino fitosanitario n. 17/2026 del 04.05.2026»,
    «VITICOLTURA»); corpo e linha larga. Contar «as primeiras cinco linhas» punha o
    corpo dentro do cabecalho num documento de tres linhas — medido a correr isto.
    Texto sem quebras de linha: as primeiras LIMITE_DO_CABECALHO letras.
    """
    t = str(alvo or "")
    if "\n" not in t.strip():
        # Texto achatado numa linha (o caso dos PDFs, 123/275 na copia da Sala): o
        # cabecalho nao pode ser o documento todo, senao nenhuma afirmacao esta «abaixo»
        # dele e a regra do ano nunca corre. Toma-se o inicio: nunca mais de 40% do
        # texto, nunca mais de LIMITE_DO_CABECALHO letras.
        return int(min(LIMITE_DO_CABECALHO, max(120, len(t) * 0.4))) if t else 0
    p = 0
    for l in t.splitlines(keepends=True):
        if len(l.strip()) >= LETRAS_DE_PROSA or p >= LIMITE_DO_CABECALHO:
            break
        p += len(l)
    return min(p, LIMITE_DO_CABECALHO)


def _cabecalho_legivel(low, fim_cab):
    """O cabecalho com os tokens dobrados pelo PDF desdobrados, SO para procurar as
    marcas de edicao. «BBOOLLLLEETTTTIINNOO» -> «bollettino». Nao devolve offsets: quem
    precisa de offset usa `_anos_em`, que anda token a token no original."""
    return " ".join(_colapsa_duplicadas(m.group(0)) for m in _RE_TOKEN.finditer(low[:fim_cab]))


def _anos_em(low, alvo, a, b):
    """Os anos escritos entre `a` e `b`, token a token, tambem quando o token vem com as
    letras dobradas pelo PDF. Devolve (ano, offset_no_original, expressao_original)."""
    fora = []
    for m in _RE_TOKEN.finditer(low[a:b]):
        tok = m.group(0)
        for cand in (tok, _colapsa_duplicadas(tok)):
            achou = _RE_ANO.search(cand)
            if achou:
                p = a + m.start()
                fora.append((achou.group(1), p, alvo[p:a + m.end()]))
                break
    return fora


def _ano_governante(low, alvo, ini, fim):
    """D147 (R2 item 2) · o ano que GOVERNA esta afirmacao, quando a expressao nao o
    escreve. Cinco condicoes, todas obrigatorias:

      (a) o cabecalho e inequivocamente de UMA edicao (tem marca de boletim/edicao);
      (b) o ano governa a afirmacao — a afirmacao esta no corpo dessa mesma edicao;
      (c) nenhum OUTRO ano pode datar A MESMA afirmacao: nem na oracao da afirmacao,
          nem entre o cabecalho e ela (ano de outra seccao ou de outro assunto mata a
          leitura; anos de ATOS citados nao contam, porque nao datam nada daqui);
      (d) os dois trechos ficam citados — o da afirmacao e o do ano;
      (e) a procedencia registra que dia/mes vem da afirmacao e o ano do cabecalho.

    Nao e mais a janela de 40 letras da primeira versao: essa lia qualquer ano perto,
    incluindo o de outro assunto. Ano nao inequivoco -> None, e o valor fica SEM_ANO.
    """
    a, b = _limites_da_oracao(low, ini, fim)
    # (c) na propria afirmacao
    na_oracao = [x for x in _anos_em(low, alvo, a, b) if not (ini <= x[1] < fim)]
    distintos = {x[0] for x in na_oracao}
    if len(distintos) > 1:
        return None, None, "AMBIGUO: mais de um ano pode datar esta afirmacao"
    if len(distintos) == 1:
        ano, p, expr = na_oracao[0]
        return ano, _basis_do_ano(alvo, p, expr), (
            "dia/mes da afirmacao; ano escrito na MESMA afirmacao («%s»)" % expr)
    # sem ano na afirmacao: o cabecalho da mesma edicao
    fim_cab = _fim_do_cabecalho(alvo)
    if ini < fim_cab:
        return None, None, "a expressao esta no proprio cabecalho: nao ha cabecalho acima dela"
    if not _RE_CABECALHO_DE_EDICAO.search(_cabecalho_legivel(low, fim_cab)):
        return None, None, "(a) o cabecalho nao se identifica como edicao: ano NAO SEI"
    no_cab = _anos_em(low, alvo, 0, fim_cab)
    distintos_cab = {x[0] for x in no_cab}
    if len(distintos_cab) != 1:
        return None, None, ("(a) o cabecalho nao traz um ano inequivoco (%s): ano NAO SEI"
                            % (", ".join(sorted(distintos_cab)) or "nenhum"))
    ano = next(iter(distintos_cab))
    # (c) nenhum outro ano entre o cabecalho e a afirmacao — tirando os anos de ATOS
    for outro, p, _ in _anos_em(low, alvo, fim_cab, a):
        if outro != ano and not _RE_ATO.search(low[max(0, p - 80):p]):
            return None, None, ("(c) ha outro ano (%s) entre o cabecalho e a afirmacao: "
                                "ano NAO SEI" % outro)
    _, p, expr = no_cab[0]
    return ano, _basis_do_ano(alvo, p, expr), (
        "dia/mes da afirmacao; ano do CABECALHO da mesma edicao («%s»), inequivoco" % expr)


def _basis_do_ano(alvo, p, expr):
    """(d) o segundo trecho: onde o ano esta escrito, com o seu offset."""
    return {"TRECHO": re.sub(r"\s+", " ", alvo[max(0, p - 60):p + 60]).strip(),
            "OFFSET": p, "EXPRESSAO": expr}


def _publicacao_provada(pub_iso, basis):
    """D63/D147: relativa so se conta com publicacao PROVADA — data ISO E base que nao
    seja NAO SEI. Sem base declarada, nao esta provada."""
    if not pub_iso or not basis:
        return False
    return not str(basis).strip().upper().startswith(("NAO SEI", "NÃO SEI", "UNKNOWN", "NOT_KNOWN"))


_SEMANA_PASSADA = ("la settimana scorsa", "la settimana appena trascorsa", "nei giorni scorsi")
_SEMANA_ATUAL = ("questa settimana", "la settimana in corso")


def _conta_relativa_pela_edicao(expr, periodo):
    """D63/D149 (R2 item 9) · uma relativa de SEMANA ancorada no periodo IMPRESSO do
    MESMO boletim e leitura valida — «questa settimana» num boletim que imprime
    «settimana 39 dal 22/09/2026 al 29/09/2026» e essa semana, sem precisar da
    publicacao. A composicao fica registada (que periodo foi usado, e como).

    Devolve (valor, inicio, fim, precisao, composicao) ou None.
    """
    if not periodo:
        return None
    e = re.sub(r"\s+", " ", _fold(expr)).strip()
    if e not in _SEMANA_PASSADA + _SEMANA_ATUAL:
        return None
    ini, fim, prec = periodo["VALOR_INICIO"], periodo["VALOR_FIM"], periodo["PRECISAO"]
    if SEM_ANO in str(ini):
        return None                      # periodo sem ano nao ancora nada
    passada = e in _SEMANA_PASSADA
    if prec == WEEK:
        m = re.match(r"^(\d{4})-W(\d{2})$", str(ini))
        if not m:
            return None
        ano, n = int(m.group(1)), int(m.group(2))
        if passada:
            n -= 1
            if n < 1:
                ano, n = ano - 1, 52
        v = _val_semana(str(ano), n)
        alcance = (v, v)
    else:
        try:
            d1, d2 = date.fromisoformat(str(ini)[:10]), date.fromisoformat(str(fim)[:10])
        except ValueError:
            return None
        if passada:
            d1, d2 = d1 - timedelta(days=7), d2 - timedelta(days=7)
        alcance = (d1.isoformat(), d2.isoformat())
        v = "%s/%s" % alcance
    composicao = {
        "ANCORA": "PERIODO_DA_EDICAO",
        "PERIODO_IMPRESSO": periodo["VALOR"],
        "PERIODO_BASIS": {"TRECHO": periodo["BASIS"]["TRECHO"],
                          "OFFSET": periodo["BASIS"]["OFFSET"],
                          "EXPRESSAO": periodo["BASIS"]["EXPRESSAO"]},
        "CONTA": ("a semana ANTERIOR ao periodo impresso" if passada
                  else "o proprio periodo impresso"),
    }
    return v, alcance[0], alcance[1], (WEEK if prec == WEEK else INTERVAL), composicao


def _conta_relativa(expr, pub_provada):
    """«ieri» -> o dia anterior a publicacao provada. Devolve None sem prova (D63).
    A precisao e a da EXPRESSAO: «lo scorso mese» da um MES, nunca um dia."""
    if not pub_provada:
        return None
    e = re.sub(r"\s+", " ", _fold(expr)).strip()
    d = date.fromisoformat(pub_provada)
    if e in ("oggi", "stamattina"):
        v = d.isoformat()
        return v, v, v, DAY
    if e == "ieri":
        v = (d - timedelta(days=1)).isoformat()
        return v, v, v, DAY
    if e in ("la settimana scorsa", "la settimana appena trascorsa", "nei giorni scorsi"):
        iso = (d - timedelta(days=7)).isocalendar()
        v = _val_semana(str(iso[0]), iso[1])
        return v, v, v, WEEK
    if e in ("questa settimana", "la settimana in corso"):
        iso = d.isocalendar()
        v = _val_semana(str(iso[0]), iso[1])
        return v, v, v, WEEK
    if e == "lo scorso mese":
        ano, mes = (d.year, d.month - 1) if d.month > 1 else (d.year - 1, 12)
        v = _val_mes(str(ano), mes)
        return v, v, v, MONTH
    return None


# «stagione 2025» fica inteiro: a palavra faz parte da expressao de safra, ao contrario
# do «in» de «in luglio», que e so a preposicao que o padrao precisou de ler.
_SO_O_NUCLEO = ("MES_SO",)


def _nucleo(alvo, ini, fim, superficie, m=None):
    """A parte da expressao que CARREGA a data, sem a preposicao que o padrao precisou
    de ler. «in luglio» -> «luglio»; num intervalo, o nucleo e o intervalo todo."""
    bruto = alvo[ini:fim]
    if superficie in _SO_O_NUCLEO and m is not None and m.lastindex:
        g = m.group(1)
        if g:
            p = _fold(bruto).find(_fold(g))
            if p >= 0:
                return bruto[p:p + len(g)]
    return bruto


def _registo(alvo, ini, fim, valor, v_ini, v_fim, precisao, ano,
             ano_origem, origem, ano_basis, superficie, porque, m=None):
    """Um tempo lido, com a base que o prova: trecho, offset e de onde veio o valor."""
    reg = {
        "VALOR": valor, "VALOR_INICIO": v_ini, "VALOR_FIM": v_fim,
        "PRECISAO": precisao,
        "ANO": ano or NAO_SEI,
        "ANO_ORIGEM": ano_origem or "NAO ESCRITO",
        "SEM_ANO": ano is None,
        "ORIGEM": origem,
        "SUPERFICIE": superficie,
        "PORQUE": porque,
        "BASIS": {"EXPRESSAO": alvo[ini:fim],
                  "EXPRESSAO_NUCLEO": _nucleo(alvo, ini, fim, superficie, m),
                  "OFFSET": ini,
                  "FIM": fim,
                  "TRECHO": re.sub(r"\s+", " ", alvo[max(0, ini - 90):fim + 90]).strip(),
                  "FRASE_BRUTA": _frase_bruta(alvo, ini, fim)},
    }
    if ano_basis:
        reg["ANO_BASIS"] = ano_basis
    return reg


def _frase_bruta(alvo, ini, fim):
    """A oracao COMO ESTA no texto (sem colapsar espacos) — quem recebe isto precisa de
    a voltar a encontrar no texto para tapar a data e perguntar de novo."""
    a, b = _limites_da_oracao(alvo, ini, fim)
    return alvo[a:b]


def _com_ano(valor, v_ini, v_fim, ano):
    """Poe o ano lido nos valores que sairam SEM_ANO. Nao mexe em mais nada."""
    troca = lambda v: str(v).replace(SEM_ANO, ano)
    return troca(valor), troca(v_ini), troca(v_fim)


# ── tipar: a que acontecimento a data pertence ───────────────────────────────
def _tipo_e_porque(low, ini, fim, valor, precisao, ano, pub_iso, contrato, origem=None,
                   assinatura=False):
    """Devolve (TIPO ou None, MOTIVO). None = descartada, com o motivo escrito."""
    antes = low[max(0, ini - JANELA_ANTES):ini]
    largo = low[max(0, ini - 220):ini]
    fim_cab = max(_fim_do_cabecalho(low), 200)
    frase = _oracao(low, ini, fim)
    depois = low[fim:fim + 60]

    # 1 · a data do ATO — primeiro, porque «Decreto n. 15068 DEL 08/09/2026» tem a
    #     forma de uma edicao e nao e uma: e a data do decreto.
    if _RE_ATO.search(antes[-80:]):
        return ACT_TIME, "data colada a um ato (decreto, determina, ordinanza, lei)"
    # 2 · o carimbo de quem publica
    perto = _distancia_da_ancora(low, ini, fim)
    if pub_iso and precisao == DAY and origem != RELATIVO_D63 and (
            valor == pub_iso or (ano is None and valor[-6:] == pub_iso[-6:])):
        # D147: a publicacao NUNCA vira facto — nem com ancora colada. A primeira versao
        # desta proposta abria excecao para «rilevazione … effettuata oggi 22 settembre»
        # (C7 do LAB) e isso reprovou tres testes vivos de uma lei que ja existe
        # («Il monitoraggio del 23 settembre 2026», publicado a 23 -> NAO SEI). O C7
        # resolve-se pelo caminho certo: «oggi» e uma RELATIVA presa a publicacao
        # provada, e sai com ORIGEM=RELATIVO_D63 — e essa nao cai aqui, senao «oggi»
        # (que por construcao da o dia da publicacao) nunca poderia datar nada.
        return PUBLICATION_TIME, "carimbo da publicacao (igual ao published_at)"
    if contrato == "EDICAO" and ini < fim_cab:
        if precisao in (INTERVAL, WEEK):
            return PERIODO_DA_EDICAO, "a fonte declara EDICAO e o cabecalho traz um periodo"
        if precisao == DAY:
            return PUBLICATION_TIME, "a fonte declara EDICAO no cabecalho"
    if assinatura:
        return PUBLICATION_TIME, "assinatura do autor/redacao com data: carimbo de publicacao"
    if _RE_PUBLICACAO.search(antes) or _RE_EDICAO.search(largo):
        if not _RE_FACTO.search(antes[-50:]):
            return PUBLICATION_TIME, "edicao / assinatura / «pubblicato» / «aggiornato al»"
    # 3 · a janela de VALIDADE
    if contrato == "VALIDADE" and precisao in (DAY, INTERVAL, WEEK) and ini < fim_cab:
        return VALIDITY_TIME, "a fonte declara VALIDADE no cabecalho"
    if _RE_VALIDADE.search(antes) or (precisao == INTERVAL and _RE_VALIDADE.search(frase)):
        return VALIDITY_TIME, "janela declarada de validade / prazo / deroga"
    if precisao in (INTERVAL, WEEK) and re.search(r"(?:bollettino|riferimento)[^.]{0,80}$", antes)             and not _RE_FACTO.search(frase):
        return PERIODO_DA_EDICAO, "periodo que a edicao cobre — nao e validade e nao e facto"
    # 4 · o que nunca e tempo de facto
    if _RE_PROGRAMA.search(antes):
        return None, "NOME_DE_PROGRAMA (DPI 2025/2026, Piano 2026): nao e data"
    if _RE_INICIO_DE_SERIE.search(antes):
        return None, "INICIO_DE_ATIVIDADE_OU_SERIE: quando algo comecou, nao o acontecimento"
    if _RE_SERIE_DE_ANOS.search(low[max(0, ini - 12):fim + 12]):
        return None, "SERIE_DE_ANOS: e o alcance da medicao, nao a data do medido"
    if _RE_COMPARACAO.search(antes) or _RE_QUANTIDADE.search(antes):
        return (MARKET_PERIOD, "ano/periodo de comparacao de preco") if _RE_MERCADO.search(frase) \
            else (None, "TERMO_DE_COMPARACAO: o ano da referencia nao e o do facto")
    if _RE_EVENTO_TECNICO.search(frase):
        return None, "EVENTO_TECNICO (convegno, fiera, corso): nao e facto do campo"
    if _RE_CONSELHO.search(antes) or _RE_CONSELHO.search(depois):
        return None, "RECOMENDACAO: conselho de tratamento nao e facto acontecido"
    if _RE_PREVISAO.search(antes) or _RE_PREVISAO.search(depois):
        return None, "PREVISAO: o que ainda nao aconteceu nao e facto"
    if pub_iso and precisao == DAY and ano and valor > pub_iso:
        return None, "DEPOIS_DA_PUBLICACAO: nao pode ser um facto ja acontecido"
    # 5 · mercado
    if precisao == SEASON:
        # D147 item 3 · a safra que ENCABECA a afirmacao e o tempo do facto que ela
        # afirma: «La campagna 2026 registra prezzi in calo del 12%» — o facto (os precos
        # cairam) e daquela campanha, com precisao de ano. MARKET_PERIOD e para a safra
        # que QUALIFICA uma cotacao ou serve de comparacao: «nella settimana 38 il prezzo
        # e…», «in linea con la campagna 2024». Quem separa e o papel na frase, nao a
        # presenca da palavra «prezzo».
        a_or, _ = _limites_da_oracao(low, ini, fim)
        encabeca = (ini - a_or) <= 25 and not _RE_QUALIFICA_COTACAO.search(antes[-25:])
        resto = frase.replace(low[ini:fim], " ")
        if encabeca:
            return FACT_TIME, "safra que encabeca a afirmacao: e o tempo do facto afirmado (ANO)"
        if not _RE_MERCADO_FORTE.search(resto) and perto is not None and perto <= DISTANCIA_DA_ANCORA:
            return FACT_TIME, "acontecimento com precisao de safra, ancora a %d letras" % perto
        return MARKET_PERIOD, "safra que qualifica cotacao / comparacao: periodo de mercado"
    if precisao == WEEK and _RE_MERCADO.search(frase):
        return MARKET_PERIOD, "semana de rilevacao de preco"
    # 6 · o facto, so com ancora PERTO
    d = perto
    if d is not None and d <= DISTANCIA_DA_ANCORA:
        if precisao == YEAR:
            # D147 item 3 (R2): «fechou 2025», «em 2025 …» E facto, com precisao ANO,
            # quando o conteudo atribui o facto aquele ano. A regra da 1.a versao («ano
            # sozinho nunca data observacao») contrariava a decisao do dono e foi
            # retirada. Continua proibido o que o dono manteve proibido: ano de NOME de
            # norma (acima, NOME_DE_PROGRAMA), campanha citada de passagem (MARKET_PERIOD),
            # ano de comparacao (acima) e o ano HISTORICO de OUTRO facto — este ultimo
            # e o que esta guarda apanha.
            if _RE_HISTORICO_DE_OUTRO.search(frase):
                return None, ("ANO_HISTORICO_DE_OUTRO_FACTO: «prima volta / risale a / "
                              "storicamente» data outro acontecimento, nao este")
            return FACT_TIME, "ano atribuido ao facto pelo conteudo, ancora a %d letras" % d
        return FACT_TIME, "ancora de acontecimento a %d letras" % d
    return None, "SEM_ANCORA_DE_ACONTECIMENTO_PERTO: data solta"


def _oracao(low, ini, fim):
    a, b = _limites_da_oracao(low, ini, fim)
    return low[a:b]


def _distancia_da_ancora(low, ini, fim):
    """Menor distancia em letras entre a data e uma palavra de acontecimento, na
    mesma oracao. `None` quando nao ha nenhuma."""
    a, b = _limites_da_oracao(low, ini, fim)
    melhor = None
    for m in _RE_FACTO.finditer(low[a:b]):
        s, e = m.start() + a, m.end() + a
        d = max(s - fim, ini - e, 0)
        melhor = d if melhor is None or d < melhor else melhor
    return melhor


# ── o corpo: sem depender de quebras de linha ────────────────────────────────
_RODAPE = re.compile(r"cookie|privacy|seguici\s+su|iscriviti|newsletter|tel\.?\s*\d|"
                     r"centralino|p\.?\s*iva|copyright|©", re.I)


def corpo_util(texto: str) -> str:
    """O texto que se le. Quando o texto vem numa linha so (123/275 na copia da
    Sala), o corpo e o texto inteiro — o vivo achava 0 linhas de corpo e devolvia
    NAO SEI por forma do ficheiro, nao por falta de data."""
    t = str(texto or "")
    linhas = [l for l in t.splitlines() if l.strip()]
    if len(linhas) <= 2:
        return t
    fica = [l for l in linhas if len(l.strip()) >= 40 and not _RODAPE.search(l)]
    return "\n".join(fica) if fica else t


# ── a porta ──────────────────────────────────────────────────────────────────
def tempos_do_texto(texto: str, published_at: str | None = None, *,
                    contrato_da_fonte: str | None = None,
                    published_at_basis: str | None = None,
                    usar_corpo: bool = True) -> dict:
    """Todos os tempos do texto, cada um no seu tipo, com precisao e base.

    `published_at` serve para TRES coisas e nenhuma quarta: reconhecer o carimbo da
    publicacao, ancorar uma expressao RELATIVA (D63) e marcar limites inferidos.
    NUNCA preenche FACT_TIME sozinho e NUNCA preenche o ano de uma data escrita.
    `published_at_basis` diz se a publicacao esta PROVADA — sem prova, nenhuma
    relativa e contada (D63).
    `contrato_da_fonte` e o que a Collection ja declara por fonte ('VALIDADE',
    'EDICAO', 'PUBLICACAO'); quando existe, manda no cabecalho.
    """
    alvo = corpo_util(texto) if usar_corpo else str(texto or "")
    low = _fold(alvo)
    pub_iso = None
    if published_at and re.match(r"^\d{4}-\d{2}-\d{2}", str(published_at)):
        pub_iso = str(published_at)[:10]
    pub_provada = pub_iso if _publicacao_provada(pub_iso, published_at_basis) else None
    contrato = (contrato_da_fonte or "").strip().upper() or None

    achados = {t: [] for t in TIPOS}
    descartados, ocupado, pendentes = [], [], []

    # ── 1.a passagem · as datas escritas ────────────────────────────────────
    for nome, rx in SUPERFICIES:
        for m in rx.finditer(low):
            ini, fim = m.start(), m.end()
            if any(ini < b and a < fim for a, b in ocupado):
                continue           # ja lido por uma superficie mais completa
            lido = _leitura(nome, m)
            if not lido:
                continue
            valor, v_ini, v_fim, precisao, ano = lido
            if precisao == NAO_SEI:
                # RELATIVA: fica para a 2.a passagem — pode ancorar no periodo IMPRESSO
                # da edicao (R2 item 9), e esse ainda nao foi lido.
                ocupado.append((ini, fim))
                pendentes.append((nome, m, ini, fim, valor))
                continue
            ano_origem = "EXPRESSAO" if ano else None
            origem, ano_basis, procedencia = LITERAL, None, None
            if ano is None and precisao in (WEEK, DAY, MONTH, INTERVAL):
                ano, ano_basis, procedencia = _ano_governante(low, alvo, ini, fim)
                if ano:
                    ano_origem, origem = "MESMO_DOCUMENTO_INEQUIVOCO", CABECALHO
                    valor, v_ini, v_fim = _com_ano(valor, v_ini, v_fim, ano)
            ocupado.append((ini, fim))
            assinatura = bool(_RE_ASSINATURA.search(alvo[max(0, ini - 70):ini]))
            tipo, porque = _tipo_e_porque(low, ini, fim, valor, precisao, ano, pub_iso,
                                          contrato, origem, assinatura)
            reg = _registo(alvo, ini, fim, valor, v_ini, v_fim, precisao, ano,
                           ano_origem, origem, ano_basis, nome, porque, m)
            if procedencia:
                reg["PROCEDENCIA_DO_ANO"] = procedencia      # (e) da D147
            if tipo is None:
                descartados.append(reg)
            else:
                achados[tipo].append(reg)

    # ── 2.a passagem · as relativas, agora que o periodo da edicao e conhecido ──
    periodo = _periodo_impresso(achados[PERIODO_DA_EDICAO])
    for nome, m, ini, fim, valor in pendentes:
        conta = _conta_relativa_pela_edicao(valor, periodo)
        composicao = None
        if conta:
            v, v_ini, v_fim, precisao, composicao = conta
            ano_basis = {"TRECHO": composicao["PERIODO_BASIS"]["TRECHO"],
                         "OFFSET": composicao["PERIODO_BASIS"]["OFFSET"],
                         "EXPRESSAO": composicao["PERIODO_BASIS"]["EXPRESSAO"]}
            procedencia = ("expressao relativa «%s» composta com o periodo IMPRESSO da "
                           "edicao (%s): %s" % (valor, composicao["PERIODO_IMPRESSO"],
                                                composicao["CONTA"]))
            ano_origem = "PERIODO_DA_EDICAO"
        else:
            conta = _conta_relativa(valor, pub_provada)
            if not conta:
                reg = _registo(alvo, ini, fim, valor, valor, valor, NAO_SEI, None,
                               "NAO ESCRITO", RELATIVO_D63, None, nome,
                               "EXPRESSAO_RELATIVA sem ancora: nem periodo impresso da "
                               "edicao nem publicacao provada (D63)", m)
                descartados.append(reg)
                continue
            v, v_ini, v_fim, precisao = conta
            ano_basis = {"TRECHO": "publicacao provada %s · base «%s»"
                                   % (pub_provada, published_at_basis or "declarada"),
                         "OFFSET": None, "EXPRESSAO": pub_provada}
            procedencia = ("expressao relativa «%s» contada a partir da publicacao PROVADA %s"
                           % (valor, pub_provada))
            ano_origem = "PUBLICACAO_PROVADA"
        assinatura = bool(_RE_ASSINATURA.search(alvo[max(0, ini - 70):ini]))
        tipo, porque = _tipo_e_porque(low, ini, fim, v, precisao, str(v)[:4], pub_iso,
                                      contrato, RELATIVO_D63, assinatura)
        reg = _registo(alvo, ini, fim, v, v_ini, v_fim, precisao, str(v)[:4],
                       ano_origem, RELATIVO_D63, ano_basis, nome, porque, m)
        reg["PROCEDENCIA_DO_ANO"] = procedencia
        if composicao:
            reg["COMPOSICAO"] = composicao
            reg["ORIGEM_DETALHE"] = "RELATIVO_EDICAO_D149"
        if tipo is None:
            descartados.append(reg)
        else:
            achados[tipo].append(reg)

    for t in TIPOS:
        achados[t].sort(key=lambda r: r["BASIS"]["OFFSET"])

    escolhido = _escolher_facto(achados[FACT_TIME])
    limites = _limites_inferidos(achados, escolhido, pub_iso)
    return {
        **achados,
        "FACT_TIME_ESCOLHIDO": escolhido,
        "LIMITES_INFERIDOS": limites,
        "DESCARTADOS": descartados,
        "LINHAS_DE_CORPO": len([l for l in str(alvo).splitlines() if l.strip()]),
        "PUBLISHED_AT": pub_iso or NAO_SEI,
        "LEI": "PUBLISHED_AT nunca preenche FACT_TIME; ano ausente fica SEM_ANO",
    }


def _periodo_impresso(periodos):
    """O periodo que a edicao IMPRIME, para ancorar as relativas de semana (R2 item 9).
    Prefere-se o que tem ano: sem ano nao ancora nada."""
    com_ano = [p for p in periodos if SEM_ANO not in str(p["VALOR_INICIO"])]
    return com_ano[0] if com_ano else None


def acontecimento_datavel(frase: str) -> bool:
    """Ha nesta afirmacao um acontecimento que POSSA ter data? (R2 item 5)

    Serve para separar dois silencios que hoje sao o mesmo e nao sao a mesma coisa:
      NAO_EXISTE  conhecimento geral, biologia, definicao, conselho — nada a datar;
      NAO_SEI     aconteceu (ha verbo/palavra de acontecimento), o texto nao diz quando.
    """
    low = _fold(frase or "")
    if _RE_FACTO.search(low):
        return True
    return not (_RE_DEFINICAO.search(low) or len(low.strip()) < 15)


_PESO_PRECISAO = {INTERVAL: 0, DAY: 1, WEEK: 2, MONTH: 3, SEASON: 4, YEAR: 5}


def _escolher_facto(candidatos):
    """Um valor, quando ha um. Com ano vence sem ano; preciso vence grosso; perto
    da ancora vence longe. Valores diferentes ficam marcados AMBIGUO — sem esconder."""
    if not candidatos:
        return None
    ordem = sorted(candidatos, key=lambda r: (r["SEM_ANO"], _PESO_PRECISAO.get(r["PRECISAO"], 9),
                                              r["BASIS"]["OFFSET"]))
    e = dict(ordem[0])
    outros = {c["VALOR"] for c in candidatos} - {e["VALOR"]}
    e["AMBIGUO"] = sorted(outros) if outros else False
    return e


def _limites_inferidos(achados, escolhido, pub_iso):
    """Limite superior: se nao ha FACT_TIME escrito mas ha publicacao provada, o
    facto e ANTERIOR a ela. E inferencia, vai marcada, e nunca entra em FACT_TIME."""
    fora = []
    if escolhido:
        return fora
    if pub_iso:
        fora.append({"LIMITE": "LATEST", "VALOR": pub_iso, "INFERENCIA": True,
                     "PORQUE": "o facto relatado e anterior ou igual a publicacao"})
    for a in achados[PUBLICATION_TIME][:1]:
        fora.append({"LIMITE": "LATEST", "VALOR": a["VALOR_FIM"], "INFERENCIA": True,
                     "PORQUE": "o carimbo de publicacao escrito no texto e posterior ao facto"})
    for a in achados[ACT_TIME][:1]:
        fora.append({"LIMITE": "LATEST", "VALOR": a["VALOR_FIM"], "INFERENCIA": True,
                     "PORQUE": "o ato que trata o facto e posterior ao facto"})
    return fora


def campos_do_fato_proposta(texto, publication_time=None, publication_time_basis=None, **kw):
    """A mesma forma de saida do vivo (`leis/fato_do_texto.campos_do_fato`), para
    o avaliador poder comparar campo a campo. So os campos de TEMPO."""
    pub = publication_time if publication_time and not str(publication_time_basis or "").upper().startswith(
        ("NAO SEI", "NÃO SEI", "UNKNOWN")) else None
    r = tempos_do_texto(texto, pub, contrato_da_fonte=kw.get("contrato_da_fonte"))
    e = r["FACT_TIME_ESCOLHIDO"]
    return {
        "fact_time": e["VALOR"] if e else NAO_SEI,
        "fact_time_precision": e["PRECISAO"] if e else "NOT_KNOWN",
        "fact_time_basis": ("%s · %s · offset %d · «%s»" % (
            e["PRECISAO"], e["PORQUE"], e["BASIS"]["OFFSET"], e["BASIS"]["TRECHO"])) if e else
        "NAO SEI · " + "; ".join("%s (%s)" % (d["VALOR"], d["PORQUE"]) for d in r["DESCARTADOS"][:6]),
        "tempos": {t: r[t] for t in TIPOS},
        "limites_inferidos": r["LIMITES_INFERIDOS"],
        "descartados": r["DESCARTADOS"],
    }


if __name__ == "__main__":
    import json
    ex = ("Il Bollettino fitosanitario relativo al monitoraggio della mosca delle olive "
          "(Bactrocera oleae) effettuato dal 1° al 4 settembre 2026 sul territorio regionale. "
          "Con Decreto Dirigenziale n. 15068 DEL 08/09/2026 e stata approvata la ridefinizione. "
          "BOLLETTINO settimana 39 dal 22/09/2026 al 29/09/2026.")
    print(json.dumps(tempos_do_texto(ex, "2026-09-24"), ensure_ascii=False, indent=1))
