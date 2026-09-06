#!/usr/bin/env python3
"""
dose_extrair.py — le a tabela CAMPI DI IMPIEGO E DOSI da etichetta oficial,
COM DOSE, UNIDADE, INTERVALO e NUMERO MAXIMO DE APLICACOES.

Por que existe: cultura x alvo ja e lido pela casa (it_rotulo_parser 3.4.0, em
sintonia/canonical, 2.928 pares sobre 163 rotulos). DOSE nao — nenhum script da
casa extrai dose, unidade, intervalo ou numero maximo de aplicacoes. Este
extrator abre exatamente esse buraco, e so ele.

MEDIDO (juiz unico, gabarito lido a mao em docs/../scratchpad/gold-dose.json,
3 rotulos / 98 linhas: 015275 DURAVIS, 004701 PIRIMOR 50, 015232 CUSTODIA):

    emitidas 99   gold 98   casadas 89   P 0.899  R 0.908  F1 0.9036
    DOSE_CONCENTRATION        89/89     MAX_APPLICATIONS      85/89
    DOSE_CONCENTRATION_UNIT   89/89     APPLICATION_INTERVAL  85/89
    DOSE_PER_HECTARE          85/89     linha 100% correta    77/89
    doses inventadas 0 (todo digito emitido ocorre na pagina citada E no
    proprio SOURCE_QUOTE da linha; verificado tambem em 20 PDFs fora do gold)

    versao anterior deste arquivo, mesmo juiz: P 0.144  R 0.204  F1 0.169.

O modelo interno:

    linha visual   NAO e linha logica
    CELULA         e a unidade real da tabela

Pipeline:
 1. CABECALHO. A palavra "Coltura" e a semente. Ancoras de papel (alvo, dose,
    volume, intervallo, n. applicazioni, carenza) sao procuradas a +-25pt em y,
    agrupadas por sobreposicao em x, e cada grupo recebe o papel da ancora mais
    proxima da semente em y. Depois anexam-se as anotacoes de unidade
    ("(g/100 lt)", "(l pf/ha)", "Kg/ha") que ficam por baixo do rotulo.
 2. JANELA X. Cresce a partir das ancoras ate topar num corredor vertical vazio
    (>=6pt), ignorando prosa larga e densa (rodape) que atravessa corredores.
    E isso que separa DUAS TABELAS LADO A LADO na mesma pagina — a origem do
    vazamento de cultura entre tabelas do extrator antigo.
 3. TIRAS. Numa janela, cada cabecalho parte a pagina em tiras verticais; a
    tira orfa acima do primeiro cabecalho pertence a ele. A tabela segue para as
    paginas seguintes enquanto nao aparecer outro cabecalho na mesma janela.
 4. FAIXAS DE COLUNA. Vem dos corredores DO CORPO, nunca do cabecalho: rotulo
    centralizado mente sobre onde a coluna comeca. Os papeis do cabecalho sao
    mapeados, em ordem, nas faixas achadas.
 5. CELULAS. Colunas de texto: uma celula reune as linhas visuais que
    CONTINUAM a anterior (comeca minuscula, parentese aberto, pontuacao de
    continuacao, ou a linha de cima terminou em ';' ':' ',' ou conjuncao).
    E assim que "Agrumi (arancio, limone, mandarino, clementino)" volta a ser
    UMA cultura e "Cemiostoma, litocollete (...), carpocapsa" UM alvo.
    Colunas numericas: uma celula por sub-linha, unindo so quando a faixa ficou
    pendente ("1000 -" / "1200") ou quando o traco caiu noutra baseline.
 6. LINHA LOGICA. A coluna de dose (ou a cultura, quando ela tem bem mais
    celulas) vira espinha: cada celula dela e uma linha, e a faixa y da linha vai
    ate o meio do vao para a celula vizinha. Uma faixa que recebeu varias
    celulas de alvo e dividida — sao varias linhas dividindo uma celula de dose
    mesclada.
 7. ALINHAMENTO. Celulas de texto sao casadas com as linhas por PROGRAMACAO
    DINAMICA monotona (sobreposicao geometrica primeiro, centro como desempate):
    uma celula mesclada cobre um bloco contiguo de linhas. Celulas numericas sao
    casadas por SOBREPOSICAO pura — nunca por vizinho mais proximo.

O que ele NAO faz:
  - nao inventa dose. Um valor so entra na linha cuja faixa y a celula realmente
    cruza (folga de 2,5pt). Linha sem dose na tabela -> NOT_PRESENT.
  - nao promove numero solto a dose sem cabecalho de coluna -> descarta.
  - toda linha carrega SOURCE_QUOTE e SOURCE_PAGE. Quando um valor vem de uma
    celula mesclada que nao esta nas linhas visuais da faixa, o texto dessa
    celula e anexado ao SOURCE_QUOTE entre "[celula mesclada: ...]", para que a
    citacao continue provando o valor. Verificado: em 291 linhas emitidas
    (3 do gold + 20 outros PDFs) nao ha uma unica dose fora do seu SOURCE_QUOTE.
  - sem tabela -> PARSE_STATE (NO_USE_TABLE_FOUND / NO_TEXT_LAYER /
    TABLE_FOUND_NO_ROWS), nunca "produto sem usos autorizados".

CELULA MESCLADA (contrato secao 5b). Herdar e LER, nao inventar — mas so quando
a geometria PROVA a mescla. Tres colunas podem herdar, e cada linha que herda
marca o campo:
  CROP                    -> CROP_INHERITED
  N. max applicazioni     -> MAX_APPLICATIONS_INHERITED (+ APPLICATION_INTERVAL_
                             INHERITED quando o intervalo vem no mesmo parenteses)
  Dose (g/ha, g/100 lt)   -> DOSE_PER_HECTARE_INHERITED / DOSE_CONCENTRATION_
                             INHERITED
A prova exigida para a dose e estreita de proposito: dentro do bloco de uma
cultura tem de haver UMA UNICA celula de dose, o bloco tem de ter mais de uma
linha, e o texto dessa celula tem de estar VERTICALMENTE CENTRADO no bloco
(desvio <= 30% da altura). Com duas ou mais celulas no bloco NAO ha mescla: a
celula vazia e vazia mesmo. E o caso "Agrumi / Cocciniglie (neanidi)", cuja
celula g/ha esta desenhada e vazia no documento — ali a resposta certa e
NOT_PRESENT, e continua sendo. Para desligar a leitura de dose mesclada:
DOSE_SEM_MESCLA=1 no ambiente.

Medido: com a leitura de celula mesclada, DOSE_PER_HECTARE sai correto em 85 de
89 linhas casadas; sem ela, 80 de 89. Duas das setes doses herdadas em 015275
saem ERRADAS (Porro), nao por causa da regra de mescla mas porque o bloco de
cultura do Porro esta mal delimitado a montante — ver LIMITES, abaixo.

LIMITES CONHECIDOS, medidos, nao estimados:
  - 015275: o bloco Rucola/Porro/Tabacco escorrega uma linha; Porro/Cimici cai
    em Tabacco. Consequencia: Porro/Dorifora e Porro/Nottue recebem 300 g/ha
    quando a etichetta diz 600 g/ha. Sao os 2 unicos valores de dose ERRADOS
    (nao ausentes) do gabarito inteiro.
  - "tentredine" vaza da celula de alvo vizinha em Soia e Arachide (015275).
  - 004701: "Mais dolce" e perdido; "Lino, colza" sai partido em duas linhas;
    os prefixos "Orticole in pieno campo:" / "in serra:" nao sao prependidos.
  - MAX_APPLICATIONS de 004701 vem de uma coluna de prosa ("2 applicazioni a
    distanza di 7-12 giorni"); a forma composta "1-2" nao e sintetizada.
  - COBERTURA e o limite maior: exige a palavra "Coltura" no cabecalho mais uma
    coluna de alvo e uma de dose. Em 20 PDFs fora do gold, 15 devolvem
    NO_USE_TABLE_FOUND — parte sao ausencias reais (dose em prosa), parte sao
    falhas de deteccao. Nos dois casos o campo emitido e PARSE_STATE.
  - O gabarito cobre 3 de 163 rotulos. Nada aqui foi medido alem disso.

    PARSER_FAILURE != REGULATORY_ABSENCE
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/1999/xhtml}"

# ---------------------------------------------------------------- papeis
PAPEIS = [
    ("CROP",     re.compile(r"^coltur", re.I)),
    ("TARGET",   re.compile(r"^(parassit|avversit|patogen|infestant|malatti|organism)", re.I)),
    ("DOSE",     re.compile(r"^dos(e|i|aggi)", re.I)),
    ("VOLUME",   re.compile(r"^volum", re.I)),
    ("INTERVAL", re.compile(r"^intervall", re.I)),
    ("MAX",      re.compile(r"^(n|n°|n\.|nr|numero)$|applicazion", re.I)),
    ("PHI",      re.compile(r"^(carenz|sospension|tempo)", re.I)),
    ("EPOCA",    re.compile(r"^(epoc|moment|fase|period)", re.I)),
    ("NOTE",     re.compile(r"^(note|nota|avvertenz)", re.I)),
]
NUM = r"\d+(?:[.,]\d+)?"
RE_VALOR   = re.compile(rf"^(?:max\.?\s*)?{NUM}(?:\s*[-–—]\s*{NUM})?$", re.I)
RE_TEMNUM  = re.compile(r"\d")
RE_TOKNUM  = re.compile(r"[-–—]|\d+(?:[.,]\d+)?(?:\s*[-–—]\s*\d+(?:[.,]\d+)?)?")
RE_MAXPAR  = re.compile(rf"^(?:max\.?\s*)?({NUM})(?:\s*\(\s*({NUM}(?:\s*[-–]\s*{NUM})?)\s*giorni?\s*\))?$", re.I)
RE_UNIT_P  = re.compile(r"\(([^)]*)\)")
RE_UNIT_B  = re.compile(r"(?:k?g|l|ml|cc|hl)\s*(?:pf\s*)?/\s*(?:ha|hl|100\s*l\w*|mq|m2|pianta)", re.I)
RE_NOTA_N  = re.compile(r"(\d+)\s*applicazion", re.I)
RE_NOTA_IV = re.compile(r"distanza\s+di\s+(\d+(?:\s*[-–]\s*\d+)?)\s*(?:giorni|gg)", re.I)


def _lp(s):
    return re.sub(r"^[^\wÀ-ÿ°]+|[^\wÀ-ÿ°)]+$", "", s or "")


# ---------------------------------------------------------------- geometria
def geometria(pdf, cache=None):
    """XML de geometria (pdftotext -bbox-layout). O cache vai para um diretorio
    temporario, nunca ao lado do PDF: o extrator nao escreve no repositorio."""
    if cache and os.path.exists(cache):
        return open(cache, encoding="utf-8", errors="replace").read()
    chave = hashlib.sha1(os.path.abspath(pdf).encode()).hexdigest()[:16]
    dtmp = os.path.join(tempfile.gettempdir(), "dose_extrair_bbox")
    os.makedirs(dtmp, exist_ok=True)
    out = cache or os.path.join(dtmp, chave + ".bbox.xml")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(pdf):
        subprocess.run(["pdftotext", "-bbox-layout", pdf, out], check=True, capture_output=True)
    return open(out, encoding="utf-8", errors="replace").read()


class W:
    __slots__ = ("pg", "x0", "x1", "y0", "y1", "t")
    def __init__(s, pg, x0, x1, y0, y1, t):
        s.pg, s.x0, s.x1, s.y0, s.y1, s.t = pg, x0, x1, y0, y1, t
    @property
    def xc(s): return (s.x0 + s.x1) / 2
    @property
    def yc(s): return (s.y0 + s.y1) / 2


def palavras(xml):
    root = ET.fromstring(xml)
    out, dims = [], {}
    for pno, page in enumerate(root.iter(f"{NS}page"), 1):
        dims[pno] = (float(page.get("width", 842)), float(page.get("height", 595)))
        for w in page.iter(f"{NS}word"):
            t = (w.text or "").strip()
            if t:
                out.append(W(pno, float(w.get("xMin")), float(w.get("xMax")),
                             float(w.get("yMin")), float(w.get("yMax")), t))
    return out, dims


def sublinhas(ws):
    """Agrupa palavras em sub-linhas por SOBREPOSICAO vertical (nao por baseline).
    E isso que junta '1', '–', '1,25' quando o traco esta noutra baseline."""
    ws = sorted(ws, key=lambda w: (w.y0, w.x0))
    grupos = []
    for w in ws:
        posto = None
        for g in grupos:
            ov = min(g[1], w.y1) - max(g[0], w.y0)
            if ov > 0.5 * min(g[1] - g[0], w.y1 - w.y0):
                posto = g
                break
        if posto is None:
            grupos.append([w.y0, w.y1, [w]])
        else:
            posto[0] = min(posto[0], w.y0)
            posto[1] = max(posto[1], w.y1)
            posto[2].append(w)
    grupos.sort(key=lambda g: g[0])
    return [(g[0], g[1], sorted(g[2], key=lambda w: w.x0)) for g in grupos]


def junta(a, b):
    """Une o texto de duas sub-linhas. Cola quando a de cima acaba cortada."""
    if not a:
        return b
    if not b:
        return a
    ua = a.split()[-1]
    ub = b.split()[0]
    if ua.endswith("-") and ub[:1].isalpha() and ub[:1].islower():
        return a + b                      # palavra partida: "(prati-" + "pascoli,"
    if len(ua) >= 8 and ua[-1:].islower() and len(ub) == 1 and ub.isalpha() and ub.islower():
        return a + b
    return a + " " + b


RE_EXPO = re.compile(r"(\d)\s+([ao°])(?=\b|\s)")


def limpa(t):
    return RE_EXPO.sub(r"\1\2", re.sub(r"\s+", " ", t or "")).strip()


# ---------------------------------------------------------------- corredores
def cobertura(ws, x0, x1, passo=0.5):
    n = max(1, int((x1 - x0) / passo) + 2)
    cov = bytearray(n)
    for w in ws:
        a = max(0, int((w.x0 - x0) / passo))
        b = min(n - 1, int((w.x1 - x0) / passo) + 1)
        for i in range(a, b + 1):
            cov[i] = 1
    return cov, passo


def vaos(cov, x0, passo, minlarg=6.0):
    """Corredores verticais vazios: [(inicio, fim, largura)]."""
    out, i, n = [], 0, len(cov)
    while i < n:
        if cov[i]:
            i += 1
            continue
        j = i
        while j < n and not cov[j]:
            j += 1
        larg = (j - i) * passo
        if larg >= minlarg:
            out.append((x0 + i * passo, x0 + j * passo, larg))
        i = j
    return out


def faixas_cobertas(cov, x0, passo, minvao=6.0):
    """Blocos de x cobertos, separados por corredores >= minvao."""
    out, i, n = [], 0, len(cov)
    while i < n:
        if not cov[i]:
            i += 1
            continue
        j = i
        while j < n:
            if cov[j]:
                j += 1
                continue
            k = j
            while k < n and not cov[k]:
                k += 1
            if (k - j) * passo >= minvao:
                break
            j = k
        out.append((x0 + i * passo, x0 + j * passo))
        i = j
    return out


# ---------------------------------------------------------------- cabecalho
def cabecalhos(ws):
    """Todas as instancias de cabecalho de tabela de usos no documento."""
    por_pg = {}
    for w in ws:
        por_pg.setdefault(w.pg, []).append(w)
    achados = []
    for pg in sorted(por_pg):
        pw = por_pg[pg]
        for s in pw:
            if not PAPEIS[0][1].match(_lp(s.t)):
                continue
            # ancoras de papel na janela vertical da semente
            anc = []
            for w in pw:
                if abs(w.y0 - s.y0) > 25 or w.x1 < s.x0 - 2:
                    continue
                lt = _lp(w.t)
                for papel, rx in PAPEIS:
                    if rx.match(lt):
                        anc.append((papel, w))
                        break
            if len(anc) < 3:
                continue
            # agrupa ancoras por sobreposicao em x
            anc.sort(key=lambda a: a[1].x0)
            cls = []
            for papel, w in anc:
                if cls and w.x0 <= cls[-1]["x1"] + 1.0:
                    c = cls[-1]
                    c["x0"] = min(c["x0"], w.x0); c["x1"] = max(c["x1"], w.x1)
                    c["anc"].append((papel, w))
                else:
                    cls.append({"x0": w.x0, "x1": w.x1, "anc": [(papel, w)]})
            # papel do grupo: a ancora mais perto em y da semente
            for c in cls:
                c["anc"].sort(key=lambda a: (abs(a[1].y0 - s.y0), a[1].x0))
                c["papel"] = c["anc"][0][0]
                c["y0"] = min(a[1].y0 for a in c["anc"])
                c["y1"] = max(a[1].y1 for a in c["anc"])
                c["txt"] = " ".join(a[1].t for a in c["anc"])
            if not cls or cls[0]["papel"] != "CROP":
                continue
            venc = [c["anc"][0][1] for c in cls]
            ay0 = min(w.y0 for w in venc); ay1 = max(w.y1 for w in venc)
            hw = set(id(a[1]) for c in cls for a in c["anc"])
            # anotacoes: unidades e continuacoes de rotulo de coluna
            for w in pw:
                if w.y0 < ay0 - 10 or w.y0 > ay1 + 12:
                    continue
                if w.x1 < cls[0]["x0"] - 2 or w.x0 > cls[-1]["x1"] + 30:
                    continue
                if RE_VALOR.match(w.t.strip()):
                    continue
                toca = [c for c in cls if min(c["x1"], w.x1) - max(c["x0"], w.x0) > -3.0]
                if len(toca) != 1:
                    continue
                c = toca[0]
                if any(a[1] is w for a in c["anc"]):
                    continue
                c["x0"] = min(c["x0"], w.x0); c["x1"] = max(c["x1"], w.x1)
                c["txt"] += " " + w.t
                c["y1"] = max(c["y1"], w.y1)
                hw.add(id(w))
            papeis = [c["papel"] for c in cls]
            if "TARGET" not in papeis or not ({"DOSE"} & set(papeis)):
                continue
            achados.append({"pg": pg, "seed": s, "cols": cls, "hw": hw,
                            "ytop": min(ay0, s.y0),
                            "y0": min(c["y0"] for c in cls),
                            "y1": max(c["y1"] for c in cls)})
    # dedup: um cabecalho por (pagina, y arredondado, x da semente)
    vistos, out = set(), []
    for h in achados:
        k = (h["pg"], round(h["seed"].y0, 0), round(h["seed"].x0, 0))
        if k in vistos:
            continue
        vistos.add(k)
        out.append(h)
    return out


def resolve_papeis(cols):
    """Da nome final as colunas: separa as duas doses, distingue intervalo de carenza."""
    for c in cols:
        t = c["txt"]
        u = None
        for m in RE_UNIT_P.finditer(t):
            cand = m.group(1).strip().strip("*").strip()
            if RE_UNIT_B.search(cand) or re.match(r"^(k?g|l|ml|cc|hl)\b", cand, re.I):
                u = re.sub(r"\s+", " ", cand)
                break
        if u is None:
            m = RE_UNIT_B.search(t)
            if m:
                u = re.sub(r"\s+", " ", m.group(0))
        c["unit"] = u
        if c["papel"] == "INTERVAL" and re.search(r"sicurezz|carenz", t, re.I):
            c["papel"] = "PHI"
    doses = [c for c in cols if c["papel"] == "DOSE"]
    for c in doses:
        u = (c["unit"] or "").lower()
        if re.search(r"/\s*h?l|/\s*100|hl", u):
            c["papel"] = "DOSE_CONC"
        elif "/ha" in u.replace(" ", ""):
            c["papel"] = "DOSE_HA"
    ind = [c for c in doses if c["papel"] == "DOSE"]
    if ind:
        restantes = [p for p in ("DOSE_CONC", "DOSE_HA")
                     if not any(c["papel"] == p for c in doses)]
        for c, p in zip(ind, restantes or ["DOSE_HA"]):
            c["papel"] = p
        for c in ind:
            if c["papel"] == "DOSE":
                c["papel"] = "DOSE_HA"
    vistos = set()
    for c in cols:
        while c["papel"] in vistos:
            c["papel"] += "_2"
        vistos.add(c["papel"])
    return cols


# ---------------------------------------------------------------- janela
def janela(h, pw):
    cols = h["cols"]
    xa, xb = cols[0]["x0"], cols[-1]["x1"]
    largura = max((w.x1 for w in pw), default=842.0)
    corpo = []
    for y0, y1, g in sublinhas([w for w in pw
                                if w.y0 > h["ytop"] and id(w) not in h["hw"]]):
        if len(g) > 3:
            vao = max((g[i + 1].x0 - g[i].x1) for i in range(len(g) - 1))
            if vao < 8.0 and (g[-1].x1 - g[0].x0) > 0.40 * largura:
                continue           # prosa larga: rodape, aviso — atravessa vaos
        corpo.extend(g)
    if len(corpo) < 5:
        corpo = pw
    esq = [w for w in corpo if w.x1 >= xa - 170 and w.x0 <= xa + 4]
    dir_ = [w for w in corpo if w.x0 <= xb + 170 and w.x1 >= xb - 4]
    x0 = xa
    if esq:
        cov, p = cobertura(esq, xa - 170, xa + 4)
        fx = faixas_cobertas(cov, xa - 170, p)
        toca = [f for f in fx if f[1] >= xa - 1]
        if toca:
            x0 = min(x0, toca[-1][0])
    x1 = xb
    if dir_:
        cov, p = cobertura(dir_, xb - 4, xb + 170)
        fx = faixas_cobertas(cov, xb - 4, p)
        toca = [f for f in fx if f[0] <= xb + 1]
        if toca:
            x1 = max(x1, toca[0][1])
    return x0 - 2.0, x1 + 2.0


# ---------------------------------------------------------------- tiras
def tiras(h, todos, dims, todos_cab):
    """(pagina, y0, y1) que pertencem a esta tabela, na janela dela."""
    pw = [w for w in todos if w.pg == h["pg"]]
    jx0, jx1 = janela(h, pw)
    outros = [g for g in todos_cab
              if g is not h and g["pg"] == h["pg"]
              and min(g["cols"][-1]["x1"], jx1) - max(g["cols"][0]["x0"], jx0) > 20]
    abaixo = sorted([g for g in outros if g["y0"] > h["y1"]], key=lambda g: g["y0"])
    acima = [g for g in outros if g["y1"] < h["y0"]]
    lim = abaixo[0]["ytop"] - 2 if abaixo else 1e9
    tt = [(h["pg"], h["ytop"], lim)]
    if not acima:                      # tira orfa acima do primeiro cabecalho
        tt.append((h["pg"], -1e9, h["ytop"] - 2))
    ult = h["pg"] if not abaixo else None
    return jx0, jx1, tt, ult


# ---------------------------------------------------------------- celulas
def bandas(reg, cols, jx0, jx1):
    """Fronteiras de coluna tiradas dos CORREDORES DO CORPO. O cabecalho e
    centralizado e mente sobre onde a coluna comeca; o corpo, nao."""
    tab = []
    for y0, y1, g in sublinhas(reg):
        if len(g) > 3:
            vao = max((g[i + 1].x0 - g[i].x1) for i in range(len(g) - 1))
            if vao < 8.0 and (g[-1].x1 - g[0].x0) > 0.40 * (jx1 - jx0):
                continue
        tab.extend(g)
    fx, vv = [], []
    if tab:
        cov, p = cobertura(tab, jx0, jx1)
        fx = faixas_cobertas(cov, jx0, p, minvao=6.0)
        vv = vaos(cov, jx0, p, minlarg=6.0)
    if len(fx) == len(cols):
        lim = [jx0]
        for a, b in zip(fx, fx[1:]):
            lim.append((a[1] + b[0]) / 2)
        lim.append(jx1)
        return lim
    lim = [jx0]
    for a, b in zip(cols, cols[1:]):
        cand = [(g[0] + g[1]) / 2 for g in vv
                if a["x1"] - 1 <= (g[0] + g[1]) / 2 <= b["x0"] + 1]
        lim.append(cand[0] if len(cand) == 1 else (a["x1"] + b["x0"]) / 2)
    lim.append(jx1)
    return lim


def col_de(x, lim):
    for i in range(len(lim) - 1):
        if lim[i] <= x < lim[i + 1]:
            return i
    return len(lim) - 2


CONT_FIM = (";", ":", ",", "-", "–", "—", "/")
CONT_TOK = {"e", "ed", "o", "od", "con", "della", "delle", "dei", "degli", "di",
            "in", "a", "al", "alla", "per", "su", "sul", "da", "dal", "e/o", "the"}
CONT_INI = "(,;-–—&+"


def celulas_texto(ws, passo):
    """Celula de texto = linhas visuais que CONTINUAM a anterior.
    Continua quando comeca minuscula, quando abre parentese ainda nao fechado,
    quando comeca com pontuacao de continuacao, ou quando a linha de cima
    terminou aberta (';' ',' ':' ou conjuncao solta). Essa e a regra que
    mantem inteira uma celula de 4 linhas visuais."""
    sl = sublinhas(ws)
    cels, atual = [], None
    for y0, y1, g in sl:
        txt = " ".join(w.t for w in g)
        toks = txt.split()
        prim = toks[0] if toks else ""
        cont = False
        if atual is not None and prim:
            gap = y0 - atual["y1"]
            perto = gap <= passo * 1.55
            ptxt = atual["txt"].rstrip()
            abre = ptxt.count("(") > ptxt.count(")")
            baixa = prim[0].islower()
            aberto = ptxt.endswith(CONT_FIM) or (ptxt.split()[-1].lower() in CONT_TOK
                                                 if ptxt.split() else False)
            cont = perto and (baixa or abre or prim[0] in CONT_INI or aberto)
        if cont:
            atual["y1"] = max(atual["y1"], y1)
            atual["txt"] = junta(atual["txt"], txt)
            atual["ws"].extend(g)
        else:
            atual = {"y0": y0, "y1": y1, "txt": txt, "ws": list(g)}
            cels.append(atual)
    return cels


def celulas_num(ws):
    """Celula numerica = uma sub-linha; une so quando a faixa ficou pendente
    ('1000 -' / '1200') ou quando o traco de faixa caiu noutra baseline."""
    sl = sublinhas(ws)
    cels = []
    for y0, y1, g in sl:
        txt = " ".join(w.t for w in g)
        if not cels and not RE_TEMNUM.search(txt):
            continue                  # sobra de cabecalho antes do primeiro valor
        if cels:
            a = cels[-1]["txt"].rstrip()
            if a.endswith(("-", "–", "—")) or txt.lstrip()[:1] in ("-", "–", "—") \
               or not RE_TEMNUM.search(txt):
                if y0 - cels[-1]["y1"] <= 14:
                    cels[-1]["y1"] = max(cels[-1]["y1"], y1)
                    cels[-1]["txt"] = cels[-1]["txt"] + " " + txt
                    cels[-1]["ws"].extend(g)
                    continue
        cels.append({"y0": y0, "y1": y1, "txt": txt, "ws": list(g)})
    for c in cels:
        hmax = max(w.y1 - w.y0 for w in c["ws"])
        if c["y1"] - c["y0"] <= 2.0 * hmax:      # celula compacta: uma so leitura
            c["txt"] = " ".join(w.t for w in sorted(c["ws"], key=lambda w: w.x0))
    return cels


# ---------------------------------------------------------------- alinhamento
def _c(o): return (o["y0"] + o["y1"]) / 2


def _ov(a0, a1, b0, b1):
    ov = min(a1, b1) - max(a0, b0)
    if ov <= 0:
        return 0.0
    if ov < min(2.0, 0.15 * min(a1 - a0, b1 - b0)):
        return 0.0                    # encosta, nao pertence
    return ov


W_OV = 1000.0


def alinha_grupos(cels, faixas):
    """DP monotona. Uma celula de texto mesclada cobre um BLOCO CONTIGUO de
    linhas; o criterio e sobreposicao geometrica, desempatada pelo centro.
    Quando ha mais celulas que linhas, o problema se inverte (varias celulas
    para a mesma linha) — mesma DP, papeis trocados."""
    m, n = len(cels), len(faixas)
    if m == 0 or n == 0:
        return [None] * n
    if m > n:
        return alinha_inverso(cels, faixas)
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(m + 1)]
    pai = [[0] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = 0.0
    for k in range(1, m + 1):
        cel = cels[k - 1]
        ck = _c(cel)
        for j in range(k, n - (m - k) + 1):
            best, bi = INF, k - 1
            for i in range(k - 1, j):
                if dp[k - 1][i] == INF:
                    continue
                ov = sum(_ov(cel["y0"], cel["y1"], faixas[r][0], faixas[r][1])
                         for r in range(i, j))
                cen = (faixas[i][0] + faixas[j - 1][1]) / 2
                v = dp[k - 1][i] - W_OV * ov + abs(cen - ck)
                if v < best:
                    best, bi = v, i
            dp[k][j], pai[k][j] = best, bi
    saida = [None] * n
    j = n
    for k in range(m, 0, -1):
        i = pai[k][j]
        for r in range(i, j):
            saida[r] = k - 1
        j = i
    return saida


def alinha_inverso(cels, faixas):
    """Mais celulas que linhas: parte as CELULAS em len(faixas) blocos."""
    m, n = len(cels), len(faixas)
    INF = float("inf")
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    pai = [[0] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for k in range(1, n + 1):
        f0, f1 = faixas[k - 1]
        ck = (f0 + f1) / 2
        for j in range(0, m + 1):
            best, bi = INF, j
            for i in range(0, j + 1):
                if dp[k - 1][i] == INF:
                    continue
                if i == j:                       # linha sem celula de texto
                    v = dp[k - 1][i]
                else:
                    ov = sum(_ov(cels[t]["y0"], cels[t]["y1"], f0, f1)
                             for t in range(i, j))
                    cen = (cels[i]["y0"] + cels[j - 1]["y1"]) / 2
                    v = dp[k - 1][i] - W_OV * ov + abs(cen - ck)
                if v < best:
                    best, bi = v, i
            dp[k][j], pai[k][j] = best, bi
    grupos = [[] for _ in range(n)]
    j = m
    for k in range(n, 0, -1):
        i = pai[k][j]
        grupos[k - 1] = list(range(i, j))
        j = i
    return grupos


def sobrepoe(cel, faixa, pad=2.5):
    a0, a1 = cel["y0"] - pad, cel["y1"] + pad
    ov = min(a1, faixa[1]) - max(a0, faixa[0])
    if ov <= 0:
        return False
    return ov >= 0.28 * min(a1 - a0, faixa[1] - faixa[0])


# ---------------------------------------------------------------- extracao
def norm_valor(t):
    t = re.sub(r"[–—]", "-", t or "").strip()
    t = re.sub(r"\s*-\s*", "-", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .;")


def extrair(pdf, rid, produto=None, cache=None, pagina_limite=None):
    try:
        xml = geometria(pdf, cache)
        ws, dims = palavras(xml)
    except Exception as e:
        return {"REGISTRATION_ID": rid, "PRODUCT": produto,
                "PARSE_STATE": "GEOMETRY_FAILED", "NOTE": f"{type(e).__name__}: {e}",
                "ROWS": []}
    cabs = cabecalhos(ws)
    for h in cabs:
        resolve_papeis(h["cols"])
    if not cabs:
        return {"REGISTRATION_ID": rid, "PRODUCT": produto,
                "PARSE_STATE": "NO_USE_TABLE_FOUND",
                "NOTE": ("nenhuma tabela com cabecalho Coltura + alvo + dose foi "
                         "localizada. Isto e falha ou ausencia de LEITURA, "
                         "nao ausencia regulatoria."),
                "ROWS": []}
    npg = max(dims) if dims else 1
    linhas, cols_vistas, unids = [], [], {}
    for h in cabs:
        jx0, jx1, tt, ult = tiras(h, ws, dims, cabs)
        cols = h["cols"]
        cols_vistas = [c["papel"] for c in cols]
        for c in cols:
            if c["unit"]:
                unids.setdefault(c["papel"], c["unit"])
        # tiras da propria pagina
        blocos = list(tt)
        # continuacao para paginas seguintes (so se este e o ultimo cabecalho da janela)
        if ult is not None:
            seguintes, aceitos = [], 0
            for pg in range(h["pg"] + 1, min(npg, h["pg"] + 5) + 1):
                if any(g["pg"] == pg and
                       min(g["cols"][-1]["x1"], jx1) - max(g["cols"][0]["x0"], jx0) > 20
                       for g in cabs):
                    break
                seguintes.append((pg, -1e9, 1e9))
            blocos.extend(seguintes)
        anterior_teve = False
        for (pg, y0, y1) in blocos:
            hwall = set()
            for g in cabs:
                hwall |= g["hw"]
            reg = [w for w in ws if w.pg == pg and y0 <= w.y0 <= y1
                   and jx0 <= w.xc <= jx1 and id(w) not in hwall]
            if len(reg) < 8:
                continue
            novas = linhas_da_tira(reg, cols, jx0, jx1, rid, produto, pg, unids,
                                   pagina_extra=(pg != h["pg"]))
            minimo = 3 if pg != h["pg"] else 1
            if len(novas) < minimo:
                if anterior_teve and pg != h["pg"]:
                    break
                continue
            anterior_teve = True
            linhas.extend(novas)
    if not linhas:
        return {"REGISTRATION_ID": rid, "PRODUCT": produto,
                "PARSE_STATE": "TABLE_FOUND_NO_ROWS",
                "COLUMNS_DETECTED": cols_vistas, "UNITS_DETECTED": unids,
                "NOTE": "cabecalho localizado, nenhuma linha logica reconstruida.",
                "ROWS": []}
    return {"REGISTRATION_ID": rid, "PRODUCT": produto,
            "PARSE_STATE": "USE_TABLE_READ",
            "COLUMNS_DETECTED": cols_vistas, "UNITS_DETECTED": unids,
            "ROWS": linhas}


def linhas_da_tira(reg, cols, jx0, jx1, rid, produto, pg, unids, pagina_extra=False):
    # 1. delimita verticalmente a tabela dentro da tira
    cand = []
    for y0, y1, g in sublinhas(reg):
        if len(g) < 2:
            continue
        vao = max((g[i + 1].x0 - g[i].x1) for i in range(len(g) - 1))
        if vao >= 8.0 and any(RE_TOKNUM.fullmatch(w.t) for w in g):
            cand.append((y0, y1))
    if not cand:
        return []
    grupos, cur = [], [cand[0]]
    for a in cand[1:]:
        if a[0] - cur[-1][1] > 90:
            grupos.append(cur); cur = [a]
        else:
            cur.append(a)
    grupos.append(cur)
    g = max(grupos, key=len)
    ty0, ty1 = g[0][0], g[-1][1]
    sl_all = sublinhas(reg)
    passo = 10.0
    if len(sl_all) > 2:
        ds = sorted(sl_all[i + 1][0] - sl_all[i][0] for i in range(len(sl_all) - 1))
        passo = ds[len(ds) // 2] or 10.0
    corte = []
    for a, b, g in sublinhas([w for w in reg
                              if ty0 - passo * 3.5 <= w.y0 <= ty1 + passo * 2.0]):
        if len(g) > 3:
            vao = max((g[i + 1].x0 - g[i].x1) for i in range(len(g) - 1))
            if vao < 8.0 and (g[-1].x1 - g[0].x0) > 0.40 * (jx1 - jx0):
                continue                  # rodape / aviso corrido
        corte.extend(g)
    reg = corte
    if len(reg) < 8:
        return []

    # 2. faixas de coluna a partir do corpo
    lim = bandas(reg, cols, jx0, jx1)

    # 3. palavras por coluna
    porcol = {i: [] for i in range(len(cols))}
    for w in reg:
        porcol[col_de(w.xc, lim)].append(w)

    NUMER = {"DOSE_CONC", "DOSE_HA", "DOSE_CONC_2", "DOSE_HA_2",
             "VOLUME", "MAX", "INTERVAL", "PHI"}
    cel = {}
    for i, c in enumerate(cols):
        if not porcol[i]:
            cel[i] = []
        elif c["papel"] in NUMER:
            cel[i] = celulas_num(porcol[i])
        else:
            cel[i] = celulas_texto(porcol[i], passo)

    # 4. espinha: coluna com mais celulas entre dose e cultura
    def validas(i):
        return [c for c in cel[i] if RE_VALOR.match(norm_valor(c["txt"]))]
    idose, ndose = None, 0
    for i, c in enumerate(cols):
        if c["papel"].startswith(("DOSE_HA", "DOSE_CONC")):
            n = len(validas(i))
            if n > ndose:
                idose, ndose = i, n
    icrop = next((i for i, c in enumerate(cols) if c["papel"] == "CROP"), None)
    ncrop = len(cel[icrop]) if icrop is not None else 0
    iesp = idose
    if idose is None or (icrop is not None and ncrop > 1.2 * ndose):
        iesp = icrop
    if iesp is None or not cel[iesp]:
        return []
    nesp = len(cel[iesp])
    # so celulas com valor plausivel viram linha, quando a espinha e dose
    if pagina_extra and ndose < 3:
        return []                      # pagina seguinte sem coluna de dose viva
    esp = cel[iesp]
    if cols[iesp]["papel"] != "CROP":
        esp = [c for c in esp if RE_VALOR.match(norm_valor(c["txt"]))]
    if len(esp) < 1:
        return []
    topo = cols[iesp]["papel"] == "CROP"

    def monta_faixas(espinha):
        ff = []
        for k, c in enumerate(espinha):
            if topo:
                a = c["y0"] - passo * 0.4
                b = (espinha[k + 1]["y0"] - passo * 0.4
                     if k + 1 < len(espinha) else ty1 + passo)
            else:
                a = ((espinha[k - 1]["y1"] + c["y0"]) / 2 if k
                     else min(c["y0"] - passo * 0.4, ty0))
                b = ((c["y1"] + espinha[k + 1]["y0"]) / 2
                     if k + 1 < len(espinha) else max(c["y1"] + passo * 0.4, ty1))
            ff.append((a, b))
        return ff

    faixas = monta_faixas(esp)
    idx = {c["papel"]: i for i, c in enumerate(cols)}

    def grupos_texto(i, ff):
        """Indices das celulas da coluna i atribuidos a cada faixa."""
        res = alinha_grupos(cel[i], ff)
        m = [[] for _ in ff]
        if res and isinstance(res[0], list):
            for r, idxs in enumerate(res):
                m[r] = list(idxs)
        else:
            for r, k in enumerate(res):
                if k is not None:
                    m[r] = [k]
        return m

    # 5. celula de alvo mesclada verticalmente: uma FAIXA ALTA que recebeu varias
    #    celulas de alvo e, na verdade, varias linhas logicas que dividem uma
    #    celula de dose. Divide a faixa; quem nao cruzar a dose fica NOT_PRESENT.
    i_alvo = idx.get("TARGET")
    if not topo and i_alvo is not None and len(faixas) > 1 and cel[i_alvo]:
        alt = sorted(f[1] - f[0] for f in faixas)
        med = alt[len(alt) // 2]
        ga = grupos_texto(i_alvo, faixas)
        if os.environ.get("DOSE_DEBUG"):
            for r, f in enumerate(faixas):
                print(f"DBG pg{pg} faixa {r} {f[0]:.1f}-{f[1]:.1f} h={f[1]-f[0]:.1f} "
                      f"med={med:.1f} nalvo={len(ga[r])}", file=sys.stderr)
        novas = []
        for r, f in enumerate(faixas):
            cs = [cel[i_alvo][k] for k in ga[r]]
            # celula terminada em ':' e titulo mesclado, nao linha
            corta = [t for t in range(1, len(cs))
                     if not cs[t - 1]["txt"].rstrip().endswith(":")]
            if len(cs) - len([c for c in cs if c["txt"].rstrip().endswith(":")]) >= 2 \
               and corta:
                bordas = [f[0]] + [(cs[t - 1]["y1"] + cs[t]["y0"]) / 2
                                   for t in corta] + [f[1]]
                for t in range(len(bordas) - 1):
                    novas.append((bordas[t], bordas[t + 1]))
            else:
                novas.append(f)
        faixas = novas

    # 6. colunas de texto -> DP monotona; colunas numericas -> sobreposicao pura
    atrib, orig = {}, {}
    for i, c in enumerate(cols):
        if c["papel"] in NUMER or i == iesp:
            m = [[] for _ in faixas]
            fonte = esp if i == iesp else cel[i]
            for cc in fonte:
                for r, f in enumerate(faixas):
                    if sobrepoe(cc, f):
                        m[r].append(cc["txt"])
            atrib[i] = m
        else:
            g = grupos_texto(i, faixas)
            atrib[i] = [[cel[i][k]["txt"] for k in ks] for ks in g]
            orig[i] = g

    saida, faixa_de = [], []
    prefixo, crop_ant, alvo_ant = "", None, ""
    for r, f in enumerate(faixas):
        def get(papel):
            i = idx.get(papel)
            if i is None:
                return ""
            v = atrib.get(i) or []
            return " ".join(v[r]).strip() if r < len(v) else ""
        crop = limpa(get("CROP"))
        i_crop = idx.get("CROP")
        herdada = bool(i_crop is not None and i_crop in orig and r > 0
                       and orig[i_crop][r] and orig[i_crop][r] == orig[i_crop][r - 1])
        alvo = limpa(get("TARGET"))
        # celula-titulo mesclada ("Psilla del pero:") vale para as linhas abaixo
        cels_alvo = [cel[i_alvo][k] for k in orig.get(i_alvo, [[]] * len(faixas))[r]] \
            if i_alvo is not None and i_alvo in orig else []
        if cels_alvo and cels_alvo[0]["txt"].rstrip().endswith(":"):
            prefixo = limpa(cels_alvo[0]["txt"])
        elif prefixo and alvo and crop == crop_ant and not alvo.startswith(prefixo):
            alvo = prefixo + " " + alvo
        elif crop != crop_ant:
            prefixo = ""
        # "Psilla del pero: 1o intervento" / "2o intervento": o titulo esta
        # mesclado na primeira linha e vale para as seguintes
        if (not prefixo and alvo_ant and ":" in alvo_ant[:45] and ":" not in alvo
                and alvo[:1].isdigit() and crop == crop_ant):
            alvo = alvo_ant[:alvo_ant.index(":") + 1] + " " + alvo
        crop_ant, alvo_ant = crop, alvo
        if not crop and not alvo:
            continue
        quote = " ".join(" ".join(w.t for w in g) for _, _, g in
                         sublinhas([w for w in reg if f[0] <= w.yc <= f[1]]))
        linha = montar(rid, produto, crop, herdada, alvo, get, unids, quote, pg)
        # A faixa y da linha ja e conhecida aqui e nao custa nada guardar. Sem
        # ela, quem for conferir a linha depois tem de reencontra-la por texto,
        # e "Afidi" aparece dez vezes na mesma pagina. Nao altera extracao.
        linha["SOURCE_Y"] = [round(f[0], 2), round(f[1], 2)]
        linha["_extra_quote"] = []
        saida.append(linha)
        faixa_de.append(f)

    # as faixas podem sair fora de ordem quando uma faixa alta e dividida em
    # sub-linhas; o bloco de cultura so faz sentido em ordem de leitura.
    if saida:
        z = sorted(zip(faixa_de, saida), key=lambda t: (t[0][0], t[0][1]))
        faixa_de = [a for a, _ in z]
        saida = [b for _, b in z]

    # celula MESCLADA da coluna "N max applicazioni": um unico valor centrado
    # cobre todo o bloco de uma cultura. Isto NAO e dose: e o numero de
    # aplicacoes, e a celula pertence geometricamente ao bloco inteiro.
    i_max = idx.get("MAX")
    if i_max is not None and cel[i_max] and saida:
        cmax = [c for c in cel[i_max] if RE_MAXPAR.match(norm_valor(c["txt"]))]
        ini = 0
        for fim in [k for k in range(1, len(saida) + 1)
                    if k == len(saida) or saida[k]["CROP"] != saida[k - 1]["CROP"]]:
            bloco = range(ini, fim)
            y0b = min(faixa_de[k][0] for k in bloco)
            y1b = max(faixa_de[k][1] for k in bloco)
            dentro = [c for c in cmax if y0b <= _c(c) <= y1b]
            if dentro and any(saida[k]["MAX_APPLICATIONS"] != "NOT_PRESENT"
                              for k in bloco):
                for k in bloco:
                    if saida[k]["MAX_APPLICATIONS"] != "NOT_PRESENT":
                        continue
                    fc = (faixa_de[k][0] + faixa_de[k][1]) / 2
                    perto = min(dentro, key=lambda c: abs(_c(c) - fc))
                    m = RE_MAXPAR.match(norm_valor(perto["txt"]))
                    saida[k]["MAX_APPLICATIONS"] = m.group(1)
                    saida[k]["MAX_APPLICATIONS_INHERITED"] = True
                    saida[k]["_extra_quote"].append(perto["txt"])
                    if m.group(2) and saida[k]["APPLICATION_INTERVAL"] == "NOT_PRESENT":
                        saida[k]["APPLICATION_INTERVAL"] = f"{m.group(2)} giorni"
                        saida[k]["APPLICATION_INTERVAL_INHERITED"] = True
            ini = fim

    # CELULA DE DOSE MESCLADA VERTICALMENTE (contrato secao 5b): so quando a
    # geometria PROVA a mescla — a coluna tem UMA unica celula de dose dentro do
    # bloco da cultura, o bloco tem mais de uma linha, e o texto dessa celula
    # esta VERTICALMENTE CENTRADO no bloco (e o que a tipografia de celula
    # mesclada faz). Com duas ou mais celulas no bloco nao ha mescla: a celula
    # vazia e vazia mesmo — e o caso "Agrumi / Cocciniglie", cuja celula g/ha e
    # ruled-and-empty no documento. Toda linha que recebe marca *_INHERITED.
    for papel, campo in ((("DOSE_HA", "DOSE_PER_HECTARE"),
                         ("DOSE_CONC", "DOSE_CONCENTRATION"))
                         if not os.environ.get("DOSE_SEM_MESCLA") else ()):
        ic = idx.get(papel)
        if ic is None or not cel.get(ic) or not saida:
            continue
        cds = [c for c in cel[ic] if RE_VALOR.match(norm_valor(c["txt"]))]
        ini = 0
        for fim in [k for k in range(1, len(saida) + 1)
                    if k == len(saida) or saida[k]["CROP"] != saida[k - 1]["CROP"]]:
            bloco = list(range(ini, fim))
            ini = fim
            if len(bloco) < 2:
                continue
            y0b = min(faixa_de[k][0] for k in bloco)
            y1b = max(faixa_de[k][1] for k in bloco)
            alt = y1b - y0b
            dentro = [c for c in cds if y0b <= _c(c) <= y1b]
            if len(dentro) != 1 or alt <= 0:
                continue
            if abs(_c(dentro[0]) - (y0b + y1b) / 2) > 0.30 * alt:
                continue          # nao esta centrado: nao e celula mesclada
            val = norm_valor(dentro[0]["txt"])
            if not any(saida[k][campo] == val for k in bloco):
                continue          # o valor nem chegou a ser lido: nao inventa
            for k in bloco:
                if saida[k][campo] != "NOT_PRESENT":
                    continue
                saida[k][campo] = val
                saida[k][campo + "_INHERITED"] = True
                saida[k][campo + "_UNIT"] = unids.get(papel) or "NOT_PRESERVED"
                saida[k]["_extra_quote"].append(dentro[0]["txt"])

    def util(r):
        if not re.match(r"[\wÀ-ÿ]", r["CROP"] or ""):
            return False                      # nota de rodape, asterisco, aspas
        if r["TARGET"] == "NOT_PRESENT" or r["CROP"] == "NOT_PRESENT":
            return False
        if any(r[k] != "NOT_PRESENT" for k in
               ("DOSE_CONCENTRATION", "DOSE_PER_HECTARE",
                "MAX_APPLICATIONS", "APPLICATION_INTERVAL")):
            return True
        # sem numero nenhum: so sobrevive se a tabela tem coluna de dose viva
        return ndose >= 3
    out = []
    for r in saida:
        if not util(r):
            continue
        extra = [t for t in dict.fromkeys(r.pop("_extra_quote", []))
                 if t and t not in r["SOURCE_QUOTE"]]
        if extra:
            r["SOURCE_QUOTE"] = (r["SOURCE_QUOTE"] + " [celula mesclada: "
                                 + " | ".join(extra) + "]")
        out.append(r)
    return out


def montar(rid, produto, crop, herdada, alvo, get, unids, quote, pg):
    def dose(papel):
        v = norm_valor(get(papel))
        if not v or not RE_VALOR.match(v):
            return "NOT_PRESENT", "NOT_PRESENT"
        return v, unids.get(papel) or "NOT_PRESERVED"
    d_conc, u_conc = dose("DOSE_CONC")
    d_ha, u_ha = dose("DOSE_HA")
    mx, iv = "NOT_PRESENT", "NOT_PRESENT"
    tm = norm_valor(get("MAX"))
    m = RE_MAXPAR.match(tm) if tm else None
    if m:
        mx = m.group(1)
        if m.group(2):
            iv = f"{m.group(2)} giorni"
    ti = norm_valor(get("INTERVAL"))
    if iv == "NOT_PRESENT" and ti and RE_VALOR.match(ti):
        iv = f"{ti} giorni"
    if mx == "NOT_PRESENT" or iv == "NOT_PRESENT":
        nota = " ".join(x for x in (get("NOTE"), get("EPOCA")) if x)
        if nota:
            ns = [int(x) for x in RE_NOTA_N.findall(nota)]
            if ns and mx == "NOT_PRESENT":
                mx = str(min(ns)) if min(ns) == max(ns) else f"{min(ns)}-{max(ns)}"
            mi = RE_NOTA_IV.search(nota)
            if mi and iv == "NOT_PRESENT":
                iv = norm_valor(mi.group(1)) + " giorni"
    fora = []
    for papel in ("DOSE_CONC", "DOSE_HA", "MAX", "INTERVAL"):
        t = (get(papel) or "").strip()
        if t and RE_TEMNUM.search(t) and t not in quote:
            fora.append(t)
    if fora:
        quote = quote + " [celula mesclada: " + " | ".join(dict.fromkeys(fora)) + "]"
    return {
        "REGISTRATION_ID": rid,
        "PRODUCT": produto,
        "CROP": crop or "NOT_PRESENT",
        "CROP_INHERITED": herdada,
        "TARGET": alvo or "NOT_PRESENT",
        "DOSE_CONCENTRATION": d_conc,
        "DOSE_CONCENTRATION_UNIT": u_conc,
        "DOSE_PER_HECTARE": d_ha,
        "DOSE_PER_HECTARE_UNIT": u_ha,
        "MAX_APPLICATIONS": mx,
        "MAX_APPLICATIONS_INHERITED": False,
        "APPLICATION_INTERVAL": iv,
        "APPLICATION_INTERVAL_INHERITED": False,
        "DOSE_CONCENTRATION_INHERITED": False,
        "DOSE_PER_HECTARE_INHERITED": False,
        "SOURCE_QUOTE": quote,
        "SOURCE_PAGE": pg,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--rid", required=True)
    ap.add_argument("--produto", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    r = extrair(a.pdf, a.rid, a.produto)
    if a.json:
        json.dump(r, sys.stdout, ensure_ascii=False, indent=1)
    else:
        print(f"{r['PARSE_STATE']}  colunas={r.get('COLUMNS_DETECTED')} "
              f"unidades={r.get('UNITS_DETECTED')}  linhas={len(r['ROWS'])}")
        for x in r["ROWS"][:200]:
            print(f"  {x['CROP'][:26]:<26} | {x['TARGET'][:34]:<34} | "
                  f"{x['DOSE_CONCENTRATION']:>10} {x['DOSE_CONCENTRATION_UNIT']:<9} | "
                  f"{x['DOSE_PER_HECTARE']:>10} {x['DOSE_PER_HECTARE_UNIT']:<8} | "
                  f"max {x['MAX_APPLICATIONS']:<4} iv {x['APPLICATION_INTERVAL']:<12} p{x['SOURCE_PAGE']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
