#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""LEITOR-DATA-YOUTUBE · 20 lidos a mao: 20 dos que ganham publicacao, ao acaso (semente fixa).
Para cada um, ao lado da data lida, o que a PROPRIA pagina diz noutros sitios: o `publishDate`
do microformat do player, a data que o leitor ve (`dateText`) e o titulo. So leitura."""
import hashlib, html, json, os, random, re, sys

o = sys.argv[1]
C = json.load(open(o + "/COMPARACAO.json", encoding="utf-8"))
D = json.load(open(o + "/depois.json", encoding="utf-8"))
raws = json.load(open("C:/Users/London1/reproc-acervo/raw.json", encoding="utf-8"))
raizes = open("C:/Users/London1/reproc-acervo/raizes.txt", encoding="utf-8").read().strip().split(";")
ganhou = [x for x in D["ITENS"] if x["PREVISTO"]["PUBLICACAO"]["BASE"] == "meta itemprop datePublished"]
random.seed(20260926)
amostra = random.sample(ganhou, 20)
por_id = {r["id"]: r for r in raws}
linhas = []
for x in amostra:
    r = por_id[x["RAW_IDS"][0]]
    b = None
    for rz in raizes:
        p = os.path.join(rz, r["storage_path"])
        if os.path.exists(p):
            y = open(p, "rb").read()
            if hashlib.sha256(y).hexdigest() == x["SHA256"]:
                b = y; break
    t = b.decode("utf-8", "replace")
    tit = re.search(r'<meta name="title" content="([^"]*)"', t)
    pub = re.findall(r'"publishDate":"([^"]+)"', t)
    vis = re.findall(r'"dateText":\{"simpleText":"([^"]+)"\}', t)
    lida = x["PREVISTO"]["PUBLICACAO"]["VALOR"]
    linhas.append({"SOURCE_ID": x["SOURCE_ID"], "RAW": x["RAW_IDS"][0], "URL": r["source_url"],
                   "TITULO": html.unescape(tit.group(1))[:90] if tit else "?",
                   "LIDA": lida, "PUBLISHDATE_DO_PLAYER": pub[:1], "DATA_VISIVEL": vis[:1],
                   "BATE_COM_O_PLAYER": bool(pub) and pub[0][:10] == lida[:10],
                   "FACTO_NAO_MEXEU": x["PREVISTO"]["DATA_DO_FATO"] == next(
                       i for i in json.load(open(o + "/antes.json", encoding="utf-8"))["ITENS"] if i["SHA256"] == x["SHA256"])["PREVISTO"]["DATA_DO_FATO"]})
json.dump(linhas, open(o + "/LIDOS-A-MAO-20.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for l in linhas:
    print("%-10s %5s %-26s player=%-27s visivel=%-14s bate=%s facto_igual=%s | %s" % (
        l["SOURCE_ID"], l["RAW"], l["LIDA"], (l["PUBLISHDATE_DO_PLAYER"] or ["-"])[0], (l["DATA_VISIVEL"] or ["-"])[0],
        l["BATE_COM_O_PLAYER"], l["FACTO_NAO_MEXEU"], l["TITULO"][:60]))
print("bate com o player: %d de 20 · data do facto igual: %d de 20" % (sum(l["BATE_COM_O_PLAYER"] for l in linhas), sum(l["FACTO_NAO_MEXEU"] for l in linhas)))
