#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EXTRATOR-LUGAR-V2 · ESTIMATIVA (nao e medida do extrator): quantos itens SEM lugar do facto teriam um comune
com SIGLA «Nome (XX)» governado por uma ancora de acontecimento — o que a lista oficial do ISTAT resolveria.
So leitura: os textos derivados da ACERVO (sha256 conferido). Teto superior: nao sabe se o nome e mesmo um comune."""
import collections, hashlib, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "leis"))
import fato_local as FL  # noqa: E402
import fato_do_texto as T  # noqa: E402

o = sys.argv[1]
D = {x["SHA256"]: x for x in json.load(open(o + "/depois.json", encoding="utf-8"))["ITENS"]}
ders = {d["id"]: d for d in json.load(open("C:/Users/London1/reproc-acervo/derivados.json", encoding="utf-8"))}
raizes = open("C:/Users/London1/reproc-acervo/raizes.txt", encoding="utf-8").read().strip().split(";")
RE_SIGLA = re.compile(r"([A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+(?:[\s-][A-ZÀ-Ý][A-Za-zÀ-ÿ'’]+){0,3})\s*\(\s*([A-Z]{2})\s*\)")
c, exemplos = collections.Counter(), []
for s, x in D.items():
    if x["PREVISTO"]["LOCAL_DO_FATO"]["VALOR"] not in ("NAO SEI", "", None) or not x.get("DERIVADO_LIDO"):
        continue
    d = ders.get(x["DERIVADO_LIDO"])
    t = None
    for rz in raizes:
        p = os.path.join(rz, d["storage_path"])
        if os.path.exists(p):
            b = open(p, "rb").read()
            if hashlib.sha256(b).hexdigest() == d["sha256"].strip():
                t = b.decode("utf-8", "replace"); break
    if not t:
        continue
    c["sem_lugar_com_texto"] += 1
    achou = False
    for frase in FL._frases(T.corpo(t)):
        pos = FL._ancoras(frase, FL.ANCORAS_POSITIVAS)
        if not pos:
            continue
        for m in RE_SIGLA.finditer(frase):
            if any(a["POS"] < m.start() for a in pos):
                achou = True
                if len(exemplos) < 15:
                    exemplos.append((x["SOURCE_ID"], "%s (%s)" % (m.group(1), m.group(2)), frase[:160]))
                break
        if achou:
            break
    c["com_comune_e_sigla_governado"] += achou
print(json.dumps(dict(c), ensure_ascii=False))
for e in exemplos:
    print(" ", e)
