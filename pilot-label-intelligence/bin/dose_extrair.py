#!/usr/bin/env python3
"""
dose_extrair.py — le a tabela CAMPI DI IMPIEGO E DOSI da etichetta oficial.

Por que existe: cultura x alvo ja e lido pela casa (it_rotulo_parser 3.4.0, em
sintonia/canonical, 2.928 pares sobre 163 rotulos). DOSE nao. Nenhum script da
casa extrai dose, unidade, intervalo ou numero maximo de aplicacoes — a busca
por chaves de dose nos 2.928 pares publicados devolve zero. Este extrator abre
exatamente esse buraco, e so ele.

Como le: geometria, nao texto corrido. `pdftotext -bbox-layout` da coordenada de
cada palavra; a tabela e reconstruida por coluna (x) e por linha (y). Ler a
tabela como texto corrido embaralha dose com alvo na primeira celula mesclada.

O que ele NAO faz, e por que isso esta escrito aqui:
  - nao inventa dose para linha que nao tem dose na tabela  -> NOT_PRESENT
  - nao herda dose de outra linha                           -> so cultura e herdada,
    e quando herdada a linha carrega CROP_INHERITED = True
  - nao promove numero solto a dose sem cabecalho de coluna -> descarta
  - toda linha emitida carrega SOURCE_QUOTE e SOURCE_PAGE

    PARSER_FAILURE != REGULATORY_ABSENCE
"""
import argparse, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/1999/xhtml}"

# Cabecalhos de coluna, em italiano de etichetta. A chave e o papel da coluna.
COLUNAS = [
    ("CROP",             re.compile(r"^coltur", re.I)),
    ("TARGET",           re.compile(r"^(parassit|avversit|patogen|infestant|malattie)", re.I)),
    ("DOSE_CONC",        re.compile(r"^dos[ie]$", re.I)),
    ("DOSE_HA",          re.compile(r"^dos[ie]$", re.I)),
    ("MAX_APPLICATIONS", re.compile(r"^(n|n°|numero)$|applicazion", re.I)),
    ("PHI",              re.compile(r"^(intervallo|carenza|tempo)", re.I)),
    ("EPOCA",            re.compile(r"^(epoca|momento|fase)", re.I)),
]
TITULO_SECAO = re.compile(r"CAMPI\s+DI\s+IMPIEGO|DOSI\s+D[’'\s]?IMPIEGO|MODALIT.\s+D[’'\s]?IMPIEGO\s+E\s+DOSI", re.I)

# Uma dose e um numero (ou faixa) com unidade agronomica plausivel, ou um numero
# nu dentro de uma coluna cujo cabecalho ja declarou a unidade.
NUMERO = r"\d+(?:[.,]\d+)?"
RE_FAIXA = re.compile(rf"^{NUMERO}(?:\s*[-–]\s*{NUMERO})?$")
RE_MAX = re.compile(rf"^(?:max\.?\s*)?({NUMERO})(?:\s*\(\s*(\d+)\s*giorni?\s*\))?$", re.I)
RE_UNIDADE = re.compile(r"(g|kg|l|ml|cc)\s*/\s*(ha|hl|100\s*l(?:t|itri)?|mq|m2|pianta)", re.I)


def geometria(pdf, cache=None):
    """XML de geometria do PDF. Usa cache quando ja existe."""
    if cache and os.path.exists(cache):
        return open(cache, encoding="utf-8", errors="replace").read()
    out = (cache or pdf) + ".bbox.xml"
    subprocess.run(["pdftotext", "-bbox-layout", pdf, out],
                   check=True, capture_output=True)
    return open(out, encoding="utf-8", errors="replace").read()


def palavras(xml):
    """[(pagina, xmin, xmax, ymin, ymax, texto)] de todo o documento."""
    root = ET.fromstring(xml)
    out = []
    for pno, page in enumerate(root.iter(f"{NS}page"), 1):
        for w in page.iter(f"{NS}word"):
            t = (w.text or "").strip()
            if not t:
                continue
            out.append((pno, float(w.get("xMin")), float(w.get("xMax")),
                        float(w.get("yMin")), float(w.get("yMax")), t))
    return out


def linhas(ws, tol=3.0):
    """Agrupa palavras em linhas visuais por proximidade vertical."""
    out, cur, ref = [], [], None
    for w in sorted(ws, key=lambda w: (w[0], round(w[3], 1), w[1])):
        if ref is None or w[0] != ref[0] or abs(w[3] - ref[3]) > tol:
            if cur:
                out.append(sorted(cur, key=lambda w: w[1]))
            cur, ref = [w], w
        else:
            cur.append(w)
    if cur:
        out.append(sorted(cur, key=lambda w: w[1]))
    return out


def achar_cabecalho(ls):
    """Acha a linha de cabecalho da tabela de usos e devolve as colunas (papel, x)."""
    for i, ln in enumerate(ls):
        texto = " ".join(w[5] for w in ln)
        if not re.search(r"coltur", texto, re.I):
            continue
        cols, usados = [], set()
        for w in ln:
            for papel, rx in COLUNAS:
                if papel in usados:
                    continue
                if rx.match(w[5]):
                    cols.append([papel, w[1], w[2]])
                    usados.add(papel)
                    break
        # Precisa de pelo menos cultura + alvo + alguma coluna de dose.
        papeis = {c[0] for c in cols}
        if "CROP" in papeis and ("TARGET" in papeis) and (papeis & {"DOSE_CONC", "DOSE_HA"}):
            return i, sorted(cols, key=lambda c: c[1])
    return None, None


def unidade_da_coluna(ls, i, cols):
    """A unidade costuma vir na linha seguinte ao cabecalho: '(g/100 lt)', '(g/ha)'."""
    un = {}
    for ln in ls[i:i + 4]:
        for w in ln:
            m = RE_UNIDADE.search(w[5].replace("(", "").replace(")", ""))
            if not m:
                continue
            centro = (w[1] + w[2]) / 2
            alvo = min(cols, key=lambda c: abs((c[1] + c[2]) / 2 - centro))
            un.setdefault(alvo[0], m.group(0).replace(" ", ""))
    return un


def fronteiras(cols):
    """Ponto de corte entre colunas: meio do vao entre uma e a seguinte."""
    xs = []
    for a, b in zip(cols, cols[1:]):
        xs.append((a[2] + b[1]) / 2)
    return xs


def coluna_de(x, cols, cortes):
    for k, corte in enumerate(cortes):
        if x < corte:
            return cols[k][0]
    return cols[-1][0]


def extrair(pdf, rid, produto=None, cache=None, pagina_limite=None):
    xml = geometria(pdf, cache)
    ws = palavras(xml)
    ls = linhas(ws)
    i, cols = achar_cabecalho(ls)
    if i is None:
        return {"REGISTRATION_ID": rid, "PRODUCT": produto,
                "PARSE_STATE": "NO_USE_TABLE_FOUND",
                "NOTE": ("nenhuma tabela com cabecalho Coltura + alvo + dose foi "
                         "localizada. Isto e falha ou ausencia de LEITURA, "
                         "nao ausencia regulatoria."),
                "ROWS": []}
    unid = unidade_da_coluna(ls, i, cols)
    cortes = fronteiras(cols)
    linhas_tab = []
    crop_atual = None
    pagina_cab = ls[i][0][0]
    for ln in ls[i + 1:]:
        pg = ln[0][0]
        if pagina_limite and pg > pagina_cab + pagina_limite:
            break
        celulas = {c[0]: [] for c in cols}
        for w in ln:
            celulas[coluna_de((w[1] + w[2]) / 2, cols, cortes)].append(w[5])
        celulas = {k: " ".join(v).strip() for k, v in celulas.items()}
        quote = " ".join(w[5] for w in ln).strip()
        # Uma nova secao/tabela reinicia o cabecalho: para de herdar cultura.
        if re.search(r"^coltur", celulas.get("CROP", ""), re.I):
            crop_atual = None
            continue
        if celulas.get("CROP"):
            crop_atual = celulas["CROP"]
        alvo = celulas.get("TARGET", "")
        if not alvo:
            continue
        herdada = not celulas.get("CROP")
        if not crop_atual:
            continue
        linhas_tab.append(montar(rid, produto, crop_atual, herdada, alvo,
                                 celulas, unid, quote, pg))
    return {"REGISTRATION_ID": rid, "PRODUCT": produto,
            "PARSE_STATE": "USE_TABLE_READ" if linhas_tab else "TABLE_FOUND_NO_ROWS",
            "COLUMNS_DETECTED": [c[0] for c in cols],
            "UNITS_DETECTED": unid,
            "ROWS": linhas_tab}


def montar(rid, produto, crop, herdada, alvo, cel, unid, quote, pg):
    def dose(papel):
        v = cel.get(papel, "").strip()
        if not v or not RE_FAIXA.match(v.replace("- ", "-").replace(" -", "-")):
            return "NOT_PRESENT", "NOT_PRESENT"
        return v, unid.get(papel, "NOT_PRESERVED")
    d_conc, u_conc = dose("DOSE_CONC")
    d_ha, u_ha = dose("DOSE_HA")
    mx, iv = "NOT_PRESENT", "NOT_PRESENT"
    m = RE_MAX.match(cel.get("MAX_APPLICATIONS", "").strip())
    if m:
        mx = m.group(1)
        iv = f"{m.group(2)} giorni" if m.group(2) else "NOT_PRESENT"
    return {
        "REGISTRATION_ID": rid,
        "PRODUCT": produto,
        "CROP": crop,
        "CROP_INHERITED": herdada,
        "TARGET": alvo,
        "DOSE_CONCENTRATION": d_conc,
        "DOSE_CONCENTRATION_UNIT": u_conc,
        "DOSE_PER_HECTARE": d_ha,
        "DOSE_PER_HECTARE_UNIT": u_ha,
        "MAX_APPLICATIONS": mx,
        "APPLICATION_INTERVAL": iv,
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
        for x in r["ROWS"][:40]:
            print(f"  {x['CROP'][:26]:<26} | {x['TARGET'][:30]:<30} | "
                  f"{x['DOSE_CONCENTRATION']:>10} {x['DOSE_CONCENTRATION_UNIT']:<9} | "
                  f"{x['DOSE_PER_HECTARE']:>10} {x['DOSE_PER_HECTARE_UNIT']:<6} | "
                  f"max {x['MAX_APPLICATIONS']:<4} iv {x['APPLICATION_INTERVAL']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
