#!/usr/bin/env python3
"""
phi_extrair.py — le o tempo de carencia da etichetta (PHI).

PHI = intervallo tra l'ultimo trattamento e la raccolta. E o numero de dias entre
a ultima aplicacao e a colheita, e e a informacao que decide se o produto pode ou
nao ser usado numa janela agronomica.

Por que existe: `it_rotulo_parser` da casa lista essa secao em SECAO_PROIBIDA,
isto e, a exclui DE PROPOSITO da geracao de pares. Entao o PHI nao esta em
nenhuma ref, em nenhum pais. Assim como a dose, e camada nova.

A secao tem forma propria e nao e a tabela de usos: e uma lista curta de
"cultura(s) -> N giorni", frequentemente com varias culturas por linha separadas
por virgula. Por isso este extrator e separado do de dose, em vez de virar mais
uma coluna la dentro.

Nao inventa: cultura sem numero de dias na secao nao vira linha.

## ESTADO: PROTOTIPO. NAO ENTRA NA DEMO.

Medido sobre os 15 produtos da demo, e o resultado nao passa no proprio criterio
deste piloto:

    2 de 15 rotulos com carencia lida, 20 linhas
    8 de 15 com a secao localizada mas nenhuma linha extraida
    5 de 15 sem secao localizada

E das 20 linhas lidas, a PRIMEIRA de cada bloco esta contaminada: DURAVIS trouxe
"Particolare sensibilita da parte di -> 7 giorni" e ELTIRA trouxe
"H332-Nocivo se inalato. delle acque dalle strade -> 3 giorni". As demais
("Arancio", "limone", "actinidia", "Barbabietola da zucchero", "Aglio",
"cocomero"...) estao corretas.

A causa e a mesma que derrubou a recuperacao de citacao em `citar.py`: a linha
visual atravessa colunas, e sem restringir por **x** o texto da coluna vizinha
entra junto. O conserto e conhecido e nao e novo — e a deteccao de coluna por
cabecalho que `dose_extrair.py` ja faz. Enquanto ele nao for aplicado aqui, este
extrator nao alimenta a tela.

    PHI_EXTRACTION_STATE = PROTOTYPE_NOT_SHIPPED

Publicar 20 linhas com uma contaminada em cada bloco seria entregar ao cliente um
tempo de carencia associado a uma frase de perigo. Melhor nada.
"""
import argparse, json, os, re, subprocess, sys
import xml.etree.ElementTree as ET

NS = "{http://www.w3.org/1999/xhtml}"

TITULO = re.compile(
    r"(intervallo\s+(?:di\s+sicurezza|tra\s+l['’]?\s*ultimo\s+trattamento)"
    r"|tempo\s+di\s+carenza|periodo\s+di\s+carenza)", re.I)
# "3 giorni", "20 gg", "14 giorni", "n.c." (non classificato / non richiesto)
DIAS = re.compile(r"^(\d{1,3})\s*(?:gg|giorni|giorno)?$", re.I)
FIM = re.compile(r"(DIVIETO|ATTENZIONE|PRESCRIZIONI|INFORMAZIONI\s+PER\s+IL\s+MEDICO|"
                 r"SMALTIMENTO|COMPATIBILIT|FITOTOSSICIT|AVVERTENZ|ETICHETTA)", re.I)


def geometria(pdf, cache=None):
    if cache and os.path.exists(cache):
        return open(cache, encoding="utf-8", errors="replace").read()
    out = (cache or pdf) + ".bbox.xml"
    subprocess.run(["pdftotext", "-bbox-layout", pdf, out], check=True, capture_output=True)
    return open(out, encoding="utf-8", errors="replace").read()


def linhas(xml, tol=3.0):
    root = ET.fromstring(xml)
    out = []
    for pno, page in enumerate(root.iter(f"{NS}page"), 1):
        ws = []
        for w in page.iter(f"{NS}word"):
            t = (w.text or "").strip()
            if t:
                ws.append((pno, float(w.get("xMin")), float(w.get("yMin")), t))
        cur, ref = [], None
        for w in sorted(ws, key=lambda w: (round(w[2], 1), w[1])):
            if ref is None or abs(w[2] - ref[2]) > tol:
                if cur:
                    out.append(cur)
                cur, ref = [w], w
            else:
                cur.append(w)
        if cur:
            out.append(cur)
    return out


def extrair(pdf, rid, produto=None, cache=None, max_linhas=40):
    ls = linhas(geometria(pdf, cache))
    inicio = None
    for i, ln in enumerate(ls):
        if TITULO.search(" ".join(w[3] for w in ln)):
            inicio = i
            break
    if inicio is None:
        return {"REGISTRATION_ID": rid, "PRODUCT": produto,
                "PARSE_STATE": "NO_PHI_SECTION_FOUND",
                "NOTE": ("nenhuma secao de tempo de carencia localizada. Estado de LEITURA: "
                         "nao afirma que o produto nao tem carencia declarada."),
                "ROWS": []}
    rows = []
    for ln in ls[inicio:inicio + max_linhas]:
        txt = " ".join(w[3] for w in ln).strip()
        if FIM.search(txt) and rows:
            break
        # a linha util termina com o numero de dias
        m = re.search(r"(.+?)\s+(\d{1,3})\s*(?:gg|giorni|giorno)\s*$", txt, re.I)
        if not m:
            continue
        culturas, dias = m.group(1), int(m.group(2))
        culturas = TITULO.sub("", culturas).strip(" :.-–")
        if not culturas or len(culturas) < 3:
            continue
        for c in re.split(r"\s*[,;]\s*|\s+e\s+", culturas):
            c = c.strip(" .:-–()")
            if len(c) < 3 or DIAS.match(c):
                continue
            rows.append({
                "REGISTRATION_ID": rid, "PRODUCT": produto,
                "CROP": c, "PHI_DAYS": dias, "PHI_UNIT": "giorni",
                "SOURCE_QUOTE": txt[:300], "SOURCE_PAGE": ln[0][0],
            })
    return {"REGISTRATION_ID": rid, "PRODUCT": produto,
            "PARSE_STATE": "PHI_READ" if rows else "PHI_SECTION_FOUND_NO_ROWS",
            "ROWS": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfdir", default="pilot-label-intelligence/labels/pdf")
    ap.add_argument("--dados", default="pilot-label-intelligence/demo/IT-LABEL-INTELLIGENCE.json")
    ap.add_argument("--demo", default="pilot-label-intelligence/demo/IT-DEMO-PRODUTOS.json")
    ap.add_argument("--cachedir", default=None)
    ap.add_argument("--out", default="pilot-label-intelligence/demo/IT-PHI.json")
    a = ap.parse_args()
    d = json.load(open(a.dados, encoding="utf-8"))
    nomes = {p["REGISTRATION_ID"]: p["PRODUCT"] for p in d["PRODUCTS"]}
    alvos = [x["REGISTRATION_ID"] for x in json.load(open(a.demo, encoding="utf-8"))["PRODUCTS"]]

    labels, com, tot = [], 0, 0
    for reg in alvos:
        pdf = os.path.join(a.pdfdir, f"{reg}.pdf")
        if not os.path.exists(pdf):
            labels.append({"REGISTRATION_ID": reg, "PRODUCT": nomes.get(reg),
                           "PARSE_STATE": "PDF_NOT_ON_DISK", "ROWS": []})
            continue
        try:
            r = extrair(pdf, reg, nomes.get(reg),
                        cache=(os.path.join(a.cachedir, f"{reg}.xml") if a.cachedir else None))
        except Exception as e:
            r = {"REGISTRATION_ID": reg, "PRODUCT": nomes.get(reg),
                 "PARSE_STATE": "PARSER_ERROR", "ERROR": type(e).__name__, "ROWS": []}
        labels.append(r)
        n = len(r["ROWS"]); tot += n; com += bool(n)
        print(f'  {reg} {str(nomes.get(reg))[:24]:<24} {r["PARSE_STATE"]:<26} linhas={n}',
              file=sys.stderr)

    out = {"DATASET": "IT-PHI",
           "O_QUE_ISTO_E": "tempo de carencia por cultura, lido da etichetta oficial",
           "O_QUE_ISTO_NAO_E": ("nao existe em nenhuma ref da casa: o parser de canonical lista "
                                "esta secao em SECAO_PROIBIDA e a exclui de proposito"),
           "LABELS_ATTEMPTED": len(labels), "LABELS_WITH_ROWS": com, "TOTAL_PHI_ROWS": tot,
           "REGRA": "cultura sem numero de dias na secao nao vira linha",
           "LABELS": labels}
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f'\n  {com}/{len(labels)} rotulos com carencia lida | {tot} linhas', file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
